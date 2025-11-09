"""Tests for argparse_ps1 package."""

import argparse
import tempfile
from pathlib import Path

from argparse_ps1 import generate_ps1_wrapper


def test_import():
    """Test that the package can be imported."""
    assert callable(generate_ps1_wrapper)


def test_generate_basic_wrapper():
    """Test generating a basic PowerShell wrapper."""
    parser = argparse.ArgumentParser(description="Test script")
    parser.add_argument("input_file", type=Path, help="Input file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_script.ps1"
        script_path = Path(__file__).parent / "test_script.py"

        result = generate_ps1_wrapper(
            parser, script_path=script_path, output_path=output_path
        )

        assert result == output_path
        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")
        assert "param(" in content
        # InputFile is positional argument, mapped as string
        assert "[string]$InputFile" in content
        assert "[switch]$Verbose" in content


def test_generate_wrapper_with_skip_dests():
    """Test generating wrapper with skip_dests parameter."""
    parser = argparse.ArgumentParser(description="Test script")
    parser.add_argument("input_file", type=Path, help="Input file")
    parser.add_argument("--make-ps1", action="store_true", help="Generate PS1 wrapper")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_script.ps1"
        script_path = Path(__file__).parent / "test_script.py"

        result = generate_ps1_wrapper(
            parser,
            script_path=script_path,
            output_path=output_path,
            skip_dests={"make_ps1"},
        )

        assert result == output_path
        content = output_path.read_text(encoding="utf-8")
        assert "make-ps1" not in content.lower()
        assert "makeps1" not in content.lower()


def test_generate_wrapper_with_output_path():
    """Test generating wrapper with custom output_path."""
    parser = argparse.ArgumentParser(description="Test script")
    parser.add_argument("input_file", type=Path)

    with tempfile.TemporaryDirectory() as tmpdir:
        custom_output = Path(tmpdir) / "custom_wrapper.ps1"
        script_path = Path(__file__).parent / "test_script.py"

        result = generate_ps1_wrapper(
            parser, script_path=script_path, output_path=custom_output
        )

        assert result == custom_output
        assert custom_output.exists()


def test_type_mapping():
    """Test Python to PowerShell type mapping."""
    parser = argparse.ArgumentParser(description="Test types")
    parser.add_argument("--count", type=int, help="Count")
    parser.add_argument("--rate", type=float, help="Rate")
    parser.add_argument("--path", type=Path, help="Path")
    parser.add_argument("--flag", action="store_true", help="Flag")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_types.ps1"
        script_path = Path(__file__).parent / "test_script.py"

        generate_ps1_wrapper(parser, script_path=script_path, output_path=output_path)

        content = output_path.read_text(encoding="utf-8")
        assert "[int]$Count" in content
        assert "[double]$Rate" in content
        # Path is mapped as string, not System.IO.FileInfo
        assert "[string]$Path" in content
        assert "[switch]$Flag" in content


def test_runner_parameter():
    """Test runner parameter (default is 'uv')."""
    parser = argparse.ArgumentParser(description="Test script")
    parser.add_argument("input_file", type=Path)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_runner.ps1"
        script_path = Path(__file__).parent / "test_script.py"

        # Default runner should be 'uv'
        generate_ps1_wrapper(parser, script_path=script_path, output_path=output_path)

        content = output_path.read_text(encoding="utf-8")
        # Should contain direct script execution (not uv run --project)
        assert "uv" in content.lower()
        assert "Direct script mode" in content


def test_project_mode():
    """Test project mode with project_root and command_name."""
    parser = argparse.ArgumentParser(description="Test script")
    parser.add_argument("input_file", type=Path)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_project.ps1"
        project_root = Path(tmpdir)
        script_path = project_root / "test_script.py"

        # Create a mock Python script
        script_path.write_text('print("test")', encoding="utf-8")

        # Create a mock pyproject.toml with [project.scripts] section
        pyproject_content = """
[project]
name = "test-project"
version = "0.1.2"

[project.scripts]
test-command = "test_module:main"
"""
        (project_root / "pyproject.toml").write_text(
            pyproject_content, encoding="utf-8"
        )

        generate_ps1_wrapper(
            parser,
            script_path=script_path,
            output_path=output_path,
            command_name="test-command",
        )

        content = output_path.read_text(encoding="utf-8")
        # Should use 'uv run --project' for project mode
        assert "uv run" in content
        assert "--project" in content
        assert "test-command" in content
        assert "test-command" in content
        assert "--project" in content


def test_cross_drive_paths():
    """Test handling of paths on different drives (Windows specific)."""
    parser = argparse.ArgumentParser(description="Test script")
    parser.add_argument("input_file", type=Path, help="Input file")
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_cross_drive.ps1"
        script_path = Path(__file__).resolve()

        # Test direct script mode (no command_name) to avoid pyproject.toml validation
        # This tests the cross-drive path calculation in _calculate_script_relative_path
        generate_ps1_wrapper(
            parser,
            script_path=script_path,
            output_path=output_path,
            # No project_root or command_name - uses direct script mode
        )

        content = output_path.read_text(encoding="utf-8")
        # Should contain the script execution command
        assert '"run"' in content  # Check for "run" argument
        assert '& "uv"' in content  # Check for uv execution
        # Should handle path calculation gracefully
        assert "$ScriptPath" in content


def test_custom_runner_parameter():
    """Test custom runner parameter functionality (from example_python.py)."""
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

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_custom_runner.ps1"
        script_path = Path(__file__).parent / "test_script.py"

        # Test with different runner configurations
        test_cases = [
            (".venv/Scripts/python.exe", "venv runner"),  # Relative path
            ("python", "system runner"),  # System command
            ("C:/Python312/python.exe", "custom runner"),  # Absolute path
        ]

        for runner, _ in test_cases:
            result = generate_ps1_wrapper(
                parser,
                script_path=script_path,
                output_path=output_path,
                skip_dests={"make_ps1"},
                runner=runner,
            )

            assert result == output_path
            assert output_path.exists()
            content = output_path.read_text(encoding="utf-8")

            # Check that runner is properly quoted in the output
            # Path normalization converts forward slashes to backslashes on Windows
            normalized_runner = str(Path(runner))
            assert f'& "{normalized_runner}"' in content

            # Check parameter mapping
            assert "[string]$Option" in content
            assert "[string]$RunnerType" in content
            # make_ps1 should be skipped
            assert "makeps1" not in content.lower()
            assert "make-ps1" not in content.lower()


def test_runner_path_normalization():
    """Test runner path normalization for Windows paths."""
    parser = argparse.ArgumentParser(description="Test script")
    parser.add_argument("input_file", type=Path)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_runner_path.ps1"
        script_path = Path(__file__).parent / "test_script.py"

        # Test various path formats
        test_runners = [
            "python",  # Simple command
            "C:\\Python312\\python.exe",  # Windows absolute path
            "C:/Python312/python.exe",  # Forward slash path
            ".venv\\Scripts\\python.exe",  # Relative Windows path
            ".venv/Scripts/python.exe",  # Relative forward slash path
        ]

        for runner in test_runners:
            generate_ps1_wrapper(
                parser, script_path=script_path, output_path=output_path, runner=runner
            )

            content = output_path.read_text(encoding="utf-8")

            # Check that the runner is properly quoted
            assert '& "' in content
            # The runner should appear in the content
            assert runner.replace("/", "\\") in content or runner in content


def test_example_python_integration():
    """Test integration with example_python.py functionality."""
    # This mimics the behavior of example_python.py
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

    # Simulate the runner configuration logic from example_python.py
    runner_configs = {
        "venv": ".venv/Scripts/python.exe",
        "system": "python",
        "custom": "C:/Python312/python.exe",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(__file__).parent / "test_script.py"

        for runner_type, runner in runner_configs.items():
            output_path = Path(tmpdir) / f"test_{runner_type}.ps1"

            result = generate_ps1_wrapper(
                parser,
                script_path=script_path,
                output_path=output_path,
                runner=runner,
            )

            assert result == output_path
            assert output_path.exists()
            content = output_path.read_text(encoding="utf-8")

            # Verify the runner is correctly embedded
            # Path normalization converts forward slashes to backslashes on Windows
            normalized_runner = str(Path(runner))
            assert f'& "{normalized_runner}"' in content

            # Verify parameter structure
            assert "param(" in content
            assert "[string]$Option" in content
            assert "[string]$RunnerType" in content

            # Verify argument handling
            assert "$Arguments" in content
            assert "exit $LASTEXITCODE" in content
