"""
Metadata API Endpoints

This module exposes endpoints for UI or external consumers to retrieve allowed values
for requirement fields (types, priorities, sources, statuses).
"""

from fastapi import APIRouter
from .schemas import RequirementType, PriorityLevel, RequirementSource, RequirementStatus, RequirementLayer
from typing import List
router = APIRouter()


@router.get("/metadata/layers", response_model=List[str])
async def get_layers():
    return [layer.value for layer in RequirementLayer]

@router.get("/metadata/types")
async def get_requirement_types():
    """Get allowed Requirement Types."""
    return [e.value for e in RequirementType]

@router.get("/metadata/priority")
async def get_priorities():
    """Get allowed Priority Levels."""
    return [e.value for e in PriorityLevel]

@router.get("/metadata/source")
async def get_sources():
    """Get allowed Sources."""
    return [e.value for e in RequirementSource]

@router.get("/metadata/status")
async def get_statuses():
    """Get allowed Requirement Statuses."""
    return [e.value for e in RequirementStatus]
