"""Basic environment for Fragua."""

from __future__ import annotations

from fragua.environments.environment import Environment
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class BasicEnvironment(Environment):
    """
    Predefined environment with the essential Fragua setup:
    - 1 Warehouse
    - 1 WarehouseManager
    - 1 Miner
    - 1 Blacksmith
    - 1 Haulier
    """

    def __init__(self, name: str):
        super().__init__(name, env_type="basic")

        # Automatically build basic setup
        logger.debug("Creating BasicEnvironment '%s'...", self.name)

        # 1. Warehouse
        warehouse = self.create_warehouse(f"{name}_warehouse")

        # 2. Warehouse Manager
        self.create_manager(f"{name}_manager", warehouse)

        # 3. Agents
        self.create_miner(f"{name}_miner")
        self.create_blacksmith(f"{name}_blacksmith")
        self.create_haulier(f"{name}_haulier")

        logger.info(
            "BasicEnvironment '%s' created successfully with warehouse, manager, and 3 agents.",
            self.name,
        )
