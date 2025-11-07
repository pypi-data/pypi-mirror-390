"""
Generic Custom Elements Manifest (CEM) parser for PyHTML.

Generates fully-typed web component classes from any custom-elements.json file.
"""

import json
import re
from pathlib import Path
from typing import Any

RESERVED_KEYWORDS = {
    "False",
    "None",
    "True",
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "try",
    "while",
    "with",
    "yield",
}

# FIX: keep those keywords in mind, consider escaping
PYHTML_BUILTINS = {"type", "id", "name", "value", "dir", "title", "open"}

# FIX: keep those keywords in mind, consider escaping
OTHER_BUILTINS = {
    "input",
    "format",
    "filter",
    "map",
    "max",
    "min",
    "range",
    "round",
    "slice",
    "sum",
    "zip",
    "help",
    "hash",
}


def sanitize_attr_name(name: str) -> str:
    """
    Convert attribute name to valid Python identifier.

    - Converts hyphens to underscores
    - Appends '_' to Python reserved keywords
    - Follows PyHTML's approach for built-ins

    Args:
        name: HTML attribute name (e.g., 'aria-label', 'for', 'from')

    Returns:
        Valid Python identifier (e.g., 'aria_label', 'for_', 'from_')
    """
    py_name = name.replace("-", "_")

    if py_name in RESERVED_KEYWORDS:
        return py_name + "_"

    if py_name in PYHTML_BUILTINS:
        return py_name
    return py_name


def sanitize_type(type_text: str) -> str:
    """
    Convert CEM type to Python type hint.

    Handles:
    - Primitive types (boolean, string, number)
    - Literal types with quoted values
    - Union types

    Args:
        type_text: Type string from CEM (e.g., "'red' | 'blue'", "boolean")

    Returns:
        Python type hint string (e.g., "Literal['red', 'blue'] | None", "bool | None")
    """
    if not type_text:
        return "str | bool | None"

    type_text = type_text.strip()

    if type_text == "boolean":
        return "bool | None"
    if type_text == "string":
        return "str | None"
    if type_text == "number":
        return "int | float | None"

    if "|" in type_text and "'" in type_text:
        values = re.findall(r"'([^']*)'", type_text)
        values = [v.strip() for v in values if v.strip()]
        if values:
            quoted = [f'"{v}"' for v in values]
            return f"Literal[{', '.join(quoted)}] | None"

    # Fallback on unknown types
    return "str | bool | None"


def escape_docstring(text: str) -> str:
    """
    Escape quotes and backslashes in docstrings.

    Args:
        text: Raw text that may contain quotes or backslashes

    Returns:
        Escaped text safe for use in triple-quoted docstrings
    """
    if not text:
        return ""
    return text.replace("\\", "\\\\").replace('"""', r"\"\"\"")


