"""Blacksmith Class."""

from __future__ import annotations

from typing import Any
from fragua.agents.agent import Agent
from fragua.agents.warehouse_manager import WarehouseManager
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Blacksmith(Agent):
    """Agent that applies forge styles to data for transformation."""

    def __init__(self, name: str, warehouse_manager: WarehouseManager):
        super().__init__(name=name, manager=warehouse_manager)
        self.role = "blacksmith"
        self.action = "forge"
        self.storage_type = "Box"

    def work(
        self,
        /,
        style: str,
        save_as: str | None = None,
        apply_to: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Execute the agent's task using the action and style defined by blacksmith role."""

        data = self.get_from_store(apply_to)
        kwargs["data"] = data
        self._execute_workflow(style, save_as, **kwargs)
