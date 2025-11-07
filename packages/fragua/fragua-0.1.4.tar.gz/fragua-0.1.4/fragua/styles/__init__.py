"""Fragua Styles package."""

# ------------------- Base Style ------------------- #
from .style import Style, STYLE_REGISTRY, register_style, get_style, list_styles

# ------------------- Delivery Style Types ------------------- #
from .delivery_styles import (
    DeliveryStyle,
    SQLDeliveryStyle,
    APIDeliveryStyle,
    ExcelDeliveryStyle,
)

# ------------------- Mine Styles ------------------- #
from .mine_styles import (
    MineStyle,
    CSVMineStyle,
    ExcelMineStyle,
    SQLMineStyle,
    APIMineStyle,
)

# ------------------- Forge Styles ------------------- #
from .forge_styles import (
    ForgeStyle,
    MLForgeStyle,
    ReportForgeStyle,
    AnalysisForgeStyle,
)


# ------------------- __all__ ------------------- #
__all__ = [
    # Base Styles
    "Style",
    "DeliveryStyle",
    "MineStyle",
    "ForgeStyle",
    # Mine Styles
    "CSVMineStyle",
    "ExcelMineStyle",
    "SQLMineStyle",
    "APIMineStyle",
    # Forge Styles
    "MLForgeStyle",
    "ReportForgeStyle",
    "AnalysisForgeStyle",
    # Delivery Styles
    "SQLDeliveryStyle",
    "APIDeliveryStyle",
    "ExcelDeliveryStyle",
    # Styles Registry Functions
    "STYLE_REGISTRY",
    "register_style",
    "get_style",
    "list_styles",
]
