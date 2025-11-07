"""Fragua environment factory and exports."""

from typing import Dict, Type
from fragua.environments.environment import Environment
from fragua.environments.basic import BasicEnvironment
from fragua.environments.empty import EmptyEnvironment

# Registry of available environment types
ENVIRONMENT_TYPES: Dict[str, Type[Environment]] = {
    "base": Environment,
    "basic": BasicEnvironment,
    "empty": EmptyEnvironment,
}


def create_fragua(name: str, env_type: str = "basic") -> Environment:
    """
    Create a Fragua environment with a specific configuration.

    Args:
        name (str): Environment name.
        env_type (str): Environment type ("basic", "free", "base", ...).

    Returns:
        Environment: Instantiated and configured environment.

    Raises:
        ValueError: If env_type is not a recognized type.
    """
    env_type = env_type.lower()
    if env_type not in ENVIRONMENT_TYPES:
        raise ValueError(
            f"Unknown environment type '{env_type}'. "
            f"Available: {list(ENVIRONMENT_TYPES.keys())}"
        )

    env_class = ENVIRONMENT_TYPES[env_type]
    environment = env_class(name)

    return environment


__all__ = [
    "Environment",
    "BasicEnvironment",
    "EmptyEnvironment",
    "create_fragua",
]
