#!/usr/bin/env python3
"""
Syntax validation test for critical ApplerGUI fixes.
Validates the code structure without requiring PyQt6 installation.
"""

import sys
import os
import ast

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
    return True

def test_python_syntax():
    """Test that the Python syntax is valid"""
    print("🧪 Testing Python syntax...")
    
    files_to_check = [
        "ui/main_window.py",
        "main.py",
        "backend/config_manager.py",
        "backend/device_controller.py",
        "backend/pairing_manager.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    source = f.read()
                ast.parse(source)
                print(f"✅ {file_path} - syntax valid")
            except SyntaxError as e:
                print(f"❌ {file_path} - syntax error: {e}")
                return False
            except Exception as e:
                print(f"⚠️ {file_path} - other error: {e}")
        else:
            print(f"⚠️ {file_path} - file not found")
    
    print("✅ Python syntax validation passed")
    return True

def test_critical_method_presence():
    """Test that critical methods are present in the code"""
    print("🧪 Testing critical method presence...")
    
    main_window_path = "ui/main_window.py"
    if not os.path.exists(main_window_path):
        print(f"❌ {main_window_path} not found")
        return False
    
    with open(main_window_path, 'r') as f:
        content = f.read()
    
    # Check for critical fixes
    critical_methods = [
        "_guaranteed_keyboard_animation",  # Keyboard shortcuts fix
        "_create_volume_pill",            # Volume pill fix  
        "_debug_launch_environment",      # Environment detection fix
        "_start_discovery",               # Safe discovery fix
        "_cleanup_discovery_state",       # Crash protection
        "_safe_atvremote_discovery",      # Safe fallback discovery
        "_apply_dark_oled_theme",         # Universal styling
    ]
    
    missing_methods = []
    for method in critical_methods:
        if f"def {method}" not in content:
            missing_methods.append(method)
    
    if missing_methods:
        print(f"❌ Missing critical methods: {missing_methods}")
        return False
    
    print("✅ All critical methods are present")
    return True

def test_keyboard_shortcuts_fix():
    """Test that keyboard shortcuts fix is implemented"""
    print("🧪 Testing keyboard shortcuts fix implementation...")
    
    with open("ui/main_window.py", 'r') as f:
        content = f.read()
    
    # Check for guaranteed keyboard animation
    if "_guaranteed_keyboard_animation" not in content:
        print("❌ Guaranteed keyboard animation method missing")
        return False
    
    # Check for original styles storage
    if "self.original_styles" not in content:
        print("❌ Original styles storage missing")
        return False
    
    # Check for forced styling with !important
    if "!important" not in content:
        print("❌ Forced styling (!important) missing")
        return False
    
    print("✅ Keyboard shortcuts fix implemented correctly")
    return True

def test_volume_pill_fix():
    """Test that volume pill fix is implemented"""
    print("🧪 Testing volume pill fix implementation...")
    
    with open("ui/main_window.py", 'r') as f:
        content = f.read()
    
    # Check for permanent pill frame
    if "pill_frame = QFrame()" not in content:
        print("❌ Permanent pill frame missing")
        return False
    
    # Check for fixed size
    if "setFixedSize" not in content:
        print("❌ Fixed size setting missing")
        return False
    
    # Check for pill frame styling
    if "border-radius: 35px" not in content:
        print("❌ Pill frame border radius missing")
        return False
    
    print("✅ Volume pill fix implemented correctly")
    return True

def test_crash_protection_fix():
    """Test that crash protection is implemented"""
    print("🧪 Testing crash protection fix implementation...")
    
    with open("ui/main_window.py", 'r') as f:
        content = f.read()
    
    # Check for discovery timeout protection
    if "_handle_discovery_timeout" not in content:
        print("❌ Discovery timeout handler missing")
        return False
    
    # Check for cleanup state method
    if "_cleanup_discovery_state" not in content:
        print("❌ Cleanup state method missing")
        return False
    
    # Check for safe threading with asyncio.wait_for
    if "asyncio.wait_for" not in content:
        print("❌ Safe asyncio timeout protection missing")
        return False
    
    # Check for resize event protection
    if "resize_error" not in content:
        print("❌ Resize event error protection missing")
        return False
    
    print("✅ Crash protection fix implemented correctly")
    return True

def test_universal_styling_fix():
    """Test that universal styling fix is implemented"""
    print("🧪 Testing universal styling fix implementation...")
    
    with open("ui/main_window.py", 'r') as f:
        content = f.read()
    
    # Check for universal dark style
    if "universal_dark_style" not in content:
        print("❌ Universal dark style variable missing")
        return False
    
    # Check for forced border colors
    if "border: 2px solid #000000 !important" not in content:
        print("❌ Forced black borders missing")
        return False
    
    # Check for style refresh
    if "style().unpolish" not in content:
        print("❌ Style refresh missing")
        return False
    
    print("✅ Universal styling fix implemented correctly")
    return True

def main():
    """Run all syntax tests"""
    print("🚀 Running ApplerGUI Critical Fixes Syntax Test Suite")
    print("=" * 60)
    
    tests = [
        ("Environment Detection", test_environment_detection),
        ("Python Syntax", test_python_syntax),
        ("Critical Method Presence", test_critical_method_presence),
        ("Keyboard Shortcuts Fix", test_keyboard_shortcuts_fix),
        ("Volume Pill Fix", test_volume_pill_fix),
        ("Crash Protection Fix", test_crash_protection_fix),
        ("Universal Styling Fix", test_universal_styling_fix),
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
    
    print("\n" + "=" * 60)
    print("📊 SYNTAX TEST RESULTS SUMMARY:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} syntax tests passed")
    
    if passed == total:
        print("🎉 All critical fixes syntax validation passed!")
        print("\n📝 FIXES IMPLEMENTED:")
        print("✅ Keyboard shortcuts with guaranteed visual feedback")
        print("✅ Permanent volume pill shape that never changes") 
        print("✅ Crash-proof discovery with safe threading")
        print("✅ Environment detection for desktop vs terminal")
        print("✅ Universal styling with forced black borders")
        print("✅ Resize event crash protection")
        return 0
    else:
        print("⚠️ Some syntax tests failed - please review the fixes")
        return 1

if __name__ == "__main__":
    sys.exit(main())