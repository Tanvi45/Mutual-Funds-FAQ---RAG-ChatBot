import os
import json
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully")
    
    def embed_chunks(self, chunks_path="data/chunks/chunks.json"):
        """Generate embeddings for chunks"""
        print("Generating embeddings...")
        
        # Load chunks
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        # Extract texts
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        print(f"Embedding {len(texts)} chunks...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Pair chunks with embeddings
        embedded_chunks = []
        for i, chunk in enumerate(chunks):
            embedded_chunks.append({
                **chunk,
                "embedding": embeddings[i].tolist()
            })
        
        # Save embeddings
        embeddings_dir = "data/embeddings"
        os.makedirs(embeddings_dir, exist_ok=True)
        embeddings_path = os.path.join(embeddings_dir, "embeddings.json")
        
        with open(embeddings_path, 'w', encoding='utf-8') as f:
            json.dump(embedded_chunks, f, indent=2)
        
        print(f"\nEmbedding complete. {len(embedded_chunks)} embeddings saved to {embeddings_path}")
        return embedded_chunks

def main():
    embedder = Embedder()
    embedder.embed_chunks()

if __name__ == "__main__":
    main()
