import logging
from typing import List
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self, model_name: str = "BAAI/bge-large-en-v1.5"):
        self.model_name = model_name
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        # encode returns a numpy array, we convert to list of floats
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()
