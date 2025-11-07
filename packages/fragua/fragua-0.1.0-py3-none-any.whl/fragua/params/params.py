"""
Base abstract class for all parameter schemas used by styles in Fragua.
"""

from typing import Dict, Tuple, Type, Any
from pydantic import BaseModel
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Params(BaseModel):
    """Base configuration model shared by all params."""

    class Config:
        """Configuration for the Params model."""

        arbitrary_types_allowed = True  # Allows DataFrame
        extra = "forbid"  # Forbid unexpected fields (strict)


PARAMS_REGISTRY: Dict[Tuple[str, str], Type[Params]] = {}


def register_params(role: str, style: str) -> Any:
    """
    Decorator to register a Params class for a given agent and style.

    Example:
        @register_params(agent="miner", style="excel")
        class ExcelMineParams(MineParams):
            ...
    """

    def decorator(cls: Type[Params]) -> Any:
        PARAMS_REGISTRY[(role, style)] = cls
        return cls

    return decorator


def get_params(role: str, style: str) -> Type[Params]:
    """
    Retrieve the registered Params class for a given role and style.

    Args:
        role (str): Name of the agent role (e.g., "miner", "blacksmith").
        style (str): Name of the style (e.g., "excel", "forge").

    Returns:
        Type[Params]: The registered Params subclass.

    Raises:
        KeyError: If no Params class is registered for the given (role, style).
    """
    try:
        return PARAMS_REGISTRY[(role, style)]
    except KeyError as exc:
        raise KeyError(
            f"No Params class registered for role='{role}', style='{style}'."
        ) from exc


def list_params(role: str | None = None) -> Dict[Tuple[str, str], str]:
    """
    List all registered Params types, optionally filtered by agent role.

    Args:
        role (str | None): Optional role name to filter by.
            If None, all registered Params are listed.

    Returns:
        Dict[Tuple[str, str], str]: A dictionary mapping (role, style) to
        the corresponding Params class name.
    """
    if role is not None:
        return {
            key: cls.__name__ for key, cls in PARAMS_REGISTRY.items() if key[0] == role
        }

    return {key: cls.__name__ for key, cls in PARAMS_REGISTRY.items()}


def create_params_class(
    role: str, style: str, class_name: str, **kwargs: Any
) -> Type[Params]:
    """
    Dynamically create and register a new Params subclass.

    Required Args:
        role (str): Role name ("miner", "blacksmith", or "haulier").
        style (str): Style name (e.g., "excel", "forge").
        class_name (str): Name of the new Params class.

    Optional kwargs:
        fields (Dict[str, tuple[type, Any] | type]): Field definitions.
        base (Type[Params]): Base class to inherit from (default: Params).
        overwrite (bool): If True, allows overwriting existing (role, style).

    Returns:
        Type[Params]: The newly created and registered Params subclass.
    """
    valid_roles = {"miner", "blacksmith", "haulier"}

    # --- Extract kwargs ---
    fields: Dict[str, tuple[type, Any] | type] = kwargs.get("fields", {})
    base: Type[Params] = kwargs.get("base", Params)
    overwrite: bool = kwargs.get("overwrite", False)

    # --- Validate role ---
    if role not in valid_roles:
        raise ValueError(
            f"Invalid role '{role}'. Must be one of: {', '.join(sorted(valid_roles))}."
        )

    # --- Prevent duplicate (role, style) unless overwrite=True ---
    key = (role, style)
    if key in PARAMS_REGISTRY and not overwrite:
        raise KeyError(
            f"A Params class is already registered for role='{role}', style='{style}'. "
            "Use overwrite=True to replace it."
        )

    # --- Prepare annotations and defaults ---
    annotations: Dict[str, type] = {}
    defaults: Dict[str, Any] = {}
    for name, value in fields.items():
        if isinstance(value, tuple):
            annotations[name] = value[0]
            defaults[name] = value[1]
        else:
            annotations[name] = value

    attrs: Dict[str, Any] = {"__annotations__": annotations, **defaults}

    # --- Dynamically create subclass ---
    cls: Type[Params] = type(class_name, (base,), attrs)

    # --- Register it ---
    PARAMS_REGISTRY[key] = cls

    # --- Log success ---
    if overwrite:
        logger.info(
            "Replaced existing Params class for role='%s', style='%s' with '%s'.",
            role,
            style,
            class_name,
        )
    else:
        logger.info(
            "Created Params class '%s' for role='%s', style='%s'.",
            class_name,
            role,
            style,
        )

    return cls
