"""
Tests for config module.
"""

import os
from unittest.mock import patch

import pytest

from fubon_api_mcp_server.config import config


class TestConfig:
    """Test config module."""

    def test_config_attributes(self):
        """Test that config has required attributes."""
        assert hasattr(config, "mcp")
        assert hasattr(config, "username")
        assert hasattr(config, "password")
        assert hasattr(config, "pfx_path")
        assert hasattr(config, "pfx_password")
        assert hasattr(config, "BASE_DATA_DIR")

    def test_data_dir_creation(self):
        """Test that data directory is created."""
        assert config.BASE_DATA_DIR.exists()
        assert config.BASE_DATA_DIR.is_dir()

    @patch.dict(os.environ, {"FUBON_USERNAME": "test_user", "FUBON_PASSWORD": "test_pass", "FUBON_PFX_PATH": "test.pfx"})
    def test_environment_variables(self):
        """Test environment variable loading."""
        # Reload config module to test env vars
        import importlib

        import fubon_api_mcp_server.config as config_module

        importlib.reload(config_module)

        # Access the reloaded config object
        reloaded_config = config_module.config
        assert reloaded_config.username == "test_user"
        assert reloaded_config.password == "test_pass"
        assert reloaded_config.pfx_path == "test.pfx"
