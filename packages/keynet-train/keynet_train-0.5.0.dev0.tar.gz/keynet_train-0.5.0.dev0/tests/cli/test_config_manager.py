"""
Tests for ConfigManager.

Tests the new save_credentials interface matching TECHSPEC v3.1.
"""

import json
import tempfile
from pathlib import Path

from keynet_train.cli.config.manager import ConfigManager


class TestSaveCredentials:
    """Test save_credentials method with new TECHSPEC interface."""

    def test_save_credentials_new_interface(self):
        """Test save_credentials with new interface (username, api_token, api_token_expires_at, harbor dict)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            manager = ConfigManager(str(config_path))

            # Call with new interface
            manager.save_credentials(
                server_url="https://api.example.com",
                username="testuser",
                api_token="token_abc123",
                api_token_expires_at="2025-12-31T23:59:59Z",
                harbor={
                    "url": "harbor.example.com",
                    "username": "harbor_user",
                    "password": "harbor_pass",
                },
            )

            # Verify saved config
            with config_path.open() as f:
                config = json.load(f)

            assert config["server_url"] == "https://api.example.com"
            assert config["username"] == "testuser"
            assert config["api_token"] == "token_abc123"
            assert config["api_token_expires_at"] == "2025-12-31T23:59:59Z"
            assert config["harbor"]["url"] == "harbor.example.com"
            assert config["harbor"]["username"] == "harbor_user"
            assert config["harbor"]["password"] == "harbor_pass"

    def test_save_credentials_last_login_updated(self):
        """Test that last_login is automatically updated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            manager = ConfigManager(str(config_path))

            manager.save_credentials(
                server_url="https://api.example.com",
                username="testuser",
                api_token="token_abc123",
                api_token_expires_at="2025-12-31T23:59:59Z",
                harbor={
                    "url": "harbor.example.com",
                    "username": "harbor_user",
                    "password": "harbor_pass",
                },
            )

            # Verify last_login exists
            with config_path.open() as f:
                config = json.load(f)

            assert "last_login" in config
            # Should be ISO 8601 format
            from datetime import datetime

            datetime.fromisoformat(
                config["last_login"].replace("Z", "+00:00")
            )  # Validate format


class TestGetApiToken:
    """Test get_api_token method (renamed from get_api_key)."""

    def test_get_api_token_returns_token(self):
        """Test get_api_token returns the api_token."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            manager = ConfigManager(str(config_path))

            manager.save_credentials(
                server_url="https://api.example.com",
                username="testuser",
                api_token="token_abc123",
                api_token_expires_at="2025-12-31T23:59:59Z",
                harbor={
                    "url": "harbor.example.com",
                    "username": "harbor_user",
                    "password": "harbor_pass",
                },
            )

            token = manager.get_api_token()
            assert token == "token_abc123"

    def test_get_api_token_returns_none_if_not_set(self):
        """Test get_api_token returns None if not configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            manager = ConfigManager(str(config_path))

            token = manager.get_api_token()
            assert token is None


class TestGetUsername:
    """Test get_username method."""

    def test_get_username_returns_username(self):
        """Test get_username returns the username."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            manager = ConfigManager(str(config_path))

            manager.save_credentials(
                server_url="https://api.example.com",
                username="testuser",
                api_token="token_abc123",
                api_token_expires_at="2025-12-31T23:59:59Z",
                harbor={
                    "url": "harbor.example.com",
                    "username": "harbor_user",
                    "password": "harbor_pass",
                },
            )

            username = manager.get_username()
            assert username == "testuser"

    def test_get_username_returns_none_if_not_set(self):
        """Test get_username returns None if not configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            manager = ConfigManager(str(config_path))

            username = manager.get_username()
            assert username is None


class TestBackwardCompatibility:
    """Test backward compatibility with old get_api_key method."""

    def test_get_api_key_still_works(self):
        """Test that get_api_key still works for backward compatibility."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            manager = ConfigManager(str(config_path))

            manager.save_credentials(
                server_url="https://api.example.com",
                username="testuser",
                api_token="token_abc123",
                api_token_expires_at="2025-12-31T23:59:59Z",
                harbor={
                    "url": "harbor.example.com",
                    "username": "harbor_user",
                    "password": "harbor_pass",
                },
            )

            # Old method should still work
            api_key = manager.get_api_key()
            assert api_key == "token_abc123"
