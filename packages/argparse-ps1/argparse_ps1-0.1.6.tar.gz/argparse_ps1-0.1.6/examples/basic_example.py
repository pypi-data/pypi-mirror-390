#!/usr/bin/env python3
"""Basic example of argparse-ps1 usage.

This example demonstrates:
- Simple argument parsing with argparse
- Generating a PowerShell wrapper script
- Using boolean flags
"""

import argparse
import sys
from pathlib import Path

from argparse_ps1 import generate_ps1_wrapper


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Simple greeting script")

    parser.add_argument(
        "--hello",
        action="store_true",
        help="Say hello",
    )

    parser.add_argument(
        "--bye",
        action="store_true",
        help="Say goodbye",
    )

    parser.add_argument(
        "--make-ps1",
        action="store_true",
        help="Generate PowerShell wrapper script",
    )

    args = parser.parse_args()

    if args.make_ps1:
        # Generate PowerShell wrapper script
        output = generate_ps1_wrapper(
            parser,
            script_path=Path(__file__).resolve(),
            skip_dests={"make_ps1"},  # Skip the --make-ps1 argument itself
        )
        print(f"Generated PowerShell wrapper: {output}")
        return 0

    # Handle greetings
    if args.hello:
        print("Hello World")

    if args.bye:
        print("Bye bye")

    if not args.hello and not args.bye:
        print("Use --hello or --bye to get a greeting!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