def generate_component_class(
    comp: dict[str, Any], *, include_slots: bool = False, prefix_to_strip: str = ""
) -> str:
    """
    Generate a PyHTML component class from CEM metadata.

    Creates a Tag subclass with:
    - Google-style docstring with attribute descriptions
    - Type-hinted __init__ method
    - Explicit None filtering
    - Reserved keyword handling

    Args:
        comp: Component metadata dict with keys: 'tag', 'name', 'attributes',
            'description', 'slots'
        include_slots: If True, include slot information in docstring

    Returns:
        Complete Python class definition as string

    """
    tag_name = comp["tag"]
    class_name = tag_name.replace("-", "_")

    # Strip prefix from class name if requested
    if prefix_to_strip and class_name.startswith(prefix_to_strip + "_"):
        class_name = class_name[len(prefix_to_strip) + 1 :]

    attributes = comp.get("attributes", [])
    description = escape_docstring(comp.get("description", "").strip())
    slots = comp.get("slots", []) if include_slots else []

    lines = []
    lines.append(f"class {class_name}(Tag):")

    # => Build docstring in Google style*
    docstring_lines = []

    if description:
        docstring_lines.append(description)
    else:
        docstring_lines.append(f"{tag_name} web component.")

    if attributes:
        docstring_lines.append("")
        docstring_lines.append("Args:")
        docstring_lines.append("    *children: Child elements and text content")

        for attr in attributes:
            attr_name = attr["name"]
            py_attr_name = sanitize_attr_name(attr_name)
            attr_desc = escape_docstring(attr.get("description", ""))
            attr_type = attr.get("type", {}).get("text", "")

            if attr_desc:
                # Wrap long descriptions
                desc_lines = attr_desc.split("\n")
                docstring_lines.append(f"    {py_attr_name}: {desc_lines[0]}")
                for line in desc_lines[1:]:
                    if line.strip():
                        docstring_lines.append(f"        {line.strip()}")
            elif attr_type:
                docstring_lines.append(f"    {py_attr_name}: Type: {attr_type}")
            else:
                docstring_lines.append(f"    {py_attr_name}: No description available")

        docstring_lines.append("    **attributes: Additional HTML attributes")

    if slots:
        docstring_lines.append("")
        docstring_lines.append("Slots:")
        for slot in slots:
            slot_name = slot.get("name", "default")
            slot_desc = escape_docstring(slot.get("description", ""))
            if slot_desc:
                docstring_lines.append(f"    {slot_name}: {slot_desc}")

    # Add example if it's a simple component
    if len(attributes) <= 3 and description:
        docstring_lines.append("")
        docstring_lines.append("Example:")
        example_attrs = ", ".join(
            [f'{sanitize_attr_name(attr["name"])}="value"' for attr in attributes[:2]]
        )
        docstring_lines.append(
            f'    >>> {class_name}("content"{", " + example_attrs if example_attrs else ""})'
        )

    docstring = '    """\n'
    for line in docstring_lines:
        docstring += f"    {line}\n" if line else "\n"
    docstring += '    """'
    lines.append(docstring)

    init_params = ["self", "*children: ChildrenType"]
    attr_updates = []

    for attr in attributes:
        attr_name = attr["name"]
        py_attr_name = sanitize_attr_name(attr_name)
        type_hint = sanitize_type(attr.get("type", {}).get("text", ""))

        init_params.append(f"{py_attr_name}: {type_hint} = None")
        attr_updates.append((py_attr_name, py_attr_name))

    init_params.append("**attributes: AttributeType")

    # build signature
    lines.append("    def __init__(")
    for param in init_params:
        lines.append(f"        {param},")
    lines.append("    ) -> None:")

    lines.append("        # Build attributes dict, filtering out None values")
    lines.append("        attributes = attributes.copy()")
    lines.append("        attributes.update({")
    for py_name, _ in attr_updates:
        lines.append(f"            '{py_name}': {py_name},")
    lines.append("        })")
    lines.append("        # Filter out None values and False booleans, convert numbers to strings")
    lines.append("        attributes = {")
    lines.append("            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v")
    lines.append("            for k, v in attributes.items()")
    lines.append("            if v is not None and v is not False")
    lines.append("        }")
    lines.append("        super().__init__(*children, **attributes)")

    lines.append("")
    lines.append("    def _get_tag_name(self) -> str:")
    lines.append(f'        return "{tag_name}"')

    return "\n".join(lines)


def extract_components(cem_path: str | Path) -> list[dict[str, Any]]:
    """
    Extract component metadata from a CEM file.

    Args:
        cem_path: Path to custom-elements.json file

    Returns:
        List of component dictionaries with keys: name, tag, attributes, slots, description
    """
    with open(cem_path, "r") as f:
        data = json.load(f)

    components = []
    for module in data.get("modules", []):
        for decl in module.get("declarations", []):
            if decl.get("tagName"):
                components.append(
                    {
                        "name": decl["name"],
                        "tag": decl["tagName"],
                        "attributes": decl.get("attributes", []),
                        "slots": decl.get("slots", []),
                        "description": decl.get("description", ""),
                    }
                )

    components.sort(key=lambda c: c["tag"])
    return components


