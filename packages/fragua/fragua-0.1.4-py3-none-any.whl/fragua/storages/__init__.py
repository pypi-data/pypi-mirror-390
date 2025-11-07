"""Fragua Store package."""

# ------------------- Storage Class ------------------- #
from .storage import Storage

# ------------------- Store Class ------------------- #
from .warehouse import Warehouse

# ------------------- Storage Types ------------------- #
from .storage_types import (
    Box,
    Wagon,
    Container,
    STORAGE_REGISTRY,
    register_storage,
    get_storage,
    list_storages,
)


# ------------------- __all__ ------------------- #
__all__ = [
    "Warehouse",
    "Storage",
    # Storage Types
    "Wagon",
    "Box",
    "Container",
    # Storage Registry Functions
    "STORAGE_REGISTRY",
    "register_storage",
    "get_storage",
    "list_storages",
]
