#!/bin/bash
# Installation script for AppleTVRemote-GUI

set -e

echo "AppleTVRemote-GUI Installation Script"
echo "====================================="

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8+ is required. Found Python $python_version"
    exit 1
fi

echo "✓ Python $python_version found"

# Check if we're on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "Warning: This application is designed for Linux. Continuing anyway..."
fi

# Install system dependencies based on distribution
echo "Installing system dependencies..."

if command -v apt-get &> /dev/null; then
    echo "Detected Debian/Ubuntu system"
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-venv python3-dev
    echo "✓ System dependencies installed (Debian/Ubuntu)"
elif command -v dnf &> /dev/null; then
    echo "Detected Fedora/RHEL system"
    sudo dnf install -y python3-pip python3-devel
    echo "✓ System dependencies installed (Fedora/RHEL)"
elif command -v pacman &> /dev/null; then
    echo "Detected Arch Linux system"
    sudo pacman -S --noconfirm python-pip
    echo "✓ System dependencies installed (Arch Linux)"
else
    echo "Unknown distribution. Please install python3-pip manually."
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user -r requirements.txt
echo "✓ Python dependencies installed"

# Run tests
echo "Running application tests..."
if python3 test_app.py; then
    echo "✓ All tests passed"
else
    echo "✗ Some tests failed, but installation may still work"
fi

# Make the application executable
chmod +x main.py

echo ""
echo "Installation complete!"
echo ""
echo "To run the application:"
echo "  python3 main.py"
echo ""
echo "To install globally (optional):"
echo "  sudo pip3 install -e ."
echo "  appletv-remote-gui"
echo ""
echo "For troubleshooting, check the README.md file."