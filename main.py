#!/usr/bin/env python3
"""
Apple TV Remote GUI - Direct Entry Point
Uses proper modular structure with ui/ and backend/ directories
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ui.main_window import MainWindow
    from backend.config_manager import ConfigManager
    from backend.device_controller import DeviceController  
    from backend.pairing_manager import PairingManager
    from PyQt6.QtWidgets import QApplication
    
    def main():
        """Main entry point"""
        app = QApplication(sys.argv)
        
        # Setup backend components
        config_manager = ConfigManager()
        device_controller = DeviceController(config_manager)
        pairing_manager = PairingManager(config_manager)
        
        # Create main window
        window = MainWindow(config_manager, device_controller, pairing_manager)
        window.show()
        
        print('✓ ApplerGUI launched successfully')
        sys.exit(app.exec())
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Ensure all modules exist in ui/ and backend/ directories")
    sys.exit(1)
except Exception as e:
    print(f"❌ Launch error: {e}")
    sys.exit(1)