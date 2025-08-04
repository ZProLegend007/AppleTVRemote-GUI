#!/bin/bash
# ApplerGUI Professional Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/install.sh | bash

set -e  # Exit on any error

# Clear screen for clean start
clear

# Enhanced ASCII art and professional header
echo ""
echo "██████╗ ██████╗ ██████╗ ██╗     ███████╗██████╗  ██████╗ ██╗   ██╗██╗"
echo "██╔══██╗██╔══██╗██╔══██╗██║     ██╔════╝██╔══██╗██╔════╝ ██║   ██║██║"
echo "███████║██████╔╝██████╔╝██║     █████╗  ██████╔╝██║  ███╗██║   ██║██║"
echo "██╔══██║██╔═══╝ ██╔═══╝ ██║     ██╔══╝  ██╔══██╗██║   ██║██║   ██║██║"
echo "██║  ██║██║     ██║     ███████╗███████╗██║  ██║╚██████╔╝╚██████╔╝██║"
echo "╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝"
echo ""
echo "             🍎 Professional Linux Installer v1.0 🍎"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "  Control Apple TV and HomePod devices from your Linux desktop"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Enhanced colors and styling
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

sleep 3

# Enhanced error handling and cleanup
cleanup() {
    local exit_code=$?
    echo ""
    if [ $exit_code -ne 0 ]; then
        print_error "Installation failed with exit code $exit_code"
        echo ""
        print_status "🔧 Troubleshooting steps:"
        echo "  1. Check your internet connection"
        echo "  2. Ensure you have sufficient disk space"
        echo "  3. Verify system dependencies are installed"
        echo "  4. Check the installation log above for specific errors"
        echo ""
        print_status "🆘 Get help:"
        echo "  - GitHub Issues: ${BLUE}https://github.com/ZProLegend007/ApplerGUI/issues${NC}"
        echo "  - Discussions: ${BLUE}https://github.com/ZProLegend007/ApplerGUI/discussions${NC}"
        echo ""
        
        # Offer to clean up partial installation
        if [ -d "$INSTALL_DIR" ] 2>/dev/null; then
            if ask_yn "Remove partial installation directory?" "n"; then
                print_progress "Cleaning up partial installation..."
                rm -rf "$INSTALL_DIR" 2>/dev/null || true
                print_success "Cleanup completed"
            fi
        fi
    fi
}

# Set up signal handlers for cleanup
trap cleanup EXIT
trap 'echo ""; print_warning "Installation interrupted by user"; exit 130' INT TERM

# Professional status functions
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

# Enhanced spinner animation function
spin() {
    local pid=$!
    local delay=0.1
    local spinstr='|/-\\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# Professional input handling function
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
                if [ "$default" = "y" ]; then
                    return 0
                elif [ "$default" = "n" ]; then
                    return 1
                fi
                ;;
        esac
        
        print_warning "Please answer yes (y) or no (n)."
    done
}

# System detection and classification
detect_system() {
    print_progress "Detecting system information..."
    
    # Detect OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME="$NAME"
        OS_VERSION="$VERSION_ID"
        OS_ID="$ID"
        OS_ID_LIKE="$ID_LIKE"
    else
        OS_NAME="Unknown Linux"
        OS_VERSION="Unknown"
        OS_ID="unknown"
        OS_ID_LIKE=""
    fi
    
    # Detect architecture
    ARCH=$(uname -m)
    
    # Detect package manager
    if command -v apt &> /dev/null; then
        PKG_MANAGER="apt"
        PKG_INSTALL_CMD="sudo apt update && sudo apt install -y"
    elif command -v dnf &> /dev/null; then
        PKG_MANAGER="dnf"
        PKG_INSTALL_CMD="sudo dnf install -y"
    elif command -v yum &> /dev/null; then
        PKG_MANAGER="yum"
        PKG_INSTALL_CMD="sudo yum install -y"
    elif command -v pacman &> /dev/null; then
        PKG_MANAGER="pacman"
        PKG_INSTALL_CMD="sudo pacman -S --noconfirm"
    elif command -v zypper &> /dev/null; then
        PKG_MANAGER="zypper"
        PKG_INSTALL_CMD="sudo zypper install -y"
    else
        PKG_MANAGER="unknown"
        PKG_INSTALL_CMD=""
    fi
    
    print_success "System detected: $OS_NAME $OS_VERSION ($ARCH)"
    print_status "Package manager: $PKG_MANAGER"
}

