"""
F_ooredoo - Secure Torrent Downloader with Tor-based Anti-Throttling
Bypasses ISP throttling through Tor network routing and traffic encryption

Author: Mohamed Aziz Bahloul
Version: 1.0.0
License: MIT
GitHub: https://github.com/AzizBahloul/F_ooredoo
"""

__version__ = "1.0.0"
__author__ = "Mohamed Aziz Bahloul"
__email__ = "aziz@example.com"  # Update with your email

from .torrent_client import TorrentClient
from .gui import TorrentGUI

__all__ = ["TorrentClient", "TorrentGUI"]
