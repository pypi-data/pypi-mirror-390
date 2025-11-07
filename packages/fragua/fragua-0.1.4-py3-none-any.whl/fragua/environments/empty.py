"""Empty Environment Class."""

from __future__ import annotations

from fragua.environments.environment import Environment
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class EmptyEnvironment(Environment):
    """
    A minimal Environment subclass that starts empty.
    It does not automatically create any Warehouse, WarehouseManager,
    or Agents. Useful for flexible or custom setups.
    """

    def __init__(self, name: str):
        super().__init__(name, env_type="empty")

        # Create only core components
        warehouse = self.create_warehouse(f"{self.name}_warehouse")
        self.create_manager(f"{self.name}_manager", warehouse)

        super().__init__(name, env_type="empty")
        logger.debug("EmptyEnvironment '%s' initialized with no components.", self.name)
        logger.info("EmptyEnvironment '%s' is ready for manual setup.", self.name)
