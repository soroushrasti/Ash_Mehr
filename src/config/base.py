from pydantic_settings import BaseSettings
from pydantic import Field
import os

class BaseConfig(BaseSettings):
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8080)
    DEBUG: str = Field(default="True")
    TOKEN: str = Field(default="your_token_here")
    # Use a relative path for the default sqlite database, overridable via env
    DATABASE_URL: str = Field(default="sqlite:///./database.db")

    model_config = {
        "env_file": ".env",  # Enable .env file loading
        "case_sensitive": False,
        "extra": "allow"
    }

settings = BaseConfig()
