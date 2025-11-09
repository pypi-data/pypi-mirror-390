#!/usr/bin/env python3
"""Advanced example with string option argument.

This example demonstrates:
- String option arguments
- Using uv run (default runner)
"""

import argparse
import sys
from pathlib import Path

from argparse_ps1 import generate_ps1_wrapper


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Advanced example with options")

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
        # Generate PowerShell wrapper script using uv run
        output = generate_ps1_wrapper(
            parser,
            script_path=Path(__file__).resolve(),
            skip_dests={"make_ps1"},
        )
        print(f"Generated PowerShell wrapper: {output}")
        return 0

    # Handle the option
    if args.option:
        print(f"Option value: {args.option}")
    else:
        print("No option provided. Use --option <value> to set a value.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
