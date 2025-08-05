"""
ApplerGUI - A modern Linux GUI application for controlling Apple TV and HomePod devices.
"""

__version__ = "1.0.0"
__author__ = "Zac"

from .main import main

# Store commit hash at build time - will be updated by the build process
__commit__ = "unknown"

# Try to get commit hash from git if available
try:
    import subprocess
    import os
    
    # Try to get commit from the package directory
    package_dir = os.path.dirname(os.path.abspath(__file__))
    result = subprocess.run(
        ['git', 'rev-parse', 'HEAD'], 
        cwd=package_dir,
        capture_output=True, 
        text=True, 
        timeout=5
    )
    if result.returncode == 0:
        __commit__ = result.stdout.strip()
except Exception:
    # If git is not available or fails, keep the default
    pass

__all__ = ["main", "__version__", "__commit__"]