from __future__ import annotations

import argparse
import os
import tomllib
from collections.abc import Iterable, Sequence
from pathlib import Path


def generate_ps1_wrapper(
    parser: argparse.ArgumentParser,
    *,
    script_path: Path,
    output_path: Path | None = None,
    output_dir: Path | None = None,
    skip_dests: Iterable[str] | None = None,
    runner: str = "uv",
    command_name: str | None = None,
) -> Path:
    """Generate a PowerShell wrapper script for the provided :mod:`argparse` parser.

    Args:
        parser: ArgumentParser instance to generate wrapper for
        script_path: Path to the Python script (absolute)
        output_path: Output path for the .ps1 file (optional)
        output_dir: Directory where .ps1 will be placed (default: script's directory)
        skip_dests: Parameter destinations to skip
        runner: Command to run Python (default: "uv")
        command_name: Command name registered in [project.scripts]. If specified,
                     automatically searches for pyproject.toml and uses --project mode.
    """

    skip = {"help"}
    if skip_dests:
        skip.update(skip_dests)

    regular_actions: list[argparse.Action] = []

    for action in parser._actions:
        if action.dest in skip:
            continue
        regular_actions.append(action)

    # Generate PowerShell-style filename: Kebab-Case.ps1
    if output_path is None:
        ps1_name = _to_powershell_filename(script_path.stem)
        if output_dir is None:
            # Default output directory is current working directory
            output_path = Path.cwd() / f"{ps1_name}.ps1"
        else:
            output_path = output_dir / f"{ps1_name}.ps1"

    # Determine execution mode based on runner and command_name
    use_project_mode = False
    project_root = None

    if runner == "uv":
        if command_name is not None:
            # uv + command_name -> project mode (must validate)
            # Find pyproject.toml by walking up from script_path
            current = script_path.parent
            while current != current.parent:
                if (current / "pyproject.toml").exists():
                    project_root = current
                    break
                current = current.parent

            if project_root is None:
                raise ValueError(
                    f"command_name '{command_name}' specified but no pyproject.toml found"
                )

            # Validate that command_name exists in [project.scripts]
            pyproject_path = project_root / "pyproject.toml"
            try:
                with pyproject_path.open("rb") as f:
                    data = tomllib.load(f)
            except Exception as e:
                raise ValueError(f"Failed to read pyproject.toml: {e}") from e

            scripts = data.get("project", {}).get("scripts", {})
            if not scripts:
                raise ValueError("No [project.scripts] section found in pyproject.toml")

            if command_name not in scripts:
                raise ValueError(
                    f"command_name '{command_name}' not found in [project.scripts]"
                )

            use_project_mode = True
        # else: uv without command_name -> direct script mode with relative path

    # Filter actions, excluding help and specified skip_dests
    regular_actions = [
        action
        for action in parser._actions
        if action.dest != "help"
        and (skip_dests is None or action.dest not in skip_dests)
    ]

    # Generate PowerShell code components
    param_block = _render_param_block(regular_actions)
    argument_conversion = _render_argument_conversion(regular_actions)

    # Handle runner path resolution
    if "/" in runner or "\\" in runner:
        # Path specified - normalize using Path
        runner_path = Path(runner)
        # Normalize path separators for consistency
        runner_literal = str(runner_path)
    else:
        # Simple command name
        runner_literal = runner

    if use_project_mode:
        # --project mode: use registered command
        if project_root is None:
            raise RuntimeError("Internal error: project_root is None in project mode")
        if command_name is None:
            raise RuntimeError("Internal error: command_name is None in project mode")
        project_relative_path = _calculate_project_relative_path(
            project_root, output_path
        )
        unknown_args_check = _render_unknown_args_check(
            runner=runner_literal, use_project_mode=True, command_name=command_name
        )
        lines: list[str] = [
            "#!/usr/bin/env pwsh",
            "",
            f"# uv run --project mode: Execute command '{command_name}' registered in [project.scripts]",
            "",
            param_block,
            unknown_args_check,
            "# Set PowerShell output encoding to UTF-8",
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8",
            "$OutputEncoding = [System.Text.Encoding]::UTF8",
            "",
            "$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path",
            project_relative_path,
            "",
            "# Set Python output encoding to UTF-8",
            '$env:PYTHONIOENCODING = "utf-8"',
            "",
            "# Execute registered command with uv run --project",
            f'$Arguments = @("run", "--project", $ProjectRoot, "{command_name}")',
            argument_conversion,
            f'& "{runner_literal}" @Arguments',
            "exit $LASTEXITCODE",
            "",
        ]
    else:
        # Direct script mode: run Python file directly
        unknown_args_check = _render_unknown_args_check(
            runner=runner_literal, use_project_mode=False, script_path=script_path
        )
        # Calculate relative path from output directory to script
        script_relative_path = _calculate_script_relative_path(script_path, output_path)

        lines = [
            "#!/usr/bin/env pwsh",
            "",
            "# Direct script mode: Execute Python file directly",
            "",
            param_block,
            "",
            "# Set script path",
            "$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path",
            script_relative_path,
            "",
            unknown_args_check,
            "# Set PowerShell output encoding to UTF-8",
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8",
            "$OutputEncoding = [System.Text.Encoding]::UTF8",
            "",
            "# Set Python output encoding to UTF-8",
            '$env:PYTHONIOENCODING = "utf-8"',
            "",
            (
                '$Arguments = @("run", $ScriptPath)'
                if runner_literal == "uv"
                else "$Arguments = @($ScriptPath)"
            ),
            argument_conversion,
            f'& "{runner_literal}" @Arguments',
            "exit $LASTEXITCODE",
            "",
        ]

    content = "\n".join(lines)
    output_path.write_text(content, encoding="utf-8-sig")
    return output_path


