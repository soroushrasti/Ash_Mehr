import os
import importlib

import typer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import router
from src.core.api_utils import print_all_api_info
from src.core.logging_middleware import LoggingMiddleware
from sqlalchemy_utils.functions import database_exists, create_database, drop_database
from src.config.database import engine
from src.core.models import Base  # Ensure all models are imported
app = FastAPI()


# Add logging middleware first (order matters)
app.add_middleware(LoggingMiddleware)

# Optionally enable CORS for frontend integration
# NOTE: Using explicit origins because allow_credentials=True cannot be used with "*"
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:8081,http://localhost:19006,http://127.0.0.1:8081,http://127.0.0.1:19006",
    ).split(",")
    if origin.strip()
]
# Also allow typical Android/Expo LAN origins (localhost, emulator, and common LAN ranges) via regex
allowed_origin_regex = os.getenv(
    "CORS_ALLOW_ORIGIN_REGEX",
    r"https?://(localhost|127\\.0\\.0\\.1|10\\.0\\.2\\.2|10\\.0\\.3\\.2|192\\.168\\.\\d{1,3}\\.\\d{1,3}|172\\.(1[6-9]|2[0-9]|3[0-1])\\.\\d{1,3}\\.\\d{1,3})(:\\d+)?",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allowed_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Generate and print all API paths and request payloads
print_all_api_info(app)

def init_db():
    """Initialize the database."""
    if not database_exists(engine.url):
        create_database(engine.url)

        Base.metadata.create_all(engine)

## start the app
if __name__ == "__main__":
    if not database_exists(engine.url):
        print("Creating database")
        init_db()

    typer.echo("Starting the app")
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
