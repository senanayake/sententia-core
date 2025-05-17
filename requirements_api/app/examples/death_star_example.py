import uuid
from ..store import requirements_store
from ..schemas import Requirement, RequirementLayer, RequirementType, RequirementSource, PriorityLevel, RequirementStatus

def create_death_star_example():
    """Inject example Death Star requirements into the in-memory store."""
    requirements_store.clear()

    example_data = [
        Requirement(
            type=RequirementType.functional,
            description="The Galactic Empire shall construct a mobile battle station capable of planetary destruction to ensure galactic stability and suppress rebellion.",
            rationale="Maintain control and deter insurgency across the galaxy.",
            source=RequirementSource.stakeholder, # Lord Vader's Edict
            priority=PriorityLevel.high,
            status=RequirementStatus.approved,
            verification="Imperial Charter",
            layer=RequirementLayer.business,
            versions=[],
            links=[]
        ),
        Requirement(
            type=RequirementType.functional,
            description="The battle station must possess a superlaser with sufficient power to destroy a planet of size comparable to Alderaan with a single focused blast.",
            rationale="Demonstrate overwhelming firepower and eliminate key rebel strongholds.",
            source=RequirementSource.document, # KDY-DS-001 Superlaser Specification
            priority=PriorityLevel.high,
            status=RequirementStatus.approved,
            verification="Successful test firing (e.g., Jedha, Scarif)",
            layer=RequirementLayer.system,
            versions=[],
            links=[]
        ),
        Requirement(
            type=RequirementType.functional,
            description="The battle station must be equipped with a Class 1 hyperdrive system allowing for rapid interstellar travel between key systems within the Empire.",
            rationale="Enable swift deployment to any sector requiring Imperial presence.",
            source=RequirementSource.document, # SFS-DS-HD-C1 Hyperdrive Manual
            priority=PriorityLevel.high,
            status=RequirementStatus.approved,
            verification="Interstellar jump completion within specified timeframes",
            layer=RequirementLayer.system,
            versions=[],
            links=[]
        ),
        Requirement(
            type=RequirementType.functional,
            description="The battle station shall be defended by a minimum of 10,000 Taim & Bak XX-9 heavy turbolaser emplacements and 2,500 Borstel NK-7 ion cannons.",
            rationale="Provide comprehensive defense against capital ship and starfighter assaults.",
            source=RequirementSource.document, # DS-DEF-GRID-LAYOUT-V2.1
            priority=PriorityLevel.high,
            status=RequirementStatus.approved,
            verification="Combat simulation and live-fire exercises",
            layer=RequirementLayer.system,
            versions=[],
            links=[]
        ),
        Requirement(
            type=RequirementType.non_functional, # Performance
            description="The superlaser must achieve full operational charge from a depleted state within 12 standard hours.",
            rationale="Ensure rapid re-engagement capability during prolonged operations.",
            source=RequirementSource.document, # SL-PWR-CYCLE-SPEC-003
            priority=PriorityLevel.high,
            status=RequirementStatus.approved,
            verification="Power cycle testing under various load conditions",
            layer=RequirementLayer.system,
            versions=[],
            links=[]
        ),
        Requirement(
            type=RequirementType.functional,
            description="The superlaser targeting software must provide accuracy to within 0.0001% of the designated planetary target coordinates at maximum range.",
            rationale="Ensure precise destruction and minimize collateral damage to non-target celestial bodies (if any).",
            source=RequirementSource.document, # TGTSYS-ACC-REQ-V4
            priority=PriorityLevel.high,
            status=RequirementStatus.approved,
            verification="Simulation, calibration routines, and post-firing analysis",
            layer=RequirementLayer.software,
            versions=[],
            links=[]
        ),
        Requirement(
            type=RequirementType.non_functional, # Usability for Bridge Crew
            description="Primary flight and weapons control interfaces shall provide intuitive feedback and require no more than 3 actions to execute critical functions (e.g., initiate jump, fire weapon).",
            rationale="Reduce operator error and improve response times during high-stress situations.",
            source=RequirementSource.document, # DS-BRIDGE-ERGONOMICS-STUDY
            priority=PriorityLevel.medium,
            status=RequirementStatus.proposed,
            verification="User acceptance testing with bridge simulator",
            layer=RequirementLayer.software,
            versions=[],
            links=[]
        ),
        Requirement(
            type=RequirementType.verification,
            description="A full-scale destructive test of the superlaser must be conducted on an uninhabited terrestrial planet prior to full operational deployment.",
            rationale="Validate end-to-end system functionality and destructive capability.",
            source=RequirementSource.document, # DS-COMMISSION-TEST-PLAN-001
            priority=PriorityLevel.high,
            status=RequirementStatus.planned,
            verification="Successful planetary destruction and system telemetry review",
            layer=RequirementLayer.test,
            versions=[],
            links=[]
        ),
        Requirement(
            type=RequirementType.non_functional, # Security
            description="All thermal exhaust ports leading to the main reactor must be shielded and no larger than 2 meters in diameter to prevent single-starfighter-exploitable vulnerabilities.",
            rationale="Protect the station's primary power source from targeted attacks.",
            source=RequirementSource.document, # DS-SECURITY-AUDIT-R2 (Post-Yavin assessment)
            priority=PriorityLevel.high, # Oops!
            status=RequirementStatus.draft, # Lesson learned
            verification="Design inspection and threat modeling",
            layer=RequirementLayer.system,
            versions=[],
            links=[]
        )
    ]

    for req_model in example_data:
        display_id = f"REQ-DS-{str(uuid.uuid4())[:6].upper()}" # Unique prefix for Death Star
        req_dict = req_model.dict()
        req_dict["display_id"] = display_id
        # 'versions' and 'links' are already part of the Requirement model, initialized to []
        requirements_store[display_id] = req_dict
