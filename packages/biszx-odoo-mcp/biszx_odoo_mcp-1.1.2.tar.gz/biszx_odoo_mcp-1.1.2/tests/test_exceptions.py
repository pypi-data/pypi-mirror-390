"""
Tests for biszx_odoo_mcp.exceptions module
"""

from biszx_odoo_mcp.exceptions import (
    AuthenticationError,
    ConnectionTimeoutError,
    InternalServerError,
    MCPError,
    ModelError,
    ModelNotFoundError,
    OdooConnectionError,
    OdooMCPError,
    OdooRPCError,
    ResourceError,
    ServerError,
    ToolError,
)


class TestOdooMCPError:
    """Test cases for OdooMCPError base exception"""

    def test_basic_initialization(self):
        """Test basic exception initialization"""
        error = OdooMCPError("Test error")
        assert str(error) == "ODOOMCPERROR: Test error"
        assert error.message == "Test error"
        assert error.error_code == "ODOOMCPERROR"
        assert error.details == {}
        assert error.original_error is None

    def test_initialization_with_all_parameters(self):
        """Test exception initialization with all parameters"""
        original_error = ValueError("Original error")
        details = {"key": "value"}

        error = OdooMCPError(
            "Test error",
            error_code="CUSTOM_ERROR",
            details=details,
            original_error=original_error,
        )

        assert error.message == "Test error"
        assert error.error_code == "CUSTOM_ERROR"
        assert error.details == details
        assert error.original_error == original_error

    def test_to_dict_basic(self):
        """Test to_dict method with basic exception"""
        error = OdooMCPError("Test error")
        result = error.to_dict()

        expected = {
            "error_type": "OdooMCPError",
            "error_code": "ODOOMCPERROR",
            "message": "Test error",
            "details": {},
        }

        assert result == expected

    def test_to_dict_with_original_error(self):
        """Test to_dict method with original error"""
        original_error = ValueError("Original error")
        error = OdooMCPError("Test error", original_error=original_error)
        result = error.to_dict()

        assert "original_error" in result
        assert result["original_error"]["type"] == "ValueError"
        assert result["original_error"]["message"] == "Original error"

    def test_str_representation(self):
        """Test string representation of exception"""
        error = OdooMCPError("Test message", error_code="TEST_CODE")
        assert str(error) == "TEST_CODE: Test message"


class TestOdooConnectionError:
    """Test cases for OdooConnectionError base class"""

    def test_basic_initialization(self):
        """Test basic initialization"""
        error = OdooConnectionError("Connection error")
        assert error.message == "Connection error"
        assert error.error_code == "ODOOCONNECTIONERROR"


class TestConnectionTimeoutError:
    """Test cases for ConnectionTimeoutError"""

    def test_basic_initialization(self):
        """Test basic initialization with default message"""
        error = ConnectionTimeoutError()
        assert "Connection to Odoo server timed out" in error.message
        assert error.error_code == "CONNECTIONTIMEOUTERROR"

    def test_initialization_with_timeout(self):
        """Test initialization with timeout parameter"""
        error = ConnectionTimeoutError(timeout=60.0)
        assert error.details["timeout_seconds"] == 60.0

    def test_custom_message(self):
        """Test initialization with custom message"""
        error = ConnectionTimeoutError("Custom timeout message")
        assert error.message == "Custom timeout message"


class TestAuthenticationError:
    """Test cases for AuthenticationError"""

    def test_basic_initialization(self):
        """Test basic initialization with default message"""
        error = AuthenticationError()
        assert "Authentication with Odoo failed" in error.message
        assert error.error_code == "AUTHENTICATIONERROR"

    def test_initialization_with_credentials(self):
        """Test initialization with username and database"""
        error = AuthenticationError(username="testuser", database="testdb")
        assert error.details["username"] == "testuser"
        assert error.details["database"] == "testdb"

    def test_custom_message(self):
        """Test initialization with custom message"""
        error = AuthenticationError("Custom auth message")
        assert error.message == "Custom auth message"


class TestModelError:
    """Test cases for ModelError"""

    def test_basic_initialization(self):
        """Test basic initialization"""
        error = ModelError("Model error")
        assert error.message == "Model error"
        assert error.error_code == "MODELERROR"


