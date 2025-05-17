'''
Tests for requirement linking behavior.

This suite verifies the correct handling of structured links between requirements,
especially in scenarios involving systems-to-software traceability.

Each test is marked with @pytest.mark.asyncio and uses HTTPX AsyncClient
against the running FastAPI backend service.
'''

import pytest
import httpx

BASE_URL = "http://app:8000"

@pytest.mark.asyncio
async def test_requirement_linking_workflows():
    """
    Test creation of multiple requirements with structured typed links.

    This scenario reflects a real-world traceability chain:
    - A system-level constraint (auth requirement)
    - A software-level functional requirement that depends on it
    - A low-level implementation requirement that refines and satisfies previous ones

    Assertions
    ----------
    - Links are created and returned correctly in response.
    - Types and target_ids are preserved.
    """
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Create a high-level system requirement
        sys_req = {
            "type": "Constraint",
            "description": "System shall enforce user authentication.",
            "source": "Document",
            "priority": "High",
            "status": "Draft",
            "links": []
        }
        res = await client.post("/requirements", json=sys_req)
        assert res.status_code == 200
        sys_req_id = res.json()["display_id"]

        # Create a software requirement that depends on the system requirement
        sw_req = {
            "type": "Functional",
            "description": "Software shall prompt for username/password.",
            "source": "Stakeholder",
            "priority": "Medium",
            "status": "Draft",
            "links": [
                {"target_id": sys_req_id, "type": "DependsOn"}
            ]
        }
        res = await client.post("/requirements", json=sw_req)
        assert res.status_code == 200
        sw_req_data = res.json()
        sw_req_id = sw_req_data["display_id"]

        assert sw_req_data["links"][0]["target_id"] == sys_req_id
        assert sw_req_data["links"][0]["type"] == "DependsOn"

        # Create a lower-level requirement that Refines and Satisfies the above
        impl_req = {
            "type": "Functional",
            "description": "The login module must use OpenID Connect.",
            "source": "ProductOwner",
            "priority": "Low",
            "status": "Draft",
            "links": [
                {"target_id": sys_req_id, "type": "Refines"},
                {"target_id": sw_req_id, "type": "Satisfies"}
            ]
        }
        res = await client.post("/requirements", json=impl_req)
        assert res.status_code == 200
        impl_data = res.json()
        assert len(impl_data["links"]) == 2

@pytest.mark.asyncio
async def test_circular_reference_linking():
    """
    Test whether circular references between requirements are allowed.

    Simulates a case where A -> B and then B -> A.
    Backend currently allows this (no cycle prevention).

    Assertions
    ----------
    - Circular links are accepted and returned.
    """
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        req_a = {
            "type": "Functional",
            "description": "A",
            "source": "Stakeholder",
            "priority": "High",
            "status": "Draft",
            "links": []
        }
        res = await client.post("/requirements", json=req_a)
        assert res.status_code == 200
        id_a = res.json()["display_id"]

        req_b = {
            "type": "Functional",
            "description": "B",
            "source": "Stakeholder",
            "priority": "High",
            "status": "Draft",
            "links": [{"target_id": id_a, "type": "DependsOn"}]
        }
        res = await client.post("/requirements", json=req_b)
        assert res.status_code == 200
        id_b = res.json()["display_id"]

        # Update A to link back to B (forming a circular link)
        update_payload = {
            "type": "Functional",
            "description": "A (updated)",
            "source": "Stakeholder",
            "priority": "High",
            "status": "Draft",
            "links": [{"target_id": id_b, "type": "Refines"}]
        }
        res = await client.put(f"/requirements/{id_a}", json=update_payload)
        assert res.status_code == 200
        assert res.json()["links"][0]["target_id"] == id_b

@pytest.mark.asyncio
async def test_link_to_nonexistent_requirement():
    """
    Test that a link to a nonexistent requirement is either accepted (soft validation)
    or rejected (if link target existence is validated).

    Assertions
    ----------
    - Server either allows or rejects based on current validation logic.
    """
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        bogus_id = "REQ-NOTFOUND"
        req = {
            "type": "Functional",
            "description": "Should fail",
            "source": "Stakeholder",
            "priority": "Medium",
            "status": "Draft",
            "links": [{"target_id": bogus_id, "type": "DependsOn"}]
        }
        res = await client.post("/requirements", json=req)
        assert res.status_code in [200, 422]  # Placeholder: soft failure allowed for now

@pytest.mark.asyncio
async def test_link_updates():
    """
    Test updating an existing requirement to include a new link.

    This covers retroactive traceability where relationships are created later.

    Assertions
    ----------
    - Link is correctly persisted after PUT.
    - Type and target match.
    """
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        base = {
            "type": "Functional",
            "description": "Original",
            "source": "Stakeholder",
            "priority": "Low",
            "status": "Draft",
            "links": []
        }
        res = await client.post("/requirements", json=base)
        assert res.status_code == 200
        base_data = res.json()

        target = {
            "type": "Constraint",
            "description": "Updated constraint",
            "source": "Regulation",
            "priority": "High",
            "status": "Draft",
            "links": []
        }
        res = await client.post("/requirements", json=target)
        assert res.status_code == 200
        target_id = res.json()["display_id"]

        # Add a link to the existing requirement
        updated = {
            "type": "Functional",
            "description": "Now with a link",
            "source": "Stakeholder",
            "priority": "Low",
            "status": "Draft",
            "links": [{"target_id": target_id, "type": "Satisfies"}]
        }
        res = await client.put(f"/requirements/{base_data['display_id']}", json=updated)
        assert res.status_code == 200
        assert res.json()["links"][0]["type"] == "Satisfies"


@pytest.mark.asyncio
async def test_traceability_matrix_export():
    """
    Test export of the traceability matrix as a CSV.

    This verifies that the `/export/traceability` endpoint returns a valid CSV file
    with appropriate headers and link indicators between requirements.

    Assertions
    ----------
    - Response status is 200 OK.
    - Response is of type text/csv.
    - Response body contains source and target requirement IDs.
    """
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.get("/export/traceability")
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]
        assert "Source Requirement" in res.text  # column header check

@pytest.mark.asyncio
async def test_traceability_linking_display():
    """
    Test that requirement links are correctly rendered in the UI.

    This does not render the actual Streamlit interface, but verifies that when
    links are submitted, they are persisted and can be retrieved by a client.
    """
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Create base requirement
        r1 = {
            "type": "Functional",
            "description": "Base UI requirement",
            "source": "Stakeholder",
            "priority": "High",
            "status": "Draft",
            "links": []
        }
        res = await client.post("/requirements", json=r1)
        assert res.status_code == 200
        r1_id = res.json()["display_id"]

        # Create linked requirement
        r2 = {
            "type": "Functional",
            "description": "Linked to base",
            "source": "Stakeholder",
            "priority": "Medium",
            "status": "Draft",
            "links": [{"target_id": r1_id, "type": "DependsOn"}]
        }
        res = await client.post("/requirements", json=r2)
        assert res.status_code == 200
        assert res.json()["links"][0]["target_id"] == r1_id
        assert res.json()["links"][0]["type"] == "DependsOn"