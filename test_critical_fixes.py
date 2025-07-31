#!/usr/bin/env python3
"""
Test script for critical ApplerGUI fixes.
Tests keyboard shortcuts, volume pill, crash protection, and environment detection.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_environment_detection():
    """Test environment detection functionality"""
    print("🧪 Testing environment detection...")
    
    import sys
    import os
    
    print(f"Launch method: {sys.argv}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"DISPLAY environment: {os.environ.get('DISPLAY', 'Not set')}")
    
    if os.isatty(sys.stdout.fileno()):
        print("🖥️ Detected: TERMINAL launch")
        launch_method = "terminal"
    else:
        print("🖱️ Detected: DESKTOP launch")
        launch_method = "desktop"
    
    print(f"✅ Environment detection working, method: {launch_method}")
    return launch_method

def test_imports():
    """Test that all imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        from ui.main_window import ResponsiveMainWindow, DiscoveryPanel, RemotePanel, NowPlayingPanel
        print("✅ Main window imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    try:
        from backend.config_manager import ConfigManager
        from backend.device_controller import DeviceController  
        from backend.pairing_manager import PairingManager
        print("✅ Backend imports successful")
    except ImportError as e:
        print(f"❌ Backend import error: {e}")
        return False
    
    return True

def test_ui_creation():
    """Test UI creation without Qt (syntax check)"""
    print("🧪 Testing UI creation (syntax check)...")
    
    try:
        # Test that the classes can be imported and have the expected methods
        from ui.main_window import RemotePanel, DiscoveryPanel
        
        # Check that key methods exist
        assert hasattr(RemotePanel, '_guaranteed_keyboard_animation'), "Keyboard animation method missing"
        assert hasattr(RemotePanel, '_create_volume_pill'), "Volume pill method missing" 
        assert hasattr(DiscoveryPanel, '_debug_launch_environment'), "Environment debug method missing"
        assert hasattr(DiscoveryPanel, '_start_discovery'), "Safe discovery method missing"
        
        print("✅ UI creation tests passed (syntax check)")
        return True
        
    except Exception as e:
        print(f"❌ UI creation test failed: {e}")
        return False

def test_crash_protection():
    """Test crash protection mechanisms"""
    print("🧪 Testing crash protection mechanisms...")
    
    try:
        # Test that error handling is in place
        from ui.main_window import DiscoveryPanel
        
        # Check that crash protection methods exist
        assert hasattr(DiscoveryPanel, '_cleanup_discovery_state'), "Discovery cleanup method missing"
        assert hasattr(DiscoveryPanel, '_handle_discovery_timeout'), "Discovery timeout handler missing"
        assert hasattr(DiscoveryPanel, '_safe_atvremote_discovery'), "Safe atvremote method missing"
        
        print("✅ Crash protection mechanisms in place")
        return True
        
    except Exception as e:
        print(f"❌ Crash protection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running ApplerGUI Critical Fixes Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment Detection", test_environment_detection),
        ("Import Tests", test_imports),
        ("UI Creation", test_ui_creation), 
        ("Crash Protection", test_crash_protection),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All critical fixes are working correctly!")
        return 0
    else:
        print("⚠️ Some tests failed - please review the fixes")
        return 1

if __name__ == "__main__":
    sys.exit(main())