import os
import importlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import router
from src.core.api_utils import print_all_api_info
from src.core.logging_middleware import LoggingMiddleware

app = FastAPI()

# Add logging middleware first (order matters)
app.add_middleware(LoggingMiddleware)

# Optionally enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Generate and print all API paths and request payloads
print_all_api_info(app)

## start the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
