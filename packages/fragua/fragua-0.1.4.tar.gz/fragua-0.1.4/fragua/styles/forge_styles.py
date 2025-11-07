"""
Forge style types for various data transformation scenarios.
"""

from abc import abstractmethod
from typing import Generic

from pandas.api.types import is_numeric_dtype
import pandas as pd

from fragua.functions.function_registry import get_function
from fragua.styles.style import Style, ResultT, register_style
from fragua.utils.logger import get_logger
from fragua.params.forge_params import (
    ForgeParamsT,
    MLForgeParamsT,
    ReportForgeParamsT,
    AnalysisForgeParamsT,
)

logger = get_logger(__name__)

action: str = "forge"


# ---------------------------------------------------------------------- #
# Base ForgeStyle
# ---------------------------------------------------------------------- #
class ForgeStyle(Style[ForgeParamsT, ResultT], Generic[ForgeParamsT, ResultT]):
    """
    Base class for ForgeStyles.

    Standard pipeline provided by Style:
        validate_params -> _run -> validate_result -> postprocess
    """

    # ---------------------------------------------------------------------- #
    # Abstract forge method (subclasses implement this)
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def forge(self, params: ForgeParamsT) -> ResultT:
        """
        Transform the input data according to params.
        Must be implemented by subclasses.
        """
        raise NotImplementedError

    # ---------------------------------------------------------------------- #
    # Internal _run implementation for Style
    # ---------------------------------------------------------------------- #
    def _run(self, params: ForgeParamsT) -> ResultT:
        """
        Executes the ForgeStyle transformation step.

        This method is called by Style.use().
        """
        logger.debug("Starting ForgeStyle '%s' transformation.", self.style_name)
        result = self.forge(params)
        logger.debug("ForgeStyle '%s' transformation completed.", self.style_name)
        return result

    # ---------------------------------------------------------------------- #
    # Utilities for DataFrames
    # ---------------------------------------------------------------------- #
    def fill_missing(
        self,
        df: pd.DataFrame,
        numeric_fill: str = "mean",
        categorical_fill: str = "unknown",
    ) -> None:
        """Fill missing values in DataFrame."""
        for col in df.columns:
            if is_numeric_dtype(df[col]):
                fill_value = df[col].mean() if numeric_fill == "mean" else 0
                df[col] = df[col].fillna(fill_value)
            else:
                df[col] = df[col].fillna(categorical_fill)
        logger.info("%s: Missing values filled.", self.style_name)

    def standardize(self, df: pd.DataFrame) -> None:
        """Standardize string columns (strip spaces and lowercase)."""
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        logger.info("%s: String columns standardized.", self.style_name)


# ---------------- MLForge ----------------
@register_style(action, "ml")
class MLForgeStyle(ForgeStyle[MLForgeParamsT, pd.DataFrame]):
    """Forge style for machine learning preprocessing."""

    def forge(self, params: MLForgeParamsT) -> pd.DataFrame:
        forge_func = get_function(action, "forge_ml")
        return forge_func(params)


# ---------------- ReportForge ----------------
@register_style(action, "report")
class ReportForgeStyle(ForgeStyle[ReportForgeParamsT, pd.DataFrame]):
    """Forge style for reporting transformations."""

    def forge(self, params: ReportForgeParamsT) -> pd.DataFrame:
        forge_func = get_function(action, "forge_report")
        return forge_func(params)


# ---------------- AnalysisForge ----------------
@register_style(action, "analysis")
class AnalysisForgeStyle(ForgeStyle[AnalysisForgeParamsT, pd.DataFrame]):
    """Forge style for data analysis transformations."""

    def forge(self, params: AnalysisForgeParamsT) -> pd.DataFrame:
        forge_func = get_function(action, "forge_analysis")
        return forge_func(params)
