"""Tests for login command"""

from unittest.mock import Mock, patch

from keynet_train.cli.commands.login import handle_login
from keynet_train.cli.config.manager import ConfigManager


class TestHandleLoginSuccess:
    """Test successful login flow"""

    @patch("keynet_train.cli.commands.login.ConfigManager")
    @patch("keynet_train.cli.commands.login.docker")
    @patch("keynet_train.cli.commands.login.Prompt.ask")
    @patch("httpx.post")
    def test_login_with_server_url_arg(
        self,
        mock_post,
        mock_prompt_ask,
        mock_docker_module,
        mock_config_manager_class,
        tmp_path,
    ):
        """Test login flow when server_url is provided as argument"""
        # Arrange
        config_path = tmp_path / "config.json"
        config_manager = ConfigManager()
        config_manager.config_path = config_path
        mock_config_manager_class.return_value = config_manager

        # Mock Rich Prompt.ask (email and password)
        mock_prompt_ask.side_effect = ["test@example.com", "testpass"]

        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "accessToken": "test_token_abc123",
            "accessTokenExpiresAt": "2025-11-05T08:00:00Z",
            "harbor": {
                "url": "https://harbor.example.com",
                "username": "robot$test123",
                "password": "harbor_pass_xyz",
            },
        }
        mock_post.return_value = mock_response

        # Mock docker login success
        mock_docker_client = Mock()
        mock_docker_client.login.return_value = {"Status": "Login Succeeded"}
        mock_docker_module.from_env.return_value = mock_docker_client

        # Create args namespace
        args = Mock()
        args.server_url = "http://localhost:6100"
        args.username = None

        # Act
        result = handle_login(args)

        # Assert
        assert result == 0

        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert (
            call_args[0][0]
            == "http://localhost:6100/app-training/v1/auth/sign-in/one-time"
        )
        assert call_args[1]["json"] == {
            "email": "test@example.com",
            "password": "testpass",
        }
        assert call_args[1]["timeout"] == 30.0

        # Verify credentials saved
        assert config_path.exists()
        import json

        saved_config = json.loads(config_path.read_text())
        assert saved_config["server_url"] == "http://localhost:6100/app-training"
        assert saved_config["username"] == "test@example.com"
        assert saved_config["api_token"] == "test_token_abc123"
        assert saved_config["api_token_expires_at"] == "2025-11-05T08:00:00Z"
        assert saved_config["harbor"]["url"] == "https://harbor.example.com"

        # Verify docker login called
        mock_docker_client.login.assert_called_once_with(
            username="robot$test123",
            password="harbor_pass_xyz",
            registry="https://harbor.example.com",
        )

    @patch("keynet_train.cli.commands.login.ConfigManager")
    @patch("keynet_train.cli.commands.login.docker")
    @patch("keynet_train.cli.commands.login.Prompt.ask")
    @patch("httpx.post")
    def test_login_with_username_arg(
        self,
        mock_post,
        mock_prompt_ask,
        mock_docker_module,
        mock_config_manager_class,
        tmp_path,
    ):
        """Test login flow when username is provided as argument"""
        # Arrange
        config_path = tmp_path / "config.json"
        config_manager = ConfigManager()
        config_manager.config_path = config_path
        mock_config_manager_class.return_value = config_manager

        # Mock Rich Prompt.ask (only password needed)
        mock_prompt_ask.return_value = "testpass"

        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "accessToken": "test_token_abc123",
            "accessTokenExpiresAt": "2025-11-05T08:00:00Z",
            "harbor": {
                "url": "https://harbor.example.com",
                "username": "robot$test123",
                "password": "harbor_pass_xyz",
            },
        }
        mock_post.return_value = mock_response

        # Mock docker login success
        mock_docker_client = Mock()
        mock_docker_client.login.return_value = {"Status": "Login Succeeded"}
        mock_docker_module.from_env.return_value = mock_docker_client

        # Create args namespace
        args = Mock()
        args.server_url = "http://localhost:6100"
        args.username = "test@example.com"

        # Act
        result = handle_login(args)

        # Assert
        assert result == 0

        # Email should not be prompted (only password)
        mock_prompt_ask.assert_called_once()

        # Verify API call with provided email
        call_args = mock_post.call_args
        assert call_args[1]["json"]["email"] == "test@example.com"


