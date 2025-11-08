"""
Tests for biszx_odoo_mcp.server.response module
"""

import json

from biszx_odoo_mcp.server.response import Response


class TestResponse:
    """Test cases for Response class"""

    def test_basic_initialization_success(self):
        """Test basic initialization with data (success case)"""
        data = {"key": "value"}
        response = Response(data=data)

        assert response.data == data
        assert response.error is None
        assert response.success is True

    def test_basic_initialization_error(self):
        """Test basic initialization with error"""
        error = {"error_type": "TestError", "message": "Test error"}
        response = Response(error=error)

        assert response.data is None
        assert response.error == error
        assert response.success is False

    def test_initialization_empty(self):
        """Test initialization with no parameters"""
        response = Response()

        assert response.data is None
        assert response.error is None
        assert response.success is True

    def test_to_dict_success(self):
        """Test to_dict method with successful response"""
        data = {"key": "value", "number": 42}
        response = Response(data=data)
        result = response.to_dict()

        expected = {"success": True, "data": data}

        assert result == expected

    def test_to_dict_error(self):
        """Test to_dict method with error response"""
        error = {"error_type": "TestError", "message": "Test error"}
        response = Response(error=error)
        result = response.to_dict()

        expected = {"success": False, "error": error}

        assert result == expected

    def test_to_json_string_success(self):
        """Test to_json_string method with successful response"""
        data = {"key": "value"}
        response = Response(data=data)
        result = response.to_json_string()

        # Parse the JSON to verify it's valid
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"] == data

    def test_to_json_string_error(self):
        """Test to_json_string method with error response"""
        error = {"error_type": "TestError", "message": "Test error"}
        response = Response(error=error)
        result = response.to_json_string()

        # Parse the JSON to verify it's valid
        parsed = json.loads(result)
        assert parsed["success"] is False
        assert parsed["error"] == error

    def test_to_json_string_custom_indent(self):
        """Test to_json_string method with custom indentation"""
        data = {"key": "value"}
        response = Response(data=data)
        result = response.to_json_string(indent=4)

        # Verify it's valid JSON and properly indented
        parsed = json.loads(result)
        assert parsed["data"] == data
        # Check that it contains proper indentation
        assert "    " in result  # 4 spaces

    def test_to_json_string_no_indent(self):
        """Test to_json_string method with no indentation"""
        data = {"key": "value"}
        response = Response(data=data)
        result = response.to_json_string(indent=0)

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed["data"] == data

    def test_success_property_logic(self):
        """Test that success property correctly reflects error state"""
        # Success when no error
        response1 = Response(data={"test": "data"})
        assert response1.success is True

        # Success when explicitly no error
        response2 = Response(data={"test": "data"}, error=None)
        assert response2.success is True

        # Not success when error present
        response3 = Response(error={"error": "message"})
        assert response3.success is False

        # Not success when both data and error (error takes precedence)
        response4 = Response(data={"test": "data"}, error={"error": "message"})
        assert response4.success is False

    def test_complex_data_structures(self):
        """Test with complex data structures"""
        complex_data = {
            "list": [1, 2, 3],
            "nested": {"inner": "value", "number": 42},
            "boolean": True,
            "null": None,
        }

        response = Response(data=complex_data)
        json_str = response.to_json_string()

        # Verify complex data survives JSON serialization
        parsed = json.loads(json_str)
        assert parsed["data"] == complex_data

    def test_error_data_structures(self):
        """Test with complex error structures"""
        complex_error = {
            "error_type": "ComplexError",
            "error_code": "COMPLEX_ERROR",
            "message": "A complex error occurred",
            "details": {"field": "value", "nested": {"inner_error": "inner_message"}},
            "original_error": {
                "type": "ValueError",
                "message": "Original error message",
            },
        }

        response = Response(error=complex_error)
        json_str = response.to_json_string()

        # Verify complex error survives JSON serialization
        parsed = json.loads(json_str)
        assert parsed["error"] == complex_error
