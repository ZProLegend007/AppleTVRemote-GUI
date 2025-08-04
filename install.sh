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

# Spinner animation function
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

# Check Python version
print_progress "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed!"
    echo ""
    print_status "Install Python 3.8+ with your package manager:"
    echo "  Ubuntu/Debian: ${BOLD}sudo apt install python3 python3-pip${NC}"
    echo "  Fedora/RHEL:   ${BOLD}sudo dnf install python3 python3-pip${NC}"
    echo "  Arch Linux:    ${BOLD}sudo pacman -S python python-pip${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Found Python $PYTHON_VERSION"

# Check pip
print_progress "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is required but not installed!"
    print_status "Install with: ${BOLD}sudo apt install python3-pip${NC}"
    exit 1
fi

print_success "pip3 is available"

# User preferences (minimal questions only)
echo ""
print_status "Essential configuration questions:"
echo ""

# Desktop entry
read -p "Create desktop entry? (Y/n): " -n 1 -r
while read -r -t 0.1; do :; done > /dev/tty 2>/dev/null  # Flush remaining input
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    CREATE_DESKTOP=true
else
    CREATE_DESKTOP=false
fi

# CLI shortcut
read -p "Create CLI command shortcut? (Y/n): " -n 1 -r
while read -r -t 0.1; do :; done < /dev/tty 2>/dev/null  # Flush remaining input
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    CREATE_CLI=true
else
    CREATE_CLI=false
fi

# Development tools
read -p "Install development tools? (y/N): " -n 1 -r
while read -r -t 0.1; do :; done < /dev/tty 2>/dev/null  # Flush remaining input
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    INSTALL_DEV=true
else
    INSTALL_DEV=false
fi

# ═══════════════════════════════════════════════════════════════════════
# SYSTEM DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════

clear
print_section "SYSTEM DEPENDENCY INSTALLATION"

# Automatically install system dependencies
print_progress "Installing system dependencies automatically..."
INSTALL_DEPS=true

# Install system dependencies if on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]] && [[ "$INSTALL_DEPS" == true ]]; then
    print_progress "Detecting Linux distribution and package manager..."
    
    # Check for common package managers and install PyQt6 dependencies
    if command -v apt &> /dev/null; then
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
            
            if sudo apt update && sudo apt install -y $MISSING_PACKAGES; then
                print_success "System dependencies installed successfully"
            else
                print_error "Failed to install system dependencies"
                print_warning "You may need to install them manually:"
                echo "  ${BOLD}sudo apt update && sudo apt install $MISSING_PACKAGES${NC}"
                read -p "Continue anyway? (y/N): " -n 1 -r
                while read -r -t 0.1; do :; done < /dev/tty 2>/dev/null  # Flush remaining input
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    exit 1
                fi
            fi
        else
            print_success "All required system packages are already installed"
        fi
        
    elif command -v dnf &> /dev/null; then
        print_success "Detected DNF package manager (Fedora/RHEL family)"
        print_status "Installing dependencies with: ${BOLD}sudo dnf install python3-devel qt6-qtbase-devel mesa-libGL-devel mesa-libEGL-devel${NC}"
        if sudo dnf install -y python3-devel qt6-qtbase-devel mesa-libGL-devel mesa-libEGL-devel; then
            print_success "System dependencies installed successfully"
        else
            print_warning "Some dependencies may need manual installation"
        fi
        
    elif command -v pacman &> /dev/null; then
        print_success "Detected Pacman package manager (Arch Linux family)"
        print_status "Installing dependencies with: ${BOLD}sudo pacman -S python qt6-base mesa${NC}"
        if sudo pacman -S --noconfirm python qt6-base mesa; then
            print_success "System dependencies installed successfully"
        else
            print_warning "Some dependencies may need manual installation"
        fi
        
    elif command -v zypper &> /dev/null; then
        print_success "Detected Zypper package manager (openSUSE)"
        print_status "Installing dependencies with: ${BOLD}sudo zypper install python3-devel libqt6-qtbase-devel Mesa-libGL-devel Mesa-libEGL-devel${NC}"
        if sudo zypper install -y python3-devel libqt6-qtbase-devel Mesa-libGL-devel Mesa-libEGL-devel; then
            print_success "System dependencies installed successfully"
        else
            print_warning "Some dependencies may need manual installation"
        fi
        
    else
        print_warning "Unknown package manager detected"
        print_status "Please install the following packages manually:"
        echo "  - Python 3 development headers"
        echo "  - Qt6 development libraries"
        echo "  - OpenGL/EGL development libraries"
        echo ""
        read -p "Continue with installation? (y/N): " -n 1 -r
        while read -r -t 0.1; do :; done < /dev/tty 2>/dev/null  # Flush remaining input
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    if [[ "$INSTALL_DEPS" == false ]]; then
        print_warning "Skipping system dependency installation (user choice)"
    else
        print_warning "Non-Linux system detected - skipping system dependencies"
    fi
fi

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

print_status "Installation configuration:"
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
read -p "Would you like to launch ApplerGUI now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
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
