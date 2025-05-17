"""
Sententia Core - Pydantic Models for Requirements (with Versioning Support)

This module defines the schemas for Requirements and their historical versions,
enabling tracking of changes over time for auditability and traceability.

Author: Chris Senanayake
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class RequirementLayer(str, Enum):
    """Enumeration of allowed requirement layers."""
    business = "Business"
    system = "System"
    software = "Software"
    test = "Test"

class RequirementType(str, Enum):
    """Enumeration of allowed requirement types."""
    functional = "Functional"
    non_functional = "Non-Functional"
    constraint = "Constraint"
    verification = "Verification"     

class PriorityLevel(str, Enum):
    """Enumeration of allowed priority levels."""
    low = "Low"
    medium = "Medium"
    high = "High"

class RequirementStatus(str, Enum):
    """Enumeration of allowed requirement statuses."""
    draft = "Draft"
    approved = "Approved"
    rejected = "Rejected"
    proposed = "Proposed"
    planned = "Planned"      

class RequirementSource(str, Enum):
    stakeholder = "Stakeholder"
    document = "Document"
    previous_system = "PreviousSystem"
    regulation = "Regulation"
    support_ticket = "SupportTicket"
    product_owner = "ProductOwner"
    developer = "Developer" 

class RequirementVersion(BaseModel):
    """
    Historical version of a requirement.

    Attributes
    ----------
    timestamp : datetime
        Time when this version was created.
    data : dict
        Snapshot of the requirement fields at that time.
    """
    timestamp: datetime
    data: dict

class LinkType(str, Enum):
    """Enumeration of allowed types of requirement-to-requirement links."""
    depends_on = "DependsOn"
    satisfies = "Satisfies"
    refines = "Refines"
    conflicts_with = "ConflictsWith"

class Link(BaseModel):
    """
    Represents a directional relationship between two requirements.

    Attributes
    ----------
    target_id : str
        Display ID of the target requirement.
    type : LinkType
        Type of relationship (e.g., DependsOn, ConflictsWith).
    """
    target_id: str
    type: LinkType


class Requirement(BaseModel):
    """
    Schema representing a software/system requirement.

    Attributes
    ----------
    type : RequirementType
        The type of requirement (Functional, Non-Functional, Constraint).
    description : str
        A short description of what the requirement entails.
    source : RequirementSource
        The origin of the requirement.
    priority : PriorityLevel
        The priority level assigned to the requirement.
    status : RequirementStatus
        The current lifecycle status of the requirement.
    rationale : Optional[str]
        An optional explanation for why the requirement exists.
    verification : Optional[str]
        An optional method or approach for verifying the requirement.
    versions : List[RequirementVersion]
        Historical versions of this requirement.
    links : Optional[List[Link]]
        Relationships to other requirements.
    """
    # ─── Server-generated fields ────────────────────────────────────
    display_id: Optional[str] = None

    # ─── Client-supplied fields (existing) ─────────────────────────    
    type: RequirementType = Field(..., description="Requirement type is required")
    description: str = Field(..., min_length=1, description="Description must not be empty")
    source: RequirementSource = Field(..., description="Source is required")
    priority: PriorityLevel = Field(..., description="Priority is required")
    status: RequirementStatus = Field(..., description="Status is required")
    layer: Optional[RequirementLayer] = None          
    rationale: Optional[str] = None
    verification: Optional[str] = None
    versions: Optional[List[RequirementVersion]] = []
    links: Optional[List[Link]] = []


class RequirementIn(BaseModel):
    """
    Payload for creating a new requirement.
    Matches `Requirement` minus server-managed fields.
    """
    type: RequirementType
    description: str
    source: RequirementSource
    priority: PriorityLevel
    status: RequirementStatus
    layer: Optional[RequirementLayer] = None            
    rationale: Optional[str] = None
    verification: Optional[str] = None
    links: Optional[List[Link]] = None