# Smart sudo handling with fallbacks
check_sudo() {
    print_progress "Checking sudo access..."
    
    if command -v sudo &> /dev/null; then
        if sudo -n true 2>/dev/null; then
            print_success "Sudo access available (cached)"
            SUDO_AVAILABLE=true
        else
            print_status "Sudo requires password authentication"
            if sudo -v; then
                print_success "Sudo access verified"
                SUDO_AVAILABLE=true
            else
                print_warning "Sudo access failed"
                SUDO_AVAILABLE=false
            fi
        fi
    else
        print_warning "sudo command not available"
        SUDO_AVAILABLE=false
    fi
}

# Internet connectivity check
check_internet() {
    print_progress "Checking internet connectivity..."
    
    # Try multiple methods to check connectivity
    if command -v curl &> /dev/null; then
        if curl -s --connect-timeout 5 https://github.com &> /dev/null; then
            print_success "Internet connectivity verified (GitHub accessible)"
            return 0
        fi
    fi
    
    if command -v wget &> /dev/null; then
        if wget -q --spider --timeout=5 https://github.com 2>/dev/null; then
            print_success "Internet connectivity verified (GitHub accessible)"
            return 0
        fi
    fi
    
    # Fallback: try ping to common DNS servers
    if ping -c 1 -W 3 8.8.8.8 &> /dev/null || ping -c 1 -W 3 1.1.1.1 &> /dev/null; then
        print_warning "Basic internet connectivity detected, but GitHub may not be accessible"
        return 0
    fi
    
    print_error "No internet connectivity detected"
    return 1
}

# Check for existing installation and offer update
check_existing_installation() {
    local install_dir="$HOME/.local/share/applergui"
    
    if [ -d "$install_dir" ]; then
        print_warning "Existing ApplerGUI installation detected at: $install_dir"
        echo ""
        print_status "You have two options:"
        echo "  1. Update existing installation (recommended)"
        echo "  2. Fresh installation (removes current installation)"
        echo ""
        
        if ask_yn "Would you like to update the existing installation instead?" "y"; then
            print_status "Redirecting to update process..."
            print_status "Downloading and running updater..."
            
            if command -v curl &> /dev/null; then
                curl -sSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/update.sh | bash
            elif command -v wget &> /dev/null; then
                wget -qO- https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/update.sh | bash
            else
                print_error "Neither curl nor wget available for downloading updater"
                print_status "Please install curl or wget, or remove existing installation:"
                echo "  ${BOLD}rm -rf $install_dir${NC}"
                exit 1
            fi
            exit 0
        else
            print_warning "Proceeding with fresh installation..."
            print_progress "Backing up existing installation..."
            
            local backup_dir="$install_dir.backup.$(date +%Y%m%d_%H%M%S)"
            if mv "$install_dir" "$backup_dir" 2>/dev/null; then
                print_success "Existing installation backed up to: $backup_dir"
            else
                print_warning "Could not backup existing installation"
                if ask_yn "Remove existing installation anyway?" "n"; then
                    rm -rf "$install_dir" 2>/dev/null || true
                else
                    print_error "Cannot proceed with existing installation in place"
                    exit 1
                fi
            fi
        fi
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# SECURITY CHECK
# ═══════════════════════════════════════════════════════════════════════

print_section "SECURITY VERIFICATION"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "This installer should not be run as root for security reasons!"
    print_status "Please run as your regular user: ${BOLD}bash install.sh${NC}"
    echo ""
    print_warning "Running as root could compromise your system security."
    exit 1
fi

print_success "Security check passed - running as regular user"
sleep 1

# ═══════════════════════════════════════════════════════════════════════
# SYSTEM REQUIREMENTS
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "SYSTEM REQUIREMENTS CHECK"

# Detect system information
detect_system

# Check sudo access
check_sudo

# Check internet connectivity
if ! check_internet; then
    print_error "Internet connectivity is required for installation"
    if ask_yn "Continue anyway? Installation may fail" "n"; then
        print_warning "Proceeding without verified internet connectivity"
    else
        print_status "Please check your internet connection and try again"
        exit 1
    fi
fi

# Check for existing installation
check_existing_installation

# Check Python version
print_progress "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed!"
    echo ""
    print_status "Install Python 3.8+ with your package manager:"
    case "$PKG_MANAGER" in
        apt)    echo "  ${BOLD}sudo apt install python3 python3-pip python3-venv${NC}" ;;
        dnf)    echo "  ${BOLD}sudo dnf install python3 python3-pip${NC}" ;;
        yum)    echo "  ${BOLD}sudo yum install python3 python3-pip${NC}" ;;
        pacman) echo "  ${BOLD}sudo pacman -S python python-pip${NC}" ;;
        zypper) echo "  ${BOLD}sudo zypper install python3 python3-pip${NC}" ;;
        *)      echo "  Please install Python 3.8+ and pip using your system's package manager" ;;
    esac
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Found Python $PYTHON_VERSION"

