from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Contract Platform Demo"
    api_prefix: str = "/api"
    secret_key: str = "dev-secret-change-me"
    access_token_exp_minutes: int = 60 * 24
    sqlalchemy_database_uri: str = "sqlite:///./demo.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

settings = Settings()
