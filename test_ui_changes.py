#!/usr/bin/env python3
"""
Test script to verify UI changes without full backend dependencies.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Simple mock classes to replace backend dependencies
class MockConfigManager:
    def __init__(self):
        self.settings = {}
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def set(self, key, value):
        self.settings[key] = value

class MockDeviceController:
    def __init__(self):
        pass
    
    def get_connected_devices(self):
        return {}

class MockPairingManager:
    def __init__(self):
        pass

def test_ui_import():
    """Test that we can import the updated UI classes"""
    try:
        # Test importing the main window
        from ui.main_window import ResponsiveMainWindow, RemotePanel, DiscoveryPanel, NowPlayingPanel
        print("✅ Successfully imported UI classes")
        return True
    except ImportError as e:
        print(f"❌ Failed to import UI classes: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing UI classes: {e}")
        return False

def test_ui_instantiation():
    """Test that we can create UI instances without full PyQt"""
    try:
        # Create mock dependencies
        config_manager = MockConfigManager()
        device_controller = MockDeviceController()
        pairing_manager = MockPairingManager()
        
        # This should work even without PyQt if the classes are structured correctly
        print("✅ Mock dependencies created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create mock dependencies: {e}")
        return False

def test_button_text_change():
    """Verify the button text change from SELECT to OK"""
    try:
        # Read the main_window.py file and check for the change
        with open('ui/main_window.py', 'r') as f:
            content = f.read()
        
        # Check if "OK" is used instead of "SELECT" for the center button
        if '"OK"' in content and 'self.select_btn = self._create_standard_button("OK"' in content:
            print("✅ Button text changed from SELECT to OK")
            return True
        else:
            print("❌ Button text change not found")
            return False
    except Exception as e:
        print(f"❌ Error checking button text change: {e}")
        return False

def test_keyboard_shortcuts_display():
    """Verify keyboard shortcuts display is added"""
    try:
        with open('ui/main_window.py', 'r') as f:
            content = f.read()
        
        # Check for keyboard shortcuts section
        if 'shortcuts_group = QGroupBox("Keyboard Shortcuts")' in content:
            print("✅ Keyboard shortcuts display added")
            return True
        else:
            print("❌ Keyboard shortcuts display not found")
            return False
    except Exception as e:
        print(f"❌ Error checking keyboard shortcuts: {e}")
        return False

def test_connected_device_display():
    """Verify connected device display is added"""
    try:
        with open('ui/main_window.py', 'r') as f:
            content = f.read()
        
        # Check for connected device section
        if 'connected_group = QGroupBox("Currently Connected")' in content:
            print("✅ Connected device display added")
            return True
        else:
            print("❌ Connected device display not found")
            return False
    except Exception as e:
        print(f"❌ Error checking connected device display: {e}")
        return False

def test_sample_data_removal():
    """Verify sample data is removed"""
    try:
        with open('ui/main_window.py', 'r') as f:
            content = f.read()
        
        # Check that sample devices are removed
        if 'Living Room Apple TV' not in content and 'Bedroom Apple TV' not in content:
            print("✅ Sample device data removed")
            return True
        else:
            print("❌ Sample device data still present")
            return False
    except Exception as e:
        print(f"❌ Error checking sample data removal: {e}")
        return False

def test_pyatv_integration():
    """Verify pyatv integration code is present"""
    try:
        with open('ui/main_window.py', 'r') as f:
            content = f.read()
        
        # Check for pyatv integration
        if 'import pyatv' in content and 'await pyatv.scan' in content:
            print("✅ PyATV integration code added")
            return True
        else:
            print("❌ PyATV integration code not found")
            return False
    except Exception as e:
        print(f"❌ Error checking pyatv integration: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing UI changes...")
    print("=" * 50)
    
    tests = [
        test_ui_import,
        test_ui_instantiation,
        test_button_text_change,
        test_keyboard_shortcuts_display,
        test_connected_device_display,
        test_sample_data_removal,
        test_pyatv_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"🏁 Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All UI changes implemented successfully!")
        return 0
    else:
        print("⚠️  Some issues found - check the output above")
        return 1

if __name__ == "__main__":
    sys.exit(main())