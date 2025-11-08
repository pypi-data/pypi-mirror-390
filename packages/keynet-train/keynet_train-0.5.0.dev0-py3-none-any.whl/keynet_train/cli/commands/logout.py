"""
Logout command implementation.

This module implements the 'logout' command to clear stored credentials.
"""

import argparse

from ..config.manager import ConfigManager


def setup_logout_parser(subparsers: argparse._SubParsersAction) -> None:
    """
    Set up the logout command parser.

    Args:
        subparsers: Subparsers action from parent parser

    """
    parser = subparsers.add_parser(
        "logout",
        help="Logout and clear credentials",
        description="Remove stored credentials from local configuration",
        epilog="""
Examples:
    # Logout and clear credentials
    keynet-train logout

Notes:
    - Removes ~/.config/keynet/config.json
    - Does not revoke API token on server
    - Does not remove docker Harbor credentials
        """,
    )

    parser.set_defaults(func=handle_logout)


def handle_logout(args: argparse.Namespace) -> int:
    """
    Handle logout command execution.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)

    """
    config_manager = ConfigManager()

    try:
        if config_manager.config_path.exists():
            config_manager.config_path.unlink()
            print("✓ 로그아웃 완료")
            print(f"   삭제됨: {config_manager.config_path}")
        else:
            print("저장된 자격증명 없음 (이미 로그아웃됨)")

        return 0

    except Exception as e:
        print(f"오류: {e}")
        return 1
