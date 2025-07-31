#!/usr/bin/env python3
"""
Test script for the new responsive three-section layout.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication
from ui.main_window_new import ResponsiveMainWindow

class DummyConfigManager:
    """Dummy config manager for testing."""
    def __init__(self):
        self.config = {}
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value

def main():
    """Main entry point for testing."""
    # Set application properties
    QCoreApplication.setApplicationName("ApplerGUI Test")
    QCoreApplication.setApplicationVersion("1.0.0")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("ApplerGUI Test")
    
    # Create dummy config manager
    config_manager = DummyConfigManager()
    
    # Create and show main window
    main_window = ResponsiveMainWindow(config_manager)
    main_window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()