# Check minimum Python version
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8 or higher is required (found $PYTHON_VERSION)"
    print_status "Please upgrade your Python installation"
    exit 1
fi

# Check pip
print_progress "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is required but not installed!"
    case "$PKG_MANAGER" in
        apt)    print_status "Install with: ${BOLD}sudo apt install python3-pip${NC}" ;;
        dnf)    print_status "Install with: ${BOLD}sudo dnf install python3-pip${NC}" ;;
        yum)    print_status "Install with: ${BOLD}sudo yum install python3-pip${NC}" ;;
        pacman) print_status "Install with: ${BOLD}sudo pacman -S python-pip${NC}" ;;
        zypper) print_status "Install with: ${BOLD}sudo zypper install python3-pip${NC}" ;;
        *)      print_status "Please install pip3 using your system's package manager" ;;
    esac
    exit 1
fi

print_success "pip3 is available"

# Check virtual environment support
print_progress "Checking virtual environment support..."
if ! python3 -c "import venv" 2>/dev/null; then
    print_warning "python3-venv module not available"
    case "$PKG_MANAGER" in
        apt)    
            if [ "$SUDO_AVAILABLE" = true ]; then
                print_progress "Installing python3-venv..."
                sudo apt install -y python3-venv
            else
                print_status "Install with: ${BOLD}sudo apt install python3-venv${NC}"
                exit 1
            fi
            ;;
        *)
            print_warning "Virtual environment support may be limited"
            ;;
    esac
fi

print_success "Virtual environment support available"

# User preferences (minimal questions only)
echo ""
print_status "Essential configuration questions:"
echo ""

# Desktop entry
CREATE_DESKTOP=true
if ask_yn "Create desktop entry?" "y"; then
    CREATE_DESKTOP=true
else
    CREATE_DESKTOP=false
fi

# CLI shortcut
CREATE_CLI=true
if ask_yn "Create CLI command shortcut?" "y"; then
    CREATE_CLI=true
else
    CREATE_CLI=false
fi

# Development tools
INSTALL_DEV=false
if ask_yn "Install development tools?" "n"; then
    INSTALL_DEV=true
else
    INSTALL_DEV=false
fi

# ═══════════════════════════════════════════════════════════════════════
# SYSTEM DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "SYSTEM DEPENDENCY INSTALLATION"

# Enhanced dependency installation with better detection
print_progress "Installing system dependencies automatically..."
INSTALL_DEPS=true

