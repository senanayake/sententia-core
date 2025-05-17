import pytest
import httpx

BASE_URL = "http://app:8000"

@pytest.mark.asyncio
async def test_icecream_layers_present():
    """Ensure example loads and requirements are layered correctly."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Load example requirements
        response = await client.post("/load-icecream-example")
        assert response.status_code == 200

        # Fetch all requirements
        response = await client.get("/requirements")
        assert response.status_code == 200
        data = response.json()

        layers = {req["layer"] for req in data}
        assert {"Business", "System", "Software", "Test"}.issubset(layers)
        assert len(data) >= 4
