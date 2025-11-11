# Integrations module - automatically imports all integration modules
# Users can import integrations like: from domolibrary2.integrations import Automation

# Import all integration modules
from . import Automation, RoleHierarchy, shortcut_fn

# Define what gets imported with "from domolibrary2.integrations import *"
__all__ = [
    "Automation",
    "RoleHierarchy",
    "shortcut_fn",
]
