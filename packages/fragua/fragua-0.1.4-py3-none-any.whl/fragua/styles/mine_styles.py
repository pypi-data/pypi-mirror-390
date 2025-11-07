"""
MineStyle types for various data extraction methods, refactored to use FUNCTION_REGISTRY.
"""

from typing import Generic
import pandas as pd

from fragua.styles.style import Style, ResultT, register_style
from fragua.params.mine_params import (
    MineParamsT,
    CSVMineParamsT,
    ExcelMineParamsT,
    SQLMineParamsT,
    APIMineParamsT,
)
from fragua.functions.function_registry import get_function
from fragua.utils.logger import get_logger

logger = get_logger(__name__)
action: str = "mine"


# ---------------------------------------------------------------------- #
# Base MineStyle
# ---------------------------------------------------------------------- #
class MineStyle(Style[MineParamsT, ResultT], Generic[MineParamsT, ResultT]):
    """
    Base class for all extraction styles in Fragua ETL.

    Standard pipeline provided by Style:
        validate_params -> _run -> validate_result -> postprocess
    """

    def mine(self, params: MineParamsT) -> ResultT:
        """
        Base mine method. Should be implemented by subclasses
        to call the appropriate registered function.
        """
        raise NotImplementedError

    def _run(self, params: MineParamsT) -> ResultT:
        """
        Executes the MineStyle extraction step.

        This method is called by Style.use().
        """
        logger.debug("Starting MineStyle '%s' extraction.", self.style_name)
        result = self.mine(params)
        logger.debug("MineStyle '%s' extraction completed.", self.style_name)
        return result


# ---------------------------------------------------------------------- #
# CSV Extraction
# ---------------------------------------------------------------------- #
@register_style(action, "csv")
class CSVMineStyle(MineStyle[CSVMineParamsT, pd.DataFrame]):
    """Extracts data from CSV files."""

    def mine(self, params: CSVMineParamsT) -> pd.DataFrame:
        func = get_function(action, "mine_csv")
        return func(params)


# ---------------------------------------------------------------------- #
# Excel Extraction
# ---------------------------------------------------------------------- #
@register_style(action, "excel")
class ExcelMineStyle(MineStyle[ExcelMineParamsT, pd.DataFrame]):
    """Extracts data from Excel files."""

    def mine(self, params: ExcelMineParamsT) -> pd.DataFrame:
        func = get_function(action, "mine_excel")
        return func(params)


# ---------------------------------------------------------------------- #
# SQL Extraction
# ---------------------------------------------------------------------- #
@register_style(action, "sql")
class SQLMineStyle(MineStyle[SQLMineParamsT, pd.DataFrame]):
    """Extracts data from SQL databases."""

    def mine(self, params: SQLMineParamsT) -> pd.DataFrame:
        func = get_function(action, "mine_sql")
        return func(params)


# ---------------------------------------------------------------------- #
# API Extraction
# ---------------------------------------------------------------------- #
@register_style(action, "mine_api")
class APIMineStyle(MineStyle[APIMineParamsT, pd.DataFrame]):
    """Extracts data from REST APIs."""

    def mine(self, params: APIMineParamsT) -> pd.DataFrame:
        func = get_function(action, "mine_api")
        return func(params)
