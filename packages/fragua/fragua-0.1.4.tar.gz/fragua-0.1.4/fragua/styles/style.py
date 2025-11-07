"""
Base class for all styles used by ETL agents in Fragua.
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, Dict, Optional, Type, Tuple
from fragua.utils.logger import get_logger
from fragua.params.params import Params

logger = get_logger(__name__)

# ---------------------------------------------------------------------- #
# Type Variables
# ---------------------------------------------------------------------- #
ResultT = TypeVar("ResultT")
ParamsT = TypeVar("ParamsT", bound=Params)


class Style(ABC, Generic[ParamsT, ResultT]):
    """
    Abstract base class for all styles in Fragua.
    Defines a standard interface for style operations.

    """

    def __init__(self, style_name: str):
        """Initialize the style with a given name and creator."""
        self.style_name = style_name

    # ---------------------------------------------------------------------- #
    # Abstract Core
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def _run(self, params: ParamsT) -> ResultT:
        """
        Core implementation of the style.

        Must be implemented by subclasses:
        - MineStyle -> extract
        - ForgeStyle -> forge
        - DeliveryStyle -> deliver
        """
        raise NotImplementedError

    def log_error(self, error: Exception) -> None:
        """Log an error with the style context."""
        logger.error(
            "[%s ERROR] %s: %s", self.__class__.__name__, type(error).__name__, error
        )

    # ---------------------------------------------------------------------- #
    # Public pipeline
    # ---------------------------------------------------------------------- #
    def use(self, params: ParamsT) -> ResultT:
        """
        Execute the full style pipeline.
        """
        try:
            result = self._run(params)

            return result

        except Exception as e:
            self.log_error(e)
            raise

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} style_name={self.style_name}>"


STYLE_REGISTRY: Dict[Tuple[str, str], Type[Style[Params, Any]]] = {}


def register_style(action: str, style: str) -> Any:
    """
    Decorator to register a Style class for a given (action, style).

    Example:
        @register_style(action="forge", style="ml")
        class MLForgeStyle(ForgeStyle):
            ...
    """

    def decorator(
        cls: Type[Style[Params, Any]],
    ) -> Type[Style[Params, Any]]:
        key = (action, style)
        if key in STYLE_REGISTRY:
            logger.warning("Overwriting existing style registration for %s", key)
        STYLE_REGISTRY[(action, style)] = cls
        logger.debug("Registered style: %s -> %s", key, cls.__name__)
        return cls

    return decorator


def get_style(action: str, style: str) -> Type[Style[Params, Any]]:
    """Retrieve a registered Style class by (action, style)."""
    try:
        return STYLE_REGISTRY[(action, style)]
    except KeyError as exc:
        logger.error("Style not found for action='%s', style='%s'", action, style)
        raise KeyError(
            f"Style not found for action='{action}', style='{style}'"
        ) from exc


def list_styles(
    action: Optional[str] = None,
) -> Dict[Tuple[str, str], Type[Style[Params, Any]]]:
    """List all registered styles, optionally filtered by action."""
    if action is not None:
        return {k: v for k, v in STYLE_REGISTRY.items() if k[0] == action}
    return dict(STYLE_REGISTRY)
