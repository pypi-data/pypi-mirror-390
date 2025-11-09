#!/usr/bin/env python3
"""Example using custom Python path.

This example demonstrates:
- Using runner with custom Python path
- Relative and absolute path specifications
"""

import argparse
import sys
from pathlib import Path

from argparse_ps1 import generate_ps1_wrapper


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Custom Python runner example")

    parser.add_argument(
        "-o",
        "--option",
        type=str,
        help="String option argument",
    )

    parser.add_argument(
        "--runner-type",
        choices=["venv", "system", "custom"],
        default="venv",
        help="Python runner type to demonstrate",
    )

    parser.add_argument(
        "--make-ps1",
        action="store_true",
        help="Generate PowerShell wrapper script",
    )

    args = parser.parse_args()

    if args.make_ps1:
        # Generate PowerShell wrapper script with different runner options
        runner_configs = {
            "venv": ".venv/Scripts/python.exe",  # Relative path to venv
            "system": "python",  # System Python
            "custom": "C:/Python312/python.exe",  # Custom absolute path (example)
        }

        runner = runner_configs[args.runner_type]

        output = generate_ps1_wrapper(
            parser,
            script_path=Path(__file__).resolve(),
            skip_dests={"make_ps1"},
            runner=runner,
        )
        print(f"Generated PowerShell wrapper with runner '{runner}': {output}")
        return 0

    # Handle the option
    if args.option:
        print(f"Custom runner ({args.runner_type}) - Option value: {args.option}")
    else:
        print(
            f"Custom runner ({args.runner_type}) - No option provided. Use --option <value> to set a value."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
