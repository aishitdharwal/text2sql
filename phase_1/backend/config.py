"""
Configuration management for the application
"""
from pydantic_settings import BaseSettings
from typing import Dict

class Settings(BaseSettings):
    # Database
    db_host: str
    db_port: int = 5432
    db_user: str
    db_password: str
    
    # Anthropic API
    anthropic_api_key: str
    
    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Team credentials and database mapping
TEAM_CREDENTIALS: Dict[str, Dict[str, str]] = {
    "sales": {
        "password": "sales123",
        "database": "sales_db"
    },
    "marketing": {
        "password": "marketing123",
        "database": "marketing_db"
    },
    "operations": {
        "password": "operations123",
        "database": "operations_db"
    }
}
