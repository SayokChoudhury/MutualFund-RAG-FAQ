import hashlib
import logging
from typing import List, Dict, Any
import chromadb

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, db_path: str = "./data/chroma_db", collection_name: str = "hdfc_mutual_fund_corpus"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Connected to ChromaDB collection '{collection_name}' at {db_path}")

    def _generate_id(self, source_url: str, chunk_index: int) -> str:
        unique_string = f"{source_url}_{chunk_index}"
        return hashlib.md5(unique_string.encode('utf-8')).hexdigest()

    def upsert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        if not chunks:
            logger.warning("No chunks to upsert.")
            return

        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            meta = chunk["metadata"]
            doc_id = self._generate_id(meta["source_url"], meta["chunk_index"])
            ids.append(doc_id)
            documents.append(chunk["text"])
            # Ensure metadata values are str, int, float, or bool
            safe_meta = {k: str(v) if not isinstance(v, (str, int, float, bool)) else v for k, v in meta.items()}
            metadatas.append(safe_meta)

        # ChromaDB accepts batches, we can upsert all at once if not too large
        logger.info(f"Upserting {len(ids)} chunks to ChromaDB...")
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        logger.info("Upsert complete.")
