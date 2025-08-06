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
import tempfile
from pathlib import Path

# Suppress Qt verbose logging for clean debug output
os.environ['QT_LOGGING_RULES'] = '*=false'
os.environ['QT_DEBUG_PLUGINS'] = '0'
os.environ['QT_ASSUME_STDERR_HAS_CONSOLE'] = '0'
os.environ['QT_QUIET'] = '1'
os.environ['QT_NO_DEBUG_OUTPUT'] = '1'

# GUI imports - moved inside launch_gui function for conditional loading

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Backend and UI imports - moved inside launch_gui function for conditional loading

class ApplerGUIApp:
    """Main application class."""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.config_manager = None
        self.device_controller = None
        self.pairing_manager = None
        self.event_loop = None
    
    def setup_application(self):
        """Set up the Qt application."""
        # Import Qt classes when needed
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QCoreApplication
        from PyQt6.QtGui import QIcon
        
        # Set application properties
        QCoreApplication.setApplicationName("ApplerGUI")
        QCoreApplication.setApplicationVersion("1.0.0")
        QCoreApplication.setOrganizationName("ApplerGUI")
        QCoreApplication.setOrganizationDomain("github.com/ZProLegend007/ApplerGUI")
        
        # Create Qt application
        self.app = QApplication(sys.argv)
        self.app.setApplicationDisplayName("ApplerGUI")
        
        # Connect cleanup to app quit signal
        self.app.aboutToQuit.connect(self.sync_cleanup)
        
        # Set application icon if available
        icon_path = project_root / "resources" / "icons" / "app_icon.png"
        if icon_path.exists():
            from PyQt6.QtGui import QIcon
            app_icon = QIcon(str(icon_path))
            self.app.setWindowIcon(app_icon)
            print(f"✅ Application icon set from: {icon_path}")
        else:
            print(f"⚠️ Application icon not found at: {icon_path}")
    
    def setup_backend(self):
        """Set up backend components."""
        from .backend.config_manager import ConfigManager
        from .backend.device_controller import DeviceController
        from .backend.pairing_manager import PairingManager
        
        self.config_manager = ConfigManager()
        # DeviceController will be initialized later after event loop is set up
        self.device_controller = None
        self.pairing_manager = PairingManager(self.config_manager)
    
    def setup_device_controller(self):
        """Set up device controller after event loop is ready."""
        from .backend.device_controller import DeviceController
        self.device_controller = DeviceController(self.config_manager, self.event_loop)
    
    def setup_ui(self):
        """Set up the main window and UI."""
        from .ui.main_window import ResponsiveMainWindow
        
        # Device controller will be initialized after event loop is ready
        self.main_window = ResponsiveMainWindow(
            self.config_manager,
            self.device_controller,  # Initially None, will be set later
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
            # Use Qt's quit mechanism for proper shutdown
            if self.app:
                self.app.quit()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def sync_cleanup(self):
        """Synchronous cleanup for Qt signals."""
        if self.main_window:
            # Save window geometry
            geometry = self.main_window.saveGeometry()
            self.config_manager.set('window_geometry', geometry.data().hex())
    
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
        """Run the application initialization."""
        try:
            # Skip auto-discovery on startup to avoid event loop conflicts
            # Manual discovery via UI uses a separate thread mechanism and works reliably
            print("🚀 ApplerGUI started successfully")
            print("💡 Use the Discovery tab to find and connect to Apple TV devices")
            
            # Try to reconnect to last used device if available
            last_device = self.config_manager.get('last_device')
            if last_device:
                known_devices = self.config_manager.get_known_devices()
                if last_device in known_devices:
                    print(f"🔄 Attempting to reconnect to last device: {last_device}")
                    try:
                        await self.device_controller.connect_device(last_device)
                        print(f"✅ Reconnected to {last_device}")
                    except Exception as e:
                        print(f"⚠️ Failed to reconnect to last device: {e}")
            
            print("✅ ApplerGUI initialization complete - app will run until closed by user")
        
        except KeyboardInterrupt:
            print("Application interrupted by user")
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            await self.cleanup()

def handle_update():
    """Handle the --update command with proper process management and signal handling."""
    print("🔄 Starting ApplerGUI update...")
    temp_script = None
    
    # Set up clean signal handling for Ctrl-C
    def signal_handler(sig, frame):
        print("\n🛑 Update interrupted by user")
        print("✅ Cleanup completed. Update cancelled.")
        # Clean up temp file
        if temp_script and os.path.exists(temp_script):
            try:
                os.unlink(temp_script)
            except Exception:
                pass
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Try to download and run the update script
        update_url = "https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/update.sh"
        result = subprocess.run(['curl', '-fsSL', update_url], capture_output=True, text=True)
        if result.returncode == 0:
            # Write the update script to a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(result.stdout)
                temp_script = f.name
            
            # Make the script executable
            os.chmod(temp_script, 0o755)
            
            # Set environment variables to help the update script identify the context
            env = os.environ.copy()
            env['APPLERGUI_UPDATE_MODE'] = '1'
            env['APPLERGUI_PARENT_PID'] = str(os.getpid())
            
            # Run the update script with proper signal handling
            # Use exec to replace current process to avoid parent detection issues
            try:
                os.execve('/bin/bash', ['bash', temp_script], env)
            except OSError:
                # Fallback to subprocess if exec fails
                result = subprocess.run(['bash', temp_script], env=env)
                if result.returncode == 0:
                    print("✅ Update completed successfully!")
                else:
                    print("❌ Update failed!")
                    sys.exit(1)
        else:
            print("❌ Failed to download update script!")
            print("💡 Please check your internet connection and try again.")
            sys.exit(1)
    except KeyboardInterrupt:
        # Handle Ctrl-C gracefully - should not reach here due to signal handler
        print("\n🛑 Update interrupted by user")
        print("✅ Update cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Update failed: {e}")
        sys.exit(1)
    finally:
        # Clean up temporary file
        if temp_script and os.path.exists(temp_script):
            try:
                os.unlink(temp_script)
            except Exception:
                pass  # Ignore cleanup errors

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

def launch_gui():
    """Launch the GUI application."""
    # Import GUI components only when needed
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QCoreApplication, QLoggingCategory, QTimer
        from PyQt6.QtGui import QPixmap, QIcon
        import qasync
    except ImportError as e:
        print(f"❌ Failed to import GUI dependencies: {e}")
        print("💡 Please install PyQt6: pip install PyQt6")
        sys.exit(1)
    
    # SUPPRESS ALL Qt logging categories
    QLoggingCategory.setFilterRules("*=false")

    from .ui.main_window import ResponsiveMainWindow
    
    # Create and set up the application
    app = ApplerGUIApp()
    app.setup_application()
    app.setup_backend()
    app.setup_signal_handlers()
    
    # Initialize async event loop integration
    loop = qasync.QEventLoop(app.app)
    asyncio.set_event_loop(loop)
    app.event_loop = loop
    
    # Set up device controller with event loop
    app.setup_device_controller()
    
    # Set up UI after backend is ready
    app.setup_ui()
    
    # Start the Qt application
    try:
        # Run the Qt application with the async event loop
        with loop:
            # Delay initialization to avoid startup race conditions
            init_timer = QTimer()
            init_timer.timeout.connect(lambda: loop.create_task(app.run()))
            init_timer.setSingleShot(True)
            init_timer.start(250)  # Increased delay for stability
            
            # Run the application - use exec() directly, not run_until_complete
            exit_code = app.app.exec()
            sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)

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
        launch_gui()
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
