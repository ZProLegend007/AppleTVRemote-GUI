#!/bin/bash
# ApplerGUI Updater Script
# Usage: curl -sSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/update.sh | bash

set -e  # Exit on any error

echo "🔄 ApplerGUI Updater"
echo "==================="

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

# Check if ApplerGUI is already installed
if ! python3 -c "import applergui" 2>/dev/null; then
    print_error "ApplerGUI is not installed!"
    print_status "Use the installer instead:"
    echo "  curl -sSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/install.sh | bash"
    exit 1
fi

# Get current version
print_status "Checking current installation..."
CURRENT_VERSION=$(python3 -c "import applergui; print(getattr(applergui, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
print_status "Current version: $CURRENT_VERSION"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "Please don't run this updater as root/sudo!"
    print_status "Run it as your regular user: bash update.sh"
    exit 1
fi

# Stop ApplerGUI if it's running
print_status "Checking for running ApplerGUI processes..."
if pgrep -f "applergui" > /dev/null; then
    print_warning "ApplerGUI is currently running"
    read -p "Stop it to proceed with update? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping ApplerGUI..."
        pkill -f "applergui" || true
        sleep 2
    else
        print_error "Cannot update while ApplerGUI is running"
        exit 1
    fi
fi

# Backup current configuration
CONFIG_DIR="$HOME/.config/applergui"
BACKUP_DIR="$HOME/.config/applergui.backup.$(date +%Y%m%d_%H%M%S)"

if [ -d "$CONFIG_DIR" ]; then
    print_status "Backing up configuration to $BACKUP_DIR"
    cp -r "$CONFIG_DIR" "$BACKUP_DIR"
    print_success "Configuration backed up"
fi

# Determine installation method
LOCAL_BIN="$HOME/.local/bin/applergui"
if [ -f "$LOCAL_BIN" ]; then
    INSTALL_METHOD="pip"
    print_status "Detected pip installation"
elif command -v applergui &> /dev/null; then
    INSTALL_METHOD="system"
    print_status "Detected system installation"
else
    print_error "Could not determine installation method"
    exit 1
fi

# Update pip first
print_status "Ensuring pip is up to date..."
python3 -m pip install --user --upgrade pip

# Perform the update
print_status "Updating ApplerGUI..."
case $INSTALL_METHOD in
    "pip")
        if pip3 install --user --upgrade git+https://github.com/ZProLegend007/ApplerGUI.git; then
            print_success "Update completed successfully!"
        else
            print_error "Update failed!"
            if [ -d "$BACKUP_DIR" ]; then
                print_status "Configuration backup is available at: $BACKUP_DIR"
            fi
            exit 1
        fi
        ;;
    "system")
        print_warning "System installation detected - attempting pip user update"
        if pip3 install --user --upgrade git+https://github.com/ZProLegend007/ApplerGUI.git; then
            print_success "Update completed successfully!"
            print_warning "Note: This may have created a user installation alongside system installation"
        else
            print_error "Update failed!"
            exit 1
        fi
        ;;
esac

# Get new version
NEW_VERSION=$(python3 -c "import applergui; print(getattr(applergui, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
print_success "Updated to version: $NEW_VERSION"

# Clean up old backup if update was successful
if [ -d "$BACKUP_DIR" ]; then
    print_status "Update successful - cleaning up backup"
    rm -rf "$BACKUP_DIR"
fi

# Check if the command is available
if command -v applergui &> /dev/null; then
    print_success "✅ Update complete!"
    print_status "Run with: applergui"
elif [ -f "$LOCAL_BIN" ]; then
    print_success "✅ Update complete!"
    print_warning "Command not in PATH. Add ~/.local/bin to your PATH:"
    echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
    echo "  source ~/.bashrc"
    print_status "Or run directly with: $LOCAL_BIN"
else
    print_warning "Update completed but command not found."
    print_status "Try running: python3 -m applergui"
fi

echo ""
print_success "🎉 ApplerGUI update completed!"
print_status "📚 Documentation: https://github.com/ZProLegend007/ApplerGUI"
print_status "🐛 Report issues: https://github.com/ZProLegend007/ApplerGUI/issues"

# Optionally start ApplerGUI
read -p "Start ApplerGUI now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting ApplerGUI..."
    if command -v applergui &> /dev/null; then
        applergui &
    elif [ -f "$LOCAL_BIN" ]; then
        "$LOCAL_BIN" &
    else
        python3 -m applergui &
    fi
    print_success "ApplerGUI started!"
fi