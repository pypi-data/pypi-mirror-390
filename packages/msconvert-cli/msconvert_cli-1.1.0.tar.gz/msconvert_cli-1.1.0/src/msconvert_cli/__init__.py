"""msconvert-cli: Python wrapper for ProteoWizard msconvert with Docker support."""

__version__ = "1.1.0"

from .converter import SimplePWizConverter
from .presets import PresetConfig

__all__ = ["PresetConfig", "SimplePWizConverter", "__version__"]
