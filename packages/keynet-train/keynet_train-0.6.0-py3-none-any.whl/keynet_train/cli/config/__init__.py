"""
Configuration management for keynet-train CLI.

This module manages registry configuration and authentication settings
stored at ~/.config/keynet/config.json.
"""

from .manager import ConfigManager

__all__ = ["ConfigManager"]
