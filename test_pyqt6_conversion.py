#!/usr/bin/env python3
"""
Test unified launch consistency and PyQt6 conversion
"""

import sys
import os
import subprocess

def test_import_syntax():
    """Test that imports work without syntax errors"""
    print("🧪 Testing import syntax...")
    
    try:
        # Test unified_launcher imports
        exec("from unified_launcher import unified_main")
        print("✅ unified_launcher imports correctly")
        
        # Test main.py imports
        with open('main.py', 'r') as f:
            main_content = f.read()
        exec(main_content)
        print("✅ main.py syntax is correct")
        
        # Test bin/applergui imports  
        with open('bin/applergui', 'r') as f:
            applergui_content = f.read()
        exec(applergui_content)
        print("✅ bin/applergui syntax is correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Import syntax error: {e}")
        return False

def test_pyqt6_conversion():
    """Test that PyQt6 syntax is correctly used"""
    print("\n🧪 Testing PyQt6 conversion...")
    
    with open('unified_launcher.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('PyQt6.QtCore', 'PyQt6 core imports'),
        ('PyQt6.QtWidgets', 'PyQt6 widgets imports'),
        ('PyQt6.QtGui', 'PyQt6 GUI imports'),
        ('Qt.Key.Key_Up', 'PyQt6 enum syntax'),
        ('app.exec()', 'PyQt6 exec syntax'),
    ]
    
    all_passed = True
    for check, description in checks:
        if check in content:
            print(f"✅ {description}")
        else:
            print(f"❌ Missing: {description}")
            all_passed = False
    
    # Check that PyQt5 is NOT used
    pyqt5_checks = ['PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui', 'app.exec_()']
    for check in pyqt5_checks:
        if check in content:
            print(f"❌ Found PyQt5 syntax: {check}")
            all_passed = False
    
    if all_passed:
        print("✅ PyQt6 conversion complete")
    
    return all_passed

def test_launch_consistency():
    """Test that both launch methods use identical imports"""
    print("\n🧪 Testing launch consistency...")
    
    with open('main.py', 'r') as f:
        main_content = f.read()
    
    with open('bin/applergui', 'r') as f:
        applergui_content = f.read()
    
    # Both should import from unified_launcher
    if 'from unified_launcher import unified_main' in main_content:
        print("✅ main.py uses unified_launcher")
    else:
        print("❌ main.py does not use unified_launcher")
        return False
    
    if 'from unified_launcher import unified_main' in applergui_content:
        print("✅ bin/applergui uses unified_launcher")
    else:
        print("❌ bin/applergui does not use unified_launcher")
        return False
    
    # Both should call unified_main()
    if 'unified_main()' in main_content:
        print("✅ main.py calls unified_main()")
    else:
        print("❌ main.py does not call unified_main()")
        return False
    
    if 'unified_main()' in applergui_content:
        print("✅ bin/applergui calls unified_main()")
    else:
        print("❌ bin/applergui does not call unified_main()")
        return False
    
    print("✅ Launch consistency verified")
    return True

def test_backup_fix():
    """Test that update script removes previous backups"""
    print("\n🧪 Testing backup fix...")
    
    with open('update.sh', 'r') as f:
        content = f.read()
    
    if 'rm -rf "$APP_DIR".backup.*' in content:
        print("✅ Update script removes previous backups")
        return True
    else:
        print("❌ Update script does not remove previous backups")
        return False

def main():
    """Run all tests"""
    print("🍎 Testing PyQt6 Conversion and Unified Launch Fixes")
    print("=" * 60)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    results = []
    results.append(test_import_syntax())
    results.append(test_pyqt6_conversion())
    results.append(test_launch_consistency())
    results.append(test_backup_fix())
    
    print("\n" + "=" * 60)
    if all(results):
        print("🎉 All tests PASSED!")
        print("✅ PyQt6 conversion complete")
        print("✅ Unified launch process implemented")
        print("✅ Backup management fixed")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())