"""
Logging middleware for FastAPI to log request and response payloads
"""
import json
import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
import asyncio

# Configure logger
logger = logging.getLogger("api_logger")
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class LoggingMiddleware:
    """
    Middleware to log API requests and responses
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Get request details
        start_time = time.time()
        method = request.method
        url = str(request.url)
        path = request.url.path
        query_params = dict(request.query_params)
        headers = dict(request.headers)

        # Get request body
        body = b""

        async def receive_wrapper():
            nonlocal body
            message = await receive()
            if message["type"] == "http.request":
                body += message.get("body", b"")
            return message

        # Parse request body
        request_payload = None
        try:
            if body:
                request_payload = json.loads(body.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            request_payload = body.decode() if body else None

        # Log request
        logger.info(f"REQUEST | {method} {path}")
        logger.info(f"REQUEST URL | {url}")
        if query_params:
            logger.info(f"REQUEST QUERY | {json.dumps(query_params, indent=2)}")
        if request_payload:
            logger.info(f"REQUEST PAYLOAD | {json.dumps(request_payload, indent=2, default=str)}")

        # Capture response
        response_body = b""
        response_status = None

        async def send_wrapper(message):
            nonlocal response_body, response_status
            if message["type"] == "http.response.start":
                response_status = message["status"]
            elif message["type"] == "http.response.body":
                response_body += message.get("body", b"")
            await send(message)

        # Process request
        await self.app(scope, receive_wrapper, send_wrapper)

        # Calculate processing time
        process_time = time.time() - start_time

        # Parse response body
        response_payload = None
        try:
            if response_body:
                response_payload = json.loads(response_body.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            response_payload = response_body.decode() if response_body else None

        # Log response
        logger.info(f"RESPONSE | {method} {path} | Status: {response_status} | Time: {process_time:.3f}s")
        logger.info("=" * 80)


async def log_request_response_middleware(request: Request, call_next: Callable):
    """
    Alternative middleware implementation using FastAPI's middleware decorator
    """
    start_time = time.time()

    # Log request
    method = request.method
    url = str(request.url)
    path = request.url.path
    query_params = dict(request.query_params)

    # Get request body
    body = await request.body()
    request_payload = None

    try:
        if body:
            request_payload = json.loads(body.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        request_payload = body.decode() if body else None

    # Log request details
    logger.info(f"REQUEST | {method} {path}")
    logger.info(f"REQUEST URL | {url}")
    if query_params:
        logger.info(f"REQUEST QUERY | {json.dumps(query_params, indent=2)}")
    if request_payload:
        logger.info(f"REQUEST PAYLOAD | {json.dumps(request_payload, indent=2, default=str)}")

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response (for non-streaming responses)
    logger.info(f"RESPONSE | {method} {path} | Status: {response.status_code} | Time: {process_time:.3f}s")

    # Note: For detailed response payload logging, we'd need to read the response body
    # which can be complex with streaming responses. The ASGI middleware above handles this better.

    logger.info("=" * 80)

    return response
