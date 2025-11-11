"""
Login command implementation.

This module implements the 'login' command for server authentication.
"""

import argparse

import docker
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from ..config.manager import ConfigManager

console = Console()


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
                # Show saved URL as default
                server_url = Prompt.ask("Server URL", default=saved_url)
            else:
                # No saved URL, prompt without default
                server_url = Prompt.ask("Server URL")

        # Validate server URL
        if not server_url:
            console.print("[red]Error: Server URL is required.[/red]")
            return 1

        # Normalize server URL (ensure /app-training path)
        server_url = _normalize_server_url(server_url)

        # Get email
        username = args.username
        if not username:
            username = Prompt.ask("Email")

        # Get password (securely)
        password = Prompt.ask("Password", password=True)

        console.print()

        # Call server API
        with console.status("[bold cyan]Authenticating...", spinner="dots"):
            try:
                response = httpx.post(
                    f"{server_url}/v1/auth/sign-in/one-time",
                    json={"email": username, "password": password},
                    timeout=30.0,
                )

                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = error_data.get("message", "Unknown error")
                    console.print(f"[red]✗ Login failed: {error_msg}[/red]")
                    return 1

                data = response.json()

            except httpx.ConnectError as e:
                console.print(f"[red]✗ Connection error: {e}[/red]")
                console.print("Could not connect to server. Please check:")
                console.print(f"  - Server URL: {server_url}")
                console.print("  - Network connectivity")
                return 1

            except httpx.TimeoutException:
                console.print(
                    f"[red]✗ Request timed out connecting to {server_url}[/red]"
                )
                return 1

            except Exception as e:
                console.print(f"[red]✗ Unexpected error during API call: {e}[/red]")
                return 1

        console.print("[green]✓ Platform authentication successful[/green]")

        # Auto docker login
        with console.status(
            f"[bold cyan]Logging into Harbor ({data['harbor']['url']})...",
            spinner="dots",
        ):
            try:
                client = docker.from_env()
                client.login(
                    username=data["harbor"]["username"],
                    password=data["harbor"]["password"],
                    registry=data["harbor"]["url"],
                )
                harbor_success = True
                harbor_error = None

            except Exception as e:
                harbor_success = False
                harbor_error = str(e)

        if harbor_success:
            console.print("[green]✓ Harbor login successful[/green]")
        else:
            console.print(f"[yellow]⚠ Docker login failed: {harbor_error}[/yellow]")
            console.print("Credentials saved, but you may need to login manually:")
            console.print(f"  docker login {data['harbor']['url']}")
            # Check if it's a Docker connection error (not installed/not running)
            error_msg_lower = harbor_error.lower() if harbor_error else ""
            if "connection" in error_msg_lower or "docker" in error_msg_lower:
                console.print()
                console.print("If Docker is not installed or running:")
                console.print(
                    "  → Install Docker Desktop: https://www.docker.com/products/docker-desktop"
                )
                console.print("  → Start Docker Desktop")

        # Save credentials
        config_manager.save_credentials(
            server_url=server_url,
            username=username,
            api_token=data["accessToken"],
            api_token_expires_at=data["accessTokenExpiresAt"],
            harbor=data["harbor"],
        )

        console.print("[green]✓ Configuration saved[/green]")

        console.print()

        # Show summary panel
        # Truncate long URLs for display
        display_url = server_url
        if len(display_url) > 45:
            display_url = display_url[:42] + "..."

        summary = f"""[bold green]Server:[/bold green]   {display_url}
[bold green]User:[/bold green]     {username}
[bold green]Expires:[/bold green]  {data["accessTokenExpiresAt"]}
[bold green]Config:[/bold green]   {config_manager.config_path}"""

        panel = Panel(
            summary,
            title="[bold green]Login Complete[/bold green]",
            border_style="green",
            padding=(1, 2),
        )

        console.print(panel)

        return 0

    except KeyboardInterrupt:
        console.print("\n[yellow]Login cancelled by user[/yellow]")
        return 1

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback

        traceback.print_exc()
        return 1
