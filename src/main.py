import os
import importlib

import typer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.base import BaseConfig

from src.api import router
from src.core.api_utils import print_all_api_info
from src.core.logging_middleware import LoggingMiddleware
from sqlalchemy_utils.functions import database_exists, create_database, drop_database
from src.config.database import engine
from src.core.models import Base  # Ensure all models are imported
app = FastAPI()
settings = BaseConfig()



# Add logging middleware first (order matters)
app.add_middleware(LoggingMiddleware)

# Optionally enable CORS for frontend integration
# Allow all origins for development/testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when using "*" for origins
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return 'Hello'

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
    uvicorn.run("src.main:app",
                host=settings.HOST,
                port=settings.PORT,
                reload=False)
