"""
DeliveryStyle types for various data delivery methods.
"""

from abc import abstractmethod
from typing import Any, Generic
import pandas as pd


from fragua.styles.style import Style, ResultT, register_style
from fragua.params.delivery_params import (
    DeliveryParamsT,
    ExcelDeliveryParamsT,
    SQLDeliveryParamsT,
    APIDeliveryParamsT,
)
from fragua.utils.logger import get_logger
from fragua.functions.function_registry import get_function

logger = get_logger(__name__)

action: str = "deliver"


# ---------------------------------------------------------------------- #
# Base DeliveryStyle
# ---------------------------------------------------------------------- #
class DeliveryStyle(Style[DeliveryParamsT, ResultT], Generic[DeliveryParamsT, ResultT]):
    """
    Base class for all delivery styles in Fragua ETL.

    Standard pipeline provided by Style:
        validate_params -> _run -> validate_result -> postprocess
    """

    @abstractmethod
    def deliver(self, params: DeliveryParamsT) -> ResultT:
        """
        Deliver the given data to the target destination.
        Must be overridden by subclasses or use function registry.
        """
        raise NotImplementedError("Subclasses must implement deliver()")

    def _run(self, params: DeliveryParamsT) -> ResultT:
        """
        Executes the DeliveryStyle delivery step.
        """
        logger.debug("Starting DeliveryStyle '%s' delivery.", self.style_name)
        result = self.deliver(params)
        logger.debug("DeliveryStyle '%s' delivery completed.", self.style_name)
        return result


# ---------------------------------------------------------------------- #
# Excel Delivery
# ---------------------------------------------------------------------- #
@register_style(action, "excel")
class ExcelDeliveryStyle(DeliveryStyle[ExcelDeliveryParamsT, pd.DataFrame]):
    """
    DeliveryStyle for exporting data to Excel files.
    Uses registered functions for pipeline steps.
    """

    def deliver(self, params: ExcelDeliveryParamsT) -> pd.DataFrame:
        delivery_func = get_function(action, "delivery_excel")
        return delivery_func(params)


# ---------------------------------------------------------------------- #
# SQL Delivery
# ---------------------------------------------------------------------- #
@register_style(action, "sql")
class SQLDeliveryStyle(DeliveryStyle[SQLDeliveryParamsT, pd.DataFrame]):
    """
    DeliveryStyle for delivering data to SQL databases.
    Uses registered functions for pipeline steps.
    """

    def deliver(self, params: SQLDeliveryParamsT) -> pd.DataFrame:
        delivery_func = get_function(action, "delivery_sql")
        return delivery_func(params)


# ---------------------------------------------------------------------- #
# API Delivery
# ---------------------------------------------------------------------- #
@register_style(action, "api")
class APIDeliveryStyle(DeliveryStyle[APIDeliveryParamsT, Any]):
    """
    DeliveryStyle for delivering data to external APIs.
    Uses registered functions for pipeline steps.
    """

    def deliver(self, params: APIDeliveryParamsT) -> Any:
        delivery_func = get_function(action, "delivery_api")
        return delivery_func(params)
