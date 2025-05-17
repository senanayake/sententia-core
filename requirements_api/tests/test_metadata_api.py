"""
Test Metadata API Endpoints

Tests for retrieving allowed values for RequirementType, PriorityLevel, RequirementSource, and RequirementStatus
from the metadata endpoints.
"""

import pytest
import httpx

BASE_URL = "http://app:8000"

@pytest.mark.asyncio
async def test_metadata_types():
    """Test retrieval of requirement types."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/metadata/types")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert all(isinstance(t, str) for t in response.json())

@pytest.mark.asyncio
async def test_metadata_priority():
    """Test retrieval of priority levels."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/metadata/priority")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert all(isinstance(p, str) for p in response.json())

@pytest.mark.asyncio
async def test_metadata_source():
    """Test retrieval of requirement sources."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/metadata/source")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert all(isinstance(s, str) for s in response.json())

@pytest.mark.asyncio
async def test_metadata_status():
    """Test retrieval of requirement statuses."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/metadata/status")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert all(isinstance(s, str) for s in response.json())

@pytest.mark.asyncio
async def test_metadata_layers():
    """Test retrieval of requirement layers."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/metadata/layers")
        assert response.status_code == 200
        assert "Business" in response.json()