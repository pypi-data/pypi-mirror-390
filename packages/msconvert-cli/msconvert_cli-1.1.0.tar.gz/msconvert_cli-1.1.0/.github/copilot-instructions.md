---
applyTo: "**"
---

# msconvert-cli Copilot Instructions

## Project Overview
Python CLI wrapper for ProteoWizard's msconvert that runs in Docker containers. Converts mass spectrometry files (`.raw`, `.wiff`, `.d`, etc.) to mzML/MGF formats with parallel processing support.

**Key Architecture:**
- `cli.py`: Argument parsing, preset selection, logging setup
- `converter.py`: Docker orchestration, file discovery, parallel execution (ThreadPoolExecutor)
- `presets.py`: Enum-based preset configs with importlib.resources for bundled files
- `configs/*.txt`: msconvert config files (key=value format, filter= lines)

## Critical Workflows

### Development Setup
```bash
uv sync                    # Install deps + editable install
uv run pre-commit install  # Setup hooks
make check                 # Run all linters (ruff, mypy, pre-commit)
make test                  # Run pytest
```

### Running Locally
```bash
uv run mscli --help                           # Test CLI
uv run mscli /path/to/data -o ./output --sage # Convert with preset
```

### Testing
- Tests live in `tests/` - primarily subprocess tests of CLI interface
- `make test` runs pytest with doctests
- `tox` for multi-Python version testing (3.9-3.13)

## Project-Specific Conventions

### Docker Resource Management
- Wine-based msconvert processes **1 file per container** for stability
- Multi-worker mode uses ThreadPoolExecutor with 1 file batches
- Resource limits: `--cpus`, `--memory`, `--memory-swap`, `--shm-size`
- Volume mounting: unique input dirs get `/input`, `/input0`, `/input1`, etc.

### Preset Config Pattern
- Presets defined in `PresetConfig` enum with config_file + description
- Config files loaded via `importlib.resources.files()` for package data
- CLI flags auto-generated from enum: `--sage`, `--casanovo`, etc.
- Mutually exclusive group ensures only one preset OR custom config

### Logging Design
- Console: WARNING+ only (minimal noise during conversions)
- File: DEBUG/INFO based on `-v` flag (detailed process tracking)
- Auto-generated log names: `msconvert_YYYYMMDD_HHMMSS.log`
- Structured batch logging with `===` separators for clarity

### Error Handling
- Docker command failures captured with stdout/stderr logging
- ThreadPoolExecutor catches KeyboardInterrupt for graceful shutdown
- Individual batch failures don't stop parallel processing
- Return codes: 0 = success, 1 = failure

## Code Quality Standards

### Ruff Configuration
- Line length: 120
- Ignored: E501 (line too long), E731 (lambda assignment), S603 (subprocess), TRY400 (logging.exception)
- Complexity exceptions: `cli.py` and `converter.py` allowed C901 complexity

### Type Hints
- `mypy --strict` equivalent settings in `pyproject.toml`
- Python 3.9+ compatibility (use `typing_extensions.Self` for <3.11)
- Use `Path` not `str` for file paths
- Union types: `Type | None` (not Optional)

### Testing Patterns
```python
# Tests use subprocess to invoke CLI
result = subprocess.run([sys.executable, "-m", "msconvert_cli.cli", "--help"], ...)
assert result.returncode == 0
```

## Common Tasks

### Adding New Preset
1. Create config file in `src/msconvert_cli/configs/<name>.txt`
2. Add enum entry to `PresetConfig` in `presets.py`
3. Update README.md with preset description
4. Test: `uv run mscli dummy.raw -o /tmp --<name>`

### Modifying Docker Command
- Edit `_build_docker_command()` in `converter.py`
- Volume mounts must be absolute paths
- Wine requires specific resource settings (shm-size important)
- Test both single-worker and parallel modes

### Debugging Conversions
- Use `-v` flag for detailed logging
- Check `msconvert_*.log` for stdout/stderr from msconvert
- Verify Docker volume mounts with `docker inspect`
- Test with single file first before parallel processing

## External Dependencies
- **Docker**: Required runtime, uses `proteowizard/pwiz-skyline-i-agree-to-the-vendor-licenses`
- **uv**: Package manager (not pip)
- **ProteoWizard**: Binary runs in container via Wine (Windows compatibility layer)

## File Naming Notes
- Package: `msconvert_cli` (underscore)
- CLI command: `mscli` (short, no underscores)
- Entry point: `msconvert_cli.cli:cli` in pyproject.toml

## Project Files
- `py.typed`: Marks package as type-hint compatible for downstream users
- `CHANGELOG.md`: Track version history following Keep a Changelog format
- `MANIFEST.in`: Ensures config files and py.typed are included in distributions
