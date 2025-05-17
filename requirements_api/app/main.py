"""
Sententia Core - Backend API for Requirements Management (with Versioning)

This module provides REST API endpoints for managing requirements, including
creation, retrieval, update, deletion, and history tracking.

Author: Chris Senanayake
"""

import uuid
from fastapi import FastAPI, HTTPException, status # Ensured status is imported
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from .schemas import Requirement, RequirementVersion, RequirementLayer
from uuid import uuid4
from .metadata import router as metadata_router
from datetime import datetime
from io import StringIO
import csv
from typing import List
from starlette.responses import StreamingResponse
#from .dev_routes import router as dev_router

# Removed duplicate import of metadata_router

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
app.include_router(metadata_router)
#app.include_router(dev_router)

from .store import requirements_store # Added import for centralized store
from .examples.ice_cream_example import create_ice_cream_example
from .examples.death_star_example import create_death_star_example # Added import for Death Star

app.include_router(metadata_router)

@app.get("/requirements")
async def get_requirements():
    """Retrieve all requirements."""
    return list(requirements_store.values())

@app.get("/requirements/view", response_class=HTMLResponse)
async def view_requirements(request: Request):
    """Render requirements as an HTML page."""
    requirements = list(requirements_store.values())
    return templates.TemplateResponse("requirements_viewer.html", {"request": request, "requirements": requirements})

@app.post("/requirements")
async def create_requirement(req: Requirement):
    """Create a new requirement."""
    display_id = f"REQ-{str(uuid4())[:8].upper()}"
    new_req = req.dict()
    new_req.update({"display_id": display_id})
    requirements_store[display_id] = new_req
    return new_req

@app.put("/requirements/{display_id}")
async def update_requirement(display_id: str, req: Requirement):
    """Update an existing requirement and track previous version."""
    if display_id not in requirements_store:
        raise HTTPException(status_code=404, detail="Requirement not found")

    # Save previous version
    old_req = requirements_store[display_id].copy()
    version = RequirementVersion(
        timestamp=datetime.utcnow(),
        data={
            "type": old_req["type"],
            "description": old_req["description"],
            "rationale": old_req.get("rationale"),
            "source": old_req["source"],
            "priority": old_req["priority"],
            "status": old_req["status"],
            "verification": old_req.get("verification")
        }
    )

    updated_req = req.dict()
    updated_req.update({"display_id": display_id})

    # Append to versions
    if "versions" not in old_req:
        old_req["versions"] = []
    updated_req["versions"] = old_req["versions"] + [version.dict()]

    requirements_store[display_id] = updated_req
    return updated_req

@app.delete("/requirements/{display_id}")
async def delete_requirement(display_id: str):
    """Delete a requirement by display ID."""
    if display_id not in requirements_store:
        raise HTTPException(status_code=404, detail="Requirement not found")
    del requirements_store[display_id]
    return {"message": "Requirement deleted successfully"}

@app.post("/load-demo/{demo_name}", status_code=status.HTTP_200_OK)
async def load_demo_data(demo_name: str):
    """
    Clears existing requirements and loads the specified demo examples.
    Supported demo_names: 'ice_cream', 'death_star'
    """
    try:
        if demo_name == "ice_cream":
            create_ice_cream_example()
            message = "Ice cream demo data loaded successfully."
        elif demo_name == "death_star":
            create_death_star_example()
            message = "Death Star demo data loaded successfully."
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Demo '{demo_name}' not found. Supported demos: 'ice_cream', 'death_star'"
            )
        return {"message": message}
    except HTTPException: # Re-raise HTTPException to return proper status code
        raise
    except Exception as e:
        # Log the exception e if you have logging setup
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load demo data for '{demo_name}': {str(e)}"
        )

@app.get("/export/traceability")
async def export_traceability():
    """
    Export traceability matrix as CSV.

    Returns
    -------
    StreamingResponse
        CSV file with source and target requirement links.
    """
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Source Requirement", "Link Type", "Target Requirement"])

    for req in requirements_store.values():
        for link in req.get("links", []):
            writer.writerow([req["display_id"], link["type"], link["target_id"]])

    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=traceability_matrix.csv"
    })
