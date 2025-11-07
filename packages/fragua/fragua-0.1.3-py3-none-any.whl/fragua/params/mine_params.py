"""
Mine parameters classes for different types of data sources.
"""

from typing import Any, Dict, Union, TypeVar
from pathlib import Path
from pydantic import Field
from fragua.params.params import Params, register_params

role: str = "miner"


class MineParams(Params):
    """Common parameters for mining agents."""

    read_kwargs: Dict[str, Any] = Field(default_factory=dict)


@register_params(role, style="csv")
class CSVMineParams(MineParams):
    """Mining parameters for CSV files."""

    path: Union[str, Path]


@register_params(role, style="excel")
class ExcelMineParams(MineParams):
    """Mining parameters for Excel files."""

    path: Union[str, Path]
    sheet_name: Union[str, int] = 0


@register_params(role, style="sql")
class SQLMineParams(MineParams):
    """Mining parameters for SQL databases."""

    connection_string: str
    query: str


@register_params(role, style="api")
class APIMineParams(MineParams):
    """Mining parameters for APIs."""

    url: str
    method: str = "GET"
    headers: Dict[str, str] = Field(default_factory=dict)
    params: Dict[str, Any] = Field(default_factory=dict)
    data: Dict[str, Any] = Field(default_factory=dict)
    auth: Dict[str, str] = Field(default_factory=dict)
    proxy: Dict[str, str] = Field(default_factory=dict)
    timeout: float = 30.0


MineParamsT = TypeVar("MineParamsT", bound=MineParams)
CSVMineParamsT = TypeVar("CSVMineParamsT", bound=CSVMineParams)
ExcelMineParamsT = TypeVar("ExcelMineParamsT", bound=ExcelMineParams)
SQLMineParamsT = TypeVar("SQLMineParamsT", bound=SQLMineParams)
APIMineParamsT = TypeVar("APIMineParamsT", bound=APIMineParams)
