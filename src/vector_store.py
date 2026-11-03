import os
import json
import chromadb

class VectorStore:
    def __init__(self, persist_directory="./chroma", collection_name="hdfc_mf_faq"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def index_documents(self, embeddings_path="data/embeddings/embeddings.json"):
        """Index documents with embeddings into ChromaDB"""
        print("Indexing documents into ChromaDB...")
        
        # Load embedded chunks
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            embedded_chunks = json.load(f)
        
        ids = []
        documents = []
        embeddings = []
        metadatas = []
        
        for chunk in embedded_chunks:
            ids.append(chunk['chunk_id'])
            documents.append(chunk['text'])
            embeddings.append(chunk['embedding'])
            metadatas.append({
                "source_id": chunk['source_id'],
                "source_name": chunk['source_name'],
                "source_url": chunk['source_url']
            })
        
        # Upsert into collection
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        print(f"Indexed {len(ids)} documents into collection '{self.collection_name}'")
        print(f"Collection count: {self.collection.count()}")
        return self.collection

def main():
    store = VectorStore()
    store.index_documents()

if __name__ == "__main__":
    main()
