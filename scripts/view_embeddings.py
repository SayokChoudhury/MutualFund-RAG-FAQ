import os
import sys
import json
import chromadb

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import config

def main():
    db_path = config.chroma_db_path
    collection_name = "hdfc_mutual_fund_corpus"
    
    if not os.path.exists(db_path):
        print(f"ChromaDB path {db_path} does not exist.")
        return

    client = chromadb.PersistentClient(path=db_path)
    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        print(f"Could not get collection '{collection_name}': {e}")
        return

    # Get a few items (e.g., limit=3)
    results = collection.get(limit=3, include=['embeddings', 'documents', 'metadatas'])
    
    if not results['ids']:
        print("Collection is empty.")
        return

    output_data = []
    for i in range(len(results['ids'])):
        chunk_id = results['ids'][i]
        document = results['documents'][i]
        metadata = results['metadatas'][i]
        embedding = results['embeddings'][i]
        if hasattr(embedding, "tolist"):
            embedding = embedding.tolist()
        
        output_data.append({
            "id": chunk_id,
            "metadata": metadata,
            "document_preview": document[:200] + "..." if len(document) > 200 else document,
            "embedding_dimensions": len(embedding),
            "embedding_preview": embedding[:10]  # Show first 10 values
        })
        
    output_file = "data/embeddings_review.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully dumped sample embeddings to {output_file}")
    
    for item in output_data:
        print(f"\nChunk ID: {item['id']}")
        print(f"Scheme: {item['metadata'].get('scheme_name', 'Unknown')}")
        print(f"Embedding Dimensions: {item['embedding_dimensions']}")
        print(f"Embedding Preview (first 5 floats): {[round(x, 4) for x in item['embedding_preview'][:5]]}")

if __name__ == "__main__":
    main()
