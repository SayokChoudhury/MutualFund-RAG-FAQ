import logging
from dataclasses import dataclass
from typing import List, Optional
import chromadb
from src.config import config
from src.ingestion.embedder import Embedder

logger = logging.getLogger(__name__)

@dataclass
class RetrievedChunk:
    text: str
    source_url: str
    scheme_name: str
    document_type: str
    scrape_date: str
    similarity_score: float

class Retriever:
    def __init__(self):
        self.db_path = config.chroma_db_path
        self.collection_name = "hdfc_mutual_fund_corpus"
        self.top_k = config.retriever_top_k
        self.similarity_threshold = config.similarity_threshold
        
        # Load embedding model
        self.embedder = Embedder(model_name=config.embedding_model)
        
        # Connect to ChromaDB
        self.client = chromadb.PersistentClient(path=self.db_path)
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except Exception as e:
            logger.error(f"Failed to load collection '{self.collection_name}'. Make sure ingestion has been run. Error: {e}")
            self.collection = None

    def _extract_scheme(self, query: str) -> Optional[str]:
        """Simple extraction logic to find scheme name in query."""
        query_lower = query.lower()
        
        # Exact substring matching for known schemes
        if "large cap" in query_lower or "large-cap" in query_lower:
            return "HDFC Large Cap Fund"
        if "mid cap" in query_lower or "mid-cap" in query_lower:
            return "HDFC Mid-Cap Fund"
        if "small cap" in query_lower or "small-cap" in query_lower:
            return "HDFC Small Cap Fund"
        if "gold" in query_lower:
            return "HDFC Gold ETF Fund of Fund"
        if "silver" in query_lower:
            return "HDFC Silver ETF FoF"
            
        return None

    def retrieve(self, query: str, top_k: int = None) -> List[RetrievedChunk]:
        if not self.collection:
            logger.warning("No ChromaDB collection available.")
            return []
            
        if top_k is None:
            top_k = self.top_k

        # 1. Embed the query
        query_embedding = self.embedder.generate_embeddings([query])[0]

        # 2. Extract scheme name for metadata filtering
        scheme_filter = self._extract_scheme(query)
        where_clause = None
        if scheme_filter:
            where_clause = {"scheme_name": {"$eq": scheme_filter}}
            logger.info(f"Query mapped to scheme: {scheme_filter}. Applying filter.")
        else:
            logger.info("No specific scheme detected in query. Searching across all.")

        # 3. Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=['documents', 'metadatas', 'distances']
        )

        retrieved_chunks = []
        if not results['ids'] or not results['ids'][0]:
            return retrieved_chunks

        docs = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]

        for doc, meta, distance in zip(docs, metadatas, distances):
            # Convert ChromaDB distance back to cosine similarity
            # Since hnsw:space = cosine, distance is 1 - cosine_similarity
            similarity = 1.0 - distance
            
            # 4. Apply similarity threshold
            if similarity >= self.similarity_threshold:
                retrieved_chunks.append(RetrievedChunk(
                    text=doc,
                    source_url=meta.get("source_url", ""),
                    scheme_name=meta.get("scheme_name", ""),
                    document_type=meta.get("document_type", ""),
                    scrape_date=meta.get("scrape_date", ""),
                    similarity_score=similarity
                ))

        logger.info(f"Retrieved {len(retrieved_chunks)} chunks above threshold {self.similarity_threshold}.")
        return retrieved_chunks
