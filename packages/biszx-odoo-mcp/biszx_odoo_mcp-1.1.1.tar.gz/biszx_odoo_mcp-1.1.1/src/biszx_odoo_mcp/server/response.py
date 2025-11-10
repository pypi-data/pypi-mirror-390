"""
Odoo MCP Server Response
"""

import json
from typing import Any, Optional


class Response:
    """
    Standard response wrapper for OdooClient methods.
    """

    def __init__(
        self,
        data: Optional[Any] = None,
        error: Optional[dict[str, Any]] = None,
    ) -> None:
        self.data = data
        self.error = error
        self.success = error is None

    def to_dict(self) -> dict[str, Any]:
        """
        Return the response as a dictionary with either 'data' or 'error' key.
        """
        if self.error is not None:
            return {"success": self.success, "error": self.error}
        return {"success": self.success, "data": self.data}

    def to_json_string(self, indent: int = 2) -> str:
        """
        Return the response as a JSON string.
        """

        return json.dumps(self.to_dict(), indent=indent)
