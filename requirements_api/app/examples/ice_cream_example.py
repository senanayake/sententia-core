import uuid
import itertools
from ..store import requirements_store
from ..schemas import (
    Requirement, RequirementLayer, RequirementType, PriorityLevel,
    RequirementStatus, RequirementSource, Link, LinkType
)


_counter = itertools.count(1)
def _id(prefix: str) -> str:
    return f"{prefix}-{next(_counter):03d}"
def create_ice_cream_example() -> None:
    """Deep-dive Ice-Cream Shop demo with full traceability."""
    requirements_store.clear()

    # ────────────────────────────────────────────────────────────────
    # 1. BUSINESS REQUIREMENTS
    # ────────────────────────────────────────────────────────────────
    bus_online_orders = Requirement(
        display_id=_id("BUS"),
        layer=RequirementLayer.business,
        type=RequirementType.functional,
        title="Online Ordering Platform",
        description="Allow customers to order ice-cream online from any device.",
        rationale="Capture digital revenue and improve customer convenience.",
        source=RequirementSource.stakeholder,
        priority=PriorityLevel.high,
        status=RequirementStatus.approved,
    )
    bus_loyalty = Requirement(
        display_id=_id("BUS"),
        layer=RequirementLayer.business,
        type=RequirementType.functional,
        title="Loyalty Program",
        description="Introduce a loyalty points program redeemable online or in-store.",
        rationale="Increase repeat purchases by 15 % within one year.",
        source=RequirementSource.product_owner,
        priority=PriorityLevel.medium,
        status=RequirementStatus.approved,
    )
    bus_food_safety = Requirement(
        display_id=_id("BUS"),
        layer=RequirementLayer.business,
        type=RequirementType.constraint,
        title="Food Safety Compliance",
        description="Comply with FDA Food Code §3-501 on dairy handling.",
        rationale="Legal compliance—avoid fines & licence suspension.",
        source=RequirementSource.regulation,
        priority=PriorityLevel.high,
        status=RequirementStatus.approved,
    )

    # ────────────────────────────────────────────────────────────────
    # 2. SYSTEM REQUIREMENTS
    # ────────────────────────────────────────────────────────────────
    sys_user_interface = Requirement(
        display_id=_id("SYS"),
        layer=RequirementLayer.system,
        type=RequirementType.functional,
        title="User Interface Design",
        description="Create an intuitive, responsive interface for online ordering.",
        rationale="Ensure ease of use for customers across different devices.",
        source=RequirementSource.stakeholder,
        priority=PriorityLevel.high,
        status=RequirementStatus.draft,
    )
    sys_payment_integration = Requirement(
        display_id=_id("SYS"),
        layer=RequirementLayer.system,
        type=RequirementType.functional,
        title="Payment System Integration",
        description="Support multiple payment methods securely.",
        rationale="Provide flexible payment options for customers.",
        source=RequirementSource.product_owner,
        priority=PriorityLevel.high,
        status=RequirementStatus.draft,
    )
    sys_concurrency = Requirement(
        display_id=_id("SYS"),
        layer=RequirementLayer.system,
        type=RequirementType.non_functional,
        description="Support ≥ 2 000 concurrent sessions with < 2 s p95 response time.",
        rationale="Handle summer promo spikes 4× larger than baseline.",
        source=RequirementSource.document,
        priority=PriorityLevel.high,
        status=RequirementStatus.proposed,
        links=[
            Link(target_id=bus_online_orders.display_id, type=LinkType.satisfies)
        ],
    )
    sys_pci = Requirement(
        display_id=_id("SYS"),
        layer=RequirementLayer.system,
        type=RequirementType.constraint,
        description="All payment processing components shall be PCI-DSS v4.0 compliant.",
        rationale="Protect cardholder data & enable external audit.",
        source=RequirementSource.regulation,
        priority=PriorityLevel.high,
        status=RequirementStatus.approved,
        links=[
            Link(target_id=bus_online_orders.display_id, type=LinkType.depends_on)
        ],
    )
    sys_loyalty_service = Requirement(
        display_id=_id("SYS"),
        layer=RequirementLayer.system,
        type=RequirementType.functional,
        description="Provide a loyalty-points micro-service with REST + Webhooks.",
        rationale="Centralise points logic for web & POS channels.",
        source=RequirementSource.product_owner,
        priority=PriorityLevel.medium,
        status=RequirementStatus.proposed,
        links=[
            Link(target_id=bus_loyalty.display_id, type=LinkType.satisfies)
        ],
    )

    # ────────────────────────────────────────────────────────────────
    # 3. SOFTWARE REQUIREMENTS
    # ────────────────────────────────────────────────────────────────
    sw_cart = Requirement(
        display_id=_id("SWS"),
        layer=RequirementLayer.software,
        type=RequirementType.functional,
        description="Implement a Vue 3 cart component supporting flavour mix-ins & toppings.",
        rationale="Smooth UX on mobile; reuse component in kiosk app.",
        source=RequirementSource.document,
        priority=PriorityLevel.medium,
        status=RequirementStatus.draft,
        links=[
            Link(target_id=sys_concurrency.display_id,  type=LinkType.depends_on),
            Link(target_id=bus_online_orders.display_id, type=LinkType.refines),
        ],
    )
    sw_loyalty_api = Requirement(
        display_id=_id("SWS"),
        layer=RequirementLayer.software,
        type=RequirementType.functional,
        description="Expose `/points/balance` & `/points/redeem` endpoints (JSON, OAuth2).",
        rationale="Integrate loyalty with website and mobile-app checkout.",
        source=RequirementSource.developer,
        priority=PriorityLevel.medium,
        status=RequirementStatus.draft,
        links=[
            Link(target_id=sys_loyalty_service.display_id, type=LinkType.satisfies),
        ],
    )
    sw_temp_monitor = Requirement(
        display_id=_id("SWS"),
        layer=RequirementLayer.software,
        type=RequirementType.functional,
        description="Store freezer temperature logs every 10 min in immutable storage.",
        rationale="Evidence for FDA audits & food-safety analytics.",
        source=RequirementSource.regulation,
        priority=PriorityLevel.high,
        status=RequirementStatus.draft,
        links=[
            Link(target_id=bus_food_safety.display_id, type=LinkType.satisfies),
        ],
    )

    # ────────────────────────────────────────────────────────────────
    # 4. TEST REQUIREMENTS
    # ────────────────────────────────────────────────────────────────
    tst_cart_mixins = Requirement(
        display_id=_id("TST"),
        layer=RequirementLayer.test,
        type=RequirementType.verification,
        description="Automated test: submit an order with ≥ 3 mix-ins and verify total price.",
        rationale="Detect price-calculation regressions.",
        source=RequirementSource.developer,
        priority=PriorityLevel.low,
        status=RequirementStatus.planned,
        verification="Pytest + Playwright",
        links=[
            Link(target_id=sw_cart.display_id, type=LinkType.depends_on),
        ],
    )
    tst_loyalty_accrual = Requirement(
        display_id=_id("TST"),
        layer=RequirementLayer.test,
        type=RequirementType.verification,
        description="API test: after purchase, customer balance increases by earned points.",
        rationale="Guarantee loyalty rules consistency.",
        source=RequirementSource.developer,
        priority=PriorityLevel.low,
        status=RequirementStatus.planned,
        verification="Postman/Newman",
        links=[
            Link(target_id=sw_loyalty_api.display_id, type=LinkType.depends_on),
        ],
    )
    tst_performance = Requirement(
        display_id=_id("TST"),
        layer=RequirementLayer.test,
        type=RequirementType.verification,
        description="Load-test checkout for 2 000 virtual users, p95 < 2 s.",
        rationale="Prove non-functional performance target.",
        source=RequirementSource.support_ticket,
        priority=PriorityLevel.medium,
        status=RequirementStatus.planned,
        verification="k6 cloud test",
        links=[
            Link(target_id=sys_concurrency.display_id, type=LinkType.satisfies),
        ],
    )
    tst_temp_monitor = Requirement(
        display_id=_id("TST"),
        layer=RequirementLayer.test,
        type=RequirementType.verification,
        description="Unit test: temperature log rejected if older than 15 min.",
        rationale="Ensure data integrity for FDA audit trail.",
        source=RequirementSource.developer,
        priority=PriorityLevel.low,
        status=RequirementStatus.planned,
        verification="Pytest",
        links=[
            Link(target_id=sw_temp_monitor.display_id, type=LinkType.depends_on),
        ],
    )

    # ────────────────────────────────────────────────────────────────
    # Persist everything
    # ────────────────────────────────────────────────────────────────
    for req in [
        bus_online_orders, bus_loyalty, bus_food_safety,
        sys_concurrency, sys_pci, sys_loyalty_service,
        sw_cart, sw_loyalty_api, sw_temp_monitor,
        tst_cart_mixins, tst_loyalty_accrual, tst_performance, tst_temp_monitor,
    ]:
        requirements_store[req.display_id] = req.dict()