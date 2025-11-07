"""Base environment class."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type, List, cast


from fragua.agents.agent import Agent
from fragua.storages.warehouse import Warehouse
from fragua.agents import WarehouseManager, Miner, Blacksmith, Haulier
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Environment:
    """
    Base Environment for Fragua.

    Manages the lifecycle and registration of a single warehouse,
    a single warehouse manager, and multiple agents of different types.
    """

    AGENT_CLASSES: Dict[str, Type[Agent]] = {
        "miner": Miner,
        "blacksmith": Blacksmith,
        "haulier": Haulier,
    }

    def __init__(self, name: str, env_type: str = "base"):
        self.name = name
        self.env_type = env_type

        # Structured component registry
        self.components: Dict[str, Any] = {
            "warehouse": None,
            "manager": None,
            "agents": {atype: [] for atype in self.AGENT_CLASSES},
        }

        logger.debug(
            "Environment '%s' initialized (type=%s).", self.name, self.env_type
        )

    # ---------------------------------------------------------------------
    # INTERNAL VALIDATION
    # ---------------------------------------------------------------------

    def _check_duplicate_name(self, name: str) -> None:
        """Ensure no component with the given name already exists."""

        # Warehouse
        wh = self.components["warehouse"]
        if wh is not None and getattr(wh, "name", None) == name:
            raise ValueError(f"Duplicate name '{name}' already used for Warehouse.")

        # Manager
        mgr = self.components["manager"]
        if mgr is not None and getattr(mgr, "name", None) == name:
            raise ValueError(
                f"Duplicate name '{name}' already used for WarehouseManager."
            )

        # Agents
        for atype, agents in self.components["agents"].items():
            for agent in agents:
                if getattr(agent, "name", None) == name:
                    raise ValueError(
                        f"Duplicate agent name detected: '{name}' ({atype})."
                    )

    # ---------------------------------------------------------------------
    # CREATION HELPERS
    # ---------------------------------------------------------------------

    def create_warehouse(self, name: Optional[str] = None) -> Warehouse:
        """Create the warehouse (only one allowed per environment)."""
        if self.components["warehouse"] is not None:
            raise RuntimeError("A warehouse already exists in this environment.")

        wh_name = name or f"{self.name}_warehouse"
        self._check_duplicate_name(wh_name)

        warehouse = Warehouse(wh_name)
        self.components["warehouse"] = warehouse
        logger.info("Warehouse created: %s", wh_name)
        return warehouse

    def create_manager(
        self, name: Optional[str] = None, warehouse: Optional[Warehouse] = None
    ) -> WarehouseManager:
        """Create the warehouse manager (only one allowed per environment)."""

        if self.components["manager"] is not None:
            raise RuntimeError("A WarehouseManager already exists in this environment.")

        # Ensure warehouse exists
        if warehouse is None:
            warehouse = self.components["warehouse"] or self.create_warehouse()

        if warehouse is None:
            raise TypeError("A warehouse is required.")

        mgr_name = name or f"{self.name}_manager"
        self._check_duplicate_name(mgr_name)

        manager = WarehouseManager(mgr_name, warehouse)
        self.components["manager"] = manager
        logger.info("WarehouseManager created: %s", mgr_name)
        return manager

    def create_agent(
        self,
        agent_type: str,
        name: Optional[str] = None,
        manager: Optional[WarehouseManager] = None,
    ) -> Agent:
        """
        Create and register an agent associated with the warehouse manager.

        Args:
            agent_type: One of 'miner', 'blacksmith', 'haulier'.
            name: Optional name for the agent.
            manager: Optional existing WarehouseManager; created if not present.
        """
        agent_type = agent_type.lower()

        if agent_type not in self.AGENT_CLASSES:
            raise ValueError(
                f"Unknown agent type '{agent_type}'. "
                f"Available: {list(self.AGENT_CLASSES.keys())}"
            )

        agent_cls = self.AGENT_CLASSES[agent_type]

        agent_name = (
            name
            or f"{self.name}_{agent_type}_{len(self.components['agents'][agent_type]) + 1}"
        )

        self._check_duplicate_name(agent_name)

        if manager is None:
            manager = self.components["manager"] or self.create_manager()

        if manager is None:
            raise TypeError("A warehouse manager is required.")

        agent = agent_cls(agent_name, manager)
        self.components["agents"][agent_type].append(agent)

        logger.info("Agent created: %s (%s)", agent_name, agent_cls.__name__)
        return agent

    def create_miner(self, name: Optional[str] = None) -> Miner:
        """Shortcut to create a Miner agent."""
        return cast(Miner, self.create_agent("miner", name))

    def create_blacksmith(self, name: Optional[str] = None) -> Blacksmith:
        """Shortcut to create a Blacksmith agent."""
        return cast(Blacksmith, self.create_agent("blacksmith", name))

    def create_haulier(self, name: Optional[str] = None) -> Haulier:
        """Shortcut to create a Haulier agent."""
        return cast(Haulier, self.create_agent("haulier", name))

    # ---------------------------------------------------------------------
    # ACCESSORS
    # ---------------------------------------------------------------------

    def get_warehouse(self) -> Optional[Warehouse]:
        """Return warehouse."""
        return cast(Optional[Warehouse], self.components["warehouse"])

    def get_manager(self) -> Optional[WarehouseManager]:
        """Return warehouse manager."""
        return cast(Optional[WarehouseManager], self.components["manager"])

    def get_agents(self, agent_type: Optional[str] = None) -> List[Any]:
        """Return all agents or those of a given type."""
        if agent_type is None:
            return [a for agents in self.components["agents"].values() for a in agents]
        if agent_type not in self.AGENT_CLASSES:
            raise ValueError(f"Invalid agent type '{agent_type}'.")
        return cast(List[Any], self.components["agents"][agent_type])

    # ---------------------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """Return environment metadata and component overview."""
        return {
            "name": self.name,
            "type": self.env_type,
            "warehouse": (
                self.components["warehouse"].__class__.__name__
                if self.components["warehouse"]
                else None
            ),
            "manager": (
                self.components["manager"].__class__.__name__
                if self.components["manager"]
                else None
            ),
            "agents": {
                atype: [getattr(a, "name", str(a)) for a in agents]
                for atype, agents in self.components["agents"].items()
            },
        }

    def __repr__(self) -> str:
        agent_count = sum(len(lst) for lst in self.components["agents"].values())
        return f"<Environment name={self.name!r} type={self.env_type!r} agents={agent_count}>"
