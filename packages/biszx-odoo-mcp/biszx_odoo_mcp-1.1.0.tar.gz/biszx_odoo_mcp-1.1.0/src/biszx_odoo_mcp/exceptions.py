"""
Custom exception classes for Odoo MCP Server.

This module defines a comprehensive hierarchy of custom exceptions for better
error handling and debugging in the Odoo MCP Server application.

Exception Hierarchy:
===================

OdooMCPError (Base)
├── OdooConnectionError
│   ├── ConnectionTimeoutError
│   ├── AuthenticationError
│   └── SSLVerificationError
├── ModelError
│   └── ModelNotFoundError
├── ServerError
│   ├── OdooRPCError
│   └── InternalServerError
└── MCPError
    ├── ResourceError
    └── ToolError
"""

from typing import Any, Optional

from odoorpc.error import RPCError


class OdooMCPError(Exception):
    """
    Base exception class for all Odoo MCP Server errors.

    This serves as the base class for all custom exceptions in the application,
    providing a consistent interface for error handling and logging.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code for programmatic handling
        details: Additional context information about the error
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional context information
            original_error: The original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        self.original_error = original_error

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the exception to a dictionary for JSON serialization.

        Returns:
            Dictionary representation of the exception
        """
        result = {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }

        if self.original_error:
            result["original_error"] = {
                "type": self.original_error.__class__.__name__,
                "message": str(self.original_error),
            }

        return result

    def __str__(self) -> str:
        """String representation of the exception."""
        return f"{self.error_code}: {self.message}"


# =============================================================================
# CONNECTION RELATED ERRORS
# =============================================================================


class OdooConnectionError(OdooMCPError):
    """Base class for Odoo connection-related errors."""


class ConnectionTimeoutError(OdooConnectionError):
    """Raised when a connection to Odoo times out."""

    def __init__(
        self,
        message: str = "Connection to Odoo server timed out",
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.get("details", {})
        if timeout is not None:
            details["timeout_seconds"] = timeout
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class AuthenticationError(OdooConnectionError):
    """Raised when authentication with Odoo fails."""

    def __init__(
        self,
        message: str = "Authentication with Odoo failed",
        username: Optional[str] = None,
        database: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.get("details", {})
        if username:
            details["username"] = username
        if database:
            details["database"] = database
        kwargs["details"] = details
        super().__init__(message, **kwargs)


# =============================================================================
# MODEL RELATED ERRORS
# =============================================================================


class ModelError(OdooMCPError):
    """Base class for model-related errors."""


class ModelNotFoundError(ModelError):
    """Raised when a requested model doesn't exist."""

    def __init__(
        self, model_name: str, message: Optional[str] = None, **kwargs: Any
    ) -> None:
        message = message or f"Model '{model_name}' not found"
        details = kwargs.get("details", {})
        details["model_name"] = model_name
        kwargs["details"] = details
        super().__init__(message, **kwargs)


# =============================================================================
# SERVER RELATED ERRORS
# =============================================================================


class ServerError(OdooMCPError):
    """Base class for server-related errors."""


class OdooRPCError(ServerError):
    """Raised when an RPC call to Odoo fails."""

    def __init__(
        self,
        error: RPCError,
        method: str,
        message: str = "RPC call failed",
        **kwargs: Any,
    ) -> None:
        kwargs["details"] = {
            "method": method,
            "odoo_error": error.info,
        }
        super().__init__(message, **kwargs)


class InternalServerError(ServerError):
    """Raised when an internal server error occurs."""


# =============================================================================
# MCP RELATED ERRORS
# =============================================================================


class MCPError(OdooMCPError):
    """Base class for MCP protocol-related errors."""


class ResourceError(MCPError):
    """Raised when an MCP resource operation fails."""

    def __init__(
        self,
        message: str = "Resource operation failed",
        resource_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.get("details", {})
        if resource_name:
            details["resource_name"] = resource_name
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class ToolError(MCPError):
    """Raised when an MCP tool operation fails."""

    def __init__(
        self,
        message: str = "Tool operation failed",
        tool_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.get("details", {})
        if tool_name:
            details["tool_name"] = tool_name
        kwargs["details"] = details
        super().__init__(message, **kwargs)
