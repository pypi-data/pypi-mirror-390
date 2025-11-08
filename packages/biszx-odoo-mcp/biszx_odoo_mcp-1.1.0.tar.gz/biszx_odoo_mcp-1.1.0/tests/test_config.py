"""
Tests for biszx_odoo_mcp.tools.config module
"""

import os
from unittest.mock import patch

import pytest
from biszx_odoo_mcp.tools.config import Config


class TestConfig:
    """Test cases for Config class"""

    def test_initialization_with_valid_env(self, mock_env_vars):
        """Test successful initialization with valid environment variables"""
        # Use the mock_env_vars fixture to set up environment
        with patch("biszx_odoo_mcp.tools.config.logger") as mock_logger:
            config = Config()

            assert config.url == "https://test.odoo.com"  # https:// from fixture
            assert config.db == "test_db"
            assert config.username == "test_user"
            assert config.password == "test_password"
            assert config.timeout == 30
            assert config.verify_ssl is True

            # Verify logging calls
            assert mock_logger.info.called

    def test_initialization_missing_required_env(self):
        """Test initialization fails with missing required environment variables"""
        # Clear all environment variables
        original_env = os.environ.copy()
        os.environ.clear()

        try:
            with pytest.raises(OSError, match="Missing required environment variable"):
                Config()
        finally:
            os.environ.update(original_env)

    def test_initialization_missing_specific_env_vars(self, mock_env_vars):
        """Test initialization fails when specific required vars are missing"""
        required_vars = ["ODOO_URL", "ODOO_DB", "ODOO_USERNAME", "ODOO_PASSWORD"]

        for var in required_vars:
            # Save original value
            original_value = os.environ.get(var)

            # Remove the variable
            if var in os.environ:
                del os.environ[var]

            try:
                with pytest.raises(
                    OSError, match=f"Missing required environment variable: {var}"
                ):
                    Config()
            finally:
                # Restore the variable
                if original_value is not None:
                    os.environ[var] = original_value

    def test_optional_env_vars_defaults(self, mock_env_vars):
        """Test that optional environment variables use defaults"""
        # Remove optional variables
        optional_vars = ["ODOO_TIMEOUT", "ODOO_VERIFY_SSL"]
        original_values = {}

        for var in optional_vars:
            if var in os.environ:
                original_values[var] = os.environ[var]
                del os.environ[var]

        try:
            with patch("biszx_odoo_mcp.tools.config.logger"):
                config = Config()

                # Check defaults
                assert config.timeout == 30  # Default timeout
                assert config.verify_ssl is True  # Default verify_ssl
        finally:
            # Restore optional variables
            for var, value in original_values.items():
                os.environ[var] = value

    def test_custom_timeout_value(self, mock_env_vars):
        """Test custom timeout value"""
        os.environ["ODOO_TIMEOUT"] = "60"

        with patch("biszx_odoo_mcp.tools.config.logger"):
            config = Config()
            assert config.timeout == 60

    def test_invalid_timeout_value(self, mock_env_vars):
        """Test invalid timeout value raises ValueError"""
        os.environ["ODOO_TIMEOUT"] = "not_a_number"

        with pytest.raises(ValueError, match="ODOO_TIMEOUT must be an integer"):
            Config()

    def test_verify_ssl_values(self, mock_env_vars):
        """Test various verify_ssl values"""
        true_values = ["1", "true", "yes", "True", "YES"]
        false_values = ["0", "false", "no", "False", "NO"]

        for value in true_values:
            os.environ["ODOO_VERIFY_SSL"] = value
            with patch("biszx_odoo_mcp.tools.config.logger"):
                config = Config()
                assert config.verify_ssl is True, f"Failed for value: {value}"

        for value in false_values:
            os.environ["ODOO_VERIFY_SSL"] = value
            with patch("biszx_odoo_mcp.tools.config.logger"):
                config = Config()
                assert config.verify_ssl is False, f"Failed for value: {value}"

    def test_invalid_verify_ssl_value(self, mock_env_vars):
        """Test invalid verify_ssl value raises ValueError"""
        os.environ["ODOO_VERIFY_SSL"] = "maybe"

        with pytest.raises(ValueError, match="ODOO_VERIFY_SSL must be"):
            Config()

    def test_url_preparation_no_protocol(self, mock_env_vars):
        """Test URL preparation adds http:// when missing"""
        os.environ["ODOO_URL"] = "example.com"

        with patch("biszx_odoo_mcp.tools.config.logger"):
            config = Config()
            assert config.url == "http://example.com"

    def test_url_preparation_with_http(self, mock_env_vars):
        """Test URL preparation preserves http://"""
        os.environ["ODOO_URL"] = "http://example.com"

        with patch("biszx_odoo_mcp.tools.config.logger"):
            config = Config()
            assert config.url == "http://example.com"

    def test_url_preparation_with_https(self, mock_env_vars):
        """Test URL preparation preserves https://"""
        os.environ["ODOO_URL"] = "https://example.com"

        with patch("biszx_odoo_mcp.tools.config.logger"):
            config = Config()
            assert config.url == "https://example.com"

    def test_url_preparation_removes_trailing_slash(self, mock_env_vars):
        """Test URL preparation removes trailing slashes"""
        test_cases = [
            ("https://example.com/", "https://example.com"),
            ("https://example.com///", "https://example.com"),
            ("example.com/", "http://example.com"),
        ]

        for input_url, expected_url in test_cases:
            os.environ["ODOO_URL"] = input_url
            with patch("biszx_odoo_mcp.tools.config.logger"):
                config = Config()
                assert config.url == expected_url, f"Failed for URL: {input_url}"

    def test_load_config_return_value(self, mock_env_vars):
        """Test that load_config returns the expected dictionary"""
        with patch("biszx_odoo_mcp.tools.config.logger"):
            config = Config()
            config_dict = config.load_config()

            expected_keys = {
                "url",
                "db",
                "username",
                "password",
                "timeout",
                "verify_ssl",
            }
            assert set(config_dict.keys()) == expected_keys

            assert config_dict["url"] == "https://test.odoo.com"
            assert config_dict["db"] == "test_db"
            assert config_dict["username"] == "test_user"
            assert config_dict["password"] == "test_password"
            assert config_dict["timeout"] == 30
            assert config_dict["verify_ssl"] is True

    def test_config_logging_output(self, mock_env_vars):
        """Test that configuration is properly logged"""
        with patch("biszx_odoo_mcp.tools.config.logger") as mock_logger:
            Config()

            # Verify that configuration info is logged
            info_calls = [call[0][0] for call in mock_logger.info.call_args_list]

            # Check that important configuration values are logged
            assert any("Odoo client configuration" in call for call in info_calls)
            assert any("test.odoo.com" in call for call in info_calls)
            assert any("test_db" in call for call in info_calls)
            assert any("test_user" in call for call in info_calls)

    def test_private_prepare_url_method(self, mock_env_vars):
        """Test the _prepare_url private method directly"""
        with patch("biszx_odoo_mcp.tools.config.logger"):
            config = Config()

            # Test various URL formats
            assert config._prepare_url("example.com") == "http://example.com"
            assert config._prepare_url("http://example.com") == "http://example.com"
            assert config._prepare_url("https://example.com") == "https://example.com"
            assert config._prepare_url("https://example.com/") == "https://example.com"
            assert (
                config._prepare_url("https://example.com///") == "https://example.com"
            )

    def test_private_validate_config_method(self, mock_env_vars):
        """Test the _validate_config private method"""
        with patch("biszx_odoo_mcp.tools.config.logger"):
            config = Config()

            # This should not raise any exception with valid environment
            config._validate_config()

            # Test invalid timeout
            os.environ["ODOO_TIMEOUT"] = "invalid"
            with pytest.raises(ValueError, match="ODOO_TIMEOUT must be an integer"):
                config._validate_config()

            # Reset timeout
            os.environ["ODOO_TIMEOUT"] = "30"

            # Test invalid verify_ssl
            os.environ["ODOO_VERIFY_SSL"] = "invalid"
            with pytest.raises(ValueError, match="ODOO_VERIFY_SSL must be"):
                config._validate_config()
