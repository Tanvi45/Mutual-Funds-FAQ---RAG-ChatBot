import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from document_loader import DocumentLoader

class Chunker:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def chunk_documents(self, documents):
        """Chunk loaded documents"""
        print("Chunking documents...")
        all_chunks = []
        chunk_id = 0
        
        for doc in documents:
            print(f"Chunking {doc['source_id']}...")
            chunks = self.splitter.split_text(doc['text'])
            
            for chunk_text in chunks:
                all_chunks.append({
                    "chunk_id": f"chunk_{chunk_id}",
                    "source_id": doc['source_id'],
                    "source_name": doc['source_name'],
                    "source_url": doc['source_url'],
                    "text": chunk_text
                })
                chunk_id += 1
            
            print(f"[OK] Created {len(chunks)} chunks from {doc['source_id']}")
        
        # Save chunks
        chunks_dir = "data/chunks"
        os.makedirs(chunks_dir, exist_ok=True)
        chunks_path = os.path.join(chunks_dir, "chunks.json")
        
        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, indent=2)
        
        print(f"\nChunking complete. {len(all_chunks)} chunks created and saved to {chunks_path}")
        return all_chunks

def main():
    # Load documents first
    loader = DocumentLoader()
    documents = loader.load_documents()
    
    # Chunk them
    chunker = Chunker(chunk_size=500, chunk_overlap=50)
    chunks = chunker.chunk_documents(documents)
    return chunks

if __name__ == "__main__":
    main()
