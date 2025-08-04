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

# Warning collection system
WARNINGS=()
add_warning() {
    WARNINGS+=("$1")
}

# Enhanced error handling and cleanup
cleanup() {
    local exit_code=$?
    echo ""
    if [ $exit_code -ne 0 ] && [ $exit_code -ne 130 ]; then
        print_error "Update failed with exit code $exit_code"
        echo ""
        print_status "🔧 Troubleshooting steps:"
        echo "  1. Check your internet connection"
        echo "  2. Ensure you have sufficient disk space"
        echo "  3. Verify ApplerGUI is properly installed"
        echo "  4. Check the update log above for specific errors"
        echo ""
        print_status "📞 Get help:"
        echo -e "  - GitHub Issues: ${BLUE}https://github.com/ZProLegend007/ApplerGUI/issues${NC}"
        echo -e "  - Discussions: ${BLUE}https://github.com/ZProLegend007/ApplerGUI/discussions${NC}"
    fi
}

# Enhanced signal handlers for cleanup
trap cleanup EXIT
trap 'echo ""; print_warning "Update interrupted by user"; echo ""; print_status "Update cancelled. You can run the updater again anytime."; exit 130' INT TERM

# Professional status functions (matching installer)
print_section() {
    echo ""
    echo -e "${BOLD}${BLUE}═════════════════════════════════════════════════════════════════════════${NC}"
    echo -e " ${WHITE}${1}${NC}"
    echo -e "${BOLD}${BLUE}═════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_status() {
    echo -e "${CYAN}[   INFO   ]${NC} $1"
}

print_success() {
    end_progress
    echo -e "${GREEN}[✓ SUCCESS ]${NC} $1"
}

print_warning() {
    end_progress
    echo -e "${YELLOW}[⚠ WARNING ]${NC} $1"
    add_warning "$1"
}

print_error() {
    end_progress
    echo -e "${RED}[✗  ERROR  ]${NC} $1"
}

# Globals for spinner control
__progress_pid=

progress() {
    local message="$1"

    # Start background spinner
    {
        local delay=0.05
        local frames=(
            "[▱▱▱▱▱▱▱▱▱▱]"
            "[▰▱▱▱▱▱▱▱▱▱]"
            "[▰▰▱▱▱▱▱▱▱▱]"
            "[▰▰▰▱▱▱▱▱▱▱]"
            "[▰▰▰▰▱▱▱▱▱▱]"
            "[▰▰▰▰▰▱▱▱▱▱]"
            "[▰▰▰▰▰▰▱▱▱▱]"
            "[▰▰▰▰▰▰▰▱▱▱]"
            "[▰▰▰▰▰▰▰▰▱▱]"
            "[▰▰▰▰▰▰▰▰▰▱]"
            "[▰▰▰▰▰▰▰▰▰▰]"
            "[▱▰▰▰▰▰▰▰▰▰]"
            "[▱▱▰▰▰▰▰▰▰▰]"
            "[▱▱▱▰▰▰▰▰▰▰]"
            "[▱▱▱▱▰▰▰▰▰▰]"
            "[▱▱▱▱▱▰▰▰▰▰]"
            "[▱▱▱▱▱▱▰▰▰▰]"
            "[▱▱▱▱▱▱▱▰▰▰]"
            "[▱▱▱▱▱▱▱▱▰▰]"
            "[▱▱▱▱▱▱▱▱▱▰]"
            "[▱▱▱▱▱▱▱▱▱▱]"
            "[▱▱▱▱▱▱▱▱▱▱]"
        )
        local num_frames=${#frames[@]}
        local i=0
        tput civis
        while true; do
            printf "\r${WHITE}"${frames[i]}"${NC} %s  " "$message"
            i=$(( (i + 1) % num_frames ))
            sleep $delay
        done
    } &
    __progress_pid=$!
    disown $__progress_pid
}

end_progress() {
    if [[ -n "$__progress_pid" ]]; then
        kill "$__progress_pid" 2>/dev/null
        wait "$__progress_pid" 2>/dev/null
        __progress_pid=
        tput cnorm
        printf "\r%*s\r" "$(tput cols)" ""  # Clear line
    fi
}

# Professional input handling function (from installer)
ask_yn() {
    local prompt="$1"
    local default="$2"
    local response
    
    while true; do
        if [ "$default" = "y" ]; then
            echo -n "${prompt} (Y/n): "
        elif [ "$default" = "n" ]; then
            echo -n "${prompt} (y/N): "
        else
            echo -n "${prompt} (y/n): "
        fi
        
        # Read from /dev/tty for proper input handling even in piped scenarios
        read -r response < /dev/tty
        
        case "$response" in
            [Yy]|[Yy][Ee][Ss])
                return 0
                ;;
            [Nn]|[Nn][Oo])
                return 1
                ;;
            "")
                # Empty response - use default
                if [ "$default" = "y" ]; then
                    return 0
                elif [ "$default" = "n" ]; then
                    return 1
                else
                    echo "Please answer yes or no."
                    continue
                fi
                ;;
            *)
                echo "Please answer yes or no."
                ;;
        esac
    done
}

