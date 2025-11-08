"""
Tests for biszx_odoo_mcp.tools.odoo_client module
"""

from unittest.mock import Mock, patch

import pytest
from biszx_odoo_mcp.exceptions import (
    AuthenticationError,
    ConnectionTimeoutError,
    InternalServerError,
    ModelNotFoundError,
    OdooRPCError,
)
from biszx_odoo_mcp.tools.odoo_client import OdooClient, get_odoo_client
from odoorpc.error import InternalError, RPCError
from odoorpc.rpc.error import ConnectorError


class TestOdooClientInitialization:
    """Test cases for OdooClient initialization and connection"""

    @patch("biszx_odoo_mcp.tools.odoo_client.odoorpc.ODOO")
    @patch("biszx_odoo_mcp.tools.odoo_client.logger")
    def test_successful_initialization(self, mock_logger, mock_odoo_rpc, mock_config):
        """Test successful client initialization"""
        # Setup mock
        mock_odoo_instance = Mock()
        mock_odoo_rpc.return_value = mock_odoo_instance

        # Mock the user search
        mock_user_model = Mock()
        mock_user_model.search.return_value = [1]
        mock_odoo_instance.env = {"res.users": mock_user_model}

        # Create client
        client = OdooClient(mock_config)

        # Verify connection setup
        mock_odoo_rpc.assert_called_once()
        mock_odoo_instance.login.assert_called_once_with(
            mock_config.db, mock_config.username, mock_config.password
        )

        assert client.odoo == mock_odoo_instance
        assert client.uid == 1

        # Verify logging
        mock_logger.info.assert_called()

    @patch("biszx_odoo_mcp.tools.odoo_client.odoorpc.ODOO")
    def test_authentication_error(self, mock_odoo_rpc, mock_config):
        """Test authentication error handling"""
        mock_odoo_instance = Mock()
        mock_odoo_rpc.return_value = mock_odoo_instance

        # Mock authentication failure
        rpc_error = RPCError("Access denied")
        mock_odoo_instance.login.side_effect = rpc_error

        with pytest.raises(AuthenticationError):
            OdooClient(mock_config)

    @patch("biszx_odoo_mcp.tools.odoo_client.odoorpc.ODOO")
    def test_connection_timeout_error(self, mock_odoo_rpc, mock_config):
        """Test connection timeout error handling"""
        mock_odoo_instance = Mock()
        mock_odoo_rpc.return_value = mock_odoo_instance

        # Mock connection timeout
        connector_error = ConnectorError("Connection timeout")
        mock_odoo_instance.login.side_effect = connector_error

        with pytest.raises(ConnectionTimeoutError):
            OdooClient(mock_config)

    @patch("biszx_odoo_mcp.tools.odoo_client.odoorpc.ODOO")
    def test_internal_error(self, mock_odoo_rpc, mock_config):
        """Test internal error handling"""
        mock_odoo_instance = Mock()
        mock_odoo_rpc.return_value = mock_odoo_instance

        # Mock internal error
        internal_error = InternalError("Internal server error")
        mock_odoo_instance.login.side_effect = internal_error

        with pytest.raises(InternalServerError):
            OdooClient(mock_config)


class TestOdooClientModelIntrospection:
    """Test cases for model introspection methods"""

    def test_search_models_success(self, mock_odoo_client):
        """Test successful model search"""
        result = mock_odoo_client.search_models("partner")

        # Verify result structure
        assert result["query"] == "partner"
        assert "length" in result
        assert "models" in result
        assert isinstance(result["models"], list)

    def test_search_models_rpc_error(self, mock_odoo_client):
        """Test model search with RPC error"""
        # Setup mock to raise OdooRPCError
        mock_model = Mock()
        mock_model.search_read.side_effect = RPCError("Test RPC Error")
        mock_odoo_client.odoo.env.__getitem__ = Mock(return_value=mock_model)

        with pytest.raises(OdooRPCError):
            mock_odoo_client.search_models("partner")

    def test_get_model_info_success(self, mock_odoo_client):
        """Test successful model info retrieval"""
        model_data = [{"model": "res.partner", "name": "Contact"}]

        # Setup mock
        mock_model = Mock()
        mock_model.search_read.return_value = model_data
        mock_odoo_client.odoo.env = {"ir.model": mock_model}

        result = mock_odoo_client.get_model_info("res.partner")

        # Verify the call
        mock_model.search_read.assert_called_once_with(
            [("model", "=", "res.partner")], ["model", "name"]
        )

        assert result == model_data[0]

    def test_get_model_info_not_found(self, mock_odoo_client):
        """Test model info when model not found"""
        # Setup mock to return empty result
        mock_model = Mock()
        mock_model.search_read.return_value = []
        mock_odoo_client.odoo.env = {"ir.model": mock_model}

        with pytest.raises(ModelNotFoundError):
            mock_odoo_client.get_model_info("nonexistent.model")

    def test_get_model_fields_success(self, mock_odoo_client, sample_field_data):
        """Test successful field retrieval"""
        # Setup mock
        mock_model = Mock()
        mock_model.fields_get.return_value = sample_field_data
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client.get_model_fields("res.partner")

        # Verify the call
        mock_model.fields_get.assert_called_once()

        # Verify result structure
        assert "length" in result
        assert "fields" in result
        assert result["fields"] == sample_field_data

    def test_get_model_fields_with_query(self, mock_odoo_client, sample_field_data):
        """Test field retrieval with query filter"""
        # Setup mock
        mock_model = Mock()
        mock_model.fields_get.return_value = sample_field_data
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client.get_model_fields("res.partner", "name")

        # Verify the call
        mock_model.fields_get.assert_called_once()

        # Verify result structure - should only include 'name' field
        assert "length" in result
        assert "fields" in result
        assert "name" in result["fields"]
        assert "email" not in result["fields"]  # Should be filtered out


