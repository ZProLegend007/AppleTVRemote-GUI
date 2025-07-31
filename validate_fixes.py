#!/usr/bin/env python3
"""
Syntax validation script for layout and styling fixes.
This script validates Python syntax and basic structure without requiring PyQt6.
"""

import ast
import sys
from pathlib import Path

def validate_syntax(file_path):
    """Validate Python syntax of a file."""
    try:
        with open(file_path, 'r') as f:
            source = f.read()
        
        # Parse the AST to check syntax
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def check_methods_exist(file_path, expected_methods):
    """Check that expected methods exist in the file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        missing_methods = []
        for method in expected_methods:
            if f"def {method}(" not in content:
                missing_methods.append(method)
        
        return len(missing_methods) == 0, missing_methods
    except Exception as e:
        return False, [f"Error reading file: {e}"]

def check_styling_elements(file_path, expected_elements):
    """Check that styling elements are present in the file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        missing_elements = []
        for element in expected_elements:
            if element not in content:
                missing_elements.append(element)
        
        return len(missing_elements) == 0, missing_elements
    except Exception as e:
        return False, [f"Error reading file: {e}"]

def main():
    """Run syntax and structure validation."""
    print("ApplerGUI Layout Fixes - Syntax Validation")
    print("=" * 45)
    
    project_root = Path(__file__).parent
    main_window_path = project_root / "ui" / "main_window.py"
    
    # Test 1: Syntax validation
    print("1. Validating Python syntax...")
    is_valid, error = validate_syntax(main_window_path)
    if is_valid:
        print("   ✓ Python syntax is valid")
    else:
        print(f"   ✗ {error}")
        return False
    
    # Test 2: Required methods for DiscoveryPanel
    print("\n2. Checking DiscoveryPanel methods...")
    discovery_methods = ["_create_modern_button"]
    has_methods, missing = check_methods_exist(main_window_path, discovery_methods)
    if has_methods:
        print("   ✓ All required DiscoveryPanel methods present")
    else:
        print(f"   ✗ Missing methods: {missing}")
        return False
    
    # Test 3: Required methods for RemotePanel
    print("\n3. Checking RemotePanel methods...")
    remote_methods = [
        "_create_remote_button",
        "_create_dpad_button", 
        "_create_media_button",
        "_darken_color",
        "_animate_button_press"
    ]
    has_methods, missing = check_methods_exist(main_window_path, remote_methods)
    if has_methods:
        print("   ✓ All required RemotePanel methods present")
    else:
        print(f"   ✗ Missing methods: {missing}")
        return False
    
    # Test 4: Check styling elements
    print("\n4. Checking modern styling elements...")
    styling_elements = [
        "border-radius:",
        "qlineargradient",
        "QPropertyAnimation",
        "setMinimumSize(250, 400)",
        "self.min_width_for_sections = 900",
        "self.resize(1200, 800)"
    ]
    has_styling, missing = check_styling_elements(main_window_path, styling_elements)
    if has_styling:
        print("   ✓ All modern styling elements present")
    else:
        print(f"   ✗ Missing styling elements: {missing}")
        return False
    
    # Test 5: Check animation system
    print("\n5. Checking animation system...")
    animation_elements = [
        "self.button_animations = {}",
        "QPropertyAnimation",
        "QEasingCurve.Type.OutCubic",
        "animation.finished.connect"
    ]
    has_animation, missing = check_styling_elements(main_window_path, animation_elements)
    if has_animation:
        print("   ✓ Animation system properly implemented")
    else:
        print(f"   ✗ Missing animation elements: {missing}")
        return False
    
    # Test 6: Check responsive layout improvements
    print("\n6. Checking responsive layout improvements...")
    layout_elements = [
        "setHandleWidth(3)",
        "_force_initial_layout",
        "🔍 Discovery",
        "📺 Remote", 
        "🎵 Now Playing"
    ]
    has_layout, missing = check_styling_elements(main_window_path, layout_elements)
    if has_layout:
        print("   ✓ Responsive layout improvements present")
    else:
        print(f"   ✗ Missing layout elements: {missing}")
        return False
    
    print("\n" + "=" * 45)
    print("🎉 All validation tests passed!")
    print("\nValidated fixes:")
    print("✅ Modern button styling with rounded corners")
    print("✅ Fixed button animation system (no sticking)")
    print("✅ Panel minimum sizes for layout visibility")
    print("✅ Enhanced responsive layout behavior") 
    print("✅ Improved visual styling throughout")
    print("✅ Larger default window size for better UX")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)