# ═══════════════════════════════════════════════════════════════════════
# INSTALLATION VERIFICATION
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "CHECKING CURRENT INSTALLATION"

# Check if ApplerGUI is already installed
progress "Verifying ApplerGUI installation..."
if ! python3 -c "import applergui" 2>/dev/null; then
    print_error "ApplerGUI is not installed on this system!"
    echo ""
    print_status "Please install ApplerGUI first using our installer:"
    echo -e "  ${BOLD}curl -fsSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/install.sh | bash${NC}"
    echo ""
    exit 1
fi

print_success "ApplerGUI installation found"

# Get current version
progress "Checking current version..."
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
progress
sleep 1
end_progress

# ═══════════════════════════════════════════════════════════════════════
# PROCESS MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "PROCESS MANAGEMENT"

# Stop ApplerGUI if it's running
progress "Checking for running ApplerGUI processes..."
if pgrep -f "applergui" > /dev/null; then
    print_warning "ApplerGUI is currently running"
    echo ""
    print_status "The application needs to be stopped for a safe update."
    if ask_yn "Stop ApplerGUI to proceed with update?" "y"; then
        progress "Stopping ApplerGUI processes..."
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

progress
sleep 1
end_progress

# ═══════════════════════════════════════════════════════════════════════
# BACKUP SYSTEM
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "BACKUP AND SAFETY"

# Backup current configuration
CONFIG_DIR="$HOME/.config/applergui"
BACKUP_DIR="$HOME/.config/applergui.backup.$(date +%Y%m%d_%H%M%S)"

if [ -d "$CONFIG_DIR" ]; then
    progress "Creating configuration backup..."
    if cp -r "$CONFIG_DIR" "$BACKUP_DIR"; then
        print_success "Configuration backed up to: ${BOLD}$BACKUP_DIR${NC}"
    else
        print_warning "Failed to create configuration backup"
        print_status "Continuing without backup..."
    fi
else
    print_status "No existing configuration found - no backup needed"
fi

# Detect installation method and paths
INSTALL_DIR="$HOME/.local/share/applergui"
VENV_PATH="$INSTALL_DIR/venv"
CLI_SCRIPT="$HOME/.local/bin/applergui"

progress "Checking installation paths..."
if [ -d "$INSTALL_DIR" ] && [ -d "$VENV_PATH" ]; then
    print_success "Found ApplerGUI installation at: ${BOLD}$INSTALL_DIR${NC}"
    INSTALL_METHOD="standard"
elif [[ -n "$VIRTUAL_ENV" ]]; then
    print_success "Virtual environment detected: ${BOLD}$VIRTUAL_ENV${NC}"
    VENV_PATH="$VIRTUAL_ENV"
    INSTALL_METHOD="venv"
elif command -v applergui &> /dev/null; then
    INSTALL_METHOD="system"
    print_success "System installation detected"
else
    print_error "Could not determine installation method"
    print_status "ApplerGUI may be installed but not properly configured"
    exit 1
fi

progress
sleep 1
end_progress

# ═══════════════════════════════════════════════════════════════════════
# INSTALLATION METHOD DETECTION
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "INSTALLATION METHOD DETECTION"

progress "Analyzing current installation..."

# Activate virtual environment for standard installation
if [[ "$INSTALL_METHOD" == "standard" ]]; then
    end_progress
    print_status "Activating virtual environment for update..."
    progress "Analyzing current installation..."
    source "$VENV_PATH/bin/activate"
    print_success "Virtual environment activated"
elif [[ "$INSTALL_METHOD" == "venv" ]]; then
    print_success "Already in virtual environment"
fi

print_success "Installation method: ${BOLD}$INSTALL_METHOD${NC}"

progress
sleep 1
end_progress

# ═══════════════════════════════════════════════════════════════════════
# DEPENDENCY UPDATE
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "DEPENDENCY UPDATE"

# Update pip first
progress "Ensuring pip is up to date..."
python -m pip install --upgrade pip &> /dev/null
print_success "pip updated successfully"

progress
sleep 1
end_progress

# ═══════════════════════════════════════════════════════════════════════
# APPLERGUI UPDATE
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "APPLERGUI UPDATE"

