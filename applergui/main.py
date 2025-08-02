#!/usr/bin/env python3
"""
ApplerGUI - A modern Linux GUI application for controlling Apple TV and HomePod devices.
"""

import sys
import os
import asyncio
import signal
import argparse
import subprocess
from pathlib import Path

# Suppress Qt verbose logging for clean debug output
os.environ['QT_LOGGING_RULES'] = '*=false'
os.environ['QT_DEBUG_PLUGINS'] = '0'
os.environ['QT_ASSUME_STDERR_HAS_CONSOLE'] = '0'
os.environ['QT_QUIET'] = '1'
os.environ['QT_NO_DEBUG_OUTPUT'] = '1'

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication, QLoggingCategory
from PyQt6.QtGui import QPixmap, QIcon
import qasync

# SUPPRESS ALL Qt logging categories
QLoggingCategory.setFilterRules("*=false")

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from .ui.main_window import ResponsiveMainWindow
from .backend.config_manager import ConfigManager
from .backend.device_controller import DeviceController
from .backend.pairing_manager import PairingManager

class ApplerGUIApp:
    """Main application class."""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.config_manager = None
        self.device_controller = None
        self.pairing_manager = None
    
    def setup_application(self):
        """Set up the Qt application."""
        # Set application properties
        QCoreApplication.setApplicationName("ApplerGUI")
        QCoreApplication.setApplicationVersion("1.0.0")
        QCoreApplication.setOrganizationName("ApplerGUI")
        QCoreApplication.setOrganizationDomain("github.com/ZProLegend007/ApplerGUI")
        
        # Create Qt application
        self.app = QApplication(sys.argv)
        self.app.setApplicationDisplayName("ApplerGUI")
        
        # Set application icon if available
        icon_path = project_root / "resources" / "icons" / "app_icon.png"
        if icon_path.exists():
            app_icon = QIcon(str(icon_path))
            self.app.setWindowIcon(app_icon)
            print(f"✅ Application icon set from: {icon_path}")
        else:
            print(f"⚠️ Application icon not found at: {icon_path}")
    
    def setup_backend(self):
        """Set up backend components."""
        self.config_manager = ConfigManager()
        self.device_controller = DeviceController(self.config_manager)
        self.pairing_manager = PairingManager(self.config_manager)
    
    def setup_ui(self):
        """Set up the main window and UI."""
        self.main_window = ResponsiveMainWindow(
            self.config_manager,
            self.device_controller,
            self.pairing_manager
        )
        
        # Apply saved window geometry if available
        geometry_hex = self.config_manager.get('window_geometry')
        if geometry_hex and isinstance(geometry_hex, str) and len(geometry_hex) > 0:
            try:
                # Convert hex string back to QByteArray
                from PyQt6.QtCore import QByteArray
                geometry = QByteArray.fromHex(geometry_hex.encode())
                if not geometry.isEmpty():
                    self.main_window.restoreGeometry(geometry)
                else:
                    print("⚠️ Invalid geometry data (empty), skipping restore")
                    self.config_manager.set('window_geometry', None)
            except Exception as e:
                print(f"⚠️ Failed to restore window geometry: {e}")
                # Clear invalid geometry data
                self.config_manager.set('window_geometry', None)
        
        # Show the main window
        self.main_window.show()
    
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(sig, frame):
            print("\nShutting down gracefully...")
            # Schedule cleanup to run in the event loop
            asyncio.create_task(self.cleanup())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def cleanup(self):
        """Clean up resources before exit."""
        if self.main_window:
            # Save window geometry
            geometry = self.main_window.saveGeometry()
            self.config_manager.set('window_geometry', geometry.data().hex())
            
            # Close main window
            self.main_window.close()
        
        # Disconnect all devices
        if self.device_controller:
            connected_devices = list(self.device_controller._connected_devices.keys())
            for device_id in connected_devices:
                await self.device_controller.disconnect_device(device_id)
    
    async def run(self):
        """Run the application."""
        try:
            # Auto-discover devices on startup if enabled
            if self.config_manager.get('auto_discover', True):
                await self.device_controller.discover_devices(
                    timeout=self.config_manager.get('discovery_timeout', 10)
                )
            
            # Try to reconnect to last used device
            last_device = self.config_manager.get('last_device')
            if last_device:
                known_devices = self.config_manager.get_known_devices()
                if last_device in known_devices:
                    await self.device_controller.connect_device(last_device)
            
            # Initialization is complete, the Qt event loop will handle the rest
            # The main() function has already set up the event loop context
        
        except KeyboardInterrupt:
            print("Application interrupted by user")
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            await self.cleanup()

def handle_update():
    """Handle the --update command."""
    print("🔄 Starting ApplerGUI update...")
    try:
        # Try to download and run the update script
        update_url = "https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/update.sh"
        result = subprocess.run(['curl', '-fsSL', update_url], capture_output=True, text=True)
        if result.returncode == 0:
            # Run the update script
            result = subprocess.run(['bash'], input=result.stdout, text=True)
            if result.returncode == 0:
                print("✅ Update completed successfully!")
            else:
                print("❌ Update failed!")
                sys.exit(1)
        else:
            print("❌ Failed to download update script!")
            print("💡 Please check your internet connection and try again.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Update failed: {e}")
        sys.exit(1)

def handle_version():
    """Handle the --version command."""
    from . import __version__
    print(f"ApplerGUI version {__version__}")

def handle_help():
    """Handle the --help command."""
    print("""ApplerGUI - Control Apple TV and HomePod devices from Linux

Usage:
    applergui                Launch the GUI application
    applergui --update       Update ApplerGUI to the latest version
    applergui --version      Show version information
    applergui --help         Show this help message

ApplerGUI is a modern Linux GUI application for controlling Apple TV and HomePod devices.
Visit https://github.com/ZProLegend007/ApplerGUI for more information.
""")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='ApplerGUI - Control Apple TV and HomePod devices', add_help=False)
    parser.add_argument('--update', action='store_true', help='Update ApplerGUI to the latest version')
    parser.add_argument('--version', action='store_true', help='Show version information')
    parser.add_argument('--help', action='store_true', help='Show help message')
    
    args, unknown = parser.parse_known_args()
    
    # Handle command line arguments
    if args.help:
        handle_help()
        return
    
    if args.version:
        handle_version()
        return
    
    if args.update:
        handle_update()
        return
    
    # No special arguments, launch the GUI
    try:
        # Create and set up the application
        app = ApplerGUIApp()
        app.setup_application()
        app.setup_backend()
        app.setup_ui()
        app.setup_signal_handlers()
        
        # Run the application with async support
        with qasync.QEventLoop(app.app) as loop:
            loop.run_until_complete(app.run())
    
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()