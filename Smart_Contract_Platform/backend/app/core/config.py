from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Contract Platform Demo"
    api_prefix: str = "/api"
    secret_key: str = "dev-secret-change-me"
    access_token_exp_minutes: int = 60 * 24
    sqlalchemy_database_uri: str = "sqlite:///./demo.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # DeepSeek API配置
    deepseek_api_key: str = ""
    deepseek_api_base: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"  # 或 "deepseek-reasoner"
    
    # RAG知识库配置
    knowledge_base_dir: str = "knowledge_base"
    chroma_db_path: str = "knowledge_base/chroma_db"
    pdfs_dir: str = "knowledge_base/pdfs"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
