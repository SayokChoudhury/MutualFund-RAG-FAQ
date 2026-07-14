import os
import sys
import json
import logging
import argparse

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import config
from src.ingestion.scraper import Scraper
from src.ingestion.chunker import Chunker
from src.ingestion.embedder import Embedder
from src.retrieval.vector_store import VectorStore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Ingest mutual fund data into Vector DB.")
    parser.add_argument("--force", action="store_true", help="Force re-scrape of all URLs.")
    args = parser.parse_args()

    metadata_file = "data/metadata.json"

    # Step 1: Scrape
    if args.force or not os.path.exists(metadata_file):
        logger.info("Starting web scraping...")
        scraper = Scraper()
        scraper.run()
    else:
        logger.info("Using existing scraped data. Use --force to re-scrape.")

    # Load metadata
    if not os.path.exists(metadata_file):
        logger.error(f"Metadata file {metadata_file} not found. Cannot proceed.")
        return

    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata_entries = json.load(f)

    # Step 2: Chunk
    logger.info("Starting chunking...")
    chunker = Chunker(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
    chunks = chunker.chunk_documents(metadata_entries)

    if not chunks:
        logger.warning("No chunks generated. Exiting.")
        return

    # Step 3: Embed
    logger.info("Generating embeddings...")
    embedder = Embedder(model_name=config.embedding_model)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedder.generate_embeddings(texts)

    # Step 4: Store
    logger.info("Storing into ChromaDB...")
    vector_store = VectorStore(db_path=config.chroma_db_path)
    vector_store.upsert_chunks(chunks, embeddings)

    logger.info("Ingestion pipeline complete!")

if __name__ == "__main__":
    main()
