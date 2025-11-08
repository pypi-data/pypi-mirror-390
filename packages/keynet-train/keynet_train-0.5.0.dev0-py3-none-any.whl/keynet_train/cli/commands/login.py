"""
Login command implementation.

This module implements the 'login' command for server authentication.
"""

import argparse
import getpass
import sys

import docker
import httpx

from ..config.manager import ConfigManager


def _normalize_server_url(url: str) -> str:
    """
    Normalize server URL by ensuring it ends with /app-training.

    Args:
        url: Raw server URL (e.g., "http://localhost:6100" or "http://localhost:6100/app-training")

    Returns:
        Normalized URL with /app-training path (e.g., "http://localhost:6100/app-training")

    Examples:
        >>> _normalize_server_url("http://localhost:6100")
        'http://localhost:6100/app-training'
        >>> _normalize_server_url("http://localhost:6100/app-training")
        'http://localhost:6100/app-training'
        >>> _normalize_server_url("http://localhost:6100/app-training/")
        'http://localhost:6100/app-training'

    """
    # Remove trailing slashes
    url = url.rstrip("/")

    # Check if already ends with /app-training or app-training
    if url.endswith("/app-training"):
        return url
    if url.endswith("app-training"):
        # Add leading slash if missing
        return url[: -len("app-training")] + "/app-training"

    # Append /app-training
    return f"{url}/app-training"


def setup_login_parser(subparsers: argparse._SubParsersAction) -> None:
    """
    Set up the login command parser.

    Args:
        subparsers: Subparsers action from parent parser

    """
    parser = subparsers.add_parser(
        "login",
        help="Login to keynet server",
        description="Authenticate with keynet server and store credentials",
        epilog="""
Examples:
    # Login without URL (uses saved URL or prompts)
    keynet-train login

    # Login to specific server
    keynet-train login https://api.example.com

    # Login with email specified
    keynet-train login https://api.example.com --username user@example.com

Notes:
    - If server URL is not provided, uses previously saved URL or prompts for input
    - Configuration is stored at ~/.config/keynet/config.json
    - File permissions are automatically set to 600 (owner only)
    - API token and Harbor credentials are stored in config file
    - After successful login, server URL is saved for future use
    - After login, docker is automatically logged into Harbor
        """,
    )

    parser.add_argument(
        "server_url",
        type=str,
        nargs="?",  # Optional positional argument
        help="Server URL (e.g., https://api.example.com). If not provided, uses saved URL or prompts for input.",
    )

    parser.add_argument(
        "--username",
        type=str,
        help="Email address (will prompt if not provided)",
    )

    parser.set_defaults(func=handle_login)


def handle_login(args: argparse.Namespace) -> int:
    """
    Handle login command execution.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)

    """
    config_manager = ConfigManager()

    try:
        # Get server URL (priority: args > saved config > user input)
        server_url = args.server_url

        if not server_url:
            # Try to get from saved config
            saved_url = config_manager.get_server_url()
            if saved_url:
                print(f"Saved server URL found: {saved_url}")
                use_saved = input("Use this URL? (Y/n): ").strip().lower()
                if use_saved in ("", "y", "yes"):
                    server_url = saved_url
                else:
                    server_url = input(
                        "Server URL (e.g., http://localhost:6100): "
                    ).strip()
            else:
                # No saved URL, prompt for input
                server_url = input("Server URL (e.g., http://localhost:6100): ").strip()

        # Validate server URL
        if not server_url:
            print("Error: Server URL is required.", file=sys.stderr)
            return 1

        # Normalize server URL (ensure /app-training path)
        server_url = _normalize_server_url(server_url)
        print(f"Connecting to: {server_url}")

        # Get email
        username = args.username
        if not username:
            username = input("Email: ")

        # Get password (securely)
        password = getpass.getpass("Password: ")

        print()
        print(f"🔐 Logging in to {server_url}...")

        # Call server API
        try:
            response = httpx.post(
                f"{server_url}/v1/auth/sign-in/one-time",
                json={"email": username, "password": password},
                timeout=30.0,
            )

            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get("message", "Unknown error")
                print(f"❌ Login failed: {error_msg}", file=sys.stderr)
                return 1

            data = response.json()

        except httpx.ConnectError as e:
            print(f"❌ Connection error: {e}", file=sys.stderr)
            print("Could not connect to server. Please check:", file=sys.stderr)
            print(f"  - Server URL: {server_url}", file=sys.stderr)
            print("  - Network connectivity", file=sys.stderr)
            return 1

        except httpx.TimeoutException:
            print(f"❌ Request timed out connecting to {server_url}", file=sys.stderr)
            return 1

        except Exception as e:
            print(f"❌ Unexpected error during API call: {e}", file=sys.stderr)
            return 1

        # Save credentials
        config_manager.save_credentials(
            server_url=server_url,
            username=username,
            api_token=data["accessToken"],
            api_token_expires_at=data["accessTokenExpiresAt"],
            harbor=data["harbor"],
        )

        print(f"✅ API token saved (expires: {data['accessTokenExpiresAt']})")

        # Auto docker login
        print(f"🔐 Logging into Harbor ({data['harbor']['url']})...")
        try:
            client = docker.from_env()
            client.login(
                username=data["harbor"]["username"],
                password=data["harbor"]["password"],
                registry=data["harbor"]["url"],
            )
            print("✅ Harbor login successful!")

        except Exception as e:
            print(f"⚠️  Docker login failed: {e}", file=sys.stderr)
            print("Credentials saved, but you may need to login manually:")
            print(f"  docker login {data['harbor']['url']}")
            # Check if it's a Docker connection error (not installed/not running)
            error_msg = str(e).lower()
            if "connection" in error_msg or "docker" in error_msg:
                print()
                print("If Docker is not installed or running:")
                print(
                    "  → Install Docker Desktop: https://www.docker.com/products/docker-desktop"
                )
                print("  → Start Docker Desktop")

        print()
        print("✅ Login complete!")
        print(f"   Config: {config_manager.config_path}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1
