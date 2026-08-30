from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql://postgres:12345678@localhost:5432/samsung_db"
    )
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    REQUEST_DELAY_MIN: float = 2.0
    REQUEST_DELAY_MAX: float = 4.0
    TARGET_PHONE_COUNT: int = 15
    BASE_URL: str = "https://www.gsmarena.com"
    SAMSUNG_PAGE_URL: str = "https://www.gsmarena.com/samsung-phones-9.php"


    # Groq & RAG Settings
    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_PERSIST_DIR: str = "data/chroma_db"


    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()