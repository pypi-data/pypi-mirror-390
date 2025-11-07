# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Type hint support marker (`py.typed`) for downstream type checking
- `--version` flag to display version information
- Coverage configuration in `pyproject.toml`
- This CHANGELOG file
- Comprehensive CLI test suite with 16 tests covering all major functionality
- Integration tests using real `.raw` file data
- Docker availability detection in tests

### Changed
- Python version requirement changed from `>=3.11` to `>=3.9` for wider compatibility
- Using `typing_extensions` for better Python 3.9+ support
- Added `from __future__ import annotations` for PEP 563 postponed evaluation

## [1.0.0] - 2024

### Added
- Initial release
- Python CLI wrapper for ProteoWizard's msconvert
- Docker-based conversion with Wine support
- Parallel processing with multi-worker support
- Preset configurations: `--sage`, `--biosaur`, `--blitzff`, `--casanovo`, `--casanovo_mgf`
- Docker resource limits: CPU, memory, swap, shared memory
- Structured logging with console and file outputs
- Support for mass spec formats: `.raw`, `.wiff`, `.d`, `.baf`, `.fid`, `.yep`, `.tsf`, `.tdf`, `.mbi`, `.lcd`, `.ms`, `.cms1`, `.ms1`, `.cms2`, `.ms2`, `.t2d`

[Unreleased]: https://github.com/pgarrett-scripps/msconvert-cli/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/pgarrett-scripps/msconvert-cli/releases/tag/v1.0.0
