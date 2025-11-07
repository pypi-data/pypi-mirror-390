"""
domolibrary2 - A Python library for interacting with Domo APIs.
"""

import sys
from pathlib import Path

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

# Initialize colored logger as global logger
# This must happen before any other imports that use logging
from .utils.logging import get_colored_logger

_logger = get_colored_logger()  # Sets as dc_logger global logger

# Import submodules to make them available
# Note: classes, client, and routes have circular dependencies
# If you encounter import errors, import individual modules directly like:
# from domolibrary2.auth import DomoAuth
# from domolibrary2.routes.user import get_user
# from domolibrary2.classes.DomoUser import DomoUser

from .base import entities, exceptions

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
