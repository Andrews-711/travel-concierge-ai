from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings - lightweight, no database configs"""
    
    # App
    APP_NAME: str = "Travel Concierge"
    VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    GEMINI_API_KEY: str = ""  # Optional - if set, uses Gemini instead of Ollama
    
    # ChromaDB (in-memory only)
    CHROMA_IN_MEMORY: bool = True
    CHROMA_COLLECTION: str = "travel_docs"
    
    # Embedding Model
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Web Search
    WEB_SEARCH_ENABLED: bool = True
    MAX_SEARCH_RESULTS: int = 5
    
    # Rate Limiting (in-memory)
    MAX_REQUESTS_PER_MINUTE: int = 60
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".txt"]
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
