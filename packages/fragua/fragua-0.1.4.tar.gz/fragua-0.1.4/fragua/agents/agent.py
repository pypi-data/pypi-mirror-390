"""
Agent class in Fragua.
Agents can take a role to work like a Miner, Blacksmith, or Transporter.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Mapping, Optional, Union
from datetime import datetime, timezone
import pandas as pd

from fragua.agents.warehouse_manager import WarehouseManager
from fragua.params.params import Params, get_params
from fragua.styles.style import get_style
from fragua.storages.storage import Storage
from fragua.storages.storage_types import Box, Wagon, get_storage
from fragua.utils.logger import get_logger
from fragua.utils.metrics import add_metadata_to_storage, generate_metadata


logger = get_logger(__name__)


class Agent(ABC):  # pylint: disable=too-many-instance-attributes
    """Agent class for ETL agents."""

    def __init__(
        self,
        name: str,
        manager: WarehouseManager,
    ):
        self.name: str = name
        self.warehouse_manager = manager
        self.role: str
        self._operations: list[dict[str, Any]] = []
        self.action: str
        self.storage_type: str

    # ----------------- Helpers ----------------- #
    def _determine_origin_name(self, origin: Any) -> Optional[str]:
        """Extract a meaningful origin name for operation metadata."""
        origin_name = None
        match origin:
            case Storage():
                origin_name = origin.__class__.__name__
                logger.debug("Detected Storage origin: %s", origin_name)
            case str() | Path():
                origin_name = Path(origin).name
                logger.debug("Detected file path origin: %s", origin_name)
            case _:
                if hasattr(origin, "path") and isinstance(origin.path, (str, Path)):
                    origin_name = Path(origin.path).name
                    logger.debug(
                        "Detected object with .path attribute: %s", origin_name
                    )
                elif hasattr(origin, "data") and isinstance(origin.data, pd.DataFrame):
                    origin_name = "DataFrame"
                    logger.debug("Detected object with .data as DataFrame")
                else:
                    logger.debug("Origin type not recognized; returning None")
        return origin_name

    def _generate_storage_name(self, style_name: str) -> str:
        """Generate a name for storage from action and style."""
        storage_name: str = f"{style_name}_{self.action}_data"
        return storage_name

    # ----------------- Metadata----------------- #
    def _generate_operation_metadata(
        self, style_name: str, storage: Storage[Any], origin: Any
    ) -> None:
        """Generate metadata from operation"""
        origin_name = self._determine_origin_name(origin)
        metadata = generate_metadata(
            storage=storage,
            metadata_type="operation",
            origin_name=origin_name,
            style_name=style_name,
        )
        add_metadata_to_storage(storage, metadata)

    # ----------------- Operations ----------------- #
    def get_operations(self) -> pd.DataFrame:
        """Return a DataFrame with all recorded operations done by the agent."""
        logger.debug(
            "[%s] Returning %d recorded operations",
            self.name,
            len(self._operations),
        )
        return pd.DataFrame(self._operations)

    def _add_operation(self, style: str, params_instance: Params) -> None:
        """Add operation to agent operations list."""
        self._operations.append(
            {
                "action": self.action,
                "style_name": style,
                "timestamp": datetime.now(timezone.utc),
                "params": params_instance,
            }
        )

    # ----------------- Create Storage ----------------- #
    def create_storage(self, data: Any) -> Storage[Any]:
        """Convert raw style output into the appropriate storage object using registry."""
        try:
            storage_cls = get_storage(self.storage_type)
        except KeyError as exc:
            raise TypeError(
                f"Result type '{self.storage_type}' is not a valid registered storage"
            ) from exc

        if self.storage_type == "Container":
            return storage_cls()

        return storage_cls(data=data)

    # ----------------- Store Manager Interaction ----------------- #
    def add_to_store(
        self,
        storage: Storage[Any],
        storage_name: str | None = None,
    ) -> None:
        """Store a Storage object via a WarehouseManager."""

        self.warehouse_manager.add(
            storage=storage,
            storage_name=storage_name,
            agent_name=self.name,
        )

    def get_from_store(self, storage_name: str | None) -> Union[
        Optional[Union[Wagon, Box]],
        Mapping[str, Union[Wagon, Box]],
        Mapping[str, Mapping[str, Union[Wagon, Box]]],
    ]:
        """Get data storage from store by a given storage name."""

        if storage_name is None:
            raise TypeError("Missing required atribute: storage_name.")

        storage = self.warehouse_manager.get(
            storage_name=storage_name, agent_name=self.name
        )

        if self.role == "haulier":
            return storage

        if isinstance(storage, (Wagon, Box)):
            df = storage.data
        elif isinstance(storage, Mapping):
            first_value = next(iter(storage.values()))
            if isinstance(first_value, (Wagon, Box)):
                df = first_value.data
            else:
                raise TypeError("Invalid nested mapping structure in store.")
        else:
            raise TypeError(f"Unexpected data type: {type(storage).__name__}")
        return df

    def auto_store(
        self, style: str, storage: Storage[Any], save_as: str | None
    ) -> None:
        """Add automatically an storage to store."""
        if save_as is not None:
            self.add_to_store(storage, save_as)
        else:
            generated_name = self._generate_storage_name(style)
            self.add_to_store(storage, generated_name)

    # ----------------- Work Pipeline ----------------- #
    def _execute_workflow(
        self,
        style: str,
        save_as: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Common workflow for agents that apply a style and store the result.
        Used by subclasses like Miner and Blacksmith.
        """
        params_instance = get_params(self.role, style)(**kwargs)
        stylized_data = get_style(self.action, style)(style).use(params_instance)

        storage = self.create_storage(stylized_data)

        self._generate_operation_metadata(
            style_name=style,
            storage=storage,
            origin=params_instance,
        )

        self._add_operation(style, params_instance)
        self.auto_store(style, storage, save_as)

    @abstractmethod
    def work(
        self,
        /,
        style: str,
        save_as: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Execute the agent's task using the action and style defined by its role."""

        self._execute_workflow(style, save_as, **kwargs)
