from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # App
    APP_NAME: str = "ContractIQ"
    
    # Secrets
    GROQ_API_KEY: str

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    CONTRACT_DIR: Path = DATA_DIR / "contracts"
    VECTOR_DB_DIR: Path = DATA_DIR / "chroma_db"

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Groq
    GROQ_MODEL: str = "llama-3.1-8b-instant"


    class Config:
        env_file = ".env"

settings = Settings()
