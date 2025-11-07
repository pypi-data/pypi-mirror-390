"""CLI tool for PyHTML CEM parser."""

import argparse
import sys
from pathlib import Path

from .cem_parser import generate_component_code


def generate_command(args):
    """Generate Python code from a CEM file."""
    cem_path = Path(args.cem_file)

    if not cem_path.exists():
        print(f"Error: CEM file not found: {cem_path}", file=sys.stderr)
        return 1

    output_dir = Path(args.output) if args.output else Path(args.package_name)

    try:
        print(f"Generating components from {cem_path}...")
        file_map = generate_component_code(
            cem_path, output_dir, args.package_name, include_slots=args.include_slots
        )

        print(f" => Generated {len(file_map)} components in {output_dir}/components/")

        return 0

    except Exception as e:
        print(f"Error generating components: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="pyhtml-cem",
        description="Generate PyHTML components from Custom Elements Manifest files",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate Python code from a CEM file"
    )
    generate_parser.add_argument("cem_file", help="Path to custom-elements.json file")
    generate_parser.add_argument(
        "-o", "--output", help="Output directory path (default: <package_name>/)"
    )
    generate_parser.add_argument(
        "-p",
        "--package-name",
        default="components",
        help="Package name for generated code (default: components)",
    )
    generate_parser.add_argument(
        "--include-slots",
        action="store_true",
        help="Include slot documentation in docstrings",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "generate":
        return generate_command(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
