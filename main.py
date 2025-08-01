#!/usr/bin/env python3
"""
Apple TV Remote GUI - Desktop Entry Point
Uses unified launcher for consistency (PyQt6)
"""

import sys
import os

# Import unified launcher and run
try:
    from unified_launcher import unified_main
    
    if __name__ == "__main__":
        unified_main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Ensure unified_launcher.py exists in the same directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Launch error: {e}")
    sys.exit(1)