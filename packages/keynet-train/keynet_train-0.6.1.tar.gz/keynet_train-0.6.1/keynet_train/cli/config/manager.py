"""
Configuration manager for keynet-train CLI.

This module manages local configuration stored at ~/.config/keynet/config.json
following XDG Base Directory specification.

Configuration includes:
- Server URL and API key
- Harbor registry credentials
- All credentials stored with proper file permissions (600)
"""

import json
import os
import stat
from pathlib import Path
from typing import Any, Optional


class ConfigManager:
    """
    Manages configuration for keynet-train CLI.

    Configuration is stored at ~/.config/keynet/config.json with the structure:
    {
        "server_url": "https://api.example.com",
        "api_key": "...",
        "harbor": {
            "url": "harbor.example.com",
            "username": "...",
            "password": "..."
        }
    }

    Credentials are obtained by logging into the Kotlin Spring Boot server,
    which returns the api_key and Harbor registry credentials.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ConfigManager.

        Args:
            config_path: Optional custom config file path.
                        Defaults to ~/.config/keynet/config.json

        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Follow XDG Base Directory specification
            config_home = os.environ.get("XDG_CONFIG_HOME")
            base_dir = Path(config_home) if config_home else Path.home() / ".config"
            self.config_path = base_dir / "keynet" / "config.json"

        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure the config directory exists with proper permissions."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Set directory permissions to 700 (owner only)
        self.config_path.parent.chmod(stat.S_IRWXU)

    def _load_config(self) -> dict[str, Any]:
        """
        Load the configuration file.

        Returns:
            Configuration dictionary

        """
        if not self.config_path.exists():
            return self._get_default_config()

        try:
            with self.config_path.open(encoding="utf-8") as f:
                config = json.load(f)

            # Validate file permissions (should be 600 or stricter)
            file_stat = self.config_path.stat()
            if file_stat.st_mode & (stat.S_IRWXG | stat.S_IRWXO):
                print(
                    f"Warning: Config file has insecure permissions: {self.config_path}"
                )
                print("Run: chmod 600 ~/.config/keynet/config.json")

            return config

        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {self.config_path}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """
        Get default configuration structure.

        Returns:
            Default config dictionary

        """
        return {
            "server_url": None,
            "username": None,
            "api_token": None,
            "api_token_expires_at": None,
            "harbor": {"url": None, "username": None, "password": None},
            "last_login": None,
        }

    def _save_config(self, config: dict[str, Any]) -> None:
        """
        Save the configuration to file with proper permissions.

        Args:
            config: Configuration dictionary to save

        """
        # Write config file
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        # Set file permissions to 600 (owner read/write only)
        self.config_path.chmod(stat.S_IRUSR | stat.S_IWUSR)

    def save_credentials(
        self,
        server_url: str,
        username: str,
        api_token: str,
        api_token_expires_at: str,
        harbor: dict[str, str],
    ) -> None:
        """
        Save credentials from server login response.

        Args:
            server_url: Server URL
            username: Username for the account
            api_token: API token (JWT) for server authentication
            api_token_expires_at: Token expiration timestamp (ISO 8601 format)
            harbor: Harbor registry credentials dict with keys: url, username, password

        """
        from datetime import datetime, timezone

        config = self._load_config()
        config["server_url"] = server_url
        config["username"] = username
        config["api_token"] = api_token
        config["api_token_expires_at"] = api_token_expires_at
        config["harbor"] = harbor
        config["last_login"] = datetime.now(timezone.utc).isoformat()
        self._save_config(config)

    def set_credentials(
        self,
        server_url: str,
        api_key: str,
        harbor_url: str,
        harbor_username: str,
        harbor_password: str,
    ) -> None:
        """
        Set credentials from server login response (DEPRECATED).

        This method is deprecated. Use save_credentials() instead.

        Args:
            server_url: Server URL
            api_key: API key for server authentication
            harbor_url: Harbor registry URL
            harbor_username: Harbor username
            harbor_password: Harbor password

        """
        # Convert to new interface
        self.save_credentials(
            server_url=server_url,
            username="",  # Legacy: no username
            api_token=api_key,
            api_token_expires_at="",  # Legacy: no expiration
            harbor={
                "url": harbor_url,
                "username": harbor_username,
                "password": harbor_password,
            },
        )

    def get_server_url(self) -> Optional[str]:
        """
        Get the configured server URL.

        Returns:
            Server URL, or None if not set

        """
        config = self._load_config()
        return config.get("server_url")

    def get_api_token(self) -> Optional[str]:
        """
        Get the API token from config file.

        Returns:
            API token, or None if not found

        """
        config = self._load_config()
        return config.get("api_token")

    def get_api_key(self) -> Optional[str]:
        """
        Get the API key from config file (DEPRECATED).

        This method is deprecated. Use get_api_token() instead.
        Provided for backward compatibility.

        Returns:
            API key/token, or None if not found

        """
        return self.get_api_token()

    def get_username(self) -> Optional[str]:
        """
        Get the username from config file.

        Returns:
            Username, or None if not found

        """
        config = self._load_config()
        return config.get("username")

    def get_harbor_credentials(self) -> Optional[dict[str, str]]:
        """
        Get Harbor registry credentials.

        Returns:
            Dictionary with 'url', 'username', 'password', or None if not configured

        """
        config = self._load_config()
        harbor_config = config.get("harbor", {})

        # Check if all required fields are present
        if (
            harbor_config.get("url")
            and harbor_config.get("username")
            and harbor_config.get("password")
        ):
            return {
                "url": harbor_config["url"],
                "username": harbor_config["username"],
                "password": harbor_config["password"],
            }

        return None

    def show_config(self) -> dict[str, Any]:
        """
        Get the full configuration (with sensitive data redacted).

        Returns:
            Configuration dictionary with redacted api_token and password

        """
        config = self._load_config()

        # Redact sensitive fields for display
        display_config = config.copy()

        # Redact API token
        if display_config.get("api_token"):
            api_token = display_config["api_token"]
            if len(api_token) > 8:
                display_config["api_token"] = f"{api_token[:4]}...{api_token[-4:]}"

        # Redact Harbor password
        if "harbor" in display_config and isinstance(display_config["harbor"], dict):
            harbor = display_config["harbor"].copy()
            if harbor.get("password"):
                password = harbor["password"]
                if len(password) > 8:
                    harbor["password"] = f"{password[:4]}...{password[-4:]}"
            display_config["harbor"] = harbor

        return display_config
