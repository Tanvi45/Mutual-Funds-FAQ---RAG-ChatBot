import os
import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

# Add new source only
NEW_SOURCE = {
    "id": "amfi_elss_lockin",
    "name": "AMFI - Categorization of Mutual Fund Schemes",
    "url": "https://www.amfiindia.com/investor/knowledge-center-info?zoneName=CategorizationOfMutualFundSchemes"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

raw_dir = "data/raw"
os.makedirs(raw_dir, exist_ok=True)

# Load existing metadata
metadata_path = os.path.join(raw_dir, "metadata.json")
with open(metadata_path, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# Check if already added
existing_ids = {m['source_id'] for m in metadata}
if NEW_SOURCE['id'] in existing_ids:
    print(f"[SKIP] {NEW_SOURCE['id']} already in metadata")
else:
    print(f"Scraping {NEW_SOURCE['name']}...")
    response = requests.get(NEW_SOURCE['url'], headers=HEADERS, timeout=30)
    response.raise_for_status()
    
    html_path = os.path.join(raw_dir, f"{NEW_SOURCE['id']}.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    for element in soup(['nav', 'header', 'footer', 'script', 'style', 'aside', 'iframe']):
        element.decompose()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks_clean = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks_clean if chunk)
    
    txt_path = os.path.join(raw_dir, f"{NEW_SOURCE['id']}.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    metadata.append({
        "source_id": NEW_SOURCE['id'],
        "name": NEW_SOURCE['name'],
        "url": NEW_SOURCE['url'],
        "fetched_at": datetime.now().isoformat(),
        "html_path": html_path,
        "txt_path": txt_path,
        "content_length": len(text)
    })
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"[OK] Saved {NEW_SOURCE['id']}.txt ({len(text)} chars)")

# Load document
with open(os.path.join(raw_dir, f"{NEW_SOURCE['id']}.txt"), 'r', encoding='utf-8') as f:
    doc_text = f.read()

document = {
    "source_id": NEW_SOURCE['id'],
    "source_name": NEW_SOURCE['name'],
    "source_url": NEW_SOURCE['url'],
    "text": doc_text
}

# Chunk
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
)
chunks = text_splitter.split_text(doc_text)
print(f"Created {len(chunks)} new chunks")

# Append to chunks.json
chunks_path = "data/chunks/chunks.json"
with open(chunks_path, 'r', encoding='utf-8') as f:
    all_chunks = json.load(f)

new_chunk_records = []
for i, chunk_text in enumerate(chunks):
    chunk_id = f"{NEW_SOURCE['id']}_chunk_{i}"
    new_chunk_records.append({
        "chunk_id": chunk_id,
        "source_id": NEW_SOURCE['id'],
        "source_name": NEW_SOURCE['name'],
        "source_url": NEW_SOURCE['url'],
        "text": chunk_text,
        "chunk_index": i
    })

all_chunks.extend(new_chunk_records)
with open(chunks_path, 'w', encoding='utf-8') as f:
    json.dump(all_chunks, f, indent=2)
print(f"Appended to chunks.json. Total chunks now: {len(all_chunks)}")

# Embed only new chunks
embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
new_embeddings = embedder.encode([c['text'] for c in new_chunk_records], convert_to_numpy=True)
new_embeddings_list = new_embeddings.tolist()

embeddings_path = "data/embeddings/embeddings.json"
with open(embeddings_path, 'r', encoding='utf-8') as f:
    all_embeddings = json.load(f)

for rec, emb in zip(new_chunk_records, new_embeddings_list):
    all_embeddings.append({
        "chunk_id": rec['chunk_id'],
        "embedding": emb
    })

with open(embeddings_path, 'w', encoding='utf-8') as f:
    json.dump(all_embeddings, f, indent=2)
print(f"Appended embeddings. Total embeddings now: {len(all_embeddings)}")

# Upsert into existing Chroma collection
client = chromadb.PersistentClient(path="./chroma")
collection = client.get_collection(name="hdfc_mf_faq")

ids = [c['chunk_id'] for c in new_chunk_records]
documents = [c['text'] for c in new_chunk_records]
metadatas = [{
    "source_id": c['source_id'],
    "source_name": c['source_name'],
    "source_url": c['source_url'],
    "chunk_index": c['chunk_index']
} for c in new_chunk_records]
embeddings = new_embeddings_list

collection.upsert(
    ids=ids,
    documents=documents,
    metadatas=metadatas,
    embeddings=embeddings
)

print(f"Upserted {len(ids)} chunks into collection 'hdfc_mf_faq'")
print(f"Collection count: {collection.count()}")
