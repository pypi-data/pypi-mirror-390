"""
Tests for biszx_odoo_mcp.server.resources module
"""

import json

import pytest
from biszx_odoo_mcp.exceptions import MCPError, OdooMCPError, ResourceError
from biszx_odoo_mcp.server import resources


def get_mock_odoo(mock_mcp_server_for_tools):
    """Helper function to get mock odoo client from mock MCP server"""
    request_context = mock_mcp_server_for_tools.get_context.return_value.request_context
    return request_context.lifespan_context.odoo


class TestSearchModelsResource:
    """Test cases for search_models_resource"""

    @pytest.mark.asyncio
    async def test_search_models_resource_success(
        self, mock_mcp_server_for_tools, sample_model_data
    ):
        """Test successful model search resource"""
        # Setup mock
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.search_models.return_value = sample_model_data

        result = await resources.search_models_resource(
            mock_mcp_server_for_tools, "partner"
        )

        # Parse JSON result
        parsed = json.loads(result)

        # Verify result structure
        assert "success" in parsed
        assert "data" in parsed
        assert parsed["success"] is True
        assert parsed["data"] == sample_model_data

    @pytest.mark.asyncio
    async def test_search_models_resource_odoo_error(self, mock_mcp_server_for_tools):
        """Test model search resource with Odoo error"""
        # Setup mock to raise OdooMCPError
        error = OdooMCPError("Test error")
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.search_models.side_effect = error

        result = await resources.search_models_resource(
            mock_mcp_server_for_tools, "partner"
        )

        # Parse JSON result
        parsed = json.loads(result)

        # Verify error response
        assert parsed["success"] is False
        assert "error" in parsed

    @pytest.mark.asyncio
    async def test_search_models_resource_unexpected_error(
        self, mock_mcp_server_for_tools
    ):
        """Test model search resource with unexpected error"""
        # Setup mock to raise generic exception
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.search_models.side_effect = ValueError("Unexpected error")

        result = await resources.search_models_resource(
            mock_mcp_server_for_tools, "partner"
        )

        # Parse JSON result
        parsed = json.loads(result)

        # Verify error response
        assert parsed["success"] is False
        assert "error" in parsed


class TestGetModelFieldsResource:
    """Test cases for get_model_fields_resource"""

    @pytest.mark.asyncio
    async def test_get_model_fields_resource_success(
        self, mock_mcp_server_for_tools, sample_field_data
    ):
        """Test successful field retrieval resource"""
        # Setup mock
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.get_model_fields.return_value = sample_field_data

        result = await resources.get_model_fields_resource(
            mock_mcp_server_for_tools, "res.partner", "name"
        )

        # Parse JSON result
        parsed = json.loads(result)

        # Verify result
        assert parsed["success"] is True
        assert parsed["data"] == sample_field_data

    @pytest.mark.asyncio
    async def test_get_model_fields_resource_error(self, mock_mcp_server_for_tools):
        """Test field retrieval resource with error"""
        error = OdooMCPError("Field error")
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.get_model_fields.side_effect = error

        result = await resources.get_model_fields_resource(
            mock_mcp_server_for_tools, "res.partner", "name"
        )

        # Parse JSON result
        parsed = json.loads(result)

        # Verify error response
        assert parsed["success"] is False
        assert "error" in parsed

    @pytest.mark.asyncio
    async def test_get_model_fields_resource_unexpected_error(
        self, mock_mcp_server_for_tools
    ):
        """Test field retrieval resource with unexpected error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.get_model_fields.side_effect = RuntimeError("Unexpected error")

        result = await resources.get_model_fields_resource(
            mock_mcp_server_for_tools, "res.partner", "name"
        )

        # Parse JSON result
        parsed = json.loads(result)

        # Verify error response
        assert parsed["success"] is False
        assert "error" in parsed
        assert "ResourceError" in parsed["error"]["error_type"]


class TestGetModelInfoResource:
    """Test cases for get_model_info_resource"""

    @pytest.mark.asyncio
    async def test_get_model_info_resource_success(self, mock_mcp_server_for_tools):
        """Test successful model info resource"""
        model_info = {"model": "res.partner", "name": "Contact"}

        # Setup mock
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.get_model_info.return_value = model_info

        result = await resources.get_model_info_resource(
            mock_mcp_server_for_tools, "res.partner"
        )

        # Parse JSON result
        parsed = json.loads(result)

        # Verify result
        assert parsed["success"] is True
        assert parsed["data"] == model_info

    @pytest.mark.asyncio
    async def test_get_model_info_resource_error(self, mock_mcp_server_for_tools):
        """Test model info resource with error"""
        error = OdooMCPError("Model not found")
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.get_model_info.side_effect = error

        result = await resources.get_model_info_resource(
            mock_mcp_server_for_tools, "nonexistent.model"
        )

        # Parse JSON result
        parsed = json.loads(result)

        # Verify error response
        assert parsed["success"] is False
        assert "error" in parsed

    @pytest.mark.asyncio
    async def test_get_model_info_resource_unexpected_error(
        self, mock_mcp_server_for_tools
    ):
        """Test model info resource with unexpected error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.get_model_info.side_effect = RuntimeError("Unexpected error")

        result = await resources.get_model_info_resource(
            mock_mcp_server_for_tools, "res.partner"
        )

        # Parse JSON result
        parsed = json.loads(result)

        # Verify error response
        assert parsed["success"] is False
        assert "error" in parsed
        assert "Unexpected error getting model info" in parsed["error"]["message"]