class TestHandleLoginErrors:
    """Test error handling in login flow"""

    @patch("keynet_train.cli.commands.login.ConfigManager")
    @patch("keynet_train.cli.commands.login.Prompt.ask")
    @patch("httpx.post")
    def test_login_with_invalid_credentials(
        self, mock_post, mock_prompt_ask, mock_config_manager_class, tmp_path
    ):
        """Test login failure with invalid credentials"""
        # Arrange
        config_path = tmp_path / "config.json"
        config_manager = ConfigManager()
        config_manager.config_path = config_path
        mock_config_manager_class.return_value = config_manager

        # Mock Rich Prompt.ask (email and password)
        mock_prompt_ask.side_effect = ["test@example.com", "wrongpass"]

        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": "AUTHENTICATION_FAILED",
            "message": "Invalid username or password",
        }
        mock_post.return_value = mock_response

        # Create args namespace
        args = Mock()
        args.server_url = "http://localhost:6100"
        args.username = None

        # Act
        result = handle_login(args)

        # Assert
        assert result == 1

        # Verify credentials NOT saved
        assert not config_path.exists()

    @patch("keynet_train.cli.commands.login.ConfigManager")
    @patch("keynet_train.cli.commands.login.docker")
    @patch("keynet_train.cli.commands.login.Prompt.ask")
    @patch("httpx.post")
    def test_login_success_but_docker_fails(
        self,
        mock_post,
        mock_prompt_ask,
        mock_docker_module,
        mock_config_manager_class,
        tmp_path,
    ):
        """Test when API login succeeds but docker login fails"""
        # Arrange
        config_path = tmp_path / "config.json"
        config_manager = ConfigManager()
        config_manager.config_path = config_path
        mock_config_manager_class.return_value = config_manager

        # Mock Rich Prompt.ask (email and password)
        mock_prompt_ask.side_effect = ["test@example.com", "testpass"]

        # Mock API success
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "accessToken": "test_token_abc123",
            "accessTokenExpiresAt": "2025-11-05T08:00:00Z",
            "harbor": {
                "url": "https://harbor.example.com",
                "username": "robot$test123",
                "password": "harbor_pass_xyz",
            },
        }
        mock_post.return_value = mock_response

        # Mock docker login failure
        import docker.errors

        mock_docker_client = Mock()
        mock_docker_client.login.side_effect = docker.errors.APIError(
            "unauthorized: authentication required"
        )
        mock_docker_module.from_env.return_value = mock_docker_client

        # Create args namespace
        args = Mock()
        args.server_url = "http://localhost:6100"
        args.username = None

        # Act
        result = handle_login(args)

        # Assert - Should still return success (credentials saved)
        assert result == 0

        # Verify credentials ARE saved (even though docker failed)
        assert config_path.exists()

    @patch("keynet_train.cli.commands.login.ConfigManager")
    @patch("keynet_train.cli.commands.login.Prompt.ask")
    @patch("httpx.post")
    def test_login_with_network_error(
        self, mock_post, mock_prompt_ask, mock_config_manager_class, tmp_path
    ):
        """Test login with network connection error"""
        # Arrange
        config_path = tmp_path / "config.json"
        config_manager = ConfigManager()
        config_manager.config_path = config_path
        mock_config_manager_class.return_value = config_manager

        # Mock Rich Prompt.ask (email and password)
        mock_prompt_ask.side_effect = ["test@example.com", "testpass"]

        # Mock network error
        import httpx

        mock_post.side_effect = httpx.ConnectError("Connection refused")

        # Create args namespace
        args = Mock()
        args.server_url = "http://localhost:6100"
        args.username = None

        # Act
        result = handle_login(args)

        # Assert
        assert result == 1

        # Verify credentials NOT saved
        assert not config_path.exists()
