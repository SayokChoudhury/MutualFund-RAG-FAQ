import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Config:
    groq_api_key: str
    chroma_db_path: str
    embedding_model: str
    llm_model: str
    llm_temperature: float
    llm_max_tokens: int
    retriever_top_k: int
    similarity_threshold: float
    chunk_size: int
    chunk_overlap: int

def load_config() -> Config:
    load_dotenv()
    
    return Config(
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        chroma_db_path=os.getenv("CHROMA_DB_PATH", "./data/chroma_db"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5"),
        llm_model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "200")),
        retriever_top_k=int(os.getenv("RETRIEVER_TOP_K", "10")),
        similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.5")),
        chunk_size=int(os.getenv("CHUNK_SIZE", "250")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
    )

config = load_config()
