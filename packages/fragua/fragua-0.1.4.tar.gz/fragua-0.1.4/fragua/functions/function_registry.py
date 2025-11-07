"""
Reusable functions module.
"""

from typing import Callable, Dict, Any

FUNCTIONS_REGISTRY: Dict[str, Dict[str, Callable[..., Any]]] = {}


def register_function(action: str, name: str) -> Callable[..., Any]:
    """
    Decorator to register a function under a specific action category ('mine', 'forge', 'delivery').
    Example:
        @register_function("mine", "mine_sql")
        def mine_sql(...): ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if action not in FUNCTIONS_REGISTRY:
            FUNCTIONS_REGISTRY[action] = {}
        if name in FUNCTIONS_REGISTRY[action]:
            raise ValueError(
                f"Function '{name}' already registered under action '{action}'."
            )
        FUNCTIONS_REGISTRY[action][name] = func
        return func

    return decorator


def get_function(action: str, name: str) -> Callable[..., Any]:
    """
    Retrieve a registered function by action and name.
    """
    try:
        return FUNCTIONS_REGISTRY[action][name]
    except KeyError as exc:
        raise ValueError(
            f"Function '{name}' not found under action '{action}'."
        ) from exc


def list_functions(action: str | None = None) -> dict[str, Any]:
    """
    List registered functions.
    If 'action' is provided, list only functions for that action.
    """
    if action:
        return FUNCTIONS_REGISTRY.get(action, {})
    return FUNCTIONS_REGISTRY
