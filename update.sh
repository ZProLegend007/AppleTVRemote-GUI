#!/bin/bash
# ApplerGUI Professional Updater
# Usage: curl -fsSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/update.sh | bash

set -e  # Exit on any error

# Clear screen for clean start
clear

# Enhanced ASCII art and professional header matching installer
echo ""
echo "██████╗ ██████╗ ██████╗ ██╗     ███████╗██████╗  ██████╗ ██╗   ██╗██╗"
echo "██╔══██╗██╔══██╗██╔══██╗██║     ██╔════╝██╔══██╗██╔════╝ ██║   ██║██║"
echo "███████║██████╔╝██████╔╝██║     █████╗  ██████╔╝██║  ███╗██║   ██║██║"
echo "██╔══██║██╔═══╝ ██╔═══╝ ██║     ██╔══╝  ██╔══██╗██║   ██║██║   ██║██║"
echo "██║  ██║██║     ██║     ███████╗███████╗██║  ██║╚██████╔╝╚██████╔╝██║"
echo "╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝"
echo ""
echo "               🔄 Professional Update System v1.0 🔄"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "  Keeping your ApplerGUI installation up to date"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Enhanced colors and styling (matching installer)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Professional status functions (matching installer)
print_section() {
    echo ""
    echo -e "${BOLD}${BLUE}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${BLUE}║${NC} ${WHITE}${1}${NC}${BOLD}${BLUE}║${NC}"
    echo -e "${BOLD}${BLUE}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_status() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓ SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠ WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗ ERROR]${NC} $1"
}

print_progress() {
    echo -e "${PURPLE}[PROGRESS]${NC} $1"
}