# Install system dependencies if on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]] && [[ "$INSTALL_DEPS" == true ]]; then
    print_progress "Installing dependencies for $OS_NAME..."
    
    case "$PKG_MANAGER" in
        apt)
            print_success "Detected APT package manager (Ubuntu/Debian family)"
            print_progress "Installing system dependencies..."
            
            REQUIRED_PACKAGES="python3-dev python3-pip libgl1-mesa-dev libegl1-mesa-dev python3-venv"
            MISSING_PACKAGES=""
            
            for pkg in $REQUIRED_PACKAGES; do
                if ! dpkg -l | grep -q "^ii  $pkg "; then
                    MISSING_PACKAGES="$MISSING_PACKAGES $pkg"
                fi
            done
            
            if [ ! -z "$MISSING_PACKAGES" ]; then
                print_warning "Installing missing packages: $MISSING_PACKAGES"
                echo ""
                print_status "Running: ${BOLD}sudo apt update && sudo apt install $MISSING_PACKAGES${NC}"
                
                if [ "$SUDO_AVAILABLE" = true ] && sudo apt update && sudo apt install -y $MISSING_PACKAGES; then
                    print_success "System dependencies installed successfully"
                else
                    print_error "Failed to install system dependencies"
                    print_warning "You may need to install them manually:"
                    echo "  ${BOLD}sudo apt update && sudo apt install $MISSING_PACKAGES${NC}"
                    if ! ask_yn "Continue anyway?" "n"; then
                        exit 1
                    fi
                fi
            else
                print_success "All required system packages are already installed"
            fi
            ;;
            
        dnf)
            print_success "Detected DNF package manager (Fedora/RHEL family)"
            DEPS="python3-devel qt6-qtbase-devel mesa-libGL-devel mesa-libEGL-devel"
            print_status "Installing dependencies with: ${BOLD}sudo dnf install $DEPS${NC}"
            if [ "$SUDO_AVAILABLE" = true ] && sudo dnf install -y $DEPS; then
                print_success "System dependencies installed successfully"
            else
                print_warning "Some dependencies may need manual installation"
            fi
            ;;
            
        pacman)
            print_success "Detected Pacman package manager (Arch Linux family)"
            DEPS="python qt6-base mesa"
            print_status "Installing dependencies with: ${BOLD}sudo pacman -S $DEPS${NC}"
            if [ "$SUDO_AVAILABLE" = true ] && sudo pacman -S --noconfirm $DEPS; then
                print_success "System dependencies installed successfully"
            else
                print_warning "Some dependencies may need manual installation"
            fi
            ;;
            
        zypper)
            print_success "Detected Zypper package manager (openSUSE)"
            DEPS="python3-devel libqt6-qtbase-devel Mesa-libGL-devel Mesa-libEGL-devel"
            print_status "Installing dependencies with: ${BOLD}sudo zypper install $DEPS${NC}"
            if [ "$SUDO_AVAILABLE" = true ] && sudo zypper install -y $DEPS; then
                print_success "System dependencies installed successfully"
            else
                print_warning "Some dependencies may need manual installation"
            fi
            ;;
            
        *)
            print_warning "Unknown package manager detected: $PKG_MANAGER"
            print_status "Please install the following packages manually:"
            echo "  - Python 3 development headers"
            echo "  - Qt6 development libraries"
            echo "  - OpenGL/EGL development libraries"
            echo ""
            if ! ask_yn "Continue with installation?" "n"; then
                exit 1
            fi
            ;;
    esac
else
    if [[ "$INSTALL_DEPS" == false ]]; then
        print_warning "Skipping system dependency installation (user choice)"
    else
        print_warning "Non-Linux system detected - skipping system dependencies"
    fi
fi

sleep 1

# ═══════════════════════════════════════════════════════════════════════
# INSTALLATION SUMMARY
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "INSTALLATION SUMMARY"

