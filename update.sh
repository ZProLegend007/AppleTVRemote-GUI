#!/bin/bash
# ApplerGUI Updater - Simple and robust update script
# Usage: curl -fsSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/update.sh | bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Global flag for cleanup
INTERRUPTED=0

# Enhanced signal handlers for proper Ctrl+C handling
cleanup_and_exit() {
    local exit_code=$?
    echo ""
    if [ $INTERRUPTED -eq 1 ]; then
        echo -e "${YELLOW}[⚠ INTERRUPTED]${NC} Update cancelled by user (Ctrl+C)"
        echo -e "${CYAN}[   INFO   ]${NC} You can run the updater again anytime to complete the update."
        echo -e "${CYAN}[   INFO   ]${NC} Your current installation remains unchanged."
        exit 130
    elif [ $exit_code -ne 0 ]; then
        echo -e "${RED}[✗  ERROR  ]${NC} Update failed with exit code $exit_code"
        echo -e "${CYAN}[   INFO   ]${NC} Please check the error messages above and try again."
    fi
}

# Signal handlers for graceful interruption
handle_interrupt() {
    INTERRUPTED=1
    echo ""
    echo -e "${YELLOW}[⚠ INTERRUPTED]${NC} Received interrupt signal..."
    echo -e "${CYAN}[   INFO   ]${NC} Cleaning up and exiting safely..."
    exit 130
}

# Set up signal traps for proper Ctrl+C handling
trap cleanup_and_exit EXIT
trap handle_interrupt INT TERM

# Print functions
print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
    echo -e " ${WHITE}$1${NC}"
    echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_status() {
    echo -e "${CYAN}[   INFO   ]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓ SUCCESS ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠ WARNING ]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗  ERROR  ]${NC} $1"
}

# Function to get Git commit hash from repository
get_git_commit() {
    local repo_dir="$1"
    if [ -d "$repo_dir/.git" ]; then
        cd "$repo_dir"
        git rev-parse HEAD 2>/dev/null
    else
        echo "no-git"
    fi
}


# Function to get latest commit hash from GitHub
get_latest_commit() {
    curl -s "https://api.github.com/repos/ZProLegend007/ApplerGUI/commits/main" | \
    grep '"sha":' | head -1 | sed 's/.*"sha": *"\([^"]*\)".*/\1/' 2>/dev/null || echo "unknown"
}

