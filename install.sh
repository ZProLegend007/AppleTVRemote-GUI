#!/bin/bash
# Enhanced one-line installer for ApplerGUI
# Usage: curl -sSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/install.sh | bash

set -e  # Exit on any error

echo "🍎 ApplerGUI One-Line Installer"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "Please don't run this installer as root/sudo!"
    print_status "Run it as your regular user: bash install.sh"
    exit 1
fi

# Check Python version
print_status "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed!"
    print_status "Please install Python 3.8+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Found Python $PYTHON_VERSION"

# Check pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is required but not installed!"
    print_status "Install with: sudo apt install python3-pip"
    exit 1
fi

# Install system dependencies if on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_status "Detecting Linux system dependencies..."
    
    # Check for common package managers and install PyQt6 dependencies
    if command -v apt &> /dev/null; then
        print_status "Detected APT package manager (Ubuntu/Debian)"
        print_status "Checking system dependencies..."
        
        MISSING_PACKAGES=""
        PACKAGES_TO_CHECK="python3-dev python3-pip libgl1-mesa-dev libegl1-mesa-dev"
        
        for pkg in $PACKAGES_TO_CHECK; do
            if ! dpkg -l | grep -q "^ii  $pkg "; then
                MISSING_PACKAGES="$MISSING_PACKAGES $pkg"
            fi
        done
        
        if [ ! -z "$MISSING_PACKAGES" ]; then
            print_warning "Some system packages are missing: $MISSING_PACKAGES"
            print_status "Please install them with:"
            echo "  sudo apt update && sudo apt install $MISSING_PACKAGES"
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    elif command -v dnf &> /dev/null; then
        print_status "Detected DNF package manager (Fedora/RHEL)"
        print_warning "You may need: sudo dnf install python3-devel qt6-qtbase-devel"
    elif command -v pacman &> /dev/null; then
        print_status "Detected Pacman package manager (Arch Linux)"
        print_warning "You may need: sudo pacman -S python qt6-base"
    fi
fi

# Choose installation method
if [ -d ".git" ] && [ -f "setup.py" ]; then
    # Local development installation
    print_status "Found local repository - installing in development mode..."
    INSTALL_METHOD="local"
    INSTALL_CMD="pip3 install --user -e ."
else
    # Remote installation via GitHub
    print_status "Installing latest version from GitHub..."
    INSTALL_METHOD="remote"
    INSTALL_CMD="pip3 install --user git+https://github.com/ZProLegend007/ApplerGUI.git"
fi

# Upgrade pip first
print_status "Ensuring pip is up to date..."
python3 -m pip install --user --upgrade pip

# Install the package
print_status "Installing ApplerGUI..."
if eval $INSTALL_CMD; then
    print_success "ApplerGUI installed successfully!"
else
    print_error "Installation failed!"
    exit 1
fi

# Check if the command is available
LOCAL_BIN="$HOME/.local/bin"
if command -v applergui &> /dev/null; then
    print_success "✅ Installation complete!"
    print_status "Run with: applergui"
elif [ -f "$LOCAL_BIN/applergui" ]; then
    print_success "✅ Installation complete!"
    print_warning "Command not in PATH. Add ~/.local/bin to your PATH:"
    echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
    echo "  source ~/.bashrc"
    print_status "Or run directly with: $LOCAL_BIN/applergui"
else
    print_warning "Installation completed but command not found."
    print_status "Try running: python3 -m applergui"
fi

# Create desktop entry if on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]] && [ -f "$LOCAL_BIN/applergui" ]; then
    DESKTOP_DIR="$HOME/.local/share/applications"
    DESKTOP_FILE="$DESKTOP_DIR/applergui.desktop"
    
    if [ ! -d "$DESKTOP_DIR" ]; then
        mkdir -p "$DESKTOP_DIR"
    fi
    
    print_status "Creating desktop entry..."
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=ApplerGUI
Comment=Control Apple TV and HomePod devices from Linux
Exec=$LOCAL_BIN/applergui
Icon=multimedia-player-apple-ipod
Categories=AudioVideo;Player;
Terminal=false
StartupNotify=true
EOF
    
    chmod +x "$DESKTOP_FILE"
    print_success "Desktop entry created at $DESKTOP_FILE"
fi

echo ""
print_success "🎉 ApplerGUI installation completed!"
print_status "📚 Documentation: https://github.com/ZProLegend007/ApplerGUI"
print_status "🐛 Report issues: https://github.com/ZProLegend007/ApplerGUI/issues"
echo ""