def generate_single_component_file(
    comp: dict[str, Any], *, include_slots: bool = False, prefix_to_strip: str = ""
) -> str:
    """
    Generate a single component Python file.

    Args:
        comp: Component metadata dictionary
        include_slots: Include slot documentation

    Returns:
        Complete Python module code for one component
    """
    tag_name = comp["tag"]
    class_name = tag_name.replace("-", "_")

    # strips prefix from class name if requested
    if prefix_to_strip and class_name.startswith(prefix_to_strip + "_"):
        class_name = class_name[len(prefix_to_strip) + 1 :]

    output = []
    output.append(f'"""')
    output.append(f"{comp['tag']} component.")
    output.append('"""')
    output.append("")
    output.append("from typing import Literal")
    output.append("from pyhtml import Tag")
    output.append("from pyhtml.__types import ChildrenType, AttributeType")
    output.append("")
    output.append("")
    output.append(
        generate_component_class(
            comp, include_slots=include_slots, prefix_to_strip=prefix_to_strip
        )
    )
    output.append("")
    output.append("")
    output.append("__all__ = [")
    output.append(f'    "{class_name}",')
    output.append("]")

    return "\n".join(output)


def generate_components_init(
    components: list[dict[str, Any]], prefix_to_strip: str = ""
) -> str:
    """
    Generate __init__.py for components/ directory.

    Args:
        components: List of component metadata dictionaries
        prefix_to_strip: Optional prefix to strip from component class names

    Returns:
        Python code for components/__init__.py with all imports
    """
    output = []
    output.append('"""All generated components."""')
    output.append("")

    # Generate imports
    for comp in components:
        tag_name = comp["tag"]
        full_class_name = tag_name.replace("-", "_")

        if prefix_to_strip and full_class_name.startswith(prefix_to_strip + "_"):
            class_name = full_class_name[len(prefix_to_strip) + 1 :]
        else:
            class_name = full_class_name

        module_name = (
            full_class_name.replace(
                tag_name.split("-")[0] + "_", "", 1
            )  # FIX: Redundant and/or precarious
            if "_" in full_class_name
            else full_class_name
        )
        output.append(f"from .{module_name} import {class_name}")

    output.append("")
    output.append("__all__ = [")
    for comp in components:
        tag_name = comp["tag"]
        full_class_name = tag_name.replace("-", "_")

        # Determine the actual class name
        if prefix_to_strip and full_class_name.startswith(prefix_to_strip + "_"):
            class_name = full_class_name[len(prefix_to_strip) + 1 :]
        else:
            class_name = full_class_name

        output.append(f'    "{class_name}",')
    output.append("]")

    return "\n".join(output)


def generate_stub_file(comp: dict[str, Any], prefix_to_strip: str = "", include_slots: bool = False) -> str:
    """
    Generate a .pyi stub file for a component.

    Args:
        comp: Component metadata dictionary
        prefix_to_strip: Optional prefix to strip from component class names
        include_slots: If True, include slot information in docstring

    Returns:
        Complete .pyi stub file content
    """
    tag_name = comp["tag"]
    class_name = tag_name.replace("-", "_")

    if prefix_to_strip and class_name.startswith(prefix_to_strip + "_"):
        class_name = class_name[len(prefix_to_strip) + 1 :]

    attributes = comp.get("attributes", [])
    description = escape_docstring(comp.get("description", "").strip())
    slots = comp.get("slots", []) if include_slots else []

    output = []
    output.append(f'"""Type stub for {tag_name} component."""')
    output.append("")
    output.append("from typing import Literal")
    output.append("from pyhtml import Tag")
    output.append("from pyhtml.__types import ChildrenType, AttributeType")
    output.append("")
    output.append("")
    output.append(f"class {class_name}(Tag):")

    # Build docstring in Google style (same as in generate_component_class)
    docstring_lines = []

    if description:
        docstring_lines.append(description)
    else:
        docstring_lines.append(f"{tag_name} web component.")

    if attributes:
        docstring_lines.append("")
        docstring_lines.append("Args:")
        docstring_lines.append("    *children: Child elements and text content")

        for attr in attributes:
            attr_name = attr["name"]
            py_attr_name = sanitize_attr_name(attr_name)
            attr_desc = escape_docstring(attr.get("description", ""))
            attr_type = attr.get("type", {}).get("text", "")

            if attr_desc:
                # Wrap long descriptions
                desc_lines = attr_desc.split("\n")
                docstring_lines.append(f"    {py_attr_name}: {desc_lines[0]}")
                for line in desc_lines[1:]:
                    if line.strip():
                        docstring_lines.append(f"        {line.strip()}")
            elif attr_type:
                docstring_lines.append(f"    {py_attr_name}: Type: {attr_type}")
            else:
                docstring_lines.append(f"    {py_attr_name}: No description available")

        docstring_lines.append("    **attributes: Additional HTML attributes")

    if slots:
        docstring_lines.append("")
        docstring_lines.append("Slots:")
        for slot in slots:
            slot_name = slot.get("name", "default")
            slot_desc = escape_docstring(slot.get("description", ""))
            if slot_desc:
                docstring_lines.append(f"    {slot_name}: {slot_desc}")

    # Add docstring to output
    docstring = '    """\n'
    for line in docstring_lines:
        docstring += f"    {line}\n" if line else "\n"
    docstring += '    """'
    output.append(docstring)

    # Build __init__ signature
    init_params = ["self", "*children: ChildrenType"]
    for attr in attributes:
        py_attr_name = sanitize_attr_name(attr["name"])
        type_hint = sanitize_type(attr.get("type", {}).get("text", ""))
        init_params.append(f"{py_attr_name}: {type_hint} = ...")
    init_params.append("**attributes: AttributeType")

    output.append("    def __init__(")
    for param in init_params:
        output.append(f"        {param},")
    output.append("    ) -> None: ...")
    output.append("")
    output.append("    def _get_tag_name(self) -> str: ...")

    return "\n".join(output)


