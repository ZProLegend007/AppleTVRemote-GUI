"""
ApplerGUI - A modern Linux GUI application for controlling Apple TV and HomePod devices.
"""

__version__ = "1.0.0"
__author__ = "Zac"

from .main import main

# Store commit hash - will be set from saved commit file during installation
__commit__ = "unknown"

# Try to get commit hash from saved file first
try:
    import os
    
    # Try to get commit from saved file in installation directory
    install_dir = os.path.expanduser("~/.local/share/applergui")
    commit_file = os.path.join(install_dir, ".commit")
    
    if os.path.exists(commit_file):
        with open(commit_file, 'r') as f:
            saved_commit = f.read().strip()
            if saved_commit and len(saved_commit) == 40:  # Valid Git commit hash length
                __commit__ = saved_commit
except Exception:
    pass

# Fallback: Try to get commit hash from git if available (development mode)
if __commit__ == "unknown":
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