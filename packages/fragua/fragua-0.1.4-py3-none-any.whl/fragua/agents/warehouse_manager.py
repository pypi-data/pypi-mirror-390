"""
WarehouseManager class in Fragua.
Handles all logic for adding, getting, removing, and listing storages.
Works with a flat Warehouse structure without grouping by type.
"""

from typing import Any, Union, Optional, Mapping, Dict, List, Literal
from datetime import datetime

from fragua.storages.storage import Storage
from fragua.utils.logger import get_logger
from fragua.utils.metrics import add_metadata_to_storage, generate_metadata
from fragua.storages.warehouse import Warehouse
from fragua.storages.storage_types import Wagon, Box

logger = get_logger(__name__)


StorageType = Literal["wagon", "box", "all"]
TYPE_MAP: Dict[str, Any] = {
    "wagon": Wagon,
    "box": Box,
}


class WarehouseManager:
    """
    Encapsulates storage management logic.
    Handles only Wagon and Box storage objects Warehoused in a flat structure.
    """

    def __init__(self, name: str, warehouse: Warehouse) -> None:
        """
        Initialize the WarehouseManager with an existing Warehouse instance.

        Args:
            Warehouse (Warehouse): The Warehouse instance to manage.
        """
        self.warehouse = warehouse
        self.name = name
        self._movement_log: List[dict[str, object]] = []

    def _generate_save_metadata(
        self, storage: Union[Wagon, Box], storage_name: str, agent_name: Optional[str]
    ) -> None:
        """Generate and attach metadata to a storage object before saving."""
        metadata_kwargs: Dict[str, Any] = {
            "metadata_type": "save",
            "storage_name": storage_name,
            "agent_name": agent_name,
            "warehouse_manager": self.name,
        }
        metadata = generate_metadata(storage, **metadata_kwargs)
        add_metadata_to_storage(storage, metadata)

    # ------------------- Movement Logging ------------------- #
    def _log_movement(
        self,
        /,
        **movement_log: Any,
    ) -> None:
        """Records a movement in the internal log."""
        now = datetime.now().astimezone()

        date_str = now.date().isoformat()
        time_str = now.time().strftime("%H:%M:%S")

        raw_offset = now.strftime("%z")
        if raw_offset and len(raw_offset) == 5:
            tz_offset = f"{raw_offset[:3]}:{raw_offset[3:]}"
        else:
            tz_offset = raw_offset or ""

        entry: dict[str, object] = {
            "date": date_str,
            "time": time_str,
            "timezone": tz_offset,
            "operation": movement_log.get("operation"),
            "storage_type": movement_log.get("storage_type"),
            "storage_name": movement_log.get("storage_name"),
            "agent_name": movement_log.get("agent_name"),
            "warehouse": getattr(self.warehouse, "warehouse_name", None),
            "success": movement_log.get("success"),
            "details": movement_log.get("details") or {},
        }

        self._movement_log.append(entry)
        logger.info(
            "[%s] Movement logged by '%s': %s '%s' by agent '%s' at %s %s %s",
            self.name,
            self.name,
            movement_log.get("operation"),
            movement_log.get("storage_name"),
            movement_log.get("agent_name"),
            entry["date"],
            entry["time"],
            entry["timezone"],
        )

    def movements_log(
        self,
        storage_type: Union[Wagon, Box, None] = None,
        storage_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        operation: Optional[str] = None,
    ) -> List[dict[str, object]]:
        """Returns movements filtered by type, object name or agent."""
        result = self._movement_log
        if storage_type:
            result = [m for m in result if m["storage_type"] == storage_type]
        if storage_name:
            result = [m for m in result if m["storage_name"] == storage_name]
        if agent_name:
            result = [m for m in result if m["agent_name"] == agent_name]
        if operation:
            result = [m for m in result if m["operation"] == operation]
        return result

    # -----------------------------
    # Add
    # -----------------------------
    def add(
        self,
        storage: Storage[Any],
        storage_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        overwrite: bool = False,
    ) -> None:
        """
        Add a Wagon or Box to the Warehouse and update movement log.

        Args:
            storage: The Wagon or Box object to Warehouse.
            storage_type: 'wagon' or 'box'.
            storage_name: Name to Warehouse the object under.
            agent_name: Optional agent performing the action.
            overwrite: Whether to overwrite if it already exists.

        Raises:
            ValueError: If storage_name is missing or storage_type is invalid.
        """
        movement_log: Dict[str, Any] = {}
        storage_type = storage.__class__.__name__.lower()
        try:
            if storage_name is None:
                raise ValueError("Missing required argument: 'storage_name'")

            if storage_type not in ("wagon", "box"):
                raise ValueError(f"Invalid storage_type '{storage_type}'")

            if storage_name in self.warehouse.data and not overwrite:
                logger.warning(
                    "[%s] %s '%s' exists. Use overwrite=True to replace.",
                    self.name,
                    storage_type,
                    storage_name,
                )
                movement_log = {
                    "operation": "add",
                    "storage_type": storage_type,
                    "storage_name": storage_name,
                    "agent_name": agent_name,
                    "success": False,
                    "details": {"reason": "exists"},
                }
                self._log_movement(**movement_log)
                return

            # Save object in Warehouse
            self.warehouse.data[storage_name] = storage

            logger.info(
                "[%s] Added %s '%s' by agent '%s'",
                self.name,
                storage_type,
                storage_name,
                agent_name,
            )

            movement_log = {
                "operation": "add",
                "storage_type": storage_type,
                "storage_name": storage_name,
                "agent_name": agent_name,
                "success": True,
            }
            self._log_movement(**movement_log)

        except Exception as e:
            movement_log = {
                "operation": "add",
                "storage_type": storage_type,
                "storage_name": storage_name or "unknown",
                "agent_name": agent_name,
                "success": False,
                "details": {"error": str(e)},
            }
            self._log_movement(**movement_log)
            raise

    # -----------------------------
    # Get
    # -----------------------------
    def get(
        self,
        agent_name: str,
        storage_type: StorageType = "all",
        storage_name: str = "all",
    ) -> Union[
        Optional[Union[Wagon, Box]],
        Mapping[str, Union[Wagon, Box]],
        Mapping[str, Mapping[str, Union[Wagon, Box]]],
    ]:
        """
        Retrieve objects from the Warehouse and log the operation.

        Args:
            storage_type: 'wagon', 'box', or 'all'
            storage_name: Name of the object, or 'all'

        Returns:
            Single object, dict of objects, or dict by type.
        """

        result: Dict[str, Union[Wagon, Box]] = {}
        try:
            if storage_type == "all":
                classes = (Wagon, Box)
            else:
                classes = TYPE_MAP[storage_type]

            for name, obj in self.warehouse.data.items():
                if not isinstance(obj, classes):
                    continue
                if storage_name not in ("all", name):
                    continue
                result[name] = obj

            self._log_movement(
                operation="get",
                storage_type=storage_type,
                storage_name=storage_name,
                agent_name=agent_name,
                success=True,
                details={"result_type": type(result).__name__},
            )

            return (
                next(iter(result.values()), None) if storage_name != "all" else result
            )

        except Exception as e:
            self._log_movement(
                operation="get",
                storage_type=storage_type,
                storage_name=storage_name,
                agent_name=None,
                success=False,
                details={"error": str(e)},
            )
            raise

    # -----------------------------
    # Remove
    # -----------------------------
    def remove(
        self,
        storage_type: StorageType,
        storage_name: str = "all",
    ) -> Union[
        Optional[Storage[Wagon | Box]],
        Mapping[str, Storage[Wagon | Box]],
        Mapping[str, Mapping[str, Storage[Wagon | Box]]],
    ]:
        """
        Remove objects from the Warehouse and log the operation.

        Args:
            storage_type: 'wagon', 'box', or 'all'
            storage_name: Name of the object, or 'all'

        Returns:
            The removed object(s) or dict by type.
        """

        removed: Dict[str, Storage[Wagon | Box]] = {}
        try:
            data = self.warehouse.data

            # Determine which classes to remove
            if storage_type == "all":
                classes = (Wagon, Box)
            else:
                classes = TYPE_MAP[storage_type]

            # Collect keys to remove
            keys_to_remove = [
                name
                for name, obj in data.items()
                if isinstance(obj, classes) and storage_name in ("all", name)
            ]

            for key in keys_to_remove:
                removed[key] = data.pop(key)

            count_removed = len(removed)

            # Log movement
            self._log_movement(
                operation="remove",
                storage_type=storage_type,
                storage_name=storage_name,
                agent_name=None,
                success=bool(removed),
                details={"removed_count": count_removed},
            )

            if removed:
                logger.info(
                    "[%s] Removed object(s) '%s' of type '%s'",
                    self.name,
                    storage_name,
                    storage_type,
                )
            else:
                logger.warning(
                    "[%s] Nothing removed for '%s' (%s)",
                    self.name,
                    storage_name,
                    storage_type,
                )

            if storage_name != "all" and removed:
                return next(iter(removed.values()))
            return removed

        except Exception as e:
            self._log_movement(
                operation="remove",
                storage_type=storage_type,
                storage_name=storage_name,
                agent_name=None,
                success=False,
                details={"error": str(e)},
            )
            raise

    # -----------------------------
    # Exists
    # -----------------------------
    def exists(self, name: str) -> bool:
        """
        Check if a specific object exists in the Warehouse.

        Args:
            name (str): Name of the object.

        Returns:
            bool: True if the object exists, False otherwise.
        """
        return name in self.warehouse.data

    # -----------------------------
    # List all metadata
    # -----------------------------
    def list_all(
        self,
        fields: Optional[List[str]] = None,
        all_fields: bool = False,
    ) -> Mapping[str, Dict[str, object]]:
        """
        Return metadata for all Warehoused objects, optionally filtered by fields.

        Args:
            fields (List[str], optional): Specific metadata fields to include.
            all_fields (bool): If True, include all metadata fields.

        Returns:
            Mapping[str, Dict[str, object]]: Dictionary of object names to filtered metadata.
        """
        default_fields = ["storage_name", "type", "rows", "columns", "checksum"]
        selected_fields = [] if all_fields else (fields or default_fields)

        result: Dict[str, Dict[str, object]] = {}

        for name, obj in self.warehouse.data.items():
            metadata = getattr(obj, "metadata", {})
            if all_fields:
                result[name] = metadata
            else:
                result[name] = {
                    k: v for k, v in metadata.items() if k in selected_fields
                }

        return result

    # -----------------------------
    # Remove all convenience
    # -----------------------------
    def remove_all(self) -> None:
        """
        Remove all objects from the Warehouse.

        Returns:
            Mapping[str, Union[Wagon, Box]]: All removed objects.
        """
        self.remove("all")
