import chromadb
from sentence_transformers import SentenceTransformer

class Retriever:
    def __init__(self, persist_directory="./chroma", collection_name="hdfc_mf_faq", 
                 model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_collection(collection_name)
        self.model = SentenceTransformer(model_name)
    
    def retrieve(self, query, top_k=80, similarity_threshold=0.3):
        """Retrieve relevant chunks for a query"""
        print(f"Retrieving for query: '{query}'")
        
        # Embed query
        query_embedding = self.model.encode([query])[0].tolist()
        
        # Query vector DB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        retrieved = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                distance = results['distances'][0][i] if results['distances'] else 1.0
                # Convert distance to similarity (for cosine, similarity = 1 - distance)
                similarity = 1 - distance if distance <= 1 else 0
                metadata = results['metadatas'][0][i]
                
                if similarity >= similarity_threshold:
                    retrieved.append({
                        "text": doc,
                        "source_id": metadata.get('source_id'),
                        "source_name": metadata.get('source_name'),
                        "source_url": metadata.get('source_url'),
                        "similarity": similarity
                    })
        
        print(f"Retrieved {len(retrieved)} relevant chunks")
        return retrieved

def main():
    retriever = Retriever()
    # Test query
    query = "What is the expense ratio of HDFC Large Cap Fund Direct Growth?"
    results = retriever.retrieve(query)
    for i, r in enumerate(results):
        print(f"\n{i+1}. [{r['source_name']}] (sim: {r['similarity']:.3f})")
        print(f"   {r['text'][:100].encode('ascii', 'ignore').decode()}...")

if __name__ == "__main__":
    main()
