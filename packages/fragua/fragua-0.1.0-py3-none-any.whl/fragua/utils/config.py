"""
Configuration management for Fragua ETL agents.

Provides centralized configuration for paths, data sources, and destinations.
"""


class Config:
    """
    Configuration class to store ETL settings.
    """

    def __init__(self) -> None:
        """
        Initialize default configuration values.
        """
        # Example default settings
        self.default_storage_path = "./data"
        self.default_logging_name = "FraguaLogger"
        self.default_format = "json"

    def set_storage_path(self, path: str) -> None:
        """
        Set the default storage path for all agents.

        Args:
            path (str): Path to storage directory.
        """
        self.default_storage_path = path

    def set_logging_name(self, name: str) -> None:
        """
        Set the default logging name.

        Args:
            name (str): Logger name.
        """
        self.default_logging_name = name

    def set_format(self, fmt: str) -> None:
        """
        Set the default data format.

        Args:
            fmt (str): Data format, e.g., "json", "csv".
        """
        self.default_format = fmt
