#!/usr/bin/env python3
"""
Simple ProteoWizard Docker Wrapper
A minimal Python wrapper to run msconvert in Docker with proper volume mounting.

This tool uses msconvert from ProteoWizard, which is licensed under Apache 2.0.
See: http://proteowizard.sourceforge.net/

ProteoWizard:
Chambers MC et al., "A cross-platform toolkit for mass spectrometry
and proteomics." Nat Biotechnol. 2012 Oct;30(10):918-20.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from . import __version__
from .converter import SimplePWizConverter
from .logging_config import setup_logging
from .presets import PresetConfig, get_preset_config_path


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Simple ProteoWizard Docker wrapper - passes arguments directly to msconvert",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True,
    )

    parser.add_argument("inputs", nargs="*", type=Path, help="Input files or directories")
    parser.add_argument("-o", "--output-dir", type=Path, required=True, help="Output directory")
    parser.add_argument(
        "-w", "--workers", type=int, default=1, help="Number of parallel Docker containers to run (default: 1)"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--log", type=Path, help="Path to log file (appends if exists)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging (debug level)")
    parser.add_argument(
        "--docker-image",
        type=str,
        help="Docker image to use (default: proteowizard/pwiz-skyline-i-agree-to-the-vendor-licenses:latest)",
    )

    # Docker resource limits
    parser.add_argument(
        "--worker-cores",
        type=float,
        help="CPU cores per worker container (e.g., 2.0, 0.5)",
    )
    parser.add_argument(
        "--worker-memory",
        type=str,
        help="Memory limit per worker container (e.g., '4g', '2048m')",
    )
    parser.add_argument(
        "--worker-swap",
        type=str,
        help="Swap memory limit per worker container (e.g., '1g', '512m'). Set to same as memory to disable swap.",
    )
    parser.add_argument(
        "--worker-shm-size",
        type=str,
        default="512m",
        help="Shared memory size per worker container (default: 512m). Important for Wine operations.",
    )

    # Preset config group - mutually exclusive
    preset_group = parser.add_mutually_exclusive_group()

    # Dynamically add arguments for each preset
    for preset in PresetConfig:
        preset_group.add_argument(
            f"--{preset.name.lower()}", action="store_const", const=preset, dest="preset", help=preset.description
        )

    preset_group.add_argument("-c", "--config", type=Path, help="Path to custom config file")

    return parser


def cli() -> None:
    """Main entry point."""
    parser = create_parser()
    args, unknown_args = parser.parse_known_args()

    if not args.inputs:
        parser.error("No input files or directories specified")

    if args.workers < 1:
        parser.error("Number of workers must be at least 1")

    # Setup logging
    log_file = args.log
    if args.verbose and not log_file:
        log_file = args.output_dir / f"msconvert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        print(f"Logging to: {log_file}")

    logger = setup_logging(log_file, args.verbose)

    # Log run configuration
    logger.info(f"Input paths: {[str(p) for p in args.inputs]}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Workers: {args.workers}")
    if args.docker_image:
        logger.info(f"Docker image: {args.docker_image}")
    if args.worker_cores:
        logger.info(f"Worker cores: {args.worker_cores}")
    if args.worker_memory:
        logger.info(f"Worker memory: {args.worker_memory}")
    if args.worker_swap:
        logger.info(f"Worker swap: {args.worker_swap}")
    logger.info(f"Worker shared memory: {args.worker_shm_size}")

    # Determine config path
    config_path = None
    if hasattr(args, "preset") and args.preset:
        config_path = get_preset_config_path(args.preset)
        if not config_path:
            msg = f"Error: Could not find {args.preset.name.lower()} preset config"
            print(msg, file=sys.stderr)
            logger.error(msg)
            sys.exit(1)
        msg = f"Using {args.preset.name.title()} preset config"
        print(msg)
        logger.info(f"Preset: {args.preset.name}")
        logger.info(f"Config file: {config_path}")
    elif args.config:
        if not args.config.exists():
            msg = f"Error: Config file not found: {args.config}"
            print(msg, file=sys.stderr)
            logger.error(msg)
            sys.exit(1)
        config_path = args.config
        msg = f"Using custom config: {config_path}"
        print(msg)
        logger.info(f"Custom config: {config_path}")

    if (args.preset or args.config) and any(arg in ["-c", "--config"] for arg in unknown_args):
        parser.error("Cannot specify config/preset and also use -c in additional arguments")

    if unknown_args:
        logger.info(f"Additional msconvert arguments: {' '.join(unknown_args)}")

    logger.info(f"{'=' * 60}")

    # Find and convert files
    converter = SimplePWizConverter(
        logger=logger,
        docker_image=args.docker_image,
        worker_cores=args.worker_cores,
        worker_memory=args.worker_memory,
        worker_swap=args.worker_swap,
        worker_shm_size=args.worker_shm_size,
    )
    files = converter.find_files(args.inputs)

    if not files:
        msg = "No supported mass spectrometry files found"
        print(msg, file=sys.stderr)
        logger.error(msg)
        sys.exit(1)

    msg = f"Found {len(files)} file{'s' if len(files) != 1 else ''} to convert"
    print(msg)
    logger.info(msg)
    logger.info("Files to convert:")
    for i, f in enumerate(files, 1):
        logger.info(f"  {i}. {f.name}")
    logger.info(f"{'=' * 60}")

    success = converter.run_msconvert(files, args.output_dir, unknown_args, config_path, args.workers)

    logger.info(f"{'=' * 60}")
    logger.info(f"Conversion {'SUCCEEDED' if success else 'FAILED'}")
    if success:
        logger.info(f"All {len(files)} files converted successfully")
    else:
        logger.error("Some files failed to convert")
    logger.info(f"{'=' * 60}")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    cli()
