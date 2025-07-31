#!/usr/bin/env python3
"""
Automated screenshot generation for the new UI.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication, QTimer
from ui.main_window_new import ResponsiveMainWindow

class DummyConfigManager:
    """Dummy config manager for testing."""
    def __init__(self):
        self.config = {}
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value

def take_screenshot(name):
    """Take a screenshot with the given name."""
    try:
        subprocess.run([
            "scrot", "-z", f"/tmp/appgui_{name}.png"
        ], env={"DISPLAY": ":99"}, check=True)
        print(f"Screenshot saved: /tmp/appgui_{name}.png")
        return True
    except Exception as e:
        print(f"Failed to take screenshot: {e}")
        return False

def main():
    """Main entry point for automated testing."""
    # Set application properties
    QCoreApplication.setApplicationName("ApplerGUI Test")
    QCoreApplication.setApplicationVersion("1.0.0")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("ApplerGUI Test")
    
    # Create config manager
    config_manager = DummyConfigManager()
    
    # Test 1: Wide layout (three sections)
    print("Testing wide layout...")
    main_window = ResponsiveMainWindow(config_manager)
    main_window.resize(1400, 800)
    main_window.show()
    
    # Process events and take screenshot
    app.processEvents()
    QTimer.singleShot(500, lambda: take_screenshot("wide_layout"))
    QTimer.singleShot(1000, lambda: test_narrow_layout(app, config_manager))
    
    # Run event loop
    app.exec()

def test_narrow_layout(app, config_manager):
    """Test narrow layout."""
    print("Testing narrow layout...")
    
    # Create new window with narrow size
    main_window = ResponsiveMainWindow(config_manager)
    main_window.resize(800, 600)
    main_window.show()
    
    # Process events and take screenshot
    app.processEvents()
    QTimer.singleShot(500, lambda: take_screenshot("narrow_layout"))
    QTimer.singleShot(1000, lambda: test_pin_overlay(app, main_window))

def test_pin_overlay(app, main_window):
    """Test PIN overlay."""
    print("Testing PIN overlay...")
    
    # Simulate device pairing request
    device_info = {
        "name": "Test Apple TV",
        "model": "Apple TV 4K",
        "id": "test_device"
    }
    
    main_window._handle_pairing_request(device_info)
    
    # Process events and take screenshot
    app.processEvents()
    QTimer.singleShot(500, lambda: take_screenshot("pin_overlay"))
    QTimer.singleShot(1000, lambda: app.quit())

if __name__ == "__main__":
    main()