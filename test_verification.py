#!/usr/bin/env python3
"""
Test that the files have correct syntax without importing PyQt6
"""

import sys
import os
import ast

def test_syntax_validity():
    """Test that all Python files have valid syntax"""
    print("🧪 Testing Python syntax...")
    
    files_to_test = [
        'unified_launcher.py',
        'main.py', 
        'bin/applergui'
    ]
    
    all_valid = True
    for file_path in files_to_test:
        try:
            with open(file_path, 'r') as f:
                source = f.read()
            ast.parse(source)
            print(f"✅ {file_path} has valid syntax")
        except SyntaxError as e:
            print(f"❌ {file_path} has syntax error: {e}")
            all_valid = False
        except Exception as e:
            print(f"❌ {file_path} error: {e}")
            all_valid = False
    
    return all_valid

def test_pyqt6_conversion():
    """Test that PyQt6 syntax is correctly used"""
    print("\n🧪 Testing PyQt6 conversion...")
    
    with open('unified_launcher.py', 'r') as f:
        content = f.read()
    
    # Check for PyQt6 imports
    pyqt6_imports = [
        'from PyQt6.QtCore import',
        'from PyQt6.QtWidgets import', 
        'from PyQt6.QtGui import'
    ]
    
    pyqt6_syntax = [
        'Qt.Key.Key_Up',
        'Qt.Key.Key_Down', 
        'Qt.Key.Key_Left',
        'Qt.Key.Key_Right',
        'app.exec()'  # PyQt6 uses exec() not exec_()
    ]
    
    # Check PyQt6 imports are present
    imports_found = 0
    for import_stmt in pyqt6_imports:
        if import_stmt in content:
            imports_found += 1
    
    if imports_found == len(pyqt6_imports):
        print("✅ All PyQt6 imports present")
    else:
        print(f"❌ Missing PyQt6 imports: {imports_found}/{len(pyqt6_imports)}")
        return False
    
    # Check PyQt6 syntax is used
    syntax_found = 0
    for syntax in pyqt6_syntax:
        if syntax in content:
            syntax_found += 1
    
    if syntax_found >= 3:  # At least some PyQt6 syntax present
        print("✅ PyQt6 syntax present")
    else:
        print(f"❌ PyQt6 syntax missing: {syntax_found}/{len(pyqt6_syntax)}")
        return False
    
    # Check that PyQt5 is NOT used
    pyqt5_patterns = ['PyQt5.', 'app.exec_()']
    for pattern in pyqt5_patterns:
        if pattern in content:
            print(f"❌ Found PyQt5 pattern: {pattern}")
            return False
    
    print("✅ PyQt6 conversion verified")
    return True

def test_unified_launch():
    """Test that both launch files use unified_launcher"""
    print("\n🧪 Testing unified launch...")
    
    # Check main.py
    with open('main.py', 'r') as f:
        main_content = f.read()
    
    # Check bin/applergui
    with open('bin/applergui', 'r') as f:
        applergui_content = f.read()
    
    checks = [
        (main_content, 'main.py', 'from unified_launcher import unified_main'),
        (main_content, 'main.py', 'unified_main()'),
        (applergui_content, 'bin/applergui', 'from unified_launcher import unified_main'),
        (applergui_content, 'bin/applergui', 'unified_main()'),
    ]
    
    all_passed = True
    for content, filename, pattern in checks:
        if pattern in content:
            print(f"✅ {filename} contains: {pattern}")
        else:
            print(f"❌ {filename} missing: {pattern}")
            all_passed = False
    
    # Check that neither uses shared_launcher anymore
    if 'from shared_launcher import' in main_content:
        print("❌ main.py still uses shared_launcher")
        all_passed = False
    
    if 'from shared_launcher import' in applergui_content:
        print("❌ bin/applergui still uses shared_launcher") 
        all_passed = False
    
    if all_passed:
        print("✅ Unified launch verified")
    
    return all_passed

def test_backup_management():
    """Test update script backup management"""
    print("\n🧪 Testing backup management...")
    
    with open('update.sh', 'r') as f:
        content = f.read()
    
    if 'rm -rf "$APP_DIR".backup.*' in content:
        print("✅ Update script removes previous backups")
        return True
    else:
        print("❌ Update script backup fix missing")
        return False

def test_requirements():
    """Test requirements.txt has PyQt6"""
    print("\n🧪 Testing requirements...")
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    if 'PyQt6>=' in content:
        print("✅ requirements.txt specifies PyQt6")
        return True
    else:
        print("❌ requirements.txt missing PyQt6")
        return False

def main():
    """Run all verification tests"""
    print("🍎 PyQt6 Conversion and Unified Launch Verification")
    print("=" * 60)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    tests = [
        test_syntax_validity,
        test_pyqt6_conversion, 
        test_unified_launch,
        test_backup_management,
        test_requirements
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    if all(results):
        print("🎉 ALL VERIFICATION TESTS PASSED!")
        print("")
        print("✅ PyQt6 conversion complete")
        print("✅ Unified launch process implemented")
        print("✅ Both main.py and applergui use identical launch process") 
        print("✅ Backup management fixed in update script")
        print("✅ Requirements updated for PyQt6")
        print("")
        print("🚀 Ready for deployment!")
        return 0
    else:
        print("❌ Some verification tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())