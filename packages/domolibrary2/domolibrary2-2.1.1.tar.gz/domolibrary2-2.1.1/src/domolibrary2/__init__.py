"""
domolibrary2 - A Python library for interacting with Domo APIs.
"""

import sys
from pathlib import Path

from .utils.logging import get_colored_logger

get_colored_logger(set_as_global=True)  # Sets as dc_logger global logger


# Always read version from pyproject.toml to ensure sync
try:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import tomli as tomllib

    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
            __version__ = pyproject_data["project"]["version"]
    else:
        # Fallback to installed package metadata
        import importlib.metadata

        __version__ = importlib.metadata.version("domolibrary2")
except Exception:
    __version__ = "unknown"

from .base import entities, exceptions  # noqa: E402

# Define what gets imported with "from domolibrary2 import *"
__all__ = [
    "__version__",
    "exceptions",
    "entities",
    # "classes",
    # "integrations",
    # "client",
    # "routes",
    # "utils",
]
