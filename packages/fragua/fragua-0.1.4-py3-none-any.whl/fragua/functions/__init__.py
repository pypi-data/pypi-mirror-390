"""
Reusable Functions Module.
"""

from fragua.functions.function_registry import (
    FUNCTIONS_REGISTRY,
    register_function,
    get_function,
    list_functions,
)

# Import modules to auto-register their functions
from fragua.functions import (
    mine_functions,
    forge_functions,
    delivery_functions,
)  # noqa: F401


__all__ = [
    # Registry Functions
    "FUNCTIONS_REGISTRY",
    "register_function",
    "get_function",
    "list_functions",
    # Mine Functions
]
