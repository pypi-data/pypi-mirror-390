"""ProteoWizard Docker converter implementation."""

from __future__ import annotations

import logging
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


class SimplePWizConverter:
    """Simple wrapper for ProteoWizard Docker container."""

    SUPPORTED_FORMATS = frozenset({
        ".raw",
        ".wiff",
        ".wiff2",
        ".d",
        ".baf",
        ".fid",
        ".yep",
        ".tsf",
        ".tdf",
        ".mbi",
        ".lcd",
        ".ms",
        ".cms1",
        ".ms1",
        ".cms2",
        ".ms2",
        ".t2d",
    })

    DEFAULT_DOCKER_IMAGE = "proteowizard/pwiz-skyline-i-agree-to-the-vendor-licenses:latest"

    def __init__(
        self,
        logger: logging.Logger | None = None,
        docker_image: str | None = None,
        worker_cores: float | None = None,
        worker_memory: str | None = None,
        worker_swap: str | None = None,
        worker_shm_size: str | None = None,
    ):
        """Initialize converter with optional logger and Docker settings."""
        self.logger = logger or logging.getLogger(__name__)
        self.docker_image = docker_image or self.DEFAULT_DOCKER_IMAGE
        self.worker_cores = worker_cores
        self.worker_memory = worker_memory
        self.worker_swap = worker_swap
        self.worker_shm_size = worker_shm_size

    def find_files(self, paths: list[Path]) -> list[Path]:
        """Find all supported mass spec files from input paths."""
        files: list[Path] = []

        for path in paths:
            if path.is_file():
                if path.suffix.lower() in self.SUPPORTED_FORMATS:
                    files.append(path.resolve())
                    self.logger.debug(f"Found supported file: {path}")
                else:
                    msg = f"Warning: {path} has unsupported format"
                    print(msg, file=sys.stderr)
                    self.logger.warning(msg)
            elif path.is_dir():
                found_files = [
                    file_path.resolve()
                    for file_path in path.rglob("*")
                    if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_FORMATS
                ]
                files.extend(found_files)
                self.logger.info(f"Found {len(found_files)} files in directory: {path}")
            else:
                msg = f"Error: {path} does not exist"
                print(msg, file=sys.stderr)
                self.logger.error(msg)

        return sorted(files)

    @staticmethod
    def get_unique_directories(files: list[Path]) -> set[Path]:
        """Get unique parent directories from file list."""
        return {f.parent for f in files}

    def _build_docker_command(
        self, files: list[Path], output_dir: Path, msconvert_args: list[str], config_path: Path | None = None
    ) -> list[str]:
        """Build complete Docker command with volume mounts."""
        cmd = ["docker", "run", "--rm"]

        # Add resource limits
        if self.worker_cores:
            cmd.extend(["--cpus", str(self.worker_cores)])

        if self.worker_memory:
            cmd.extend(["--memory", self.worker_memory])

        if self.worker_swap:
            # Docker expects memory-swap to be total (memory + swap)
            # If user wants to disable swap, they should set it equal to memory
            cmd.extend(["--memory-swap", self.worker_swap])

        if self.worker_shm_size:
            cmd.extend(["--shm-size", self.worker_shm_size])

        # Mount input directories
        input_dirs = self.get_unique_directories(files)
        dir_mappings = {
            input_dir: f"/input{i}" if i > 0 else "/input" for i, input_dir in enumerate(sorted(input_dirs))
        }

        for input_dir, mount_point in dir_mappings.items():
            cmd.extend(["-v", f"{input_dir}:{mount_point}"])

        # Mount config directory if provided
        if config_path:
            config_path = config_path.resolve()
            cmd.extend(["-v", f"{config_path.parent}:/config"])

        # Mount output directory
        cmd.extend(["-v", f"{output_dir}:/output"])

        # Add image and command
        cmd.extend([self.docker_image, "wine", "msconvert"])

        # Add input files with Docker paths
        for file_path in files:
            docker_dir = dir_mappings[file_path.parent]
            cmd.append(f"{docker_dir}/{file_path.name}")

        # Add output and config
        cmd.extend(["-o", "/output"])

        if config_path:
            cmd.extend(["-c", f"/config/{config_path.name}"])

        cmd.extend(msconvert_args)

        return cmd

    def _run_single_batch(
        self,
        files: list[Path],
        output_dir: Path,
        msconvert_args: list[str],
        config_path: Path | None = None,
        batch_num: int | None = None,
    ) -> tuple[bool, list[Path]]:
        """Run msconvert for a single batch of files."""
        if not files:
            return True, []

        cmd = self._build_docker_command(files, output_dir, msconvert_args, config_path)

        batch_label = f" (batch {batch_num})" if batch_num is not None else ""
        file_name = files[0].name if len(files) == 1 else f"{len(files)} files"

        self.logger.info(f"{'=' * 60}")
        self.logger.info(f"Starting conversion{batch_label}: {file_name}")
        self.logger.info(f"{'=' * 60}")
        self.logger.debug(f"Command: {' '.join(cmd)}")
        self.logger.debug(f"Files in batch: {[f.name for f in files]}")

        print(f"Running{batch_label}: {len(files)} file(s)")

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            msg = f"Error{batch_label}: msconvert failed with return code {e.returncode}"
            print(msg, file=sys.stderr)
            self.logger.error(msg)

            if e.stdout:
                self.logger.error("msconvert stdout before failure:")
                for line in e.stdout.strip().split("\n"):
                    self.logger.error(f"  {line}")

            if e.stderr:
                self.logger.error("msconvert stderr:")
                for line in e.stderr.strip().split("\n"):
                    self.logger.error(f"  {line}")
                print(f"stderr: {e.stderr}", file=sys.stderr)
            else:
                self.logger.error("No stderr output available")

            self.logger.error(f"✗ Batch {batch_num} failed")
            self.logger.error(f"{'=' * 60}")
            return False, files
        except KeyboardInterrupt:
            msg = f"\nInterrupted by user{batch_label}"
            print(msg, file=sys.stderr)
            self.logger.warning(msg)
            self.logger.warning(f"{'=' * 60}")
            return False, files
        else:
            if result.stdout:
                self.logger.info("msconvert output:")
                for line in result.stdout.strip().split("\n"):
                    self.logger.info(f"  {line}")

            self.logger.info(f"✓ Batch {batch_num} completed successfully")
            self.logger.info(f"{'=' * 60}")
            return result.returncode == 0, files

    def run_msconvert(
        self,
        files: list[Path],
        output_dir: Path,
        msconvert_args: list[str],
        config_path: Path | None = None,
        workers: int = 1,
    ) -> bool:
        """Run msconvert in Docker with proper volume mounting."""
        if not files:
            msg = "No supported files found"
            print(msg, file=sys.stderr)
            self.logger.error(msg)
            return False

        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Output directory: {output_dir}")

        # Single worker mode
        if workers == 1:
            cmd = self._build_docker_command(files, output_dir, msconvert_args, config_path)
            print(f"Running: {' '.join(cmd)}")
            self.logger.info(f"Running single worker mode with {len(files)} files")
            self.logger.debug(f"Command: {' '.join(cmd)}")

            try:
                result = subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                msg = f"Error: msconvert failed with return code {e.returncode}"
                print(msg, file=sys.stderr)
                self.logger.error(msg)
                return False
            except KeyboardInterrupt:
                msg = "\nInterrupted by user"
                print(msg, file=sys.stderr)
                self.logger.warning(msg)
                return False
            else:
                self.logger.info("Conversion completed successfully")
                return result.returncode == 0

        # Multiple workers mode
        print(f"Using {workers} parallel workers (1 file per worker)")
        self.logger.info(f"Using {workers} parallel workers (1 file per worker)")
        self.logger.info("Note: Wine-based msconvert processes one file at a time for stability")

        file_batches = [[f] for f in files]
        self.logger.info(f"Processing {len(files)} files with up to {workers} concurrent workers")

        all_success = True
        total = len(file_batches)

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_batch = {
                executor.submit(self._run_single_batch, batch, output_dir, msconvert_args, config_path, i + 1): i
                for i, batch in enumerate(file_batches)
            }

            try:
                for future in as_completed(future_to_batch):
                    success, batch_files = future.result()

                    if success:
                        msg = f"✓ File {future_to_batch[future] + 1}/{total} completed: {batch_files[0].name}"
                        print(msg)
                        self.logger.info(msg)
                    else:
                        msg = f"✗ File {future_to_batch[future] + 1}/{total} failed: {batch_files[0].name}"
                        print(msg, file=sys.stderr)
                        self.logger.error(msg)
                        all_success = False

            except KeyboardInterrupt:
                msg = "\nInterrupted by user - cancelling remaining tasks"
                print(msg, file=sys.stderr)
                self.logger.warning(msg)
                executor.shutdown(wait=False, cancel_futures=True)
                return False

        if all_success:
            self.logger.info("All files completed successfully")
        else:
            self.logger.error("Some files failed")

        return all_success
