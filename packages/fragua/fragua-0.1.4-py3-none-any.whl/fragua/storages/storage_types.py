"""
Storage types for storing different kinds of data.
"""

from typing import Any, Dict, Union, Type, TypeVar
from fragua.storages.storage import Storage

STORAGE_REGISTRY: Dict[str, Type[Storage[Any]]] = {}
S = TypeVar("S", bound="Storage[Any]")


def register_storage(cls: Type[S]) -> Type[S]:
    """Register a Storage subclass in the global registry."""
    STORAGE_REGISTRY[cls.__name__] = cls
    return cls


def get_storage(name: str) -> Type[Storage[Any]]:
    """Retrieve a Storage subclass from the registry by name."""
    if name not in STORAGE_REGISTRY:
        raise KeyError(f"Storage class '{name}' not registered.")
    return STORAGE_REGISTRY[name]


def list_storages() -> list[str]:
    """Return a list of all registered storage class names."""
    return list(STORAGE_REGISTRY.keys())


@register_storage
class Wagon(Storage[Any]):
    """Storage type for raw data."""


@register_storage
class Box(Storage[Any]):
    """Storage type for transformed data."""


@register_storage
class Container(Storage[Any]):
    """
    Storage designed to contain other storages (Wagon and Box).
    """

    def __init__(self) -> None:
        super().__init__(data=None)
        self._content: Dict[str, Union[Wagon, Box]] = {}

    def add_storage(self, storage_name: str, storage: Union[Wagon, Box]) -> None:
        """Add a sub-storage (Wagon or Box) to the container."""
        self._content[storage_name] = storage

    def get_storage(self, name: str) -> Union[Wagon, Box]:
        """Retrieve a specific sub-storage by name."""
        return self._content[name]

    def list_storages(self) -> dict[str, str]:
        """Return a mapping of contained storages: name -> type."""
        return {name: s.__class__.__name__ for name, s in self._content.items()}

    def remove_storage(self, name: str) -> None:
        """Remove a sub-storage by name."""
        self._content.pop(name, None)

    def clear(self) -> None:
        """Remove all contained storages."""
        self._content.clear()

    def __repr__(self) -> str:
        items = ", ".join(self._content.keys()) or "empty"
        return f"<Container: {items}>"
