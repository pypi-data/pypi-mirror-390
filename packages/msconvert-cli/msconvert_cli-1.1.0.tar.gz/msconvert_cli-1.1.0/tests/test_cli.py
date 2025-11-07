"""Tests for CLI functionality."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

# Test data
TEST_RAW_FILE = Path(__file__).parent / "data" / "A_1_neg_2100u15c_BEH130_18Jul2025.raw"

# Check if running in CI or inside Docker (where nested Docker won't work)
IN_CI = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"
IN_DOCKER = os.path.exists("/.dockerenv")
SKIP_DOCKER_TESTS = IN_CI or IN_DOCKER


@pytest.fixture
def temp_output(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(
            ["docker", "ps"],  # noqa: S607
            capture_output=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    else:
        return result.returncode == 0


# Basic CLI Tests


def test_help_command():
    """Test that --help command works without errors."""
    result = subprocess.run(
        [sys.executable, "-m", "msconvert_cli.cli", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "ProteoWizard Docker wrapper" in result.stdout
    assert "--output-dir" in result.stdout
    assert "--workers" in result.stdout
    assert "--sage" in result.stdout
    assert "--casanovo" in result.stdout


def test_help_short_flag():
    """Test that -h works the same as --help."""
    result = subprocess.run(
        [sys.executable, "-m", "msconvert_cli.cli", "-h"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "ProteoWizard Docker wrapper" in result.stdout


def test_version_flag() -> None:
    """Test that --version displays version information."""
    result = subprocess.run(
        [sys.executable, "-m", "msconvert_cli.cli", "--version"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0


def test_version_in_help():
    """Test that help shows all preset options."""
    result = subprocess.run(
        [sys.executable, "-m", "msconvert_cli.cli", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    # Check all presets are listed
    assert "--blitzff" in result.stdout
    assert "--biosaur" in result.stdout
    assert "--casanovo_mgf" in result.stdout


def test_missing_required_args():
    """Test that missing required arguments shows proper error."""
    result = subprocess.run(
        [sys.executable, "-m", "msconvert_cli.cli"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "required" in result.stderr.lower() or "error" in result.stderr.lower()


def test_missing_output_dir():
    """Test that missing output directory shows error."""
    result = subprocess.run(
        [sys.executable, "-m", "msconvert_cli.cli", str(TEST_RAW_FILE)],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "required" in result.stderr.lower()


def test_no_input_files(tmp_path: Path) -> None:
    """Test that no input files shows error."""
    result = subprocess.run(
        [sys.executable, "-m", "msconvert_cli.cli", "-o", str(tmp_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0


def test_nonexistent_input_file(temp_output: Path) -> None:
    """Test that nonexistent input file is handled."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "msconvert_cli.cli",
            "nonexistent.raw",
            "-o",
            str(temp_output),
            "--sage",
        ],
        capture_output=True,
        text=True,
    )

    # Should exit with error code 1 (no supported files found)
    assert result.returncode == 1


