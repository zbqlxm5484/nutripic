from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ai_internal_api_key: str
    ai_env: str = "local"
    ai_generation_provider: str = "fallback"
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    ai_model_name: str | None = None
    ai_temperature: float = 0.2
    ai_max_tokens: int = 2000
    vector_db_url: str | None = None
    vector_db_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8-sig", extra="ignore")


settings = Settings()
