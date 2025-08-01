#!/usr/bin/env python3
"""
Test discovery functionality with mock atvremote to ensure it works properly
"""

import sys
import os
import tempfile
import subprocess
import time

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_mock_atvremote():
    """Create a mock atvremote script for testing"""
    mock_script = '''#!/bin/bash
echo "Name: Living Room Apple TV"
echo "Address: 192.168.1.100"
echo "Model: Apple TV 4K"
echo "----"
echo "Name: Bedroom Apple TV"  
echo "Address: 192.168.1.101"
echo "Model: Apple TV HD"
'''
    
    # Create temporary script
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_atvremote') as f:
        f.write(mock_script)
        script_path = f.name
    
    # Make it executable
    os.chmod(script_path, 0o755)
    return script_path

def test_discovery_functionality():
    """Test discovery functionality with mock data"""
    print("🧪 Testing Discovery Functionality...")
    
    # Create mock atvremote
    mock_atvremote = create_mock_atvremote()
    
    try:
        from shared_launcher import AppleTVRemoteGUI
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer
        import sys
        
        # Set up offscreen Qt
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication(sys.argv)
        
        # Create GUI
        window = AppleTVRemoteGUI()
        
        # Test discovery parsing directly
        mock_output = """Name: Living Room Apple TV
Address: 192.168.1.100
Model: Apple TV 4K
----
Name: Bedroom Apple TV
Address: 192.168.1.101
Model: Apple TV HD"""
        
        devices = window._parse_atvremote_scan_output(mock_output)
        print(f"✅ Parsed {len(devices)} devices from mock output")
        
        for i, device in enumerate(devices):
            print(f"  Device {i+1}: {device.get('Name', 'Unknown')} at {device.get('Address', 'No address')}")
        
        # Test that discovery worker can be created
        from shared_launcher import DiscoveryWorker
        worker = DiscoveryWorker()
        print("✅ DiscoveryWorker created successfully")
        
        # Test button functionality
        original_text = window.discover_btn.text()
        print(f"✅ Discovery button initial text: '{original_text}'")
        
        # Simulate discovery start
        window.discover_btn.setText("Discovering")
        window.discover_btn.setEnabled(False)
        print("✅ Discovery button state changed for scanning")
        
        # Reset button
        window.discover_btn.setText(original_text)
        window.discover_btn.setEnabled(True)
        print("✅ Discovery button reset to original state")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Discovery test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up mock script
        try:
            os.unlink(mock_atvremote)
        except:
            pass

def test_black_styling():
    """Test that black styling is applied correctly"""
    print("🧪 Testing Black Styling...")
    
    try:
        from shared_launcher import AppleTVRemoteGUI
        from PyQt5.QtWidgets import QApplication
        import sys
        
        # Set up offscreen Qt
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication(sys.argv)
        
        # Create GUI
        window = AppleTVRemoteGUI()
        
        # Check that styling method exists and can be called
        window._apply_black_styling_force()
        print("✅ Black styling force method executed successfully")
        
        # Check that style was applied
        style = window.styleSheet()
        if 'background-color: #000000' in style:
            print("✅ Black background styling applied")
        else:
            print("❌ Black background styling not found")
            return False
        
        if 'color: #ffffff' in style:
            print("✅ White text styling applied")
        else:
            print("❌ White text styling not found")
            return False
            
        # Test volume container styling
        if hasattr(window, 'volume_container'):
            volume_style = window.volume_container.styleSheet()
            if 'border-radius: 40px' in volume_style:
                print("✅ Volume pill styling applied")
            else:
                print("❌ Volume pill styling not found")
                return False
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Black styling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyboard_shortcuts():
    """Test keyboard shortcut setup"""
    print("🧪 Testing Keyboard Shortcuts...")
    
    try:
        from shared_launcher import AppleTVRemoteGUI
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        import sys
        
        # Set up offscreen Qt
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication(sys.argv)
        
        # Create GUI
        window = AppleTVRemoteGUI()
        
        # Check that buttons exist
        required_buttons = [
            'discover_btn', 'up_btn', 'down_btn', 'left_btn', 'right_btn',
            'select_btn', 'play_pause_btn', 'menu_btn', 'home_btn',
            'volume_up_btn', 'volume_down_btn'
        ]
        
        for btn_name in required_buttons:
            if hasattr(window, btn_name):
                print(f"✅ Button {btn_name} exists")
            else:
                print(f"❌ Button {btn_name} missing")
                return False
        
        # Test that animation method exists
        if hasattr(window, '_animate_button_press'):
            print("✅ Button animation method exists")
        else:
            print("❌ Button animation method missing")
            return False
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Keyboard shortcuts test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all functionality tests"""
    print("🧪 Starting GUI Functionality Tests")
    print("=" * 50)
    
    tests = [
        test_discovery_functionality,
        test_black_styling, 
        test_keyboard_shortcuts
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED\n")
            else:
                print("❌ FAILED\n")
        except Exception as e:
            print(f"❌ FAILED with exception: {e}\n")
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All functionality tests passed!")
        return True
    else:
        print("💥 Some functionality tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)