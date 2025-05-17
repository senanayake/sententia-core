import pytest
from pydantic import ValidationError

# Adjust the import path based on your project structure and how tests are run.
# If 'app' is a top-level package for tests:
from app.schemas import Requirement, RequirementType, RequirementSource, PriorityLevel, RequirementStatus, RequirementLayer, Link, LinkType, RequirementVersion
from datetime import datetime

# Or, if your PYTHONPATH is set to 'requirements_api' for tests:
# from schemas import Requirement, RequirementType, RequirementSource, PriorityLevel, RequirementStatus, RequirementLayer

def test_requirement_model_instantiation_success():
    """
    Test that the Requirement model can be successfully instantiated
    with all required fields, including display_id.
    """
    valid_data = {
        "display_id": "REQ-001",
        "type": RequirementType.functional,
        "description": "The system shall allow users to log in.",
        "source": RequirementSource.stakeholder,
        "priority": PriorityLevel.high,
        "status": RequirementStatus.draft,
        "layer": RequirementLayer.software
    }
    try:
        req = Requirement(**valid_data)
        assert req.display_id == "REQ-001"
        assert req.type == RequirementType.functional
        assert req.description == "The system shall allow users to log in."
        # ... assert other fields as well for completeness
    except ValidationError as e:
        pytest.fail(f"Requirement model instantiation failed with valid data: {e}")

def test_requirement_model_missing_display_id():
    """
    Test that Requirement model instantiation fails if 'display_id' is missing,
    as it's a mandatory field.
    """
    invalid_data_missing_display_id = {
        # "display_id": "REQ-002", # Missing
        "type": RequirementType.non_functional,
        "description": "The system shall be available 99.9% of the time.",
        "source": RequirementSource.document,
        "priority": PriorityLevel.medium,
        "status": RequirementStatus.approved,
        "layer": RequirementLayer.system
    }
    with pytest.raises(ValidationError) as excinfo:
        Requirement(**invalid_data_missing_display_id)
    
    # Check that 'display_id' is mentioned in the error details
    assert "display_id" in str(excinfo.value).lower()
    # More specific check if Pydantic error structure is known:
    # errors = excinfo.value.errors()
    # assert any(err['loc'][0] == 'display_id' and err['type'] == 'missing' for err in errors)

def test_requirement_model_display_id_is_str():
    """
    Test that display_id must be a string.
    Pydantic should enforce this type.
    """
    invalid_data_wrong_type = {
        "display_id": 12345, # Not a string
        "type": RequirementType.functional,
        "description": "Test description.",
        "source": RequirementSource.developer,
        "priority": PriorityLevel.low,
        "status": RequirementStatus.proposed,
        "layer": RequirementLayer.test
    }
    with pytest.raises(ValidationError) as excinfo:
        Requirement(**invalid_data_wrong_type)
    
    # Check that 'display_id' and a type error are mentioned
    assert "display_id" in str(excinfo.value).lower()
    # errors = excinfo.value.errors()
    # assert any(err['loc'][0] == 'display_id' and 'string' in err['type'] for err in errors)

# You could also add tests for other fields, enum validation, etc.

# --- Enum Validation Tests ---

VALID_BASE_REQUIREMENT_DATA = {
    "display_id": "REQ-ENUM-TEST",
    "description": "Test enum validation.",
    "source": RequirementSource.developer, # Valid default
    "priority": PriorityLevel.low,      # Valid default
    "status": RequirementStatus.draft,    # Valid default
    "layer": RequirementLayer.software  # Valid default
}

@pytest.mark.parametrize("enum_field, valid_enum_value, EnumClass", [
    ("type", RequirementType.functional, RequirementType),
    ("source", RequirementSource.stakeholder, RequirementSource),
    ("priority", PriorityLevel.high, PriorityLevel),
    ("status", RequirementStatus.approved, RequirementStatus),
    ("layer", RequirementLayer.business, RequirementLayer),
])
def test_requirement_model_valid_enum_values(enum_field, valid_enum_value, EnumClass):
    """Test Requirement model accepts valid enum values."""
    data = {
        **VALID_BASE_REQUIREMENT_DATA,
        "type": RequirementType.constraint, # A valid default for type if not the one being tested
        enum_field: valid_enum_value
    }
    # Ensure the base 'type' is valid if we are testing another field
    if enum_field != "type":
        data["type"] = RequirementType.functional
    
    try:
        req = Requirement(**data)
        assert getattr(req, enum_field) == valid_enum_value
    except ValidationError as e:
        pytest.fail(f"Requirement model instantiation failed for {enum_field} with valid enum {valid_enum_value}: {e}")