# Main update logic
main() {
    clear
    print_header "APPLERGUI UPDATE SYSTEM"
    
    echo -e "🔄 ${BOLD}ApplerGUI Updater${NC}"
    echo ""
    
    # Check if ApplerGUI is installed
    print_status "Checking ApplerGUI installation..."
    if ! python3 -c "import applergui" 2>/dev/null; then
        print_error "ApplerGUI is not installed on this system!"
        echo ""
        print_status "Please install ApplerGUI first using:"
        echo -e "  ${BOLD}curl -fsSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/install.sh | bash${NC}"
        
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
#        read -r response < /dev/tty
        
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
if ! python3 -c "import applergui" &>/dev/null; then
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
        pkill -f "applergui" &> /dev/null || true
        sleep 2
        
        # Verify processes are stopped
        if pgrep -f "applergui" > /dev/null; then
            print_warning "Some processes are still running, forcing termination..."
            pkill -9 -f "applergui" &> /dev/null || true
            sleep 1
        fi
        
        print_success "ApplerGUI processes stopped"
    else
        print_error "Cannot update while ApplerGUI is running"
        print_status "Please close ApplerGUI manually and run the updater again."
        main
        exit 1
    fi
    print_success "ApplerGUI installation found"
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "This updater should not be run as root for security reasons!"
        print_status "Please run as your regular user"
        exit 1
    fi
    print_success "Security check passed"
    
    # Detect installation paths
    INSTALL_DIR="$HOME/.local/share/applergui"
    VENV_PATH="$INSTALL_DIR/venv"
    
    print_status "Detecting installation method..."
    if [ -d "$INSTALL_DIR" ] && [ -d "$VENV_PATH" ]; then
        INSTALL_METHOD="standard"
        print_success "Found standard installation at: $INSTALL_DIR"
    elif [[ -n "$VIRTUAL_ENV" ]]; then
        INSTALL_METHOD="venv"
        VENV_PATH="$VIRTUAL_ENV"
        print_success "Found virtual environment: $VIRTUAL_ENV"
    else
        INSTALL_METHOD="system"
        print_success "Found system/user installation"
    fi

    
    # Get current commit hash
    progress "Checking for updates..."
    CURRENT_COMMIT="unknown"
    if [ "$INSTALL_METHOD" = "standard" ] && [ -d "$INSTALL_DIR/.git" ]; then
        CURRENT_COMMIT=$(get_git_commit "$INSTALL_DIR")
    fi
    
    # Get latest commit hash from GitHub
    LATEST_COMMIT=$(get_latest_commit)
    
    if [ "$LATEST_COMMIT" = "unknown" ]; then
        print_warning "Could not fetch latest version from GitHub"
        print_status "Proceeding with update anyway..."
    elif [ "$CURRENT_COMMIT" = "$LATEST_COMMIT" ] && [ "$CURRENT_COMMIT" != "unknown" ]; then
        print_success "Already up to date (commit: ${CURRENT_COMMIT:0:8})"
        echo ""
        print_status "No update needed. Your ApplerGUI is already at the latest version."
        exit 0
    else
        if [ "$CURRENT_COMMIT" != "unknown" ]; then
            print_success "Update available: ${CURRENT_COMMIT:0:8} -> ${LATEST_COMMIT:0:8}"

else
    end_progress
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

print_status "This may take a few minutes depending on your internet connection..."
progress "Updating ApplerGUI to the latest version..."

case $INSTALL_METHOD in
    "standard"|"venv")
        end_progress
        print_status "Updating virtual environment installation..."
        progress "Updating ApplerGUI to the latest version..."
        if pip install --upgrade git+https://github.com/ZProLegend007/ApplerGUI.git &> /dev/null; then
            print_success "Update completed successfully!"
        main
        else
            print_status "Update available (current version unknown)"
        fi
    
    # Stop ApplerGUI if running
    print_status "Checking for running ApplerGUI processes..."
    if pgrep -f "applergui" > /dev/null; then
        print_warning "ApplerGUI is currently running"
        print_status "Stopping ApplerGUI for safe update..."
        pkill -f "applergui" 2>/dev/null || true
        sleep 2
        if pgrep -f "applergui" > /dev/null; then
            print_warning "Force stopping remaining processes..."
            pkill -9 -f "applergui" 2>/dev/null || true
            sleep 1
        fi
        print_success "ApplerGUI processes stopped"
    else
        print_success "No running processes found"
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

if python -c "import applergui" &>/dev/null; then
    print_success "✅ ApplerGUI module imported successfully"
    print_success "✅ Update complete!"
    main
    
    # Activate virtual environment if needed
    if [[ "$INSTALL_METHOD" == "standard" ]]; then
        print_status "Activating virtual environment..."
        source "$VENV_PATH/bin/activate"
        print_success "Virtual environment activated"
    fi
    
    # Perform update
    print_status "Updating ApplerGUI..."
    case $INSTALL_METHOD in
        "standard"|"venv")
            if pip install --upgrade git+https://github.com/ZProLegend007/ApplerGUI.git > /dev/null 2>&1; then
                print_success "Update completed successfully!"
            else
                print_error "Update failed!"
                exit 1
            fi
            ;;
        "system")
            if pip3 install --user --upgrade git+https://github.com/ZProLegend007/ApplerGUI.git > /dev/null 2>&1; then
                print_success "Update completed successfully!"
            else
                print_error "Update failed!"
                exit 1
            fi
            ;;
    esac
    
    # Verify update
    print_status "Verifying update..."
    if python3 -c "import applergui; print('Update verified')" 2>/dev/null; then
        print_success "Update verification passed"
    else
        print_warning "Update completed but verification failed"
    fi
    
    # Success message
    echo ""
    print_header "UPDATE COMPLETE"
    echo -e "🎉 ${BOLD}${GREEN}ApplerGUI has been updated successfully!${NC} 🎉"
    echo ""
    print_status "You can now launch ApplerGUI with the latest features:"
    if command -v applergui &> /dev/null; then
        echo -e "  ${CYAN}applergui${NC}"
    else
        echo -e "  ${CYAN}python3 -m applergui${NC}"
    fi
    echo ""
    print_success "Update completed! Enjoy the latest features! 🍎"
}

# Run main function
main "$@"
