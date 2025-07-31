#!/usr/bin/env python3
"""
Test our new main window implementation with dummy backends.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication, QTimer, QObject

class DummyConfigManager:
    """Dummy config manager."""
    def __init__(self):
        self.config = {}
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value

class DummyDeviceController(QObject):
    """Dummy device controller."""
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager

class DummyPairingManager(QObject):
    """Dummy pairing manager."""
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager

def main():
    """Test the main application with dummy backends."""
    # Set application properties
    QCoreApplication.setApplicationName("ApplerGUI")
    QCoreApplication.setApplicationVersion("1.0.0")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("ApplerGUI")
    
    try:
        # Import our new main window
        from ui.main_window import MainWindow
        
        # Create dummy backend components
        config_manager = DummyConfigManager()
        device_controller = DummyDeviceController(config_manager)
        pairing_manager = DummyPairingManager(config_manager)
        
        # Create main window with new UI
        main_window = MainWindow(config_manager, device_controller, pairing_manager)
        main_window.show()
        
        # Take screenshot after delay
        QTimer.singleShot(1000, lambda: take_screenshot("final_app_test"))
        QTimer.singleShot(2000, lambda: app.quit())
        
        # Run the application
        app.exec()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

def take_screenshot(name):
    """Take a screenshot with the given name."""
    import subprocess
    try:
        subprocess.run([
            "scrot", "-z", f"/tmp/appgui_{name}.png"
        ], env={"DISPLAY": ":99"}, check=True)
        print(f"Screenshot saved: /tmp/appgui_{name}.png")
        return True
    except Exception as e:
        print(f"Failed to take screenshot: {e}")
        return False

if __name__ == "__main__":
    sys.exit(main())