@pytest.mark.parametrize("enum_field, EnumClass", [
    ("type", RequirementType),
    ("source", RequirementSource),
    ("priority", PriorityLevel),
    ("status", RequirementStatus),
    ("layer", RequirementLayer), # Layer is optional, but if provided, must be valid
])
def test_requirement_model_invalid_enum_values(enum_field, EnumClass):
    """Test Requirement model rejects invalid enum values."""
    data = {
        **VALID_BASE_REQUIREMENT_DATA,
        "type": RequirementType.constraint, # A valid default for type
         enum_field: "INVALID_ENUM_VALUE_XYZ"
    }
    # Ensure the base 'type' is valid if we are testing another field
    if enum_field != "type":
        data["type"] = RequirementType.functional

    with pytest.raises(ValidationError) as excinfo:
        Requirement(**data)
    
    errors = excinfo.value.errors()
    assert any(err['loc'][0] == enum_field and err['input'] == "INVALID_ENUM_VALUE_XYZ" for err in errors), \
        f"Expected ValidationError on field '{enum_field}' for input 'INVALID_ENUM_VALUE_XYZ', got: {errors}"


# --- Optional Fields & Constraints Tests ---

def test_requirement_model_optional_fields_not_provided():
    """Test Requirement model with optional fields not provided (using defaults)."""
    data = {
        "display_id": "REQ-OPT-NP",
        "type": RequirementType.functional,
        "description": "Desc for optional test.",
        "source": RequirementSource.developer,
        "priority": PriorityLevel.medium,
        "status": RequirementStatus.proposed,
        # layer, rationale, verification, versions, links are omitted
    }
    req = Requirement(**data)
    assert req.layer is None # Default for Optional[RequirementLayer]
    assert req.rationale is None
    assert req.verification is None
    assert req.versions == [] # Default for Optional[List[RequirementVersion]]
    assert req.links == []    # Default for Optional[List[Link]]

def test_requirement_model_optional_fields_provided():
    """Test Requirement model with optional fields provided with valid values."""
    # We need Link and RequirementVersion to be importable if we are to provide them
    # from app.schemas import Link, LinkType, RequirementVersion (ensure these are imported at the top)
    # from datetime import datetime # ensure imported

    link_data = {"target_id": "REQ-TARGET-1", "type": LinkType.depends_on} 
    version_data = {"timestamp": datetime.now(), "data": {"description": "Old desc"}}

    data = {
        "display_id": "REQ-OPT-P",
        "type": RequirementType.non_functional,
        "description": "Desc for optional provided test.",
        "source": RequirementSource.document,
        "priority": PriorityLevel.high,
        "status": RequirementStatus.approved,
        "layer": RequirementLayer.system,
        "rationale": "This is why.",
        "verification": "Check X and Y.",
        "versions": [version_data], 
        "links": [link_data]        
    }
    
    req = Requirement(**data)
    assert req.layer == RequirementLayer.system
    assert req.rationale == "This is why."
    assert req.verification == "Check X and Y."
    assert len(req.versions) == 1
    assert req.versions[0].data["description"] == "Old desc" 
    assert len(req.links) == 1
    assert req.links[0].target_id == "REQ-TARGET-1" 
    assert req.links[0].type == LinkType.depends_on

def test_requirement_model_description_min_length():
    """Test Requirement model 'description' field min_length constraint."""
    invalid_data = {
        "display_id": "REQ-DESC-EMPTY",
        "type": RequirementType.functional,
        "description": "", # Empty string, should fail min_length=1
        "source": RequirementSource.developer,
        "priority": PriorityLevel.low,
        "status": RequirementStatus.draft,
    }
    with pytest.raises(ValidationError) as excinfo:
        Requirement(**invalid_data)
    
    errors = excinfo.value.errors()
    assert any(err['loc'][0] == 'description' and 'string should have at least 1 character' in err['msg'].lower() for err in errors), \
        f"Expected ValidationError for empty description, got: {errors}"

    valid_data = {**invalid_data, "description": "D"} # Single character, should pass
    try:
        Requirement(**valid_data)
    except ValidationError as e:
        pytest.fail(f"Requirement instantiation failed with single char description: {e}")

