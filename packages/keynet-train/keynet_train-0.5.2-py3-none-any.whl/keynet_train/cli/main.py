"""
CLI main entry point for keynet-train.

This module provides the main() function that serves as the CLI entry point.
"""

import argparse
import logging
import sys

from .. import __version__
from .commands.login import setup_login_parser
from .commands.logout import setup_logout_parser
from .commands.push import setup_push_parser


def main() -> int:
    """
    Main entry point for keynet-train CLI.

    Returns:
        Exit code (0 for success, non-zero for errors)

    """
    # Suppress httpx INFO logs (e.g., "HTTP Request: GET ...")
    logging.getLogger("httpx").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(
        prog="keynet-train",
        description="Training utilities for keynet - Build and push container images with OCI artifacts",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"keynet-train {__version__}",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Register commands
    setup_login_parser(subparsers)
    setup_logout_parser(subparsers)
    setup_push_parser(subparsers)

    # Parse arguments
    args = parser.parse_args()

    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 0

    # Execute command handler
    if hasattr(args, "func"):
        return args.func(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
