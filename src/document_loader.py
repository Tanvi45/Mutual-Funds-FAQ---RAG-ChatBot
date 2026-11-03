import os
import json

class DocumentLoader:
    def __init__(self, raw_dir="data/raw", metadata_file="data/raw/metadata.json"):
        self.raw_dir = raw_dir
        self.metadata_file = metadata_file
    
    def load_documents(self):
        """Load, validate and structure documents from data/raw/"""
        print("Loading documents from data/raw/...")
        
        # Load metadata
        if not os.path.exists(self.metadata_file):
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_file}")
        
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        documents = []
        
        for item in metadata:
            txt_path = item['txt_path']
            print(f"Loading {item['source_id']}...")
            
            # Validate file exists
            if not os.path.exists(txt_path):
                print(f"[WARN] File not found: {txt_path}")
                continue
            
            # Read and validate
            with open(txt_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            if not text.strip():
                print(f"[WARN] Empty file: {txt_path}")
                continue
            
            # Structure document with metadata
            document = {
                "source_id": item['source_id'],
                "source_name": item['name'],
                "source_url": item['url'],
                "text": text
            }
            documents.append(document)
            print(f"[OK] Loaded {item['source_id']} ({len(text)} chars)")
        
        # Save loaded documents for explicit demonstration
        loaded_path = os.path.join(self.raw_dir, "loaded_documents.json")
        with open(loaded_path, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2)
        
        print(f"\nLoading complete. {len(documents)} documents loaded and structured.")
        return documents

def main():
    loader = DocumentLoader()
    documents = loader.load_documents()
    return documents

if __name__ == "__main__":
    main()