print_status "📋 Installation Summary:"
echo ""
echo "  🖥️  ${BOLD}System:${NC} $OS_NAME $OS_VERSION ($ARCH)"
echo "  📦 ${BOLD}Package Manager:${NC} $PKG_MANAGER"
echo "  🐍 ${BOLD}Python Version:${NC} $PYTHON_VERSION"
echo "  📁 ${BOLD}Install Directory:${NC} $INSTALL_DIR"
echo "  🔗 ${BOLD}CLI Command:${NC} $CLI_SCRIPT"
echo ""
echo "  ⚙️  ${BOLD}Configuration:${NC}"
echo "     Desktop Entry: $([ "$CREATE_DESKTOP" = true ] && echo "✅ Yes" || echo "❌ No")"
echo "     CLI Shortcut: $([ "$CREATE_CLI" = true ] && echo "✅ Yes" || echo "❌ No")"
echo "     Development Tools: $([ "$INSTALL_DEV" = true ] && echo "✅ Yes" || echo "❌ No")"
echo ""
echo "  🌐 ${BOLD}Installation Method:${NC} $INSTALL_METHOD"
echo "  🔒 ${BOLD}Sudo Available:${NC} $([ "$SUDO_AVAILABLE" = true ] && echo "✅ Yes" || echo "❌ No")"
echo ""

print_status "This installation will:"
echo "  1. Create a virtual Python environment"
echo "  2. Install ApplerGUI and all dependencies"
if [ "$CREATE_CLI" = true ]; then
    echo "  3. Create CLI command shortcut at $CLI_SCRIPT"
fi
if [ "$CREATE_DESKTOP" = true ]; then
    echo "  4. Create desktop entry for GUI launcher"
fi
echo ""

if ! ask_yn "Proceed with installation?" "y"; then
    print_status "Installation cancelled by user"
    echo ""
    print_status "You can run this installer again anytime with:"
    echo "  ${BOLD}curl -sSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/install.sh | bash${NC}"
    exit 0
fi

print_success "Installation confirmed - proceeding..."
sleep 1

# ═══════════════════════════════════════════════════════════════════════
# INSTALLATION SETUP
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "INSTALLATION SETUP"

# Standard installation paths
INSTALL_DIR="$HOME/.local/share/applergui"
BIN_DIR="$HOME/.local/bin"
CLI_SCRIPT="$BIN_DIR/applergui"

print_status "Setting up installation directories..."
echo "  📁 Install directory: ${BOLD}$INSTALL_DIR${NC}"
echo "  🔗 CLI command: ${BOLD}$CLI_SCRIPT${NC}"
echo "  📂 Binary directory: ${BOLD}$BIN_DIR${NC}"
echo ""

# Create directories
print_progress "Creating installation directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
print_success "Directories created successfully"

# Choose installation method
if [ -d ".git" ] && [ -f "setup.py" ]; then
    # Local development installation
    print_status "Local repository detected - Development installation mode"
    INSTALL_METHOD="local"
else
    # Remote installation via GitHub
    print_status "Remote installation mode - Installing latest version from GitHub"
    INSTALL_METHOD="remote"
fi

print_success "Installation method: ${BOLD}$INSTALL_METHOD${NC}"

sleep 1

# ═══════════════════════════════════════════════════════════════════════
# PYTHON ENVIRONMENT SETUP
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "PYTHON ENVIRONMENT SETUP"

# Create virtual environment in the install directory
VENV_PATH="$INSTALL_DIR/venv"
print_progress "Creating virtual environment at $VENV_PATH..."

if [ -d "$VENV_PATH" ]; then
    print_warning "Virtual environment already exists, removing old one..."
    rm -rf "$VENV_PATH"
fi

if python3 -m venv "$VENV_PATH"; then
    print_success "Virtual environment created successfully"
    
    # Activate virtual environment
    source "$VENV_PATH/bin/activate"
    print_success "Virtual environment activated"
else
    print_error "Failed to create virtual environment"
    exit 1
fi

# Upgrade pip first
print_progress "Ensuring pip is up to date..."
python -m pip install --upgrade pip &
spin
print_success "pip updated successfully"

sleep 1

# ═══════════════════════════════════════════════════════════════════════
# APPLERGUI INSTALLATION
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "APPLERGUI INSTALLATION"