class TestOdooClientSearchOperations:
    """Test cases for search and read operations"""

    def test_search_ids_success(self, mock_odoo_client, sample_domain):
        """Test successful ID search"""
        expected_ids = [1, 2, 3]

        # Setup mock
        mock_model = Mock()
        mock_model.search.return_value = expected_ids
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client.search_ids("res.partner", sample_domain)

        # Verify the call
        mock_model.search.assert_called_once_with(sample_domain)
        assert result == expected_ids

    def test_search_ids_with_options(self, mock_odoo_client, sample_domain):
        """Test ID search with offset, limit, and order"""
        expected_ids = [1, 2]

        # Setup mock
        mock_model = Mock()
        mock_model.search.return_value = expected_ids
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client.search_ids(
            "res.partner", sample_domain, offset=10, limit=2, order="name ASC"
        )

        # Verify the call with options
        mock_model.search.assert_called_once_with(
            sample_domain, offset=10, limit=2, order="name ASC"
        )
        assert result == expected_ids

    def test_search_count_success(self, mock_odoo_client, sample_domain):
        """Test successful count search"""
        expected_count = 42

        # Setup mock
        mock_model = Mock()
        mock_model.search_count.return_value = expected_count
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client.search_count("res.partner", sample_domain)

        # Verify the call
        mock_model.search_count.assert_called_once_with(sample_domain)
        assert result == expected_count

    def test_search_read_success(
        self, mock_odoo_client, sample_domain, sample_record_data
    ):
        """Test successful search and read"""
        # Setup mock
        mock_model = Mock()
        mock_model.search_read.return_value = sample_record_data
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client.search_read("res.partner", sample_domain)

        # Verify the call
        mock_model.search_read.assert_called_once_with(sample_domain)
        assert result == sample_record_data

    def test_search_read_with_options(
        self, mock_odoo_client, sample_domain, sample_record_data
    ):
        """Test search and read with all options"""
        fields = ["name", "email"]

        # Setup mock
        mock_model = Mock()
        mock_model.search_read.return_value = sample_record_data
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client.search_read(
            "res.partner",
            sample_domain,
            fields=fields,
            offset=5,
            limit=10,
            order="name ASC",
        )

        # Verify the call with all options
        mock_model.search_read.assert_called_once_with(
            sample_domain, fields=fields, offset=5, limit=10, order="name ASC"
        )
        assert result == sample_record_data

    def test_read_records_success(self, mock_odoo_client, sample_record_data):
        """Test successful record reading"""
        record_ids = [1, 2]

        # Setup mock
        mock_model = Mock()
        mock_recordset = Mock()
        mock_recordset.read.return_value = sample_record_data
        mock_model.browse.return_value = mock_recordset
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client.read_records("res.partner", record_ids)

        # Verify the calls
        mock_model.browse.assert_called_once_with(record_ids)
        mock_recordset.read.assert_called_once_with()
        assert result == sample_record_data

    def test_read_records_with_fields(self, mock_odoo_client, sample_record_data):
        """Test record reading with specific fields"""
        record_ids = [1, 2]
        fields = ["name", "email"]

        # Setup mock
        mock_model = Mock()
        mock_recordset = Mock()
        mock_recordset.read.return_value = sample_record_data
        mock_model.browse.return_value = mock_recordset
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client.read_records("res.partner", record_ids, fields=fields)

        # Verify the calls
        mock_model.browse.assert_called_once_with(record_ids)
        mock_recordset.read.assert_called_once_with(fields)
        assert result == sample_record_data


