"""argparse-ps1: Generate PowerShell wrapper scripts for Python scripts executed with uv.

This library provides functionality to automatically generate PowerShell (.ps1) wrapper
scripts from Python scripts that use argparse for command-line argument parsing.

The generated PowerShell scripts provide a native PowerShell interface while internally
invoking the Python script with uv (or direct Python execution).
"""

from __future__ import annotations

from .argparse_ps1 import generate_ps1_wrapper

__all__ = ["generate_ps1_wrapper"]
__version__ = "0.1.5"