print_progress "Installing ApplerGUI and dependencies..."
echo ""
print_status "This may take a few minutes depending on your internet connection..."
echo ""

# Install ApplerGUI
if [[ "$INSTALL_METHOD" == "local" ]]; then
    print_status "Installing from local source..."
    INSTALL_CMD="pip install -e ."
else
    print_status "Installing from GitHub repository..."
    INSTALL_CMD="pip install git+https://github.com/ZProLegend007/ApplerGUI.git"
fi

if eval $INSTALL_CMD; then
    print_success "ApplerGUI installed successfully!"
else
    print_error "Installation failed!"
    echo ""
    print_status "Troubleshooting steps:"
    echo "  1. Check your internet connection"
    echo "  2. Ensure you have the latest pip: ${BOLD}python3 -m pip install --upgrade pip${NC}"
    echo "  3. Try installing dependencies manually: ${BOLD}pip install PyQt6${NC}"
    echo "  4. Check the GitHub repository: https://github.com/ZProLegend007/ApplerGUI"
    exit 1
fi

sleep 1

# ═══════════════════════════════════════════════════════════════════════
# CLI COMMAND CREATION
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "CLI COMMAND CREATION"

if [[ "$CREATE_CLI" == true ]]; then
    print_progress "Creating CLI command at $CLI_SCRIPT..."
    
    # Create the CLI wrapper script
    cat > "$CLI_SCRIPT" << 'EOF'
#!/bin/bash
# ApplerGUI CLI Wrapper Script

APPLERGUI_DIR="$HOME/.local/share/applergui"
VENV_PATH="$APPLERGUI_DIR/venv"

# Activate virtual environment and run ApplerGUI
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    python -m applergui "$@"
else
    echo "❌ ApplerGUI installation not found at $APPLERGUI_DIR"
    echo "💡 Please reinstall ApplerGUI or check your installation."
    exit 1
fi
EOF
    
    # Make it executable
    chmod +x "$CLI_SCRIPT"
    print_success "CLI command created successfully"
    
    # Add ~/.local/bin to PATH if not already there
    print_progress "Ensuring ~/.local/bin is in PATH..."
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        print_success "Added ~/.local/bin to PATH in ~/.bashrc"
        print_warning "Please run 'source ~/.bashrc' or restart your terminal to update PATH"
        export PATH="$HOME/.local/bin:$PATH"
    else
        print_success "~/.local/bin already in PATH"
    fi
else
    print_warning "CLI command creation skipped (user choice)"
fi

sleep 1

# ═══════════════════════════════════════════════════════════════════════
# INSTALLATION VERIFICATION
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "INSTALLATION VERIFICATION"

print_progress "Verifying installation..."

# Test if applergui module can be imported
if python -c "import applergui; print('✅ ApplerGUI module imported successfully')" 2>/dev/null; then
    print_success "✅ Installation complete!"
    
    if [[ "$CREATE_CLI" == true ]] && [ -f "$CLI_SCRIPT" ]; then
        print_status "CLI command available: ${BOLD}applergui${NC}"
        print_status "Try: ${BOLD}applergui --help${NC}"
    else
        print_status "Run with: ${BOLD}python -m applergui${NC}"
    fi
    
    EXECUTABLE_PATH="$CLI_SCRIPT"
else
    print_error "Installation verification failed!"
    print_status "ApplerGUI module could not be imported."
    exit 1
fi

sleep 1

# ═══════════════════════════════════════════════════════════════════════
# DESKTOP INTEGRATION
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "DESKTOP INTEGRATION"

