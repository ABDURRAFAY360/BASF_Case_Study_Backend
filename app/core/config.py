from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "BASF Book Recommendation System"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Book Recommendation FastAPI Application"
    AUTHOR_NAME: str = "Abdur Rafay"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
