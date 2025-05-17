import pytest
import httpx
from typing import AsyncGenerator

from app.main import app # Import your FastAPI application

@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Provides an asynchronous HTTP client for testing the FastAPI application.
    The client is configured to make requests directly to the app in-memory.
    """
    async with httpx.AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        yield client