echo ""
print_status "This may take a few minutes depending on your internet connection..."
echo ""
progress "Updating ApplerGUI to the latest version..."

case $INSTALL_METHOD in
    "standard"|"venv")
        end_progress
        print_status "Updating virtual environment installation..."
        progress "Updating ApplerGUI to the latest version..."
        if pip install --upgrade git+https://github.com/ZProLegend007/ApplerGUI.git > /dev/null; then
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
        print_warning "System installation detected - updating to user installation for safety"
        print_status "This will create a user installation alongside the system installation"
        progress "Updating ApplerGUI to the latest version..."
        if pip3 install --user --upgrade git+https://github.com/ZProLegend007/ApplerGUI.git > /dev/null; then
            print_success "Update completed successfully!"
            print_warning "Note: User installation will take precedence over system installation"
        else
            print_error "Update failed!"
            exit 1
        fi
        ;;
esac

progress
sleep 1
end_progress

# ═══════════════════════════════════════════════════════════════════════
# UPDATE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "UPDATE VERIFICATION"

# Get new version
progress "Verifying update..."
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
    echo ""
    print_status "Update successful! The configuration backup can be safely removed."
    if ask_yn "Remove backup directory?" "y"; then
        rm -rf "$BACKUP_DIR"
        print_success "Backup directory removed"
    else
        print_status "Backup kept at: ${BOLD}$BACKUP_DIR${NC}"
    fi
fi

progress
sleep 1
end_progress

# ═══════════════════════════════════════════════════════════════════════
# POST-UPDATE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "POST-UPDATE VERIFICATION"

# Check if the command is available
progress "Verifying executable availability..."

if python -c "import applergui; print('✅ ApplerGUI module imported successfully')" 2>/dev/null; then
    print_success "✅ Update complete!"
    
    if [ -f "$CLI_SCRIPT" ]; then
        print_status "CLI command available: ${BOLD}applergui${NC}"
    else
        print_status "Run with: ${BOLD}python -m applergui${NC}"
    fi
else
    print_warning "Update completed but module verification failed."
    print_status "Try running: ${BOLD}python -m applergui${NC}"
fi

progress
sleep 1
end_progress

# ═══════════════════════════════════════════════════════════════════════
# UPDATE COMPLETE
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "UPDATE COMPLETE"

echo ""
echo -e "🎉 ${BOLD}${GREEN}ApplerGUI has been updated successfully!${NC} 🎉"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo -e "📋 ${BOLD}What's Next:${NC}"
echo ""
echo -e "  1. ${BOLD}Launch ApplerGUI:${NC}"
if [ -f "$CLI_SCRIPT" ]; then
    echo -e "     ${CYAN}applergui${NC}"
else
    echo -e "     ${CYAN}python -m applergui${NC}"
fi
echo ""
echo -e "  2. ${BOLD}Check for new features:${NC}"
echo "     - Review the application interface for updates"
echo "     - Check settings for new configuration options"
echo "     - Test device connectivity and new features"
echo ""
echo -e "  3. ${BOLD}Report issues:${NC}"
echo "     - If you encounter any problems after the update"
echo "     - Visit our GitHub issues page for support"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo -e "📚 ${BOLD}Resources:${NC}"
echo -e "   Documentation: ${BLUE}https://github.com/ZProLegend007/ApplerGUI${NC}"
echo -e "   Report Issues:  ${BLUE}https://github.com/ZProLegend007/ApplerGUI/issues${NC}"
echo -e "   Get Support:   ${BLUE}https://github.com/ZProLegend007/ApplerGUI/discussions${NC}"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Launch option
if ask_yn "Would you like to launch ApplerGUI now?" "n"; then
    print_status "Launching ApplerGUI..."
    
    if [ -f "$CLI_SCRIPT" ]; then
        "$CLI_SCRIPT" &
    else
        python -m applergui &
    fi
    
    print_success "ApplerGUI launched! Check your desktop for the application window."
else
    print_status "ApplerGUI is ready to use. Launch it whenever you're ready!"
fi

echo ""
print_success "Thank you for keeping ApplerGUI up to date! Enjoy the latest features! 🍎"

# Display warning summary if any warnings were collected
if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo ""
    print_section "⚠️  UPDATE WARNINGS SUMMARY"
    echo "The following ${#WARNINGS[@]} warning(s) were encountered during update:"
    echo ""
    for i in "${!WARNINGS[@]}"; do
        echo "  $((i+1)). ${WARNINGS[i]}"
    done
    echo ""
    print_status "These warnings don't prevent ApplerGUI from working, but you may want to address them."
    print_status "For help with any issues, visit: ${BLUE}https://github.com/ZProLegend007/ApplerGUI/discussions${NC}"
fi

echo ""
