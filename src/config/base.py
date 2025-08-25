from pydantic_settings import BaseSettings
from pydantic import Field
import os

class BaseConfig( BaseSettings):
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8080)
    DEBUG: str = Field(default="True")
    TOKEN: str = Field(default="your_token_here")
    # Use absolute path for database file
    DATABASE_URL: str = Field(default=f"sqlite:////{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../database.db'))}")

    model_config = {
        "env_file": None,  # Disable .env file loading on Railway
        "case_sensitive": False,
        "extra": "allow"
    }

settings = BaseConfig()
