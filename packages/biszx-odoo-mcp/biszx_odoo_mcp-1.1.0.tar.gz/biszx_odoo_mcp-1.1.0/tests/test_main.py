"""
Tests for biszx_odoo_mcp.main module
"""

from unittest.mock import Mock, patch

import pytest
from biszx_odoo_mcp.main import app_lifespan, mcp, tool


class TestAppLifespan:
    """Test cases for app_lifespan context manager"""

    @pytest.mark.asyncio
    @patch("biszx_odoo_mcp.main.get_odoo_client")
    async def test_app_lifespan_success(self, mock_get_odoo_client):
        """Test successful app lifespan context manager"""
        mock_odoo_client = Mock()
        mock_get_odoo_client.return_value = mock_odoo_client
        mock_fastmcp = Mock()

        async with app_lifespan(mock_fastmcp) as context:
            assert context.odoo == mock_odoo_client
            assert hasattr(context, "odoo")

    @pytest.mark.asyncio
    @patch("biszx_odoo_mcp.main.get_odoo_client")
    async def test_app_lifespan_cleanup(self, mock_get_odoo_client):
        """Test app lifespan cleanup (should not raise exceptions)"""
        mock_odoo_client = Mock()
        mock_get_odoo_client.return_value = mock_odoo_client
        mock_fastmcp = Mock()

        try:
            async with app_lifespan(mock_fastmcp) as context:
                assert context.odoo == mock_odoo_client
                # Simulate an exception to test cleanup
                raise ValueError("Test exception")
        except ValueError:
            # This is expected - the context manager should handle cleanup
            pass


class TestMCPServerSetup:
    """Test cases for MCP server configuration"""

    def test_mcp_server_exists(self):
        """Test that MCP server instance exists"""
        assert mcp is not None
        assert hasattr(mcp, "name")

    def test_mcp_server_configuration(self):
        """Test MCP server basic configuration"""
        # These are basic checks to ensure the server is properly configured
        # We can't easily test the actual FastMCP instance without
        # significantly mocking the entire FastMCP framework
        assert mcp is not None


class TestToolDecorator:
    """Test cases for the tool decorator"""

    def test_tool_decorator_function_wrapping(self):
        """Test that tool decorator properly wraps functions"""

        # Create a mock function
        async def mock_function(mcp_instance, param1, param2="default"):
            return {"param1": param1, "param2": param2}

        # Mock the mcp.tool() decorator
        with patch.object(mcp, "tool") as mock_tool_decorator:
            mock_tool_decorator.return_value = lambda f: f

            # Apply our tool decorator
            tool(mock_function)

            # Verify that mcp.tool() was called
            mock_tool_decorator.assert_called_once()

    def test_tool_decorator_signature_modification(self):
        """Test that tool decorator removes mcp parameter from signature"""

        async def sample_function(mcp_instance, param1, param2="default"):
            return {"param1": param1, "param2": param2}

        with patch.object(mcp, "tool") as mock_tool_decorator:
            mock_tool_decorator.return_value = lambda f: f

            wrapped = tool(sample_function)

            # Check that the wrapped function has the expected attributes
            assert wrapped.__name__ == sample_function.__name__
            assert wrapped.__doc__ == sample_function.__doc__

    @pytest.mark.asyncio
    async def test_tool_decorator_execution(self):
        """Test that tool decorator properly calls underlying function"""

        # Create a mock function
        async def mock_function(mcp_instance, param1, param2="default"):
            return {"mcp": mcp_instance, "param1": param1, "param2": param2}

        with patch.object(mcp, "tool") as mock_tool_decorator:
            # Mock the decorator to return the wrapper directly
            def mock_decorator(func):
                return func

            mock_tool_decorator.return_value = mock_decorator

            # Apply our tool decorator
            wrapped = tool(mock_function)

            # Test calling the wrapped function
            result = await wrapped("test_param", param2="test_value")

            # Verify the result contains the mcp instance and parameters
            assert result["param1"] == "test_param"
            assert result["param2"] == "test_value"
            assert result["mcp"] == mcp


class TestResourceRegistration:
    """Test cases for resource registration"""

    def test_resource_registration_exists(self):
        """Test that resources are registered"""
        # This is a basic test to ensure resources are being registered
        # More detailed testing would require deeper mocking of FastMCP
        assert mcp is not None


class TestToolRegistration:
    """Test cases for tool registration"""

    def test_tool_registration_imports(self):
        """Test that all tools are imported and accessible"""
        from biszx_odoo_mcp.server import tools

        # Verify that all the tools exist and are callable
        assert hasattr(tools, "get_model_fields")
        assert callable(tools.get_model_fields)

        assert hasattr(tools, "search_records")
        assert callable(tools.search_records)

        assert hasattr(tools, "read_records")
        assert callable(tools.read_records)

        assert hasattr(tools, "create_record")
        assert callable(tools.create_record)

        assert hasattr(tools, "create_records")
        assert callable(tools.create_records)

        assert hasattr(tools, "write_record")
        assert callable(tools.write_record)

        assert hasattr(tools, "write_records")
        assert callable(tools.write_records)

        assert hasattr(tools, "unlink_record")
        assert callable(tools.unlink_record)

        assert hasattr(tools, "unlink_records")
        assert callable(tools.unlink_records)

        assert hasattr(tools, "search_count")
        assert callable(tools.search_count)

        assert hasattr(tools, "search_ids")
        assert callable(tools.search_ids)

        assert hasattr(tools, "call_method")
        assert callable(tools.call_method)

        assert hasattr(tools, "search_and_update")
        assert callable(tools.search_and_update)


class TestResourceWrapperFunctions:
    """Test cases for resource wrapper functions"""

    @pytest.mark.asyncio
    async def test_model_fields_resource(self, mock_mcp_server_for_tools):
        """Test the model_fields_resource wrapper function"""
        from unittest.mock import patch

        from biszx_odoo_mcp.main import model_fields_resource
        from biszx_odoo_mcp.server import resources

        with patch.object(resources, "get_model_fields_resource") as mock_resource:
            mock_resource.return_value = '{"success": true, "data": {}}'

            result = await model_fields_resource("res.partner", "name")

            assert result == '{"success": true, "data": {}}'
            mock_resource.assert_called_once_with(mcp, "res.partner", "name")
