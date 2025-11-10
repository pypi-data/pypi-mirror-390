"""
Odoo Configuration for MCP server integration
"""

import os
import re
from typing import Any

from loguru import logger


class Config:
    """
    Odoo client configuration
    """

    url: str
    db: str
    username: str
    password: str
    timeout: int
    verify_ssl: bool

    def __init__(self) -> None:
        """
        Initialize the Config object and load configuration
        """
        self.__dict__.update(self.load_config())
        self.url = self._prepare_url(self.url)

        logger.info("🔧 Odoo client configuration:")
        logger.info(f"  URL: {self.url}")
        logger.info(f"  Database: {self.db}")
        logger.info(f"  Username: {self.username}")
        logger.info(f"  Timeout: {self.timeout}s")
        logger.info(f"  Verify SSL: {self.verify_ssl}")

    def load_config(self) -> dict[str, Any]:
        """
        Load Odoo configuration from environment variables or config file

        Raises:
            OSError: If required environment variables are missing
        Returns:
            dict: Configuration parameters for Odoo client
        """

        self._validate_config()
        return {
            "url": os.environ["ODOO_URL"],
            "db": os.environ["ODOO_DB"],
            "username": os.environ["ODOO_USERNAME"],
            "password": os.environ["ODOO_PASSWORD"],
            "timeout": int(os.environ.get("ODOO_TIMEOUT", "30")),
            "verify_ssl": os.environ.get("ODOO_VERIFY_SSL", "1").lower()
            in ("1", "true", "yes"),
        }

    def _validate_config(self) -> None:
        """
        Validate the loaded configuration parameters
        Raises:
            ValueError: If any required parameter is missing or invalid
        """
        required_env = {"ODOO_URL", "ODOO_DB", "ODOO_USERNAME", "ODOO_PASSWORD"}
        for var in required_env:
            if var not in os.environ:
                raise OSError(f"Missing required environment variable: {var}")
        if "ODOO_TIMEOUT" in os.environ:
            try:
                int(os.environ["ODOO_TIMEOUT"])
            except ValueError:
                raise ValueError("ODOO_TIMEOUT must be an integer") from None
        if "ODOO_VERIFY_SSL" in os.environ and os.environ[
            "ODOO_VERIFY_SSL"
        ].lower() not in (
            "1",
            "true",
            "yes",
            "0",
            "false",
            "no",
        ):
            raise ValueError("ODOO_VERIFY_SSL must be 1, true, yes, 0, false, or no")

    def _prepare_url(self, url: str) -> str:
        """
        Prepare the URL by ensuring it has a protocol and no trailing slash

        Args:
            url: The URL to prepare

        Returns:
            str: The prepared URL
        """
        if not re.match(r"^https?://", url):
            url = f"http://{url}"
        return url.rstrip("/")
