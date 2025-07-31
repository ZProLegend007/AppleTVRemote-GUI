#!/usr/bin/env python3
"""
Test script to validate the critical fixes without requiring full GUI.
Tests the core logic and button styling changes.
"""

import sys
import re
from pathlib import Path

def test_splitter_fixes():
    """Test that splitter layout fixes are in place."""
    print("Testing splitter layout fixes...")
    
    # Read the main window file
    main_window_path = Path("ui/main_window.py")
    if not main_window_path.exists():
        print("✗ main_window.py not found")
        return False
    
    content = main_window_path.read_text()
    
    # Test 1: Check that panels are not added to both containers initially
    # Should not have the problematic dual-container setup
    dual_container_pattern = r'self\.tab_widget\.addTab\(self\.discovery_panel.*\n.*self\.tab_widget\.addTab\(self\.remote_panel.*\n.*self\.tab_widget\.addTab\(self\.now_playing_panel'
    if re.search(dual_container_pattern, content, re.MULTILINE):
        # Check if it's in the wrong place (initial setup vs. method)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'self.tab_widget.addTab(self.discovery_panel' in line:
                # Check if it's in _setup_ui (bad) or _move_panels_to_tabs (good)
                context_lines = lines[max(0, i-20):i+10]
                context = '\n'.join(context_lines)
                if 'def _setup_ui(' in context and 'def _move_panels_to_tabs(' not in context:
                    print("✗ Panels still being added to both containers in _setup_ui")
                    return False
    
    # Test 2: Check for improved _move_panels_to_splitter method
    if '_move_panels_to_splitter' not in content:
        print("✗ _move_panels_to_splitter method missing")
        return False
    
    # Check for the critical size setting with force refresh
    if 'self.splitter.setSizes([400, 400, 400])' not in content:
        print("✗ Missing critical splitter size setting")
        return False
    
    if 'QTimer.singleShot(10, lambda: self.splitter.setSizes([400, 400, 400]))' not in content:
        print("✗ Missing force refresh for splitter sizes")
        return False
    
    # Test 3: Check for enhanced debugging
    if 'Splitter count:' not in content or 'Discovery panel size:' not in content:
        print("✗ Missing enhanced debugging output")
        return False
    
    print("✓ Splitter layout fixes implemented correctly")
    return True

def test_colored_button_removal():
    """Test that all colored buttons have been removed."""
    print("\nTesting colored button removal...")
    
    main_window_path = Path("ui/main_window.py")
    content = main_window_path.read_text()
    
    # Test 1: Check for removed color parameters in button creation
    if 'def _create_remote_button(self, text, color,' in content:
        print("✗ Remote button creation still takes color parameter")
        return False
    
    # Test 2: Check for no colored hex codes in button styles
    problematic_colors = [
        r'#e74c3c',  # Red (MENU button)
        r'#3498db',  # Blue (HOME button) 
        r'#ff9500',  # Orange (media buttons)
        r'#e67e22',  # Orange gradient
        r'#d35400',  # Dark orange
        r'#4a90e2',  # Blue progress/sliders
        r'#357abd',  # Dark blue
        r'#007acc'   # Blue animation
    ]
    
    found_colors = []
    for pattern in problematic_colors:
        if re.search(pattern, content, re.IGNORECASE):
            found_colors.append(pattern.upper())
    
    if found_colors:
        print(f"✗ Found problematic colored elements: {found_colors}")
        return False
    
    # Test 3: Check button creation calls don't pass colors
    if '"MENU", "#e74c3c"' in content or '"HOME", "#3498db"' in content:
        print("✗ Button creation calls still passing colors")
        return False
    
    # Test 4: Check that clean neutral styling is used
    if 'background-color: #f8f8f8' not in content:
        print("✗ Missing clean neutral button background")
        return False
    
    if 'border: 1px solid #ccc' not in content:
        print("✗ Missing clean neutral button borders")
        return False
    
    print("✓ All colored buttons successfully removed")
    return True

def test_pin_dialog_cleanup():
    """Test that PIN dialog uses clean neutral styling."""
    print("\nTesting PIN dialog cleanup...")
    
    pin_dialog_path = Path("ui/pin_dialog.py")
    if not pin_dialog_path.exists():
        print("✗ pin_dialog.py not found")
        return False
    
    content = pin_dialog_path.read_text()
    
    # Test 1: Check for clean neutral styling
    if 'background: #f8f8f8' not in content:
        print("✗ Missing clean dialog background")
        return False
    
    # Test 2: Check that red validation border is removed
    if 'border: 2px solid red' in content:
        print("✗ Still using red validation border")
        return False
    
    # Test 3: Check for clean button creation method
    if '_create_clean_button' not in content:
        print("✗ Missing clean button creation method")
        return False
    
    print("✓ PIN dialog uses clean neutral styling")
    return True

def test_animation_cleanup():
    """Test that button animations use neutral colors."""
    print("\nTesting button animation cleanup...")
    
    main_window_path = Path("ui/main_window.py")
    content = main_window_path.read_text()
    
    # Check that animation doesn't use blue color
    if '#007acc' in content:
        print("✗ Button animation still uses blue color")
        return False
    
    # Check for neutral animation
    if 'background-color: #e0e0e0' not in content:
        print("✗ Missing neutral button animation")
        return False
    
    print("✓ Button animations use neutral colors")
    return True

def main():
    """Run all fix validation tests."""
    print("ApplerGUI Critical Fixes Validation")
    print("=" * 40)
    
    tests = [
        ("Splitter Layout Fixes", test_splitter_fixes),
        ("Colored Button Removal", test_colored_button_removal),
        ("PIN Dialog Cleanup", test_pin_dialog_cleanup),
        ("Animation Cleanup", test_animation_cleanup)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("Fix Validation Results:")
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All critical fixes validated successfully!")
        print("\nKey fixes implemented:")
        print("- ✅ Fixed splitter layout to prevent empty sizes []")
        print("- ✅ Removed all colored buttons (red MENU, blue HOME, orange media)")
        print("- ✅ Implemented clean neutral button styling")
        print("- ✅ Updated PIN dialog with neutral styling")
        print("- ✅ Fixed button animations to use neutral colors")
        print("- ✅ Enhanced debugging output for layout issues")
        return True
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)