class TestOdooClientCRUDOperations:
    """Test cases for CRUD operations"""

    def test_create_records_success(self, mock_odoo_client):
        """Test successful record creation"""
        values_list = [{"name": "Test 1"}, {"name": "Test 2"}]
        expected_ids = [10, 11]

        # Setup mock
        mock_model = Mock()
        mock_model.create.return_value = expected_ids
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client.create_records("res.partner", values_list)

        # Verify the call
        mock_model.create.assert_called_once_with(values_list)
        assert result == expected_ids

    def test_write_records_success(self, mock_odoo_client):
        """Test successful record update"""
        record_ids = [1, 2]
        values = {"name": "Updated Name"}

        # Setup mock
        mock_model = Mock()
        mock_recordset = Mock()
        mock_recordset.write.return_value = True
        mock_model.browse.return_value = mock_recordset
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client.write_records("res.partner", record_ids, values)

        # Verify the calls
        mock_model.browse.assert_called_once_with(record_ids)
        mock_recordset.write.assert_called_once_with(values)
        assert result is True

    def test_unlink_records_success(self, mock_odoo_client):
        """Test successful record deletion"""
        record_ids = [1, 2]

        # Setup mock
        mock_model = Mock()
        mock_recordset = Mock()
        mock_recordset.unlink.return_value = True
        mock_model.browse.return_value = mock_recordset
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client.unlink_records("res.partner", record_ids)

        # Verify the calls
        mock_model.browse.assert_called_once_with(record_ids)
        mock_recordset.unlink.assert_called_once()
        assert result is True


class TestOdooClientMethodExecution:
    """Test cases for generic method execution"""

    def test_execute_method_success(self, mock_odoo_client):
        """Test successful method execution"""
        expected_result = "method_result"

        # Setup mock
        mock_model = Mock()
        mock_method = Mock(return_value=expected_result)
        mock_model.test_method = mock_method
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client.execute_method(
            "res.partner", "test_method", "arg1", "arg2", kwarg1="value1"
        )

        # Verify the call
        mock_method.assert_called_once_with("arg1", "arg2", kwarg1="value1")
        assert result == expected_result

    def test_call_method_success(self, mock_odoo_client):
        """Test successful method call"""
        expected_result = [(1, "Test Name")]
        args = [1]
        kwargs = {}

        # Setup mock
        mock_model = Mock()
        mock_method = Mock(return_value=expected_result)
        mock_model.name_get = mock_method
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client.call_method("res.partner", "name_get", args, kwargs)

        # Verify the call
        mock_method.assert_called_once_with(*args, **kwargs)
        assert result == expected_result

    def test_call_method_returns_none(self, mock_odoo_client):
        """Test method call that returns None"""
        args = []
        kwargs = {}

        # Setup mock to return None
        mock_model = Mock()
        mock_method = Mock(return_value=None)
        mock_model.test_method = mock_method
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        with pytest.raises(ValueError, match="Failed to call method test_method"):
            mock_odoo_client.call_method("res.partner", "test_method", args, kwargs)


class TestOdooClientUtilityMethods:
    """Test cases for utility methods"""

    def test_ensure_connected_success(self, mock_odoo_client):
        """Test _ensure_connected with valid connection"""
        result = mock_odoo_client._ensure_connected()
        assert result == mock_odoo_client.odoo

    def test_ensure_connected_no_connection(self, mock_config):
        """Test _ensure_connected with no connection"""
        # Create client without mocking the connection
        with patch("biszx_odoo_mcp.tools.odoo_client.odoorpc.ODOO"):
            client = OdooClient.__new__(OdooClient)
            client.config = mock_config
            client.odoo = None
            client.uid = None

            with pytest.raises(InternalServerError, match="Not connected to Odoo"):
                client._ensure_connected()

    def test_get_model_success(self, mock_odoo_client):
        """Test _get_model method"""
        mock_model = Mock()
        mock_odoo_client.odoo.env = {"res.partner": mock_model}

        result = mock_odoo_client._get_model("res.partner")
        assert result == mock_model


class TestGetOdooClient:
    """Test cases for the get_odoo_client function"""

    @patch("biszx_odoo_mcp.tools.odoo_client.Config")
    @patch("biszx_odoo_mcp.tools.odoo_client.OdooClient")
    def test_get_odoo_client(self, mock_odoo_client_class, mock_config_class):
        """Test get_odoo_client function"""
        mock_config = Mock()
        mock_config_class.return_value = mock_config
        mock_client = Mock()
        mock_odoo_client_class.return_value = mock_client

        result = get_odoo_client()

        # Verify calls
        mock_config_class.assert_called_once()
        mock_odoo_client_class.assert_called_once_with(config=mock_config)
        assert result == mock_client
