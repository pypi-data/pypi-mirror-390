"""
Lightweight in-memory store structure.
The StoreManager handles all the logic.
"""

from typing import Dict
from fragua.storages.storage import Storage
from fragua.storages.storage_types import Wagon, Box


class Warehouse:
    """
    Simple container for Wagons and Boxes.
    Warehouse manager is responsible for all operations.
    """

    def __init__(self, warehouse_name: str = "warehouse") -> None:
        """
        Initialize a warehouse.

        Args:
            warehouse_name (str): Name of the warehouse.
        """
        self.warehouse_name = warehouse_name
        self._warehouse: Dict[str, Storage[Wagon | Box]] = {}

    @property
    def data(self) -> Dict[str, Storage[Wagon | Box]]:
        """
        Expose the raw internal storage mapping.

        Returns: Dict[str, Union[Wagon, Box]]: Stored objects by name.
        """
        return self._warehouse