# Spinner animation function (matching installer)
spin() {
    local pid=$!
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# ═══════════════════════════════════════════════════════════════════════
# INSTALLATION VERIFICATION
# ═══════════════════════════════════════════════════════════════════════

print_section "CHECKING CURRENT INSTALLATION"

# Check if ApplerGUI is already installed
print_progress "Verifying ApplerGUI installation..."
if ! python3 -c "import applergui" 2>/dev/null; then
    print_error "ApplerGUI is not installed on this system!"
    echo ""
    print_status "Please install ApplerGUI first using our installer:"
    echo "  ${BOLD}curl -fsSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/install.sh | bash${NC}"
    echo ""
    exit 1
fi

print_success "ApplerGUI installation found"

# Get current version
print_progress "Checking current version..."
CURRENT_VERSION=$(python3 -c "import applergui; print(getattr(applergui, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
print_success "Current version: ${BOLD}$CURRENT_VERSION${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "This updater should not be run as root for security reasons!"
    print_status "Please run as your regular user: ${BOLD}bash update.sh${NC}"
    echo ""
    print_warning "Running as root could compromise your system security."
    exit 1
fi

print_success "Security check passed - running as regular user"
sleep 1

# ═══════════════════════════════════════════════════════════════════════
# PROCESS MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "PROCESS MANAGEMENT"

# Stop ApplerGUI if it's running
print_progress "Checking for running ApplerGUI processes..."
if pgrep -f "applergui" > /dev/null; then
    print_warning "ApplerGUI is currently running"
    echo ""
    print_status "The application needs to be stopped for a safe update."
    read -p "Stop ApplerGUI to proceed with update? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_progress "Stopping ApplerGUI processes..."
        pkill -f "applergui" || true
        sleep 2
        
        # Verify processes are stopped
        if pgrep -f "applergui" > /dev/null; then
            print_warning "Some processes are still running, forcing termination..."
            pkill -9 -f "applergui" || true
            sleep 1
        fi
        
        print_success "ApplerGUI processes stopped"
    else
        print_error "Cannot update while ApplerGUI is running"
        print_status "Please close ApplerGUI manually and run the updater again."
        exit 1
    fi
else
    print_success "No running ApplerGUI processes found"
fi

sleep 1

# ═══════════════════════════════════════════════════════════════════════
# BACKUP SYSTEM
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "BACKUP AND SAFETY"

# Backup current configuration
CONFIG_DIR="$HOME/.config/applergui"
BACKUP_DIR="$HOME/.config/applergui.backup.$(date +%Y%m%d_%H%M%S)"

if [ -d "$CONFIG_DIR" ]; then
    print_progress "Creating configuration backup..."
    if cp -r "$CONFIG_DIR" "$BACKUP_DIR"; then
        print_success "Configuration backed up to: ${BOLD}$BACKUP_DIR${NC}"
    else
        print_warning "Failed to create configuration backup"
        print_status "Continuing without backup..."
    fi
else
    print_status "No existing configuration found - no backup needed"
fi

# Detect virtual environment
VENV_PATH=""
if [[ -n "$VIRTUAL_ENV" ]]; then
    print_success "Virtual environment detected: ${BOLD}$VIRTUAL_ENV${NC}"
    VENV_PATH="$VIRTUAL_ENV"
    IN_VENV=true
elif [ -d "$HOME/.local/share/applergui-venv" ]; then
    VENV_PATH="$HOME/.local/share/applergui-venv"
    print_status "Found ApplerGUI virtual environment: ${BOLD}$VENV_PATH${NC}"
    print_status "Activating virtual environment for update..."
    source "$VENV_PATH/bin/activate"
    IN_VENV=true
else
    print_status "No virtual environment detected - using system Python"
    IN_VENV=false
fi

sleep 1

# ═══════════════════════════════════════════════════════════════════════
# INSTALLATION METHOD DETECTION
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "INSTALLATION METHOD DETECTION"

# Determine installation method
LOCAL_BIN="$HOME/.local/bin/applergui"
VENV_BIN="$VENV_PATH/bin/applergui"

print_progress "Analyzing current installation..."

if [[ "$IN_VENV" == true ]] && [ -f "$VENV_BIN" ]; then
    INSTALL_METHOD="venv"
    print_success "Detected virtual environment installation"
    print_status "Installation path: ${BOLD}$VENV_BIN${NC}"
elif [ -f "$LOCAL_BIN" ]; then
    INSTALL_METHOD="user"
    print_success "Detected user installation"
    print_status "Installation path: ${BOLD}$LOCAL_BIN${NC}"
elif command -v applergui &> /dev/null; then
    INSTALL_METHOD="system"
    print_success "Detected system installation"
    SYSTEM_PATH=$(which applergui)
    print_status "Installation path: ${BOLD}$SYSTEM_PATH${NC}"
else
    print_error "Could not determine installation method"
    print_status "ApplerGUI may be installed but not properly configured"
    exit 1
fi

sleep 1

# ═══════════════════════════════════════════════════════════════════════
# DEPENDENCY UPDATE
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "DEPENDENCY UPDATE"

# Update pip first
print_progress "Ensuring pip is up to date..."
if [[ "$IN_VENV" == true ]]; then
    python -m pip install --upgrade pip &
else
    python3 -m pip install --user --upgrade pip &
fi
spin
print_success "pip updated successfully"

sleep 1

# ═══════════════════════════════════════════════════════════════════════
# APPLERGUI UPDATE
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "APPLERGUI UPDATE"

print_progress "Updating ApplerGUI to the latest version..."
echo ""
print_status "This may take a few minutes depending on your internet connection..."
echo ""

case $INSTALL_METHOD in
    "venv")
        print_status "Updating virtual environment installation..."
        if pip install --upgrade git+https://github.com/ZProLegend007/ApplerGUI.git; then
            print_success "Update completed successfully!"
        else
            print_error "Update failed!"
            if [ -d "$BACKUP_DIR" ]; then
                print_status "Configuration backup is available at: ${BOLD}$BACKUP_DIR${NC}"
            fi
            exit 1
        fi
        ;;
    "user")
        print_status "Updating user installation..."
        if pip3 install --user --upgrade git+https://github.com/ZProLegend007/ApplerGUI.git; then
            print_success "Update completed successfully!"
        else
            print_error "Update failed!"
            if [ -d "$BACKUP_DIR" ]; then
                print_status "Configuration backup is available at: ${BOLD}$BACKUP_DIR${NC}"
            fi
            exit 1
        fi
        ;;
    "system")
        print_warning "System installation detected - attempting user update for safety"
        print_status "This will create a user installation alongside the system installation"
        if pip3 install --user --upgrade git+https://github.com/ZProLegend007/ApplerGUI.git; then
            print_success "Update completed successfully!"
            print_warning "Note: User installation will take precedence over system installation"
        else
            print_error "Update failed!"
            exit 1
        fi
        ;;
esac

sleep 1

# ═══════════════════════════════════════════════════════════════════════
# UPDATE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "UPDATE VERIFICATION"

# Get new version
print_progress "Verifying update..."
NEW_VERSION=$(python3 -c "import applergui; print(getattr(applergui, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")