def _render_param_block(actions: Sequence[argparse.Action]) -> str:
    lines: list[str] = ["param("]

    # Add -Help parameter first
    lines.append("    [switch]$Help,")

    for index, action in enumerate(actions):
        rendered = _render_param_line(action)

        if index < len(actions) - 1:
            rendered += ","
        lines.append(f"    {rendered}")

    lines.append(")\n")
    return "\n".join(lines)


def _render_unknown_args_check(
    runner: str,
    use_project_mode: bool,
    command_name: str | None = None,
    script_path: Path | None = None,
) -> str:
    """Render unknown arguments check and help handling."""
    if use_project_mode:
        if command_name is None:
            raise RuntimeError("Internal error: command_name is None in project mode")
        help_command = f'$HelpArgs = @("run", "--project", $ProjectRoot, "{command_name}", "--help")'
    else:
        if script_path is None:
            raise RuntimeError("Internal error: script_path is None in direct mode")
        if runner == "uv":
            help_command = '$HelpArgs = @("run", $ScriptPath, "--help")'
        else:
            help_command = '$HelpArgs = @($ScriptPath, "--help")'

    return f"""
# Check for unknown parameters
if ($args.Count -gt 0) {{
    Write-Error "Unknown parameter(s): $($args -join ', ')"
    $Help = $true
}}

# Display help
if ($Help) {{
    {help_command}
    & "{runner}" @HelpArgs
    exit 0
}}
"""


def _render_param_line(action: argparse.Action) -> str:
    name = _to_pascal_case(action.dest)
    type_hint, default_literal = _determine_param_type_and_default(action)

    parts: list[str] = []

    validate_set = _render_validate_set(action)
    if validate_set:
        parts.append(validate_set)

    parts.append(f"[{type_hint}]${name}")

    if default_literal is not None:
        parts[-1] += f" = {default_literal}"

    return "\n    ".join(parts)


def _determine_param_type_and_default(
    action: argparse.Action,
) -> tuple[str, str | None]:
    # Check if action is a boolean flag by examining the action attribute
    # Note: action.action is not a string, it's the action class itself
    action_class = action.__class__.__name__
    if action_class in ("_StoreTrueAction", "_StoreFalseAction"):
        return "switch", None

    python_type = action.type

    if python_type is int:
        ps_type = "int"
    elif python_type is float:
        ps_type = "double"
    elif python_type is Path:
        ps_type = "string"
    else:
        ps_type = "string"

    if action.default in (None, argparse.SUPPRESS):
        return ps_type, None

    if isinstance(action.default, bool):
        default_literal = "$true" if action.default else "$false"
    elif isinstance(action.default, str):
        default_literal = f'"{action.default}"'
    else:
        default_literal = str(action.default)

    return ps_type, default_literal


def _render_validate_set(action: argparse.Action) -> str | None:
    choices = getattr(action, "choices", None)
    if not choices:
        return None
    joined = '", "'.join(str(choice) for choice in choices)
    return f'[ValidateSet("{joined}")]'


def _render_argument_conversion(actions: Sequence[argparse.Action]) -> str:
    lines: list[str] = []

    for action in actions:
        name = _to_pascal_case(action.dest)
        variable = f"${name}"

        if not action.option_strings:
            # Positional arguments: Add as-is (no absolute path conversion)
            lines.append(f"$Arguments += {variable}")
            continue

        option = _select_option_string(action.option_strings)

        # Check if action is a boolean flag by examining the action class
        action_class = action.__class__.__name__
        if action_class in ("_StoreTrueAction", "_StoreFalseAction"):
            lines.append(f'if ({variable}) {{ $Arguments += "{option}" }}')
            continue

        condition = _build_assignment_condition(action, name)
        # Optional arguments: Convert Path type to absolute path
        if action.type is Path:
            assignment = f'$Arguments += "{option}", (Resolve-Path {variable}).Path'
        else:
            assignment = f'$Arguments += "{option}", {variable}'
        lines.append(f"if ({condition}) {{ {assignment} }}")

    return "\n".join(lines)


