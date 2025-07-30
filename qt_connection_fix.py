#!/usr/bin/env python3
"""
Qt Connection Fix Script for ApplerGUI
Ensures proper signal connection error handling
"""

import sys
import os
from pathlib import Path

def fix_qt_connections():
    """Fix any potential Qt signal connection issues"""
    
    print("🔧 Checking Qt signal connections...")
    
    # Check if we can import Qt modules
    try:
        from PyQt6.QtCore import QObject, pyqtSignal
        print("✓ PyQt6 imports successful")
    except ImportError as e:
        print(f"✗ PyQt6 import failed: {e}")
        return False
    
    # Test signal connection functionality
    try:
        class TestSignalClass(QObject):
            test_signal = pyqtSignal(str)
        
        test_obj = TestSignalClass()
        
        def test_handler(message):
            print(f"Test signal received: {message}")
        
        # Test connection
        test_obj.test_signal.connect(test_handler)
        test_obj.test_signal.emit("test message")
        
        print("✓ Qt signal connections working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Qt signal connection test failed: {e}")
        return False

def check_pairing_manager_signals():
    """Check PairingManager signal connections specifically"""
    
    print("🔧 Checking PairingManager signals...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.pairing_manager import PairingManager
        from backend.config_manager import ConfigManager
        
        # Create instances
        config = ConfigManager()
        pm = PairingManager(config)
        
        # Check all required signals exist
        required_signals = [
            'pairing_started',
            'pairing_pin_required', 
            'pairing_device_code_required',
            'pairing_progress',
            'pairing_completed',
            'pairing_failed'
        ]
        
        missing_signals = []
        for signal_name in required_signals:
            if not hasattr(pm, signal_name):
                missing_signals.append(signal_name)
        
        if missing_signals:
            print(f"✗ Missing signals: {missing_signals}")
            return False
        
        # Test signal connections
        def test_callback(*args):
            pass
        
        for signal_name in required_signals:
            signal = getattr(pm, signal_name)
            signal.connect(test_callback)
        
        print("✓ All PairingManager signals connected successfully")
        return True
        
    except Exception as e:
        print(f"✗ PairingManager signal check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main connection check and fix function"""
    
    print("ApplerGUI Qt Connection Fix")
    print("="*40)
    
    success = True
    
    # Check basic Qt functionality
    if not fix_qt_connections():
        success = False
    
    # Check PairingManager specifically
    if not check_pairing_manager_signals():
        success = False
    
    if success:
        print("\n✓ All Qt connections are working properly")
        print("✓ No fixes needed")
        return 0
    else:
        print("\n✗ Some Qt connection issues detected")
        print("✗ Please check your PyQt6 installation")
        return 1

if __name__ == "__main__":
    sys.exit(main())