if [[ "$NEW_VERSION" != "$CURRENT_VERSION" ]]; then
    print_success "Successfully updated from ${BOLD}$CURRENT_VERSION${NC} to ${BOLD}$NEW_VERSION${NC}"
elif [[ "$NEW_VERSION" == "$CURRENT_VERSION" ]]; then
    print_success "Already at latest version: ${BOLD}$NEW_VERSION${NC}"
else
    print_warning "Version verification inconclusive"
fi

# Clean up backup if update was successful
if [ -d "$BACKUP_DIR" ]; then
    print_progress "Cleaning up backup..."
    echo ""
    print_status "Update successful! The configuration backup can be safely removed."
    read -p "Remove backup directory? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        rm -rf "$BACKUP_DIR"
        print_success "Backup directory removed"
    else
        print_status "Backup kept at: ${BOLD}$BACKUP_DIR${NC}"
    fi
fi

sleep 1

# ═══════════════════════════════════════════════════════════════════════
# POST-UPDATE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "POST-UPDATE VERIFICATION"

# Check if the command is available
print_progress "Verifying executable availability..."

if [[ "$IN_VENV" == true ]] && [ -f "$VENV_BIN" ]; then
    print_success "✅ Update complete (Virtual Environment)!"
    echo ""
    print_status "To run ApplerGUI:"
    echo "  ${BOLD}source $VENV_PATH/bin/activate && applergui${NC}"
    
elif command -v applergui &> /dev/null; then
    print_success "✅ Update complete!"
    print_status "Run with: ${BOLD}applergui${NC}"
    
elif [ -f "$LOCAL_BIN" ]; then
    print_success "✅ Update complete!"
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        print_warning "Command not in PATH. Add ~/.local/bin to your PATH:"
        echo "  ${BOLD}echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc${NC}"
        echo "  ${BOLD}source ~/.bashrc${NC}"
    fi
    print_status "Or run directly with: ${BOLD}$LOCAL_BIN${NC}"
    
else
    print_warning "Update completed but command not found."
    print_status "Try running: ${BOLD}python3 -m applergui${NC}"
fi

sleep 1

# ═══════════════════════════════════════════════════════════════════════
# UPDATE COMPLETE
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "UPDATE COMPLETE"

echo ""
echo "🎉 ${BOLD}${GREEN}ApplerGUI has been updated successfully!${NC} 🎉"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "📋 ${BOLD}What's Next:${NC}"
echo ""
echo "  1. ${BOLD}Launch ApplerGUI:${NC}"
if [[ "$IN_VENV" == true ]]; then
    echo "     ${CYAN}source $VENV_PATH/bin/activate && applergui${NC}"
elif command -v applergui &> /dev/null; then
    echo "     ${CYAN}applergui${NC}"
elif [ -f "$LOCAL_BIN" ]; then
    echo "     ${CYAN}$LOCAL_BIN${NC}"
else
    echo "     ${CYAN}python3 -m applergui${NC}"
fi
echo ""
echo "  2. ${BOLD}Check for new features:${NC}"
echo "     - Review the application interface for updates"
echo "     - Check settings for new configuration options"
echo "     - Test device connectivity and new features"
echo ""
echo "  3. ${BOLD}Report issues:${NC}"
echo "     - If you encounter any problems after the update"
echo "     - Visit our GitHub issues page for support"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "📚 ${BOLD}Resources:${NC}"
echo "   Documentation: ${BLUE}https://github.com/ZProLegend007/ApplerGUI${NC}"
echo "   Report Issues:  ${BLUE}https://github.com/ZProLegend007/ApplerGUI/issues${NC}"
echo "   Get Support:   ${BLUE}https://github.com/ZProLegend007/ApplerGUI/discussions${NC}"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Launch option
read -p "Would you like to launch ApplerGUI now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Launching ApplerGUI..."
    
    if [[ "$IN_VENV" == true ]]; then
        source "$VENV_PATH/bin/activate" && applergui &
    elif command -v applergui &> /dev/null; then
        applergui &
    elif [ -f "$LOCAL_BIN" ]; then
        "$LOCAL_BIN" &
    else
        python3 -m applergui &
    fi
    
    print_success "ApplerGUI launched! Check your desktop for the application window."
else
    print_status "ApplerGUI is ready to use. Launch it whenever you're ready!"
fi

echo ""
print_success "Thank you for keeping ApplerGUI up to date! Enjoy the latest features! 🍎"
echo ""