def generate_components_init_stub(
    components: list[dict[str, Any]], prefix_to_strip: str = ""
) -> str:
    """
    Generate __init__.pyi stub for components/ directory.

    Args:
        components: List of component metadata dictionaries
        prefix_to_strip: Optional prefix to strip from component class names

    Returns:
        Python stub code for components/__init__.pyi
    """
    output = []
    output.append('"""Type stubs for all generated components."""')
    output.append("")

    for comp in components:
        tag_name = comp["tag"]
        full_class_name = tag_name.replace("-", "_")

        # Determine the actual class name (with prefix stripped if requested)
        if prefix_to_strip and full_class_name.startswith(prefix_to_strip + "_"):
            class_name = full_class_name[len(prefix_to_strip) + 1 :]
        else:
            class_name = full_class_name

        module_name = (
            full_class_name.replace(tag_name.split("-")[0] + "_", "", 1)
            if "_" in full_class_name
            else full_class_name
        )
        output.append(f"from .{module_name} import {class_name} as {class_name}")

    output.append("")
    output.append("__all__: list[str]")

    return "\n".join(output)


def generate_main_init_stub(
    components: list[dict[str, Any]], prefix_to_strip: str = ""
) -> str:
    """
    Generate __init__.pyi stub for main package directory.

    Args:
        components: List of component metadata dictionaries
        prefix_to_strip: Optional prefix to strip from component class names

    Returns:
        Python stub code for __init__.pyi
    """
    output = []
    output.append('"""Type stubs for lazy-loaded components."""')
    output.append("")
    output.append("from .components import (")

    for comp in components:
        tag_name = comp["tag"]
        full_class_name = tag_name.replace("-", "_")

        # Determine the actual class name
        if prefix_to_strip and full_class_name.startswith(prefix_to_strip + "_"):
            class_name = full_class_name[len(prefix_to_strip) + 1 :]
        else:
            class_name = full_class_name

        output.append(f"    {class_name} as {class_name},")

    output.append(")")
    output.append("")
    output.append("__all__: list[str]")

    return "\n".join(output)


