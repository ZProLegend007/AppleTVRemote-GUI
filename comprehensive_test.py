#!/usr/bin/env python3
"""
Comprehensive test for the reverted ApplerGUI system
Tests all core functionality per the problem statement requirements
"""

import sys
import os
import tempfile
import shutil

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from ui.main_window import MainWindow, DiscoveryWorker
        print("✅ MainWindow and DiscoveryWorker imported successfully")
        
        from backend.config_manager import ConfigManager
        print("✅ ConfigManager imported successfully")
        
        from backend.device_controller import DeviceController
        print("✅ DeviceController imported successfully")
        
        from backend.pairing_manager import PairingManager
        print("✅ PairingManager imported successfully")
        
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
        from PyQt6.QtGui import QFont, QKeySequence, QShortcut
        print("✅ PyQt6 components imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_backend_functionality():
    """Test backend component functionality"""
    print("\n🧪 Testing backend functionality...")
    
    try:
        from backend.config_manager import ConfigManager
        from backend.device_controller import DeviceController
        from backend.pairing_manager import PairingManager
        
        # Test ConfigManager
        config = ConfigManager()
        config.set('test_key', 'test_value')
        value = config.get('test_key')
        assert value == 'test_value', f"Expected 'test_value', got '{value}'"
        print("✅ ConfigManager set/get functionality working")
        
        # Test DeviceController
        device_controller = DeviceController(config)
        print("✅ DeviceController instantiation working")
        
        # Test PairingManager
        pairing_manager = PairingManager(config)
        print("✅ PairingManager instantiation working")
        
        return True
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def test_discovery_parsing():
    """Test discovery functionality"""
    print("\n🧪 Testing discovery parsing...")
    
    try:
        from ui.main_window import DiscoveryWorker
        
        worker = DiscoveryWorker()
        
        # Test with sample atvremote output
        sample_output = '''Name: Living Room Apple TV
Address: 192.168.1.10
Model: Apple TV 4K
Identifier: ABCD-1234-EFGH
----
Name: Bedroom Apple TV
Address: 192.168.1.20
Model: Apple TV HD
Identifier: IJKL-5678-MNOP
----'''
        
        devices = worker.parse_scan_output(sample_output)
        
        assert len(devices) == 2, f"Expected 2 devices, got {len(devices)}"
        assert devices[0]['Name'] == 'Living Room Apple TV'
        assert devices[1]['Address'] == '192.168.1.20'
        
        print(f"✅ Discovery parsing working: {len(devices)} devices parsed")
        
        return True
    except Exception as e:
        print(f"❌ Discovery test error: {e}")
        return False

def test_main_window_creation():
    """Test MainWindow creation and styling"""
    print("\n🧪 Testing MainWindow creation...")
    
    try:
        from ui.main_window import MainWindow
        from backend.config_manager import ConfigManager
        from backend.device_controller import DeviceController
        from backend.pairing_manager import PairingManager
        from PyQt6.QtWidgets import QApplication
        
        # Set offscreen platform to avoid display issues
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        app = QApplication([])
        
        # Setup backend components
        config_manager = ConfigManager()
        device_controller = DeviceController(config_manager)
        pairing_manager = PairingManager(config_manager)
        
        # Create main window
        window = MainWindow(config_manager, device_controller, pairing_manager)
        
        # Test window properties
        assert window.windowTitle() == "Apple TV Remote GUI"
        assert window.size().width() == 300
        assert window.size().height() == 500
        
        # Test that black styling contains expected elements
        style = window.styleSheet()
        assert "#000000" in style, "Black styling not found"
        assert "background-color: #000000" in style, "Black background not found"
        
        print("✅ MainWindow creation and black styling working")
        
        return True
    except Exception as e:
        print(f"❌ MainWindow test error: {e}")
        return False

def test_main_launcher():
    """Test main.py launcher functionality"""
    print("\n🧪 Testing main.py launcher...")
    
    try:
        # Test that main.py can be imported without error
        import main
        print("✅ main.py imports successfully")
        
        # Check that it doesn't reference unified_launcher
        with open('main.py', 'r') as f:
            content = f.read()
            assert 'unified_launcher' not in content, "main.py still references unified_launcher"
            assert 'from ui.main_window import MainWindow' in content, "main.py doesn't import MainWindow"
            assert 'from backend.' in content, "main.py doesn't import backend modules"
        
        print("✅ main.py uses correct modular structure")
        
        return True
    except Exception as e:
        print(f"❌ Main launcher test error: {e}")
        return False

def test_app_structure():
    """Test that app structure matches requirements"""
    print("\n🧪 Testing app structure...")
    
    try:
        # Check required directories exist
        assert os.path.exists('ui/'), "ui/ directory not found"
        assert os.path.exists('backend/'), "backend/ directory not found"
        print("✅ ui/ and backend/ directories exist")
        
        # Check required files exist
        required_files = [
            'ui/main_window.py',
            'backend/config_manager.py', 
            'backend/device_controller.py',
            'backend/pairing_manager.py',
            'main.py',
            'install.sh',
            'update.sh'
        ]
        
        for file_path in required_files:
            assert os.path.exists(file_path), f"Required file {file_path} not found"
        
        print("✅ All required files exist")
        
        # Check MainWindow is simplified (should be much smaller than original)
        with open('ui/main_window.py', 'r') as f:
            lines = len(f.readlines())
            assert lines < 400, f"MainWindow too complex: {lines} lines (should be < 400)"
            
        print(f"✅ MainWindow is simplified: {lines} lines")
        
        return True
    except Exception as e:
        print(f"❌ App structure test error: {e}")
        return False

def test_launcher_script_template():
    """Test launcher script template"""
    print("\n🧪 Testing launcher script template...")
    
    try:
        assert os.path.exists('launcher_template.sh'), "launcher_template.sh not found"
        
        with open('launcher_template.sh', 'r') as f:
            content = f.read()
            
        # Check for required elements
        assert 'from ui.main_window import MainWindow' in content
        assert 'from backend.config_manager import ConfigManager' in content  
        assert 'from backend.device_controller import DeviceController' in content
        assert 'from backend.pairing_manager import PairingManager' in content
        assert 'export GTK_THEME="Adwaita"' in content
        assert 'export QT_STYLE_OVERRIDE=""' in content
        
        print("✅ Launcher script template contains required elements")
        
        return True
    except Exception as e:
        print(f"❌ Launcher script test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🍎 ApplerGUI Comprehensive Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_backend_functionality, 
        test_discovery_parsing,
        test_main_window_creation,
        test_main_launcher,
        test_app_structure,
        test_launcher_script_template
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System successfully reverted and working!")
        return True
    else:
        print("❌ Some tests failed - system needs fixes")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)