def _select_option_string(option_strings: Sequence[str]) -> str:
    for option in option_strings:
        if option.startswith("--"):
            return option
    return option_strings[0]


def _build_assignment_condition(action: argparse.Action, name: str) -> str:
    variable = f"${name}"
    python_type = action.type

    if action.default in (None, argparse.SUPPRESS):
        # When default is None
        if python_type is int or python_type is float:
            # Numeric type: $null check
            return f"$null -ne {variable}"
        else:
            # String type: also check for empty string
            return f"-not [string]::IsNullOrEmpty({variable})"

    if isinstance(action.default, bool):
        default_literal = "$true" if action.default else "$false"
    elif isinstance(action.default, str):
        default_literal = f'"{action.default}"'
    else:
        default_literal = str(action.default)

    return f"{variable} -ne {default_literal}"


def _to_pascal_case(source: str) -> str:
    return "".join(part.capitalize() for part in source.split("_"))


def _to_powershell_filename(source: str) -> str:
    """Convert Python script name to PowerShell naming convention.

    Examples:
        folders_zip_convert -> Folders-Zip-Convert
        my_script -> My-Script
        test_file_utils -> Test-File-Utils

    Args:
        source: Python script name (e.g., 'folders_zip_convert')

    Returns:
        PowerShell-style filename (e.g., 'Folders-Zip-Convert')
    """
    # Split by underscore and capitalize each part
    parts = source.split("_")
    capitalized_parts = [part.capitalize() for part in parts]
    # Join with hyphen
    return "-".join(capitalized_parts)


def _calculate_script_relative_path(script_path: Path, output_path: Path) -> str:
    """Calculate PowerShell Join-Path command for relative script location.

    Args:
        script_path: Absolute path to Python script
        output_path: Absolute path to output .ps1 file

    Returns:
        PowerShell code line to set $ScriptPath variable

    Examples:
        script: /scripts/basic_example.py, output: /scripts/Basic-Example.ps1
        -> $ScriptPath = (Join-Path $ScriptDir "basic_example.py")

        script: /scripts/subdir/script.py, output: /scripts/wrapper.ps1
        -> $ScriptPath = (Join-Path $ScriptDir "subdir" | Join-Path -ChildPath "script.py")
    """

    script_abs = script_path.resolve()
    output_abs = output_path.resolve()
    output_dir = output_abs.parent

    # Check if both paths are on the same drive (Windows specific)
    try:
        # Try to calculate relative path
        rel_path = os.path.relpath(script_abs, output_dir)

        # Convert to Path and get parts
        parts = Path(rel_path).parts

        # Build nested Join-Path for script
        if len(parts) == 1:
            # Same directory
            return f'$ScriptPath = (Join-Path $ScriptDir "{parts[0]}")'

        # Multiple parts - build nested Join-Path
        result = "$ScriptDir"
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                # Last part (filename)
                result = f'(Join-Path {result} "{part}")'
            else:
                # Directory part
                result = f'(Join-Path {result} "{part}")'

        return f"$ScriptPath = {result}"

    except ValueError:
        # Different drives on Windows, use absolute path
        return f'$ScriptPath = "{script_abs}"'


def _calculate_project_relative_path(project_root: Path, output_path: Path) -> str:
    """Calculate PowerShell Join-Path command for relative project root location.

    Args:
        project_root: Absolute path to project root (pyproject.toml location)
        output_path: Absolute path to output .ps1 file

    Returns:
        PowerShell code line to set $ProjectRoot variable

    Examples:
        project: /scripts, output: /scripts/wrapper.ps1
        -> $ProjectRoot = $ScriptDir

        project: /scripts, output: /scripts/subdir/wrapper.ps1
        -> $ProjectRoot = (Join-Path $ScriptDir "..")
    """

    project_abs = project_root.resolve()
    output_abs = output_path.resolve()
    output_dir = output_abs.parent

    # Check if both paths are on the same drive (Windows specific)
    try:
        # Try to calculate relative path
        rel_path = os.path.relpath(project_abs, output_dir)

        # Convert to Path and get parts
        parts = Path(rel_path).parts

        # Build nested Join-Path
        if not parts or parts == (".",):
            # Same directory
            return "$ProjectRoot = $ScriptDir"

        result = "$ScriptDir"
        for part in parts:
            result = f'(Join-Path {result} "{part}")'

        return f"$ProjectRoot = {result}"

    except ValueError:
        # Different drives on Windows, use absolute path
        return f'$ProjectRoot = "{project_abs}"'
