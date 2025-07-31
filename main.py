#!/usr/bin/env python3
"""
Apple TV Remote GUI - Main Entry Point
Forces consistent launch behavior for both desktop and terminal
"""

import sys
import os

def setup_environment():
    """Setup consistent environment"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    os.environ['PYTHONPATH'] = script_dir
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'
    os.environ['QT_QPA_PLATFORM'] = 'xcb'

def main():
    """Main application entry point"""
    print("🍎 Apple TV Remote GUI Starting...")
    
    # Setup environment consistently
    setup_environment()
    
    try:
        from PyQt5.QtWidgets import QApplication
        from applergui_main import AppleTVRemoteGUI
        
        app = QApplication(sys.argv)
        app.setApplicationName("Apple TV Remote GUI")
        
        # Create main window
        window = AppleTVRemoteGUI()
        window.show()
        
        # Apply styling after show
        window._apply_consistent_styling()
        
        # Run application
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()