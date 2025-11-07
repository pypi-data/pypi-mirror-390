#!/usr/bin/env python3
"""
Regenerate WebAwesome components from CEM.

This script regenerates all WebAwesome components from the custom-elements.json
file. Run this when the WebAwesome/Shoelace library is updated.

Usage:
    # As installed script
    regen-webawesome

    # Or directly
    python -m pyhtml_cem.scripts.regen_webawesome
"""

import shutil
import sys
from pathlib import Path

from pyhtml_cem.cem_parser import generate_component_code


def main():
    """Regenerate WebAwesome components."""
    # Find project root (where pyproject.toml is)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    cem_file = project_root / "manifests" / "WebAwesome.json"
    output_dir = project_root / "pyhtml_cem" / "webawesome"

    print("=" * 60)
    print("Regenerating WebAwesome Components")
    print("=" * 60)
    print()

    # Check CEM file exists
    if not cem_file.exists():
        print(f"Error: CEM file not found at {cem_file}")
        print()
        print("Expected location: manifests/WebAwesome.json")
        print("Make sure the WebAwesome manifest is in the manifests directory")
        return 1

    # Delete old webawesome module
    if output_dir.exists():
        print("X - Deleting old webawesome module...")
        shutil.rmtree(output_dir)
        print("✓ - Deleted")

    # Generate new components
    print("Generating components...")
    try:
        file_map = generate_component_code(
            cem_file, output_dir, "webawesome", include_slots=True, prefix_to_strip="wa"
        )

        print(f"✓ Generated {len(file_map)} components")
        print(f"✓ Created split files in components/")
        print(f"✓ Created .pyi stub files")
        print(f"✓ Created py.typed marker")
        print(f"✓ Created lazy loading __init__.py")

    except Exception as e:
        print(f"   Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    print()
    print("=" * 60)
    print("WebAwesome components regenerated successfully!")
    print("=" * 60)
    print()
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