class TestModelNotFoundError:
    """Test cases for ModelNotFoundError"""

    def test_basic_initialization(self):
        """Test basic initialization with model name"""
        error = ModelNotFoundError("res.partner")
        assert "Model 'res.partner' not found" in error.message
        assert error.details["model_name"] == "res.partner"

    def test_custom_message(self):
        """Test initialization with custom message"""
        error = ModelNotFoundError("res.partner", "Custom not found message")
        assert error.message == "Custom not found message"
        assert error.details["model_name"] == "res.partner"


class TestServerError:
    """Test cases for ServerError"""

    def test_basic_initialization(self):
        """Test basic initialization"""
        error = ServerError("Server error")
        assert error.message == "Server error"
        assert error.error_code == "SERVERERROR"


class TestOdooRPCError:
    """Test cases for OdooRPCError"""

    def test_initialization_with_rpc_error(self, mock_rpc_error):
        """Test initialization with RPCError"""
        error = OdooRPCError(mock_rpc_error, "test_method")
        assert error.message == "RPC call failed"
        assert error.details["method"] == "test_method"
        assert error.details["odoo_error"] == mock_rpc_error.info

    def test_custom_message(self, mock_rpc_error):
        """Test initialization with custom message"""
        error = OdooRPCError(mock_rpc_error, "test_method", "Custom RPC error")
        assert error.message == "Custom RPC error"


class TestInternalServerError:
    """Test cases for InternalServerError"""

    def test_basic_initialization(self):
        """Test basic initialization"""
        error = InternalServerError("Internal error")
        assert error.message == "Internal error"
        assert error.error_code == "INTERNALSERVERERROR"


class TestMCPError:
    """Test cases for MCPError"""

    def test_basic_initialization(self):
        """Test basic initialization"""
        error = MCPError("MCP error")
        assert error.message == "MCP error"
        assert error.error_code == "MCPERROR"


class TestResourceError:
    """Test cases for ResourceError"""

    def test_basic_initialization(self):
        """Test basic initialization with default message"""
        error = ResourceError()
        assert "Resource operation failed" in error.message
        assert error.error_code == "RESOURCEERROR"

    def test_initialization_with_resource_name(self):
        """Test initialization with resource name"""
        error = ResourceError(resource_name="test_resource")
        assert error.details["resource_name"] == "test_resource"

    def test_custom_message(self):
        """Test initialization with custom message"""
        error = ResourceError("Custom resource error")
        assert error.message == "Custom resource error"


class TestToolError:
    """Test cases for ToolError"""

    def test_basic_initialization(self):
        """Test basic initialization with default message"""
        error = ToolError()
        assert "Tool operation failed" in error.message
        assert error.error_code == "TOOLERROR"

    def test_initialization_with_tool_name(self):
        """Test initialization with tool name"""
        error = ToolError(tool_name="test_tool")
        assert error.details["tool_name"] == "test_tool"

    def test_custom_message(self):
        """Test initialization with custom message"""
        error = ToolError("Custom tool error")
        assert error.message == "Custom tool error"


class TestExceptionHierarchy:
    """Test exception inheritance hierarchy"""

    def test_inheritance_chain(self):
        """Test that all exceptions inherit from appropriate base classes"""
        # Connection errors
        assert issubclass(OdooConnectionError, OdooMCPError)
        assert issubclass(ConnectionTimeoutError, OdooConnectionError)
        assert issubclass(AuthenticationError, OdooConnectionError)

        # Model errors
        assert issubclass(ModelError, OdooMCPError)
        assert issubclass(ModelNotFoundError, ModelError)

        # Server errors
        assert issubclass(ServerError, OdooMCPError)
        assert issubclass(OdooRPCError, ServerError)
        assert issubclass(InternalServerError, ServerError)

        # MCP errors
        assert issubclass(MCPError, OdooMCPError)
        assert issubclass(ResourceError, MCPError)
        assert issubclass(ToolError, MCPError)

    def test_all_inherit_from_base(self):
        """Test that all custom exceptions inherit from OdooMCPError"""
        exceptions = [
            OdooConnectionError,
            ModelError,
            ModelNotFoundError,
            ServerError,
            OdooRPCError,
            InternalServerError,
            MCPError,
            ResourceError,
            ToolError,
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, OdooMCPError)
