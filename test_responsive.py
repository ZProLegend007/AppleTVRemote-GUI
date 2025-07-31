#!/usr/bin/env python3
"""
Test script to demonstrate responsive layout behavior.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
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

class ResponsiveTestWindow(QWidget):
    """Test window with controls to test responsive behavior."""
    
    def __init__(self):
        super().__init__()
        self.config_manager = DummyConfigManager()
        self.main_window = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup test controls."""
        self.setWindowTitle("Responsive Layout Test")
        self.setGeometry(100, 100, 300, 200)
        
        layout = QVBoxLayout(self)
        
        # Button to show wide layout
        wide_btn = QPushButton("Show Wide Layout (1400x800)")
        wide_btn.clicked.connect(self.show_wide_layout)
        layout.addWidget(wide_btn)
        
        # Button to show narrow layout  
        narrow_btn = QPushButton("Show Narrow Layout (800x600)")
        narrow_btn.clicked.connect(self.show_narrow_layout)
        layout.addWidget(narrow_btn)
        
        # Button to test PIN overlay
        pin_btn = QPushButton("Test PIN Overlay")
        pin_btn.clicked.connect(self.test_pin_overlay)
        layout.addWidget(pin_btn)
    
    def show_wide_layout(self):
        """Show wide three-section layout."""
        if self.main_window:
            self.main_window.close()
        
        self.main_window = ResponsiveMainWindow(self.config_manager)
        self.main_window.resize(1400, 800)
        self.main_window.show()
        
        # Take screenshot after a short delay
        QTimer.singleShot(1000, lambda: self.take_screenshot("wide"))
    
    def show_narrow_layout(self):
        """Show narrow tabbed layout."""
        if self.main_window:
            self.main_window.close()
        
        self.main_window = ResponsiveMainWindow(self.config_manager)
        self.main_window.resize(800, 600)
        self.main_window.show()
        
        # Take screenshot after a short delay
        QTimer.singleShot(1000, lambda: self.take_screenshot("narrow"))
    
    def test_pin_overlay(self):
        """Test the PIN overlay functionality."""
        if not self.main_window:
            self.show_wide_layout()
            
        # Simulate device pairing request
        device_info = {
            "name": "Test Apple TV",
            "model": "Apple TV 4K",
            "id": "test_device"
        }
        
        QTimer.singleShot(1500, lambda: self.main_window._handle_pairing_request(device_info))
        QTimer.singleShot(2500, lambda: self.take_screenshot("pin_overlay"))
    
    def take_screenshot(self, name):
        """Take a screenshot with the given name."""
        import subprocess
        try:
            subprocess.run([
                "scrot", "-z", f"/tmp/appgui_{name}.png"
            ], env={"DISPLAY": ":99"}, check=True)
            print(f"Screenshot saved: /tmp/appgui_{name}.png")
        except Exception as e:
            print(f"Failed to take screenshot: {e}")

def main():
    """Main entry point for testing."""
    # Set application properties
    QCoreApplication.setApplicationName("ApplerGUI Responsive Test")
    QCoreApplication.setApplicationVersion("1.0.0")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("ApplerGUI Responsive Test")
    
    # Create and show test window
    test_window = ResponsiveTestWindow()
    test_window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()