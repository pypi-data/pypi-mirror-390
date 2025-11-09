# argparse-ps1

**Generate PowerShell wrapper scripts from Python argparse parsers**

[![PyPI version](https://badge.fury.io/py/argparse-ps1.svg)](https://badge.fury.io/py/argparse-ps1)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/shimarch/argparse-ps1/workflows/CI/badge.svg)](https://github.com/shimarch/argparse-ps1/actions)

`argparse-ps1` automatically generates PowerShell (.ps1) wrapper scripts for Python scripts that use `argparse`. This provides native PowerShell tab completion and parameter binding for your Python scripts.

## Features

- 🚀 **Automatic Generation**: Creates PowerShell wrappers from `ArgumentParser` objects
- 🎯 **Type Mapping**: Maps Python types to PowerShell parameter types
- 📝 **Native Interface**: Provides PowerShell-style parameter names and help
- ⚙️ **Multiple Runners**: Supports `uv`, `python`, or custom runners
- 🔧 **Zero Dependencies**: Uses only Python standard library

## Installation

```bash
pip install argparse-ps1
```

## Quick Start

Add wrapper generation to your Python script:

```python
from argparse_ps1 import generate_ps1_wrapper

# Your existing argparse code
parser = argparse.ArgumentParser(description="My script")
parser.add_argument("--hello", action="store_true", help="Say hello")
parser.add_argument("--option", type=str, help="String option")

# Generate PowerShell wrapper
if "--make-ps1" in sys.argv:
    output = generate_ps1_wrapper(parser, script_path=Path(__file__))
    print(f"Generated: {output}")
    sys.exit(0)
```

Generate the wrapper:

```bash
python my_script.py --make-ps1
# Creates My-Script.ps1
```

Use the PowerShell wrapper:

```powershell
.\My-Script.ps1 -Hello -Option "test"
```

## Examples

See the [examples/](examples/) directory for complete working examples:

- **[basic_example.py](examples/basic_example.py)**: Simple boolean flags
- **[example.py](examples/example.py)**: String options with `uv run`
- **[example_uv_project.py](examples/example_uv_project.py)**: Using `uv run --project`
- **[example_python.py](examples/example_python.py)**: Using `python` runner instead of `uv`

### Project Mode Requirements

For project mode examples (`example_uv_project.py`), you need:

1. **Proper pyproject.toml structure** with `[project.scripts]` entry
2. **Package structure** with `__init__.py` files
3. **Correct execution method**: Use `uv run python example_uv_project.py` instead of script entries

## Usage Modes

### Default: uv run (Direct Script)

```python
generate_ps1_wrapper(parser, script_path=Path(__file__))
# Creates: & uv run script.py @args
```

### Project Mode: uv run --project

```python
generate_ps1_wrapper(
    parser,
    script_path=Path(__file__),
    project_root=Path(".."),
    command_name="my-command"  # Must exist in [project.scripts]
)
# Creates: & uv run --project .. my-command @args
```

### Custom Runner

Use alternative Python executables instead of `uv`:

```python
# System Python
generate_ps1_wrapper(
    parser,
    script_path=Path(__file__),
    runner="python"
)
# Creates: & python script.py @args

# Virtual environment Python (relative path)
generate_ps1_wrapper(
    parser,
    script_path=Path(__file__),
    runner=".venv/Scripts/python.exe"  # Windows
    # runner=".venv/bin/python"        # Unix/macOS
)
# Creates: & .venv\Scripts\python.exe script.py @args

# Custom Python installation (absolute path)
generate_ps1_wrapper(
    parser,
    script_path=Path(__file__),
    runner="C:/Python312/python.exe"
)
# Creates: & "C:/Python312/python.exe" script.py @args
```

**Note**: See [example_python.py](examples/example_python.py) for a complete working example.

## API Reference

```python
def generate_ps1_wrapper(
    parser: argparse.ArgumentParser,
    *,
    script_path: Path,
    output_path: Path | None = None,
    output_dir: Path | None = None,
    skip_dests: Iterable[str] | None = None,
    runner: str = "uv",
    command_name: str | None = None,
) -> Path
```

**Parameters:**

- `parser`: Your `ArgumentParser` instance
- `script_path`: Path to your Python script (absolute path required)
- `output_path`: Specific output file path (optional, overrides output_dir)
- `output_dir`: Output directory (default: current working directory)
- `skip_dests`: Argument destinations to exclude from wrapper
- `runner`: Command to run Python scripts (default: "uv", can be "python")
- `command_name`: Command name in `[project.scripts]` (enables project mode for uv)

## Type Mapping

| Python Type  | PowerShell Type | Example                |
| ------------ | --------------- | ---------------------- |
| `str`        | `[string]`      | `-Name "value"`        |
| `int`        | `[int]`         | `-Count 42`            |
| `float`      | `[double]`      | `-Rate 3.14`           |
| `Path`       | `[string]`      | `-File "path/to/file"` |
| `store_true` | `[switch]`      | `-Verbose`             |

## Requirements

- Python 3.11+
- Windows PowerShell or PowerShell Core

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please see [DEVELOPMENT.md](DEVELOPMENT.md) for setup instructions.
