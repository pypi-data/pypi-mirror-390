"""
Tests for biszx_odoo_mcp.server.tools module
"""

import pytest
from biszx_odoo_mcp.exceptions import OdooMCPError
from biszx_odoo_mcp.server import tools


def get_mock_odoo(mock_mcp_server):
    """Helper to get mock odoo client from mcp server"""
    return mock_mcp_server.get_context().request_context.lifespan_context.odoo


class TestSearchModels:
    """Test cases for search_models tool"""

    @pytest.mark.asyncio
    async def test_search_models_success(
        self, mock_mcp_server_for_tools, sample_model_data
    ):
        """Test successful model search"""
        # Setup mock - access the odoo client through the mock structure
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.search_models.return_value = sample_model_data

        result = await tools.search_models(mock_mcp_server_for_tools, "partner")

        # Verify result structure
        assert "success" in result
        assert "data" in result
        assert result["success"] is True
        assert result["data"] == sample_model_data

    @pytest.mark.asyncio
    async def test_search_models_odoo_error(self, mock_mcp_server_for_tools):
        """Test model search with Odoo error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        # Setup mock to raise OdooMCPError
        error = OdooMCPError("Test error")
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.search_models.side_effect = error

        result = await tools.search_models(mock_mcp_server_for_tools, "partner")

        # Verify error response
        assert "success" in result
        assert "error" in result
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_search_models_unexpected_error(self, mock_mcp_server_for_tools):
        """Test model search with unexpected error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        # Setup mock to raise generic exception
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.search_models.side_effect = ValueError("Unexpected error")

        result = await tools.search_models(mock_mcp_server_for_tools, "partner")

        # Verify error response
        assert "success" in result
        assert "error" in result
        assert result["success"] is False