def generate_component_code(
    cem_path: str | Path,
    output_dir: str | Path,
    package_name: str = "components",
    *,
    include_slots: bool = False,
    prefix_to_strip: str = "",
) -> dict[str, Path]:
    """
    Generate split component files from a CEM file.

    Args:
        cem_path: Path to custom-elements.json file
        output_dir: Directory to write component files to
        package_name: Name for the generated package (used in docstring)
        include_slots: If True, include slot documentation in component docstrings
        prefix_to_strip: Optional prefix to strip from component names for unprefixed aliases
                        (e.g., "wa" creates both wa_button and button)

    Returns:
        Dictionary mapping component names to their file paths

    Example:
        >>> files = generate_component_code("custom-elements.json", "my_lib/components")
        >>> "wa_button" in files
        True
    """
    output_dir = Path(output_dir)
    components = extract_components(cem_path)

    components_dir = output_dir / "components"
    components_dir.mkdir(parents=True, exist_ok=True)

    file_map = {}

    for comp in components:
        class_name = comp["tag"].replace("-", "_")
        prefix = comp["tag"].split("-")[0] + "_"
        module_name = (
            class_name.replace(prefix, "", 1)
            if class_name.startswith(prefix)
            else class_name
        )
        filename = f"{module_name}.py"

        content = generate_single_component_file(
            comp, include_slots=include_slots, prefix_to_strip=prefix_to_strip
        )
        file_path = components_dir / filename
        file_path.write_text(content)
        file_map[class_name] = file_path

        stub_content = generate_stub_file(comp, prefix_to_strip=prefix_to_strip, include_slots=include_slots)
        stub_path = components_dir / f"{module_name}.pyi"
        stub_path.write_text(stub_content)

    init_content = generate_components_init(components, prefix_to_strip)
    (components_dir / "__init__.py").write_text(init_content)

    components_init_stub = generate_components_init_stub(components, prefix_to_strip)
    (components_dir / "__init__.pyi").write_text(components_init_stub)

    main_init_content = generate_main_init(package_name, components, prefix_to_strip)
    (output_dir / "__init__.py").write_text(main_init_content)

    main_init_stub = generate_main_init_stub(components, prefix_to_strip)
    (output_dir / "__init__.pyi").write_text(main_init_stub)

    (output_dir / "py.typed").write_text("")

    return file_map


def generate_main_init(
    package_name: str, components: list[dict[str, Any]], prefix_to_strip: str = ""
) -> str:
    """
    Generate main __init__.py with lazy loading support.

    Args:
        package_name: Name of the package
        components: List of component metadata dictionaries
        prefix_to_strip: Optional prefix to strip from component class names

    Returns:
        Python code for main __init__.py
    """
    output = []
    output.append('"""')
    output.append(f"{package_name.capitalize()} components for PyHTML.")
    output.append("")
    output.append(
        f"Auto-generated from Custom Elements Manifest - {len(components)} components."
    )
    output.append("")
    output.append(
        "This module uses lazy loading: components are only imported when first accessed."
    )
    output.append('"""')
    output.append("")
    output.append("__all__ = [")

    for comp in components:
        tag_name = comp["tag"]
        full_class_name = tag_name.replace("-", "_")

        # Determine the actual class name
        if prefix_to_strip and full_class_name.startswith(prefix_to_strip + "_"):
            class_name = full_class_name[len(prefix_to_strip) + 1 :]
        else:
            class_name = full_class_name

        output.append(f'    "{class_name}",')

    output.append("]")
    output.append("")
    output.append("")
    output.append("_component_cache = {}")
    output.append("")
    output.append("")
    output.append("def __getattr__(name: str):")
    output.append('    """Lazy load components on demand."""')
    output.append("    if name in __all__:")
    output.append("        if name not in _component_cache:")
    output.append("            from . import components")
    output.append("            _component_cache[name] = getattr(components, name)")
    output.append("        return _component_cache[name]")
    output.append(
        f'    raise AttributeError(f"module {{__name__}} has no attribute {{name}}")'
    )

    return "\n".join(output)


__all__ = [
    "generate_component_code",
    "generate_component_class",
    "generate_single_component_file",
    "generate_components_init",
    "generate_components_init_stub",
    "generate_main_init",
    "generate_main_init_stub",
    "generate_stub_file",
    "extract_components",
    "sanitize_attr_name",
    "sanitize_type",
    "escape_docstring",
    "RESERVED_KEYWORDS",
    "PYHTML_BUILTINS",
]
