#!/usr/bin/env python3
"""
Test the main application with new UI to ensure compatibility.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication, QTimer
from ui.main_window import MainWindow
from backend.config_manager import ConfigManager
from backend.device_controller import DeviceController
from backend.pairing_manager import PairingManager

def main():
    """Test the main application."""
    # Set application properties
    QCoreApplication.setApplicationName("ApplerGUI")
    QCoreApplication.setApplicationVersion("1.0.0")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("ApplerGUI")
    
    try:
        # Create backend components
        config_manager = ConfigManager()
        device_controller = DeviceController(config_manager)
        pairing_manager = PairingManager(config_manager)
        
        # Create main window with new UI
        main_window = MainWindow(config_manager, device_controller, pairing_manager)
        main_window.show()
        
        # Take screenshot after delay
        QTimer.singleShot(1000, lambda: take_screenshot("main_app_test"))
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