"""
Tests for Requirements API endpoints.

Verifies CRUD operations, validation errors, and versioning
behaviour for the requirements backend.
"""

import pytest
import httpx

BASE_URL = "http://app:8000"


@pytest.mark.asyncio
async def test_create_read_update_delete_requirement():
    """Test full CRUD lifecycle for a requirement."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        payload = {
            "type": "Functional",
            "layer": "System",                    # ← NEW
            "description": "System must allow password reset.",
            "source": "Stakeholder",
            "priority": "High",
            "status": "Draft",
            "links": []
        }

        # CREATE
        resp = await client.post("/requirements", json=payload)
        assert resp.status_code == 200
        created = resp.json()
        display_id = created["display_id"]

        # READ (collection)
        resp = await client.get("/requirements")
        assert resp.status_code == 200
        assert any(r["display_id"] == display_id for r in resp.json())

        # UPDATE
        payload["description"] = "System must allow password reset (updated)."
        resp = await client.put(f"/requirements/{display_id}", json=payload)
        assert resp.status_code == 200
        assert resp.json()["description"].endswith("(updated).")

        # DELETE
        resp = await client.delete(f"/requirements/{display_id}")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_requirement_missing_fields():
    """Ensure 422 is returned when required fields are missing."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        invalid_cases = [
            # missing type
            {
                "layer": "Business",
                "description": "Test",
                "source": "Stakeholder",
                "priority": "High",
                "status": "Draft",
            },
            # missing description
            {
                "type": "Functional",
                "layer": "Business",
                "source": "Stakeholder",
                "priority": "High",
                "status": "Draft",
            },
            # missing source
            {
                "type": "Functional",
                "layer": "Business",
                "description": "Test",
                "priority": "High",
                "status": "Draft",
            },
            # missing priority
            {
                "type": "Functional",
                "layer": "Business",
                "description": "Test",
                "source": "Stakeholder",
                "status": "Draft",
            },
            # missing status
            {
                "type": "Functional",
                "layer": "Business",
                "description": "Test",
                "source": "Stakeholder",
                "priority": "High",
            },
        ]

        for case in invalid_cases:
            resp = await client.post("/requirements", json=case)
            assert resp.status_code == 422


@pytest.mark.asyncio
async def test_versioning_behavior():
    """Verify that updating a requirement stores the previous state in versions."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        payload = {
            "type": "Functional",
            "layer": "Business",                 # ← NEW
            "description": "Initial description",
            "source": "Stakeholder",
            "priority": "High",
            "status": "Draft",
        }

        # create
        resp = await client.post("/requirements", json=payload)
        assert resp.status_code == 200
        display_id = resp.json()["display_id"]

        # update
        payload["description"] = "Updated description"
        resp = await client.put(f"/requirements/{display_id}", json=payload)
        assert resp.status_code == 200

        # fetch & check versions
        resp = await client.get("/requirements")
        fetched = next(r for r in resp.json() if r["display_id"] == display_id)
        assert "versions" in fetched
        assert len(fetched["versions"]) == 1
        assert fetched["versions"][0]["data"]["description"] == "Initial description"