class TestGetModelInfo:
    """Test cases for get_model_info tool"""

    @pytest.mark.asyncio
    async def test_get_model_info_success(self, mock_mcp_server_for_tools):
        """Test successful model info retrieval"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        model_info = {"model": "res.partner", "name": "Contact"}

        # Setup mock
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.get_model_info.return_value = model_info

        result = await tools.get_model_info(mock_mcp_server_for_tools, "res.partner")

        # Verify result
        assert result["success"] is True
        assert result["data"] == model_info

    @pytest.mark.asyncio
    async def test_get_model_info_error(self, mock_mcp_server_for_tools):
        """Test model info with error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        error = OdooMCPError("Model not found")
        mock_odoo.get_model_info.side_effect = error

        result = await tools.get_model_info(
            mock_mcp_server_for_tools, "nonexistent.model"
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_model_info_unexpected_error(self, mock_mcp_server_for_tools):
        """Test model info with unexpected error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.get_model_info.side_effect = RuntimeError("Unexpected error")

        result = await tools.get_model_info(mock_mcp_server_for_tools, "res.partner")

        # Verify error response
        assert result["success"] is False
        assert "error" in result
        assert "Unexpected error getting model info" in result["error"]["message"]


class TestGetModelFields:
    """Test cases for get_model_fields tool"""

    @pytest.mark.asyncio
    async def test_get_model_fields_success(
        self, mock_mcp_server_for_tools, sample_field_data
    ):
        """Test successful field retrieval"""
        # Setup mock
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.get_model_fields.return_value = sample_field_data

        result = await tools.get_model_fields(
            mock_mcp_server_for_tools, "res.partner", "name"
        )

        # Verify result
        assert result["success"] is True
        assert result["data"] == sample_field_data

    @pytest.mark.asyncio
    async def test_get_model_fields_error(self, mock_mcp_server_for_tools):
        """Test field retrieval with error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        error = OdooMCPError("Field error")
        mock_odoo.get_model_fields.side_effect = error

        result = await tools.get_model_fields(
            mock_mcp_server_for_tools, "res.partner", "name"
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_model_fields_unexpected_error(self, mock_mcp_server_for_tools):
        """Test field retrieval with unexpected error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.get_model_fields.side_effect = RuntimeError("Unexpected error")

        result = await tools.get_model_fields(
            mock_mcp_server_for_tools, "res.partner", "name"
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result
        assert "Unexpected error getting model fields" in result["error"]["message"]


class TestSearchRecords:
    """Test cases for search_records tool"""

    @pytest.mark.asyncio
    async def test_search_records_success(
        self, mock_mcp_server_for_tools, sample_domain, sample_record_data
    ):
        """Test successful record search"""
        # Setup mock
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.search_read.return_value = sample_record_data

        result = await tools.search_records(
            mock_mcp_server_for_tools, "res.partner", sample_domain
        )

        # Verify result
        assert result["success"] is True
        assert result["data"] == sample_record_data

    @pytest.mark.asyncio
    async def test_search_records_with_options(
        self, mock_mcp_server_for_tools, sample_domain, sample_record_data
    ):
        """Test record search with all options"""
        # Setup mock
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.search_read.return_value = sample_record_data

        result = await tools.search_records(
            mock_mcp_server_for_tools,
            "res.partner",
            sample_domain,
            fields=["name", "email"],
            limit=10,
            offset=5,
            order="name ASC",
        )

        # Verify result
        assert result["success"] is True
        assert result["data"] == sample_record_data

    @pytest.mark.asyncio
    async def test_search_records_error(self, mock_mcp_server_for_tools, sample_domain):
        """Test record search with error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        error = OdooMCPError("Search error")
        mock_odoo.search_read.side_effect = error

        result = await tools.search_records(
            mock_mcp_server_for_tools, "res.partner", sample_domain
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result


class TestReadRecords:
    """Test cases for read_records tool"""

    @pytest.mark.asyncio
    async def test_read_records_success(
        self, mock_mcp_server_for_tools, sample_record_data
    ):
        """Test successful record reading"""
        record_ids = [1, 2]

        # Setup mock
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.read_records.return_value = sample_record_data

        result = await tools.read_records(
            mock_mcp_server_for_tools, "res.partner", record_ids
        )

        # Verify result
        assert result["success"] is True
        assert result["data"] == sample_record_data

    @pytest.mark.asyncio
    async def test_read_records_with_fields(
        self, mock_mcp_server_for_tools, sample_record_data
    ):
        """Test record reading with specific fields"""
        record_ids = [1, 2]
        fields = ["name", "email"]

        # Setup mock
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.read_records.return_value = sample_record_data

        result = await tools.read_records(
            mock_mcp_server_for_tools, "res.partner", record_ids, fields=fields
        )

        # Verify result
        assert result["success"] is True
        assert result["data"] == sample_record_data

    @pytest.mark.asyncio
    async def test_read_records_error(self, mock_mcp_server_for_tools):
        """Test record reading with error"""
        record_ids = [1, 2]
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        error = OdooMCPError("Read error")
        mock_odoo.read_records.side_effect = error

        result = await tools.read_records(
            mock_mcp_server_for_tools, "res.partner", record_ids
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result


class TestCreateRecord:
    """Test cases for create_record tool"""

    @pytest.mark.asyncio
    async def test_create_record_success(self, mock_mcp_server_for_tools):
        """Test successful record creation"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        values = {"name": "Test Record"}
        expected_id = 42

        # Setup mock
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.create_records.return_value = expected_id

        result = await tools.create_record(
            mock_mcp_server_for_tools, "res.partner", values
        )

        # Verify result
        assert result["success"] is True
        assert result["data"]["id"] == expected_id

    @pytest.mark.asyncio
    async def test_create_record_error(self, mock_mcp_server_for_tools):
        """Test record creation with error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        values = {"name": "Test Record"}
        error = OdooMCPError("Creation error")
        mock_odoo.create_records.side_effect = error

        result = await tools.create_record(
            mock_mcp_server_for_tools, "res.partner", values
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result


class TestCreateRecords:
    """Test cases for create_records tool"""

    @pytest.mark.asyncio
    async def test_create_records_success(self, mock_mcp_server_for_tools):
        """Test successful multiple record creation"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        values_list = [{"name": "Test 1"}, {"name": "Test 2"}]
        expected_ids = [42, 43]

        # Setup mock
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.create_records.return_value = expected_ids

        result = await tools.create_records(
            mock_mcp_server_for_tools, "res.partner", values_list
        )

        # Verify result
        assert result["success"] is True
        assert result["data"]["ids"] == expected_ids

    @pytest.mark.asyncio
    async def test_create_records_error(self, mock_mcp_server_for_tools):
        """Test multiple record creation with error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        values_list = [{"name": "Test 1"}, {"name": "Test 2"}]
        error = OdooMCPError("Create error")
        mock_odoo.create_records.side_effect = error

        result = await tools.create_records(
            mock_mcp_server_for_tools, "res.partner", values_list
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result


class TestWriteRecord:
    """Test cases for write_record tool"""

    @pytest.mark.asyncio
    async def test_write_record_success(self, mock_mcp_server_for_tools):
        """Test successful record update"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        record_id = 1
        values = {"name": "Updated Name"}

        # Setup mock
        mock_odoo.write_records.return_value = True

        result = await tools.write_record(
            mock_mcp_server_for_tools, "res.partner", record_id, values
        )

        # Verify result
        assert result["success"] is True
        assert result["data"]["success"] is True

    @pytest.mark.asyncio
    async def test_write_record_error(self, mock_mcp_server_for_tools):
        """Test record update with error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        record_id = 1
        values = {"name": "Updated Name"}
        error = OdooMCPError("Write error")
        mock_odoo.write_records.side_effect = error

        result = await tools.write_record(
            mock_mcp_server_for_tools, "res.partner", record_id, values
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result


class TestWriteRecords:
    """Test cases for write_records tool"""

    @pytest.mark.asyncio
    async def test_write_records_success(self, mock_mcp_server_for_tools):
        """Test successful multiple record update"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        record_ids = [1, 2]
        values = {"active": False}

        # Setup mock
        mock_odoo.write_records.return_value = True

        result = await tools.write_records(
            mock_mcp_server_for_tools, "res.partner", record_ids, values
        )

        # Verify result
        assert result["success"] is True
        assert result["data"]["success"] is True

    @pytest.mark.asyncio
    async def test_write_records_error(self, mock_mcp_server_for_tools):
        """Test multiple record update with error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        record_ids = [1, 2]
        values = {"active": False}
        error = OdooMCPError("Write error")
        mock_odoo.write_records.side_effect = error

        result = await tools.write_records(
            mock_mcp_server_for_tools, "res.partner", record_ids, values
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result


class TestUnlinkRecord:
    """Test cases for unlink_record tool"""

    @pytest.mark.asyncio
    async def test_unlink_record_success(self, mock_mcp_server_for_tools):
        """Test successful record deletion"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        record_id = 1

        # Setup mock
        mock_odoo.unlink_records.return_value = True

        result = await tools.unlink_record(
            mock_mcp_server_for_tools, "res.partner", record_id
        )

        # Verify result
        assert result["success"] is True
        assert result["data"]["success"] is True

    @pytest.mark.asyncio
    async def test_unlink_record_error(self, mock_mcp_server_for_tools):
        """Test record deletion with error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        record_id = 1
        error = OdooMCPError("Deletion error")
        mock_odoo.unlink_records.side_effect = error

        result = await tools.unlink_record(
            mock_mcp_server_for_tools, "res.partner", record_id
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result


class TestUnlinkRecords:
    """Test cases for unlink_records tool"""

    @pytest.mark.asyncio
    async def test_unlink_records_success(self, mock_mcp_server_for_tools):
        """Test successful multiple record deletion"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        record_ids = [1, 2]

        # Setup mock
        mock_odoo.unlink_records.return_value = True

        result = await tools.unlink_records(
            mock_mcp_server_for_tools, "res.partner", record_ids
        )

        # Verify result
        assert result["success"] is True
        assert result["data"]["success"] is True

    @pytest.mark.asyncio
    async def test_unlink_records_error(self, mock_mcp_server_for_tools):
        """Test multiple record deletion with error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        record_ids = [1, 2]
        error = OdooMCPError("Delete error")
        mock_odoo.unlink_records.side_effect = error

        result = await tools.unlink_records(
            mock_mcp_server_for_tools, "res.partner", record_ids
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result


class TestSearchCount:
    """Test cases for search_count tool"""

    @pytest.mark.asyncio
    async def test_search_count_success(self, mock_mcp_server_for_tools, sample_domain):
        """Test successful count search"""
        expected_count = 42

        # Setup mock
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.search_count.return_value = expected_count

        result = await tools.search_count(
            mock_mcp_server_for_tools, "res.partner", sample_domain
        )

        # Verify result
        assert result["success"] is True
        assert result["data"]["count"] == expected_count

    @pytest.mark.asyncio
    async def test_search_count_error(self, mock_mcp_server_for_tools, sample_domain):
        """Test count search with error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        error = OdooMCPError("Count error")
        mock_odoo.search_count.side_effect = error

        result = await tools.search_count(
            mock_mcp_server_for_tools, "res.partner", sample_domain
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result


class TestSearchIds:
    """Test cases for search_ids tool"""

    @pytest.mark.asyncio
    async def test_search_ids_success(self, mock_mcp_server_for_tools, sample_domain):
        """Test successful ID search"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        expected_ids = [1, 2, 3]

        # Setup mock
        mock_odoo.search_ids.return_value = expected_ids

        result = await tools.search_ids(
            mock_mcp_server_for_tools, "res.partner", sample_domain
        )

        # Verify result
        assert result["success"] is True
        assert result["data"]["ids"] == expected_ids

    @pytest.mark.asyncio
    async def test_search_ids_with_options(
        self, mock_mcp_server_for_tools, sample_domain
    ):
        """Test ID search with options"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        expected_ids = [1, 2]

        # Setup mock
        mock_odoo.search_ids.return_value = expected_ids

        result = await tools.search_ids(
            mock_mcp_server_for_tools,
            "res.partner",
            sample_domain,
            offset=10,
            limit=2,
            order="name ASC",
        )

        # Verify result
        assert result["success"] is True
        assert result["data"]["ids"] == expected_ids

    @pytest.mark.asyncio
    async def test_search_ids_error(self, mock_mcp_server_for_tools, sample_domain):
        """Test ID search with error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        error = OdooMCPError("Search error")
        mock_odoo.search_ids.side_effect = error

        result = await tools.search_ids(
            mock_mcp_server_for_tools, "res.partner", sample_domain
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result


class TestCallMethod:
    """Test cases for call_method tool"""

    @pytest.mark.asyncio
    async def test_call_method_success(self, mock_mcp_server_for_tools):
        """Test successful method call"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        expected_result = [(1, "Test Name")]
        args = [1]
        kwargs = {}

        # Setup mock
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.call_method.return_value = expected_result

        result = await tools.call_method(
            mock_mcp_server_for_tools, "res.partner", "name_get", args, kwargs
        )

        # Verify result
        assert result["success"] is True
        assert result["data"] == expected_result

    @pytest.mark.asyncio
    async def test_call_method_with_defaults(self, mock_mcp_server_for_tools):
        """Test method call with default parameters"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        expected_result = "method_result"

        # Setup mock
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.call_method.return_value = expected_result

        result = await tools.call_method(
            mock_mcp_server_for_tools, "res.partner", "test_method"
        )

        # Verify result
        assert result["success"] is True
        assert result["data"] == expected_result

        # Verify call with default empty args and kwargs
        mock_odoo.call_method.assert_called_with("res.partner", "test_method", [], {})

    @pytest.mark.asyncio
    async def test_call_method_error(self, mock_mcp_server_for_tools):
        """Test method call with error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        error = OdooMCPError("Method call error")
        mock_odoo.call_method.side_effect = error

        result = await tools.call_method(
            mock_mcp_server_for_tools, "res.partner", "test_method"
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result


class TestSearchAndUpdate:
    """Test cases for search_and_update tool"""

    @pytest.mark.asyncio
    async def test_search_and_update_success(
        self, mock_mcp_server_for_tools, sample_domain
    ):
        """Test successful search and update"""
        record_ids = [1, 2, 3]
        values = {"active": False}

        # Setup mocks
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.search_ids.return_value = record_ids
        mock_odoo.write_records.return_value = True

        result = await tools.search_and_update(
            mock_mcp_server_for_tools, "res.partner", sample_domain, values
        )

        # Verify result
        assert result["success"] is True
        assert result["data"]["affected_records"] == len(record_ids)
        assert result["data"]["record_ids"] == record_ids
        assert result["data"]["updated"] is True

    @pytest.mark.asyncio
    async def test_search_and_update_no_records(
        self, mock_mcp_server_for_tools, sample_domain
    ):
        """Test search and update with no matching records"""
        values = {"active": False}

        # Setup mock to return empty list
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        mock_odoo.search_ids.return_value = []

        result = await tools.search_and_update(
            mock_mcp_server_for_tools, "res.partner", sample_domain, values
        )

        # Verify result
        assert result["success"] is True
        assert result["data"]["affected_records"] == 0
        assert "No records found" in result["data"]["message"]

    @pytest.mark.asyncio
    async def test_search_and_update_error(
        self, mock_mcp_server_for_tools, sample_domain
    ):
        """Test search and update with error"""
        mock_odoo = get_mock_odoo(mock_mcp_server_for_tools)
        values = {"active": False}
        error = OdooMCPError("Search error")
        mock_odoo.search_ids.side_effect = error

        result = await tools.search_and_update(
            mock_mcp_server_for_tools, "res.partner", sample_domain, values
        )

        # Verify error response
        assert result["success"] is False
        assert "error" in result