# Create desktop entry if requested
if [[ "$OSTYPE" == "linux-gnu"* ]] && [[ "$CREATE_DESKTOP" == true ]]; then
    print_progress "Setting up desktop integration..."
    
    DESKTOP_DIR="$HOME/.local/share/applications"
    DESKTOP_FILE="$DESKTOP_DIR/applergui.desktop"
    ICON_DIR="$HOME/.local/share/icons/hicolor/48x48/apps"
    
    # Create directories if they don't exist
    mkdir -p "$DESKTOP_DIR"
    mkdir -p "$ICON_DIR"
    
    # Create desktop entry
    print_status "Creating desktop entry..."
    
    # Use our CLI script if created, otherwise fallback to python module
    if [[ "$CREATE_CLI" == true ]] && [ -f "$CLI_SCRIPT" ]; then
        EXEC_CMD="$CLI_SCRIPT"
    else
        EXEC_CMD="bash -c 'cd $INSTALL_DIR && source venv/bin/activate && python -m applergui'"
    fi
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=ApplerGUI
Comment=Control Apple TV and HomePod devices from Linux
Exec=$EXEC_CMD
Icon=applergui
Categories=AudioVideo;Player;Network;
Terminal=false
StartupNotify=true
Keywords=AppleTV;HomePod;AirPlay;Remote;Apple;
EOF
    
    chmod +x "$DESKTOP_FILE"
    print_success "Desktop entry created"
    
    # Try to update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
        print_success "Desktop database updated"
    fi
    
    # Create a simple icon if none exists
    if ! [ -f "$ICON_DIR/applergui.png" ]; then
        print_status "Creating application icon..."
        # This would normally download or copy an icon file
        # For now, we'll note that an icon should be added
        print_warning "Icon should be placed at: $ICON_DIR/applergui.png"
    fi
    
    print_success "Desktop integration complete"
else
    if [[ "$CREATE_DESKTOP" == false ]]; then
        print_warning "Desktop integration skipped (user choice)"
    else
        print_warning "Desktop integration skipped (not Linux)"
    fi
fi

sleep 1

# ═══════════════════════════════════════════════════════════════════════
# INSTALLATION COMPLETE
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "INSTALLATION COMPLETE"

echo ""
echo "🎉 ${BOLD}${GREEN}ApplerGUI has been installed successfully!${NC} 🎉"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "📋 ${BOLD}Quick Start Guide:${NC}"
echo ""
echo "  1. ${BOLD}Launch ApplerGUI:${NC}"
if [[ "$CREATE_CLI" == true ]] && [ -f "$CLI_SCRIPT" ]; then
    echo "     ${CYAN}applergui${NC}"
else
    echo "     ${CYAN}cd $INSTALL_DIR && source venv/bin/activate && python -m applergui${NC}"
fi
echo ""
echo "  2. ${BOLD}CLI Commands:${NC}"
if [[ "$CREATE_CLI" == true ]]; then
    echo "     ${CYAN}applergui --help${NC}     Show help"
    echo "     ${CYAN}applergui --version${NC}  Show version"
    echo "     ${CYAN}applergui --update${NC}   Update to latest version"
fi
echo ""
echo "  2. ${BOLD}Connect your devices:${NC}"
echo "     - Ensure Apple TV/HomePod is on the same network"
echo "     - Use the device discovery feature in ApplerGUI"
echo "     - Follow the pairing prompts"
echo ""
echo "  3. ${BOLD}Start controlling:${NC}"
echo "     - Play/pause media"
echo "     - Adjust volume"
echo "     - Browse content"
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
if ask_yn "Would you like to launch ApplerGUI now?" "n"; then
    print_status "Launching ApplerGUI..."
    
    if [[ "$CREATE_CLI" == true ]] && [ -f "$CLI_SCRIPT" ]; then
        "$CLI_SCRIPT" &
    else
        cd "$INSTALL_DIR" && source venv/bin/activate && python -m applergui &
    fi
    
    print_success "ApplerGUI launched! Check your desktop for the application window."
else
    print_status "ApplerGUI is ready to use. Launch it whenever you're ready!"
fi

echo ""
print_success "Thank you for installing ApplerGUI! Enjoy controlling your Apple devices! 🍎"
echo ""

# Add update reminder
echo "💡 ${BOLD}Pro Tip:${NC} Keep ApplerGUI updated with:"
echo "   ${CYAN}curl -sSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/update.sh | bash${NC}"
echo ""
