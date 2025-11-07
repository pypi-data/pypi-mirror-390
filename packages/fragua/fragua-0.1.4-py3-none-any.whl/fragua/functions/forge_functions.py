"""
Reusable Forge Functions.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from pandas.errors import UndefinedVariableError
from sklearn.preprocessing import MinMaxScaler

from fragua.functions.function_registry import register_function
from fragua.params.forge_params import (
    ForgeParams,
    MLForgeParams,
    ReportForgeParams,
    AnalysisForgeParams,
)
from fragua.utils.logger import get_logger

logger = get_logger(__name__)

action: str = "forge"


# ----------------------------- #
# --- Functions --- #
# ----------------------------- #
@register_function(action, "fill_missing")
def fill_missing(params: ForgeParams) -> ForgeParams:
    """
    Fill missing values in numeric and categorical columns.

    Args:
        params (ForgeParams): Parameters containing the DataFrame and strategy attributes.

    Returns:
        ForgeParams: Params object with updated data.
    """
    df = params.data.copy()
    numeric_fill = getattr(params, "numeric_fill", "mean")
    categorical_fill = getattr(params, "categorical_fill", "unknown")

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            fill_value = df[col].mean() if numeric_fill == "mean" else 0
            df[col] = df[col].fillna(fill_value)
        else:
            df[col] = df[col].fillna(categorical_fill)

    params.data = df
    logger.info("forge: Missing values filled.")
    return params


@register_function(action, "standardize")
def standardize(params: ForgeParams) -> ForgeParams:
    """
    Standardize string columns by trimming and lowering case.

    Args:
        params (ForgeParams): Parameters containing the DataFrame.

    Returns:
        ForgeParams: Params object with updated data.
    """
    df = params.data.copy()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip().str.lower()
    params.data = df
    logger.info("forge: String columns standardized.")
    return params


@register_function(action, "encode_categoricals")
def encode_categoricals(params: ForgeParams) -> ForgeParams:
    """
    Encode categorical columns into dummy variables.

    Args:
        params (ForgeParams): Parameters containing the DataFrame.

    Returns:
        ForgeParams: Params object with updated data.
    """
    df = params.data.copy()
    cat_cols = df.select_dtypes(include="object").columns
    if len(cat_cols) > 0:
        df = pd.get_dummies(df, columns=cat_cols)
        logger.info("forge: Encoded categoricals: %s", list(cat_cols))
    params.data = df
    return params


@register_function(action, "scale_numeric")
def scale_numeric(params: ForgeParams) -> ForgeParams:
    """
    Scale numeric columns using MinMaxScaler.

    Args:
        params (ForgeParams): Parameters containing the DataFrame.

    Returns:
        ForgeParams: Params object with updated data.
    """
    df = params.data.copy()
    num_cols = df.select_dtypes(include="number").columns
    if len(num_cols) > 0:
        scaler = MinMaxScaler()
        df[num_cols] = scaler.fit_transform(df[num_cols])
        logger.info("forge: Scaled numeric columns: %s", list(num_cols))
    params.data = df
    return params


@register_function(action, "treat_outliers")
def treat_outliers(params: ForgeParams) -> ForgeParams:
    """
    Cap outliers in numeric columns using the IQR method.

    Args:
        params (ForgeParams): Parameters containing the DataFrame and outlier threshold.

    Returns:
        ForgeParams: Params object with updated data.
    """
    df = params.data.copy()
    factor = getattr(params, "outlier_threshold", 1.5) or 1.5
    num_cols = df.select_dtypes(include="number").columns

    for col in num_cols:
        Q1, Q3 = df[col].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        df[col] = np.clip(df[col], Q1 - factor * IQR, Q3 + factor * IQR)

    params.data = df
    logger.info("forge: Outliers treated with factor %.2f", factor)
    return params


@register_function(action, "add_derived_columns")
def add_derived_columns(params: ForgeParams) -> ForgeParams:
    """
    Add derived or computed columns to the DataFrame.

    Args:
        params (ForgeParams): Parameters containing the DataFrame and derived column definitions.

    Returns:
        ForgeParams: Params object with updated data.
    """
    df = params.data.copy()
    derived = getattr(params, "derived_columns", None)

    if derived:
        for new_col, expr in derived.items():
            try:
                df[new_col] = df.eval(expr)
                logger.debug(
                    "forge: Derived column '%s' created from '%s'.", new_col, expr
                )
            except (UndefinedVariableError, SyntaxError, TypeError, ValueError) as e:
                logger.warning("forge: Could not compute '%s': %s", new_col, e)
    elif {"quantity", "price"}.issubset(df.columns):
        df["total"] = df["quantity"] * df["price"]
        logger.debug("forge: Default derived column 'total' added.")

    params.data = df
    return params


@register_function(action, "format_numeric")
def format_numeric(params: ForgeParams) -> ForgeParams:
    """
    Format numeric columns by rounding to a given precision.

    Args:
        params ForgeParams): Parameters containing the DataFrame and rounding precision.

    Returns:
        ForgeParams: Params object with updated data.
    """
    df = params.data.copy()
    precision = getattr(params, "rounding_precision", 2) or 2
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].round(precision)

    params.data = df
    logger.info("forge: Numeric columns formatted with precision %d", precision)
    return params


@register_function(action, "group_and_aggregate")
def group_and_aggregate(params: ForgeParams) -> ForgeParams:
    """
    Group and aggregate data based on provided columns and aggregation functions.

    Args:
        params (ForgeParams): Parameters containing DataFrame, groupby_cols, and agg_functions.

    Returns:
        ForgeParams: Params object with grouped and aggregated data.
    """
    df = params.data.copy()
    groupby_cols = getattr(params, "groupby_cols", []) or []
    agg_functions = getattr(params, "agg_functions", {}) or {}

    if groupby_cols:
        if agg_functions:
            df = df.groupby(groupby_cols).agg(agg_functions).reset_index()
            logger.info("forge: Grouped by %s with custom aggregations.", groupby_cols)
        else:
            df = df.groupby(groupby_cols).agg("sum").reset_index()
            logger.info(
                "forge: Grouped by %s using default sum aggregation.", groupby_cols
            )

    params.data = df
    return params


@register_function(action, "sort_dataframe")
def sort_dataframe(params: ForgeParams) -> ForgeParams:
    """
    Sort DataFrame by specified columns.

    Args:
        params (ForgeParams): Parameters containing DataFrame and sort_by attribute.

    Returns:
        ForgeParams: Params object with sorted data.
    """
    df = params.data.copy()
    sort_by = getattr(params, "sort_by", []) or []

    if sort_by:
        df = df.sort_values(by=sort_by)
        logger.info("forge: Sorted DataFrame by %s.", sort_by)

    params.data = df
    return params


# ----------------------------- #
# --- MLForge Pipeline --- #
# ----------------------------- #
@register_function("forge", "forge_ml")
def forge_ml(params: MLForgeParams) -> pd.DataFrame:
    """
    Full MLForge pipeline using registered functions:
    fill_missing, standardize, encode_categoricals, treat_outliers, scale_numeric.

    Args:
        params (MLForgeParams): Parameters including data and preprocessing options.

    Returns:
        pd.DataFrame: Transformed DataFrame for ML.
    """
    for func in [
        fill_missing,
        standardize,
        encode_categoricals,
        treat_outliers,
        scale_numeric,
    ]:
        params = func(params)
    return params.data


# ----------------------------- #
# --- ReportForge Pipeline --- #
# ----------------------------- #
@register_function("forge", "forge_report")
def forge_report(params: ReportForgeParams) -> pd.DataFrame:
    """
    Full ReportForge pipeline using registered functions:
    fill_missing, standardize, add_derived_columns, and formatting.
    """
    for func in [
        fill_missing,
        standardize,
        add_derived_columns,
        format_numeric,
    ]:
        params = func(params)
    return params.data


# ----------------------------- #
# --- AnalysisForge Pipeline --- #
# ----------------------------- #
@register_function("forge", "forge_analysis")
def forge_analysis(params: AnalysisForgeParams) -> pd.DataFrame:
    """
    Full AnalysisForge pipeline using registered functions:
    fill_missing, standardize, group/aggregate, sort.
    """
    for func in [
        fill_missing,
        standardize,
        group_and_aggregate,
        sort_dataframe,
    ]:
        params = func(params)
    return params.data
