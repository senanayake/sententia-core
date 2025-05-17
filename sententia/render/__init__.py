
"""Rendering helpers for Sententia documents.

Usage:
    from sententia.render import render_doc
    markdown = render_doc("srd", context_dict_or_dataclass)
"""

from pathlib import Path
from typing import Any, Mapping

from jinja2 import Environment, FileSystemLoader, select_autoescape

_TEMPLATE_BASE = Path(__file__).parent / "templates"

env = Environment(
    loader=FileSystemLoader(_TEMPLATE_BASE),
    autoescape=select_autoescape(["md", "html"])
)

def _to_mapping(ctx: Any) -> Mapping[str, Any]:
    """Convert Pydantic/dataclass/object or dict to a plain mapping."""
    if isinstance(ctx, Mapping):
        return ctx
    if hasattr(ctx, "dict"):
        return ctx.dict()  # Pydantic
    return ctx.__dict__

def render_doc(kind: str, ctx: Any) -> str:
    """Render templates/<kind>/body.md.j2 using *ctx*.

    *kind*: subfolder name inside templates/
    *ctx*:  dict, pydantic model, or plain object with attributes.
    """
    template_path = f"{kind}/body.md.j2"
    template = env.get_template(template_path)
    return template.render(**_to_mapping(ctx))
