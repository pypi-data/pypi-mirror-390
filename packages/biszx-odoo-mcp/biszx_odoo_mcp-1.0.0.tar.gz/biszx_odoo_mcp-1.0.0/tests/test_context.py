"""
Tests for biszx_odoo_mcp.server.context module
"""

from unittest.mock import Mock

from biszx_odoo_mcp.server.context import AppContext


class TestAppContext:
    """Test cases for AppContext class"""

    def test_initialization(self, mock_odoo_client):
        """Test basic initialization of AppContext"""
        context = AppContext(odoo=mock_odoo_client)

        assert context.odoo == mock_odoo_client
        assert hasattr(context, "odoo")

    def test_dataclass_behavior(self, mock_odoo_client):
        """Test that AppContext behaves as a dataclass"""
        from dataclasses import fields

        context = AppContext(odoo=mock_odoo_client)

        # Test that it's a dataclass with the expected fields
        dataclass_fields = fields(context)
        field_names = [field.name for field in dataclass_fields]
        assert "odoo" in field_names

    def test_context_immutability(self, mock_odoo_client):
        """Test context field access and modification"""
        context = AppContext(odoo=mock_odoo_client)

        # Test that we can access the odoo client
        odoo_client = context.odoo
        assert odoo_client == mock_odoo_client

        # Test that we can modify the reference (dataclass is mutable by default)
        new_mock_client = Mock()
        context.odoo = new_mock_client
        assert context.odoo == new_mock_client

    def test_string_representation(self, mock_odoo_client):
        """Test string representation of AppContext"""
        context = AppContext(odoo=mock_odoo_client)
        str_repr = str(context)

        # Should contain the class name and the odoo client reference
        assert "AppContext" in str_repr
        assert "odoo=" in str_repr

    def test_equality(self, mock_odoo_client):
        """Test equality comparison of AppContext instances"""
        context1 = AppContext(odoo=mock_odoo_client)
        context2 = AppContext(odoo=mock_odoo_client)

        # Same client reference should be equal
        assert context1 == context2

        # Different client should not be equal
        different_client = Mock()
        context3 = AppContext(odoo=different_client)
        assert context1 != context3