def test_conflicting_presets(temp_output: Path) -> None:
    """Test that using multiple presets is not allowed."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "msconvert_cli.cli",
            str(TEST_RAW_FILE),
            "-o",
            str(temp_output),
            "--sage",
            "--casanovo",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "not allowed" in result.stderr.lower()


# Conversion Tests (require Docker)


@pytest.mark.skipif(SKIP_DOCKER_TESTS, reason="Skipping Docker tests in CI/container environment")
@pytest.mark.skipif(not TEST_RAW_FILE.exists(), reason="Test data file not found")
def test_conversion_with_sage_preset(temp_output: Path, docker_available: bool) -> None:
    """Test basic conversion with Sage preset."""
    if not docker_available:
        pytest.skip("Docker not available or not running")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "msconvert_cli.cli",
            str(TEST_RAW_FILE),
            "-o",
            str(temp_output),
            "--sage",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

    # Check output file was created (Sage preset creates .mzML.gz)
    output_files = list(temp_output.glob("*.mzML*"))
    assert len(output_files) == 1
    assert output_files[0].stat().st_size > 0


@pytest.mark.skipif(not TEST_RAW_FILE.exists(), reason="Test data file not found")
def test_conversion_with_verbose_logging(temp_output: Path, docker_available: bool) -> None:
    """Test conversion with verbose logging."""
    if not docker_available:
        pytest.skip("Docker not available or not running")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "msconvert_cli.cli",
            str(TEST_RAW_FILE),
            "-o",
            str(temp_output),
            "--sage",
            "-v",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0

    # Check log file was created
    log_files = list(temp_output.glob("msconvert_*.log"))
    assert len(log_files) == 1
    assert log_files[0].stat().st_size > 0

    # Check log contains expected content
    log_content = log_files[0].read_text()
    assert "Input paths:" in log_content
    assert "Output directory:" in log_content
    assert "Preset: SAGE" in log_content


@pytest.mark.skipif(SKIP_DOCKER_TESTS, reason="Skipping Docker tests in CI/container environment")
@pytest.mark.skipif(not TEST_RAW_FILE.exists(), reason="Test data file not found")
def test_conversion_with_custom_log_file(temp_output: Path, docker_available: bool) -> None:
    """Test conversion with custom log file path."""
    if not docker_available:
        pytest.skip("Docker not available or not running")

    log_file = temp_output / "custom.log"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "msconvert_cli.cli",
            str(TEST_RAW_FILE),
            "-o",
            str(temp_output),
            "--sage",
            "-v",
            "--log",
            str(log_file),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0
    assert log_file.exists()
    assert log_file.stat().st_size > 0


@pytest.mark.skipif(SKIP_DOCKER_TESTS, reason="Skipping Docker tests in CI/container environment")
@pytest.mark.skipif(not TEST_RAW_FILE.exists(), reason="Test data file not found")
def test_conversion_with_biosaur_preset(temp_output: Path, docker_available: bool) -> None:
    """Test conversion with Biosaur preset."""
    if not docker_available:
        pytest.skip("Docker not available or not running")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "msconvert_cli.cli",
            str(TEST_RAW_FILE),
            "-o",
            str(temp_output),
            "--biosaur",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0

    # Check output file was created (Biosaur preset)
    output_files = list(temp_output.glob("*.mzML*"))
    assert len(output_files) == 1


@pytest.mark.skipif(SKIP_DOCKER_TESTS, reason="Skipping Docker tests in CI/container environment")
@pytest.mark.skipif(not TEST_RAW_FILE.exists(), reason="Test data file not found")
def test_conversion_with_casanovo_mgf_preset(temp_output: Path, docker_available: bool) -> None:
    """Test conversion with Casanovo MGF preset."""
    if not docker_available:
        pytest.skip("Docker not available or not running")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "msconvert_cli.cli",
            str(TEST_RAW_FILE),
            "-o",
            str(temp_output),
            "--casanovo_mgf",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0

    # Check MGF output file was created
    output_files = list(temp_output.glob("*.mgf"))
    assert len(output_files) == 1


@pytest.mark.skipif(SKIP_DOCKER_TESTS, reason="Skipping Docker tests in CI/container environment")
@pytest.mark.skipif(not TEST_RAW_FILE.exists(), reason="Test data file not found")
def test_conversion_with_resource_limits(temp_output: Path, docker_available: bool) -> None:
    """Test conversion with Docker resource limits."""
    if not docker_available:
        pytest.skip("Docker not available or not running")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "msconvert_cli.cli",
            str(TEST_RAW_FILE),
            "-o",
            str(temp_output),
            "--sage",
            "--worker-cores",
            "1.0",
            "--worker-memory",
            "2g",
            "--worker-shm-size",
            "1g",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0

    # Check output file was created (resource limits)
    output_files = list(temp_output.glob("*.mzML*"))
    assert len(output_files) == 1


@pytest.mark.skipif(SKIP_DOCKER_TESTS, reason="Skipping Docker tests in CI/container environment")
@pytest.mark.skipif(not TEST_RAW_FILE.exists(), reason="Test data file not found")
def test_conversion_with_multiple_workers(temp_output: Path, docker_available: bool) -> None:
    """Test conversion with multiple workers (single file still uses 1 worker effectively)."""
    if not docker_available:
        pytest.skip("Docker not available or not running")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "msconvert_cli.cli",
            str(TEST_RAW_FILE),
            "-o",
            str(temp_output),
            "--sage",
            "--workers",
            "2",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0

    # Check output file was created (multiple workers)
    output_files = list(temp_output.glob("*.mzML*"))
    assert len(output_files) == 1
