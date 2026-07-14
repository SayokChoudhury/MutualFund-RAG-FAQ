import os
import sys
import json

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import config
from src.ingestion.chunker import Chunker

def main():
    metadata_file = "data/metadata.json"
    if not os.path.exists(metadata_file):
        print("No metadata.json found.")
        return

    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata_entries = json.load(f)

    chunker = Chunker(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
    chunks = chunker.chunk_documents(metadata_entries)
    
    # Dump to data/chunks_review.json
    output_file = "data/chunks_review.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully dumped {len(chunks)} chunks to {output_file}")

if __name__ == "__main__":
    main()