class TestGetDomainHelpResource:
    """Test cases for get_domain_help_resource"""

    @pytest.mark.asyncio
    async def test_get_domain_help_resource(self):
        """Test domain help resource"""
        result = await resources.get_domain_help_resource()

        # Parse JSON result
        parsed = json.loads(result)

        # Verify result structure
        assert "success" in parsed
        assert "data" in parsed
        assert parsed["success"] is True

        # Verify help content
        data = parsed["data"]
        assert "odoo_domain_syntax" in data

        domain_help = data["odoo_domain_syntax"]
        assert "description" in domain_help
        assert "syntax" in domain_help
        assert "operators" in domain_help
        assert "logical_operators" in domain_help
        assert "examples" in domain_help

        # Verify some specific operators
        operators = domain_help["operators"]
        assert "=" in operators
        assert "!=" in operators
        assert "like" in operators
        assert "in" in operators

        # Verify logical operators
        logical_ops = domain_help["logical_operators"]
        assert "&" in logical_ops
        assert "|" in logical_ops
        assert "!" in logical_ops

        # Verify examples exist and are properly formatted
        examples = domain_help["examples"]
        assert isinstance(examples, list)
        assert len(examples) > 0

        for example in examples:
            assert "description" in example
            assert "domain" in example


class TestGetOperationsHelpResource:
    """Test cases for get_operations_help_resource"""

    @pytest.mark.asyncio
    async def test_get_operations_help_resource(self):
        """Test operations help resource"""
        result = await resources.get_operations_help_resource()

        # Parse JSON result
        parsed = json.loads(result)

        # Verify result structure
        assert "success" in parsed
        assert "data" in parsed
        assert parsed["success"] is True

        # Verify help content
        data = parsed["data"]
        assert "mcp_tools" in data
        assert "common_workflows" in data

        tools_help = data["mcp_tools"]
        assert "data_retrieval" in tools_help
        assert "data_modification" in tools_help
        assert "advanced" in tools_help

        # Verify data retrieval tools
        data_retrieval = tools_help["data_retrieval"]
        assert "get_model_fields" in data_retrieval
        assert "search_records" in data_retrieval
        assert "read_records" in data_retrieval
        assert "search_ids" in data_retrieval
        assert "search_count" in data_retrieval

        # Verify data modification tools
        data_modification = tools_help["data_modification"]
        assert "create_record" in data_modification
        assert "create_records" in data_modification
        assert "write_record" in data_modification
        assert "write_records" in data_modification
        assert "unlink_record" in data_modification
        assert "unlink_records" in data_modification

        # Verify advanced tools
        advanced = tools_help["advanced"]
        assert "call_method" in advanced
        assert "search_and_update" in advanced

        # Verify workflows
        workflows = data["common_workflows"]
        assert isinstance(workflows, list)
        assert len(workflows) > 0

        for workflow in workflows:
            assert "name" in workflow
            assert "steps" in workflow
            assert isinstance(workflow["steps"], list)


class TestResourceErrorHandling:
    """Test cases for resource error handling"""

    @pytest.mark.asyncio
    async def test_resource_error_creation(self):
        """Test ResourceError creation and usage"""
        error = ResourceError("Test resource error", resource_name="test_resource")

        assert error.message == "Test resource error"
        assert error.details["resource_name"] == "test_resource"
        assert error.error_code == "RESOURCEERROR"

        # Test to_dict method
        error_dict = error.to_dict()
        assert error_dict["error_type"] == "ResourceError"
        assert error_dict["message"] == "Test resource error"
        assert error_dict["details"]["resource_name"] == "test_resource"

    @pytest.mark.asyncio
    async def test_resource_error_inheritance(self):
        """Test ResourceError inheritance"""
        error = ResourceError("Test")

        # Check inheritance chain
        assert isinstance(error, ResourceError)
        assert isinstance(error, MCPError)
        assert isinstance(error, OdooMCPError)
        assert isinstance(error, Exception)
