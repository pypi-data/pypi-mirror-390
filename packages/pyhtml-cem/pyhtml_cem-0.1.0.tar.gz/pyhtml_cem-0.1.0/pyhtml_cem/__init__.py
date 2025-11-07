"""
PyHTML CEM - Custom Elements Manifest parser and component libraries.

This package provides:
1. A generic CEM parser (`cem_parser`) for generating PyHTML components from
   any Custom Elements Manifest file
2. Pre-generated component for `webawesome` (formely ShoeLace)

Usage:
    # Use the parser as a library
    from pyhtml_cem import generate_component_code
    code = generate_component_code("custom-elements.json", "my_library")

    # Use pre-generated libraries
    import pyhtml_cem.webawesome.components as wa
    page = wa.card(wa_button("Click me", variant="brand"))

"""

from .cem_parser import (
    PYHTML_BUILTINS,
    RESERVED_KEYWORDS,
    escape_docstring,
    generate_component_class,
    generate_component_code,
    sanitize_attr_name,
    sanitize_type,
)

__version__ = "0.1.0"

__all__ = [
    "generate_component_code",
    "generate_component_class",
    "sanitize_attr_name",
    "sanitize_type",
    "escape_docstring",
    "RESERVED_KEYWORDS",
    "PYHTML_BUILTINS",
]
