"""
Reusable Delivery Functions.
"""

import os
from typing import Any
import pandas as pd
import requests
from sqlalchemy import create_engine

from fragua.functions.function_registry import register_function
from fragua.params.delivery_params import (
    ExcelDeliveryParams,
    SQLDeliveryParams,
    APIDeliveryParams,
)

action: str = "deliver"

# ----------------------------- #
# --- Excel Helpers --- #
# ----------------------------- #


@register_function(action, "validate_excel_params")
def validate_excel_params(params: ExcelDeliveryParams) -> None:
    """
    Validate Excel delivery parameters.

    Args:
        params (ExcelDeliveryParams): Parameters for Excel delivery.

    Raises:
        TypeError: If data is not a DataFrame.
        ValueError: If destination folder is missing.
    """
    if not isinstance(params.data, pd.DataFrame):
        raise TypeError("ExcelDeliveryStyle requires a pandas DataFrame")
    if not params.destination:
        raise ValueError("Destination folder is required")


@register_function(action, "build_excel_path")
def build_excel_path(params: ExcelDeliveryParams) -> str:
    """
    Build the full path for the Excel file, adding '.xlsx' if missing.

    Args:
        params (ExcelDeliveryParams): Parameters including destination and file_name.

    Returns:
        str: Full path to the Excel file.
    """
    os.makedirs(params.destination, exist_ok=True)

    _, ext = os.path.splitext(params.file_name)
    file_name = params.file_name if ext else f"{params.file_name}.xlsx"

    return os.path.join(params.destination, file_name)


@register_function(action, "convert_datetime_columns")
def convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert timezone-aware datetime columns to naive datetime.

    Args:
        df (pd.DataFrame): DataFrame to process.

    Returns:
        pd.DataFrame: DataFrame with naive datetime columns.
    """
    datetime_cols = df.select_dtypes(include=["datetimetz"]).columns
    if len(datetime_cols) > 0:
        df = df.copy()
        for col in datetime_cols:
            df[col] = df[col].dt.tz_convert(None)
    return df


@register_function(action, "write_excel")
def write_excel(df: pd.DataFrame, path: str, sheet_name: str, index: bool) -> None:
    """
    Write or append a DataFrame to an Excel file.

    Args:
        df (pd.DataFrame): DataFrame to write.
        path (str): Full path to Excel file.
        sheet_name (str): Sheet name to write to.
        index (bool): Whether to write the index.
    """
    if os.path.exists(path):
        with pd.ExcelWriter(
            path, mode="a", engine="openpyxl", if_sheet_exists="new"
        ) as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=index)
    else:
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=index)


@register_function(action, "delivery_excel")
def delivery_excel(params: ExcelDeliveryParams) -> pd.DataFrame:
    """
    Full Excel delivery pipeline.

    Args:
        params (ExcelDeliveryParams): Parameters for delivery.

    Returns:
        pd.DataFrame: Delivered DataFrame.
    """
    validate_excel_params(params)
    path = build_excel_path(params)
    df = convert_datetime_columns(params.data)
    write_excel(df, path, params.sheet_name or "Sheet1", params.index)
    return df


# ----------------------------- #
# --- SQL Helpers --- #
# ----------------------------- #


@register_function(action, "validate_sql_params")
def validate_sql_params(params: SQLDeliveryParams) -> None:
    """
    Validate SQL delivery parameters.

    Args:
        params (SQLDeliveryParams): Parameters for SQL delivery.

    Raises:
        TypeError: If data is not a DataFrame.
        ValueError: If destination or table_name is missing.
    """
    if not isinstance(params.data, pd.DataFrame):
        raise TypeError("SQLDeliveryStyle requires a pandas DataFrame")
    if not params.destination:
        raise ValueError("destination (connection_string) is required")
    if not params.table_name:
        raise ValueError("table_name is required")


@register_function(action, "write_sql")
def write_sql(params: SQLDeliveryParams) -> pd.DataFrame:
    """
    Write a DataFrame to a SQL table.

    Args:
        params (SQLDeliveryParams): Parameters including data and table information.

    Returns:
        pd.DataFrame: Delivered DataFrame.
    """
    engine = create_engine(params.destination)
    try:
        params.data.to_sql(
            name=params.table_name,
            con=engine,
            if_exists=params.if_exists,
            index=params.index,
            chunksize=params.chunksize,
        )
    finally:
        engine.dispose()
    return params.data


@register_function(action, "delivery_sql")
def delivery_sql(params: SQLDeliveryParams) -> pd.DataFrame:
    """
    Full SQL delivery pipeline.

    Args:
        params (SQLDeliveryParams): Parameters for delivery.

    Returns:
        pd.DataFrame: Delivered DataFrame.
    """
    validate_sql_params(params)
    return write_sql(params)


# ----------------------------- #
# --- API Helpers --- #
# ----------------------------- #


@register_function(action, "validate_api_params")
def validate_api_params(params: APIDeliveryParams) -> None:
    """
    Validate API delivery parameters.

    Args:
        params (APIDeliveryParams): Parameters for API delivery.

    Raises:
        ValueError: If data or endpoint is missing.
    """
    if params.data is None:
        raise ValueError("data is required")
    if not params.endpoint:
        raise ValueError("endpoint is required")


@register_function(action, "send_api_request")
def send_api_request(params: APIDeliveryParams) -> Any:
    """
    Send a REST API request with the provided data.

    Args:
        params (APIDeliveryParams): Parameters including endpoint, method, headers, and data.

    Returns:
        Any: The delivered data.
    """
    headers: dict[Any, Any] = params.headers or {}
    if params.auth:
        token = params.auth.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"

    response = requests.request(
        method=params.method,
        url=params.endpoint,
        json=params.data,
        headers=headers,
        timeout=params.timeout,
    )
    response.raise_for_status()
    return params.data


@register_function(action, "delivery_api")
def delivery_api(params: APIDeliveryParams) -> Any:
    """
    Full API delivery pipeline.

    Args:
        params (APIDeliveryParams): Parameters for delivery.

    Returns:
        Any: Delivered data.
    """
    validate_api_params(params)
    return send_api_request(params)
