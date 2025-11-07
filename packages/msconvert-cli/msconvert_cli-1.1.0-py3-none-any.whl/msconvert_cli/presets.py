"""Preset configurations for msconvert."""

from __future__ import annotations

import importlib.resources
from enum import Enum
from importlib.resources import as_file
from pathlib import Path

from typing_extensions import Self


class PresetConfig(Enum):
    """Available preset configurations."""

    SAGE = ("sage", "Sage preset config (mzml, 32-bit, zlib/gzip)")
    BIOSAUR = ("biosaur", "Biosaur preset config (mzml)")
    BLITZFF = ("blitzff", "BlitzFF preset config (mzml, MS1 only, 32-bit, zlib/gzip)")
    CASANOVO = ("casanovo", "Casanovo preset config (mzml, mzwindow [50-2500], denoise, top 200 peaks)")
    CASANOVO_MGF = ("casanovo_mgf", "Casanovo MGF preset config (mgf, mzwindow [50-2500], denoise, top 200 peaks)")

    def __init__(self, config_file: str, description: str):
        self.config_file = config_file
        self.description = description

    @classmethod
    def from_name(cls, name: str) -> Self | None:
        """Get preset by name (case-insensitive)."""
        for preset in cls:
            if preset.name.lower() == name.lower():
                return preset
        return None


def get_preset_config_path(preset: PresetConfig) -> Path | None:
    """Get path to a preset config file."""
    try:
        config_file = (
            importlib.resources.files("msconvert_cli").joinpath("configs").joinpath(f"{preset.config_file}.txt")
        )
        return as_file(config_file).__enter__()
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        return None
