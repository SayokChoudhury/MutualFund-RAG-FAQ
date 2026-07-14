import json
import logging
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class Chunker:
    def __init__(self, chunk_size: int = 250, chunk_overlap: int = 50):
        # We use a character text splitter but approximate tokens (1 token ~ 4 chars)
        self.chunk_size = chunk_size * 4 
        self.chunk_overlap = chunk_overlap * 4
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def chunk_documents(self, metadata_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        for entry in metadata_entries:
            try:
                with open(entry["processed_file"], "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                logger.error(f"Failed to read {entry['processed_file']}: {e}")
                continue

            if not text.strip():
                continue

            split_texts = self.splitter.split_text(text)
            for i, chunk_text in enumerate(split_texts):
                chunk_meta = {
                    "text": chunk_text,
                    "metadata": {
                        "source_url": entry["source_url"],
                        "scheme_name": entry["scheme_name"],
                        "document_type": entry["document_type"],
                        "scrape_date": entry["scrape_date"],
                        "chunk_index": i
                    }
                }
                chunks.append(chunk_meta)
                
        logger.info(f"Generated {len(chunks)} chunks from {len(metadata_entries)} documents.")
        return chunks
