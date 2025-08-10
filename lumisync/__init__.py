"""
LumiSync - Linux Settings Synchronization Tool

A modern, user-friendly application for synchronizing Linux desktop settings
and application profiles across devices using cloud storage.
"""

__version__ = "0.1.0"
__author__ = "LumiSync Development Team"
__email__ = "dev@lumisync.org"
__license__ = "MIT"

# Version info tuple for programmatic access
VERSION_INFO = tuple(map(int, __version__.split('.')))

# Application metadata
APP_NAME = "LumiSync"
APP_DESCRIPTION = "Linux Settings Synchronization Tool"
APP_URL = "https://github.com/lumisync/lumisync"

# Supported platforms
SUPPORTED_PLATFORMS = ["linux"]
SUPPORTED_DESKTOPS = ["gnome", "kde", "xfce"]  # Future support
SUPPORTED_CLOUDS = ["google_drive", "onedrive", "box", "pcloud"]  # Planned
