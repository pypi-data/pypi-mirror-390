#!/usr/bin/env python3
"""
Command-line interface for F_ooredoo torrent downloader
Entry point: fuckooredoo
"""

import sys
import os
import subprocess
import platform


def check_tor_installed():
    """Check if Tor is installed and provide installation instructions"""
    system = platform.system().lower()
    
    # Check if tor is available in PATH
    try:
        if system == "windows":
            subprocess.run(["where", "tor"], capture_output=True, check=True)
        else:
            subprocess.run(["which", "tor"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Tor not found, provide installation instructions
    print("\n⚠️  Tor is not installed on your system!")
    print("\n📦 Installation Instructions:\n")
    
    if system == "linux":
        print("Ubuntu/Debian:")
        print("  sudo apt update && sudo apt install tor")
        print("\nFedora:")
        print("  sudo dnf install tor")
        print("\nArch Linux:")
        print("  sudo pacman -S tor")
    elif system == "darwin":
        print("macOS:")
        print("  brew install tor")
        print("\nOr visit: https://www.torproject.org/download/")
    elif system == "windows":
        print("Windows:")
        print("  Download Tor Browser from: https://www.torproject.org/download/")
        print("  Or use Chocolatey: choco install tor")
    
    print("\n❌ Please install Tor and run 'fuckooredoo' again.\n")
    return False


def check_tor_running():
    """Check if Tor service is running"""
    system = platform.system().lower()
    
    try:
        import socket
        # Try to connect to default Tor SOCKS port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 9050))
        sock.close()
        
        if result == 0:
            return True
        else:
            print("\n⚠️  Tor is installed but not running!")
            print("\n🚀 Starting Tor:\n")
            
            if system == "linux":
                print("  sudo systemctl start tor")
                print("  # Or: sudo service tor start")
            elif system == "darwin":
                print("  brew services start tor")
            elif system == "windows":
                print("  Start Tor Browser or run: tor.exe")
            
            print("\n❌ Please start Tor and run 'fuckooredoo' again.\n")
            return False
    except Exception as e:
        print(f"\n⚠️  Could not check Tor status: {e}")
        return False


def main():
    """Main entry point for the application"""
    print("=" * 70)
    print("🚀 F_ooredoo - Secure Torrent Downloader v1.0.0")
    print("   By Mohamed Aziz Bahloul")
    print("=" * 70)
    print()
    
    # Check if Tor is installed
    if not check_tor_installed():
        sys.exit(1)
    
    # Check if Tor is running
    if not check_tor_running():
        sys.exit(1)
    
    print("✅ Tor is running!")
    print("🔒 All traffic will be routed through Tor")
    print("🚀 Starting F_ooredoo...\n")
    
    # Import and run the main application
    try:
        import customtkinter as ctk
        from fuckooredoo.torrent_client import TorrentClient
        from fuckooredoo.gui import TorrentGUI
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create the torrent client with Tor enabled
        client = TorrentClient()
        
        # Create and run the GUI
        app = TorrentGUI(client)
        app.run()
        
    except KeyboardInterrupt:
        print("\n\n✋ Application stopped by user")
        sys.exit(0)
    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("\n📦 Please reinstall the package:")
        print("   pip install --upgrade fuckooredoo")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
