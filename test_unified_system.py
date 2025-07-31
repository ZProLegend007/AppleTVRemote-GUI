#!/usr/bin/env python3
"""
Test script to validate that the unified launch system works correctly.
Tests import consistency and launch path uniformity.
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_unified_launch_system():
    """Test that both main.py and bin/applergui use unified launch system"""
    print("🧪 Testing Unified Launch System...")
    
    # Test shared_launcher imports
    try:
        from shared_launcher import unified_main, setup_environment, AppleTVRemoteGUI, DiscoveryWorker
        print("✅ shared_launcher module imports successful")
    except Exception as e:
        print(f"❌ shared_launcher import failed: {e}")
        return False
    
    # Test main.py structure
    try:
        with open('main.py', 'r') as f:
            main_content = f.read()
        
        if 'from shared_launcher import unified_main' in main_content:
            print("✅ main.py imports from shared_launcher")
        else:
            print("❌ main.py does not import from shared_launcher")
            return False
            
        if 'unified_main()' in main_content:
            print("✅ main.py calls unified_main()")
        else:
            print("❌ main.py does not call unified_main()")
            return False
            
    except Exception as e:
        print(f"❌ main.py validation failed: {e}")
        return False
    
    # Test bin/applergui structure
    try:
        with open('bin/applergui', 'r') as f:
            applergui_content = f.read()
        
        if 'from shared_launcher import unified_main' in applergui_content:
            print("✅ bin/applergui imports from shared_launcher")
        else:
            print("❌ bin/applergui does not import from shared_launcher")
            return False
            
        if 'unified_main()' in applergui_content:
            print("✅ bin/applergui calls unified_main()")
        else:
            print("❌ bin/applergui does not call unified_main()")
            return False
            
    except Exception as e:
        print(f"❌ bin/applergui validation failed: {e}")
        return False
    
    return True

def test_discovery_fixes():
    """Test that discovery functionality has proper imports and structure"""
    print("🧪 Testing Discovery Fixes...")
    
    try:
        from shared_launcher import DiscoveryWorker
        print("✅ DiscoveryWorker can be imported")
        
        # Check that DiscoveryWorker has required methods
        worker = DiscoveryWorker()
        
        if hasattr(worker, 'run') and callable(getattr(worker, 'run')):
            print("✅ DiscoveryWorker has run method")
        else:
            print("❌ DiscoveryWorker missing run method")
            return False
            
        if hasattr(worker, 'finished') and hasattr(worker, 'error'):
            print("✅ DiscoveryWorker has required signals")
        else:
            print("❌ DiscoveryWorker missing required signals")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Discovery test failed: {e}")
        return False

def test_environment_setup():
    """Test that environment setup is consistent"""
    print("🧪 Testing Environment Setup...")
    
    try:
        from shared_launcher import setup_environment
        print("✅ setup_environment function available")
        
        # Test calling setup_environment (this should not fail)
        original_dir = os.getcwd()
        setup_environment()
        print("✅ setup_environment executes without errors")
        
        # Check that environment variables are set
        required_env_vars = ['PYTHONPATH', 'QT_QPA_PLATFORM', 'DISPLAY']
        for var in required_env_vars:
            if var in os.environ:
                print(f"✅ Environment variable {var} is set")
            else:
                print(f"❌ Environment variable {var} is missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Environment setup test failed: {e}")
        return False

def test_gui_class_structure():
    """Test that GUI class has required methods"""
    print("🧪 Testing GUI Class Structure...")
    
    try:
        from shared_launcher import AppleTVRemoteGUI
        print("✅ AppleTVRemoteGUI can be imported")
        
        # Check required methods exist
        required_methods = [
            '_setup_ui',
            '_setup_discovery', 
            '_setup_keyboard_shortcuts',
            '_apply_black_styling_force',
            '_safe_start_discovery',
            '_parse_atvremote_scan_output'
        ]
        
        for method_name in required_methods:
            if hasattr(AppleTVRemoteGUI, method_name):
                print(f"✅ AppleTVRemoteGUI has {method_name} method")
            else:
                print(f"❌ AppleTVRemoteGUI missing {method_name} method")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ GUI class structure test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting Unified Launch System Tests")
    print("=" * 50)
    
    tests = [
        test_unified_launch_system,
        test_discovery_fixes,
        test_environment_setup,
        test_gui_class_structure
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
        print("🎉 All tests passed! Unified launch system is working correctly.")
        return True
    else:
        print("💥 Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)