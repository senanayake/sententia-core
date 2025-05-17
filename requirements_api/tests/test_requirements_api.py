import pytest
import httpx
from typing import Dict, Any

from app.schemas import RequirementType, RequirementSource, PriorityLevel, RequirementStatus, RequirementLayer, LinkType

# Base URL for the API
BASE_URL = "http://localhost:8000" # Assuming the API runs on port 8000

# --- Test Data ---
VALID_REQUIREMENT_PAYLOAD: Dict[str, Any] = {
    "display_id": "REQ-API-001",
    "type": RequirementType.functional.value,
    "description": "The system shall allow users to log in via OAuth2.",
    "source": RequirementSource.stakeholder.value,
    "priority": PriorityLevel.high.value,
    "status": RequirementStatus.proposed.value,
    "layer": RequirementLayer.system.value,
    "rationale": "To provide secure and easy access.",
    "verification": "Manual test: User attempts login with valid Google credentials.",
    "links": [
        {"target_id": "REQ-SYS-AUTH-002", "type": LinkType.depends_on.value}
    ]
}


# --- Helper Functions (if any, e.g., to clear data before tests if needed) ---
# For now, we assume the in-memory store is clean or tests are independent.

# --- API Tests ---

@pytest.mark.asyncio
async def test_create_requirement_valid_data(async_client: httpx.AsyncClient):
    """Test creating a requirement with valid data."""
    payload = VALID_REQUIREMENT_PAYLOAD.copy()
    payload["display_id"] = "REQ-API-CREATE-VALID" # Ensure unique ID for test

    response = await async_client.post(f"{BASE_URL}/requirements", json=payload)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
    
    data = response.json()
    assert data["display_id"] == payload["display_id"]
    assert data["description"] == payload["description"]
    assert data["type"] == payload["type"]
    assert data["source"] == payload["source"]
    assert data["priority"] == payload["priority"]
    assert data["status"] == payload["status"]
    assert data["layer"] == payload["layer"]
    assert data["rationale"] == payload["rationale"]
    assert data["verification"] == payload["verification"]
    assert len(data["links"]) == 1
    assert data["links"][0]["target_id"] == payload["links"][0]["target_id"]
    assert data["links"][0]["type"] == payload["links"][0]["type"]
    assert "versions" in data # versions should be initialized
    assert isinstance(data["versions"], list)

    # TODO: Add a GET request here to verify persistence if needed,
    # or rely on subsequent tests for read operations.
