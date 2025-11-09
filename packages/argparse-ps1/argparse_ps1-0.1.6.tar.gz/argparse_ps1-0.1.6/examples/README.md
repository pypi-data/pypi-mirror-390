# Examples

This directory contains working examples of argparse-ps1 usage.

## Available Examples

### basic_example.py

Simple example with boolean flags:

```bash
python basic_example.py --make-ps1
.\Basic-Example.ps1 -Hello
.\Basic-Example.ps1 -Bye
```

### example.py

Example with string options using `uv run` (default):

```bash
python example.py --make-ps1
.\Example.ps1 -Option "test value"
```

### example_uv_project.py

Example using `uv run --project` mode:

```bash
python example_uv_project.py --make-ps1
.\Example-Uv-Project.ps1 -Option "project mode"
```

### example_python.py

Example using `python` runner instead of `uv`:

```bash
python example_python.py --make-ps1
.\Example-Python.ps1 -Option "python runner"
```

## Running Examples

1. Navigate to the examples directory:

   ```bash
   cd examples
   ```

2. Generate PowerShell wrappers:

   ```bash
   python basic_example.py --make-ps1
   python example.py --make-ps1
   # etc.
   ```

3. Use the generated PowerShell scripts:
   ```powershell
   .\Basic-Example.ps1 -Help
   .\Example.ps1 -Option "test"
   ```

All examples include proper tab completion and help documentation in PowerShell.
