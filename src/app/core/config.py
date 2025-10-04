from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "BASF Book Recommendation System"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Book Recommendation FastAPI Application"
    AUTHOR_NAME: str = "Abdur Rafay"
    DATABASE_URL: str
    USERS_SEED_FILE: str = "data/users_seed.json"
    BOOKS_SEED_FILE: str = "data/books_seed.json"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    GOOGLE_BOOKS_ENABLED: bool = True
    GOOGLE_BOOKS_DEFAULT_QUERY: str = "python programming"
    GOOGLE_BOOKS_MAX_RESULTS: int = 20
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
