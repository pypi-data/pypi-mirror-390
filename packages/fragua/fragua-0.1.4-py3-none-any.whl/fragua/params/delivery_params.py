"""
Delivery parameters classes for different types of data destinations.
"""

from typing import Dict, TypeVar
from pandas import DataFrame
from fragua.params.params import Params, register_params

role: str = "haulier"


class DeliveryParams(Params):
    """Common parameters for delivery agents."""

    data: DataFrame
    destination: str


@register_params(role, style="excel")
class ExcelDeliveryParams(DeliveryParams):
    """Parameters for Excel delivery."""

    file_name: str | None = None
    sheet_name: str | None = None
    index: bool = False
    engine: str | None = None


@register_params(role, style="sql")
class SQLDeliveryParams(DeliveryParams):
    """Parameters for SQL delivery."""

    table_name: str
    if_exists: str = "fail"
    index: bool = False
    chunksize: int | None = None


@register_params(role, style="api")
class APIDeliveryParams(DeliveryParams):
    """Parameters for API delivery."""

    endpoint: str
    method: str = "POST"
    headers: Dict[str, str] | None = None
    auth: Dict[str, str] | None = None
    timeout: float = 30.0


DeliveryParamsT = TypeVar("DeliveryParamsT", bound=DeliveryParams)
ExcelDeliveryParamsT = TypeVar("ExcelDeliveryParamsT", bound=ExcelDeliveryParams)
SQLDeliveryParamsT = TypeVar("SQLDeliveryParamsT", bound=SQLDeliveryParams)
APIDeliveryParamsT = TypeVar("APIDeliveryParamsT", bound=APIDeliveryParams)
