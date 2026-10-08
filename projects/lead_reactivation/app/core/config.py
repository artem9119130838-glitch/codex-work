from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "n8n_email_ai"
    VERSION: str = "0.1.0"
    
    # Database
    POSTGRES_USER: str = "n8n_marketing"
    POSTGRES_PASSWORD: str = "localpassword"
    POSTGRES_DB: str = "marketing_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5433"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Cloud LLM Settings
    LLM_API_KEY: Optional[str] = None
    LLM_API_KEY_DRAFTS_ONLY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "deepseek"
    
    # IMAP Settings
    IMAP_HOST: str = ""
    IMAP_SERVER: str = ""
    IMAP_USER: str = ""
    IMAP_PASSWORD: str = ""
    IMAP_MAILBOX: str = "INBOX"
    
    # 1C OData Settings
    ONEC_ODATA_URL: str = ""
    ONEC_ODATA_USER: str = ""
    ONEC_ODATA_PASSWORD: str = ""
    
    # Bitrix24 Settings
    BITRIX24_WEBHOOK_URL: Optional[str] = None

    # API Security
    API_SECRET_KEY: str = "secret-dev-key-123"  # Default for local testing
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
