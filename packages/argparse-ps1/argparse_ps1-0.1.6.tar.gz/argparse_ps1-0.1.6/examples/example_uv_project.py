#!/usr/bin/env python3
"""Example using uv run --project mode.

This example demonstrates:
- Using project mode with command_name
- Requires pyproject.toml with [project.scripts] section
"""

import argparse
import sys
from pathlib import Path

from argparse_ps1 import generate_ps1_wrapper


def main() -> int:
    """Main entry point."""
    print("=" * 60)
    print("PROJECT MODE EXAMPLE")
    print("=" * 60)
    print("This example demonstrates uv run with project mode.")
    print("NOTE: For proper PowerShell wrapper generation, you need:")
    print("  1. A pyproject.toml with [project.scripts] entry")
    print("  2. Proper package structure")
    print("  3. Examples should be run as: uv run python example_uv_project.py")
    print("-" * 60)

    parser = argparse.ArgumentParser(description="Project mode example")

    parser.add_argument(
        "-o",
        "--option",
        type=str,
        help="String option argument",
    )

    parser.add_argument(
        "--make-ps1",
        action="store_true",
        help="Generate PowerShell wrapper script",
    )

    args = parser.parse_args()

    if args.make_ps1:
        # Generate PowerShell wrapper script using uv run --project
        # This requires a pyproject.toml with [project.scripts] entry
        output = generate_ps1_wrapper(
            parser,
            script_path=Path(__file__).resolve(),
            skip_dests={"make_ps1"},
            command_name="example-uv-project",  # Matches [project.scripts]
        )
        print(f"Generated PowerShell wrapper: {output}")
        return 0

    # Handle the option
    if args.option:
        print(f"Project mode - Option value: {args.option}")
    else:
        print("Project mode - No option provided. Use --option <value> to set a value.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
