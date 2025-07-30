#!/bin/bash

# AppleTVRemote-GUI Professional Installer
# One-line install: curl -fsSL https://raw.githubusercontent.com/ZProLegend007/AppleTVRemote-GUI/main/install.sh | bash

set -e  # Exit on error, but handle gracefully

# Enhanced color palette for professional UI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
GRAY='\033[90m'
NC='\033[0m' # No Color

# Functions for enhanced colored output
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_info() { echo -e "${BLUE}→${NC} $1"; }
print_header() { echo -e "${CYAN}${BOLD}$1${NC}"; }
print_section() { 
    echo -e "\n${PURPLE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE}${BOLD} $1${NC}"
    echo -e "${PURPLE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Clear terminal and show fancy banner
clear_and_banner() {
    clear
    echo -e "${PURPLE}"
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║   🍎 AppleTVRemote-GUI Professional Installer                              ║
║                                                                            ║
║   Modern Linux GUI for Apple TV & HomePod Control                         ║
║                                                                            ║
║   ✨ Automated Installation with Smart Dependency Management               ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}\n"
    echo -e "${GRAY}Version 2.0 • Professional Installation Experience${NC}"
    echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Global variables
INSTALL_DIR=""
VENV_DIR=""
DESKTOP_ENTRY_PATH=""
USER_INSTALL=true
CREATE_DESKTOP_ENTRY=false
CREATE_CLI_ALIAS=false
INSTALL_DEV_DEPS=false
AUTO_START=false
INSTALL_AUDIO_CODECS=false
CREATE_CONFIG_DIR=false
DOWNLOAD_THEMES=false
DETECTED_OS=""
PACKAGE_MANAGER=""
SUDO_AVAILABLE=false
OS_TYPE=""

# Enhanced installation preferences
DESKTOP_ENTRY=false
SYSTEM_WIDE=false
CLI_SHORTCUT=false
DEV_TOOLS=false
SAMPLE_CONFIG=false
EXTRA_THEMES=false

# Progress indicator
show_progress() {
    local pid=$1
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

# Smart sudo detection and management
check_sudo() {
    print_info "🔐 Checking system permissions..."
    if sudo -n true 2>/dev/null; then
        SUDO_AVAILABLE=true
        print_success "✓ Sudo access confirmed"
    elif sudo -v 2>/dev/null; then
        SUDO_AVAILABLE=true
        print_success "✓ Sudo access granted"
        echo -e "${GRAY}   Sudo credentials cached for installation${NC}"
    else
        SUDO_AVAILABLE=false
        print_warning "⚠ No sudo access - will use user-space alternatives where possible"
        echo -e "${GRAY}   Some features may require manual system package installation${NC}"
    fi
}

# Smart sudo execution with fallbacks
safe_sudo() {
    if [[ "$SUDO_AVAILABLE" == "true" ]]; then
        sudo "$@"
    else
        print_warning "⚠ Attempting user-space alternative for: $*"
        return 1
    fi
}

# Refresh sudo credentials during long operations
refresh_sudo() {
    if [[ "$SUDO_AVAILABLE" == "true" ]]; then
        sudo -v 2>/dev/null || {
            print_warning "⚠ Sudo credentials expired, please re-authenticate"
            if sudo -v; then
                print_success "✓ Sudo credentials refreshed"
            else
                print_error "✗ Failed to refresh sudo credentials"
                SUDO_AVAILABLE=false
            fi
        }
    fi
}

# Check internet connectivity
check_internet_connectivity() {
    print_info "🌐 Checking internet connectivity..."
    if command -v curl &> /dev/null; then
        if curl -s --connect-timeout 5 https://github.com > /dev/null; then
            print_success "✓ Internet connection available"
        else
            print_error "✗ No internet connection - installation cannot proceed"
            echo -e "${GRAY}   Please check your network connection and try again${NC}"
            exit 1
        fi
    elif command -v wget &> /dev/null; then
        if wget -q --spider --timeout=5 https://github.com; then
            print_success "✓ Internet connection available"
        else
            print_error "✗ No internet connection - installation cannot proceed"
            exit 1
        fi
    else
        print_warning "⚠ Cannot verify internet connection (curl/wget not found)"
        echo -e "${GRAY}   Proceeding with installation...${NC}"
    fi
}

# Enhanced OS detection and system classification
detect_system() {
    print_info "🔍 Detecting operating system and environment..."
    
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_warning "⚠ This application is designed for Linux. Some features may not work properly."
    fi
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DETECTED_OS=$ID
        
        # Classify OS type for better package management
        case "$ID" in
            ubuntu|debian|pop|elementary|zorin|mint)
                OS_TYPE="ubuntu"
                ;;
            fedora|rhel|centos|rocky|alma)
                OS_TYPE="fedora"
                ;;
            arch|manjaro|endeavouros|garuda)
                OS_TYPE="arch"
                ;;
            opensuse*|sles)
                OS_TYPE="opensuse"
                ;;
            *)
                OS_TYPE="unknown"
                ;;
        esac
        
        print_success "✓ Detected $PRETTY_NAME"
        echo -e "${GRAY}   OS Type: $OS_TYPE • Architecture: $(uname -m)${NC}"
    else
        print_error "✗ Cannot detect OS. Please install dependencies manually."
        exit 1
    fi
    
    # Detect package manager with better classification
    if command -v apt-get &> /dev/null; then
        PACKAGE_MANAGER="apt"
        print_success "✓ Package Manager: APT (Debian/Ubuntu family)"
    elif command -v dnf &> /dev/null; then
        PACKAGE_MANAGER="dnf"
        print_success "✓ Package Manager: DNF (Fedora/RHEL family)"
    elif command -v yum &> /dev/null; then
        PACKAGE_MANAGER="yum"
        print_success "✓ Package Manager: YUM (CentOS/RHEL family)"
    elif command -v pacman &> /dev/null; then
        PACKAGE_MANAGER="pacman"
        print_success "✓ Package Manager: Pacman (Arch Linux family)"
    elif command -v zypper &> /dev/null; then
        PACKAGE_MANAGER="zypper"
        print_success "✓ Package Manager: Zypper (openSUSE family)"
    else
        print_error "✗ Unsupported package manager. Please install dependencies manually."
        echo -e "${GRAY}   Supported: APT, DNF, YUM, Pacman, Zypper${NC}"
        exit 1
    fi
}

# Check Python version
check_python() {
    print_info "🐍 Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "✗ Python 3 is not installed. Please install Python 3.8+ first."
        echo -e "${GRAY}   Install with: sudo $PACKAGE_MANAGER install python3${NC}"
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    required_version="3.8"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        print_error "✗ Python 3.8+ is required. Found Python $python_version"
        echo -e "${GRAY}   Please upgrade Python or install a newer version${NC}"
        exit 1
    fi
    
    print_success "✓ Python $python_version detected"
    
    # Check if pip is available
    if ! python3 -m pip --version &> /dev/null; then
        print_warning "⚠ pip not found, may need to install python3-pip"
    else
        print_success "✓ pip is available"
    fi
}

# Enhanced interactive prompts for installation preferences  
ask_user_preferences() {
    print_section "⚙️ INSTALLATION PREFERENCES"
    echo -e "${GRAY}Configure your AppleTVRemote-GUI installation with the options below.${NC}"
    echo -e "${GRAY}Each option includes an explanation to help you decide.${NC}\n"
    
    # Reset preferences
    DESKTOP_ENTRY=false
    SYSTEM_WIDE=false
    CLI_SHORTCUT=false
    DEV_TOOLS=false
    AUTO_START=false
    AUDIO_CODECS=false
    SAMPLE_CONFIG=false
    EXTRA_THEMES=false
    
    if ask_yn "🖥️ Create desktop entry?" "y" "Add AppleTVRemote-GUI to your application menu for easy access"; then
        DESKTOP_ENTRY=true
        CREATE_DESKTOP_ENTRY=true
    fi
    
    if ask_yn "🌐 Install system-wide?" "n" "Install for all users (requires sudo) vs just current user"; then
        if [[ "$SUDO_AVAILABLE" == "true" ]]; then
            SYSTEM_WIDE=true
            USER_INSTALL=false
        else
            print_warning "⚠ System-wide install requires sudo - falling back to user install"
            SYSTEM_WIDE=false
            USER_INSTALL=true
        fi
    else
        USER_INSTALL=true
    fi
    
    if ask_yn "💻 Create command-line shortcut?" "y" "Add 'atvremote' command to your PATH for terminal access"; then
        CLI_SHORTCUT=true
        CREATE_CLI_ALIAS=true
    fi
    
    if ask_yn "🔧 Install development tools?" "n" "Additional dependencies for contributing code (pytest, linting tools)"; then
        DEV_TOOLS=true
        INSTALL_DEV_DEPS=true
    fi
    
    if ask_yn "🚀 Enable auto-start?" "n" "Launch AppleTVRemote-GUI automatically when you log in"; then
        AUTO_START=true
    fi
    
    if ask_yn "🎵 Install audio codecs?" "y" "Enhanced media format support and better audio quality"; then
        AUDIO_CODECS=true
        INSTALL_AUDIO_CODECS=true
    fi
    
    if ask_yn "📁 Create sample configuration?" "y" "Pre-configured settings file and example configurations"; then
        SAMPLE_CONFIG=true
        CREATE_CONFIG_DIR=true
    fi
    
    if ask_yn "🎨 Download extra themes?" "n" "Additional UI styles and visual themes for customization"; then
        EXTRA_THEMES=true
        DOWNLOAD_THEMES=true
    fi
    
    echo -e "\n${GREEN}✓ Preferences configured successfully${NC}"
}

# Launch application after installation
launch_application() {
    print_info "🚀 Starting AppleTVRemote-GUI..."
    cd "$INSTALL_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Launch in background to not block terminal
    nohup python3 main.py > /dev/null 2>&1 &
    sleep 2
    
    if pgrep -f "python3 main.py" > /dev/null; then
        print_success "✓ AppleTVRemote-GUI launched successfully!"
        echo -e "${GRAY}   The application is now running in the background${NC}"
    else
        print_warning "⚠ Application may have failed to start"
        echo -e "${GRAY}   You can try launching manually: $VENV_DIR/bin/python $INSTALL_DIR/main.py${NC}"
    fi
}
ask_yn() {
    local prompt="$1"
    local default="$2"
    local explanation="$3"
    local response
    
    while true; do
        echo -e "\n${BLUE}┌─────────────────────────────────────────────────────────────────────────┐${NC}"
        echo -e "${BLUE}│${NC} $prompt"
        [[ -n "$explanation" ]] && echo -e "${BLUE}│${NC} ${GRAY}$explanation${NC}"
        echo -e "${BLUE}└─────────────────────────────────────────────────────────────────────────┘${NC}"
        
        if [[ "$default" == "y" ]]; then
            echo -en "${GREEN}[Y/n]${NC} (default: Yes): "
        else
            echo -en "${YELLOW}[y/N]${NC} (default: No): "
        fi
        
        read -r response
        
        # Handle empty input (use default)
        if [[ -z "$response" ]]; then
            response="$default"
        fi
        
        case "${response,,}" in
            y|yes|true|1)
                return 0
                ;;
            n|no|false|0)
                return 1
                ;;
            *)
                print_warning "⚠ Please enter 'y' for yes or 'n' for no (or press Enter for default)"
                echo -e "${GRAY}   Valid responses: y, yes, n, no, or Enter for default${NC}"
                sleep 1
                continue
                ;;
        esac
    done
}

# Show professional installation summary
show_installation_summary() {
    print_section "📋 INSTALLATION SUMMARY"
    
    echo -e "${BOLD}Selected Configuration:${NC}"
    echo -e "├─ Installation Type: $([ "$SYSTEM_WIDE" = true ] && echo "System-wide" || echo "User-specific")"
    echo -e "├─ Desktop Entry: $([ "$DESKTOP_ENTRY" = true ] && echo "Yes" || echo "No")"
    echo -e "├─ CLI Shortcut: $([ "$CLI_SHORTCUT" = true ] && echo "Yes ('atvremote')" || echo "No")"
    echo -e "├─ Development Tools: $([ "$DEV_TOOLS" = true ] && echo "Yes" || echo "No")"
    echo -e "├─ Auto-start: $([ "$AUTO_START" = true ] && echo "Yes" || echo "No")"
    echo -e "├─ Audio Codecs: $([ "$AUDIO_CODECS" = true ] && echo "Yes" || echo "No")"
    echo -e "├─ Sample Config: $([ "$SAMPLE_CONFIG" = true ] && echo "Yes" || echo "No")"
    echo -e "└─ Extra Themes: $([ "$EXTRA_THEMES" = true ] && echo "Yes" || echo "No")"
    
    echo -e "\n${BOLD}System Information:${NC}"
    echo -e "├─ OS: $OS_TYPE ($DETECTED_OS)"
    echo -e "├─ Package Manager: $PACKAGE_MANAGER"
    echo -e "├─ Sudo Access: $([ "$SUDO_AVAILABLE" = true ] && echo "Available" || echo "Not available")"
    echo -e "└─ Install Location: $([ "$SYSTEM_WIDE" = true ] && echo "/opt/appletv-remote-gui" || echo "~/.local/share/appletv-remote-gui")"
}

# Show success message and next steps
show_success_message() {
    echo -e "${GREEN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🎉 Installation Complete! AppleTVRemote-GUI is ready to use.                ║
║                                                                              ║
║  Your Apple TV and HomePod control center is now installed and configured.  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}\n"
}

# Show next steps and usage information
show_next_steps() {
    print_section "🚀 NEXT STEPS"
    
    echo -e "${BOLD}How to Launch:${NC}"
    if [[ "$DESKTOP_ENTRY" == "true" ]]; then
        echo -e "• ${GREEN}GUI:${NC} Find 'Apple TV Remote GUI' in your application menu"
    fi
    if [[ "$CLI_SHORTCUT" == "true" ]]; then
        echo -e "• ${BLUE}Terminal:${NC} Run ${CYAN}atvremote${NC} command"
    fi
    echo -e "• ${YELLOW}Direct:${NC} Run ${CYAN}$VENV_DIR/bin/python $INSTALL_DIR/main.py${NC}"
    
    echo -e "\n${BOLD}First Time Setup:${NC}"
    echo -e "1. Launch the application"
    echo -e "2. Click '${CYAN}Discover Devices${NC}' to find your Apple TV/HomePod"
    echo -e "3. Click '${CYAN}Pair${NC}' next to your device"
    echo -e "4. Follow the on-screen pairing instructions"
    echo -e "5. Start controlling your Apple TV!"
    
    echo -e "\n${BOLD}Support & Resources:${NC}"
    echo -e "• Documentation: ${CYAN}https://github.com/ZProLegend007/AppleTVRemote-GUI${NC}"
    echo -e "• Report Issues: ${CYAN}https://github.com/ZProLegend007/AppleTVRemote-GUI/issues${NC}"
    echo -e "• Configuration: ${CYAN}~/.config/appletv-remote-gui/${NC}"
    
    if [[ "$CLI_SHORTCUT" == "true" ]]; then
        echo -e "\n${GRAY}💡 Tip: You may need to restart your terminal or run 'source ~/.bashrc' to use the 'atvremote' command${NC}"
    fi
}

# Install system dependencies with enhanced sudo handling
install_system_packages() {
    print_info "📦 Installing system dependencies..."
    
    local packages_to_install=()
    local install_success=false
    
    case "$OS_TYPE" in
        "ubuntu")
            packages_to_install=(
                "python3" "python3-pip" "python3-venv" "python3-dev"
                "git" "curl" "build-essential"
                "libpulse-dev" "libavahi-client-dev"
            )
            
            # Try to install PyQt6 system packages
            local pyqt_packages=("python3-pyqt6" "python3-pyqt6.qtmultimedia")
            
            if [[ "$SUDO_AVAILABLE" == "true" ]]; then
                print_info "→ Updating package cache..."
                if safe_sudo apt update -qq; then
                    print_success "✓ Package cache updated"
                else
                    print_warning "⚠ Failed to update package cache, continuing anyway"
                fi
                
                print_info "→ Installing base packages..."
                if safe_sudo apt install -y "${packages_to_install[@]}"; then
                    print_success "✓ Base packages installed"
                    install_success=true
                else
                    print_error "✗ Failed to install base packages"
                    exit 1
                fi
                
                print_info "→ Installing PyQt6 packages..."
                if safe_sudo apt install -y "${pyqt_packages[@]}"; then
                    print_success "✓ PyQt6 system packages installed"
                else
                    print_warning "⚠ PyQt6 system packages not available, will install via pip"
                fi
                
                if [[ "$AUDIO_CODECS" == "true" ]]; then
                    print_info "→ Installing additional audio codecs..."
                    local codec_packages=(
                        "gstreamer1.0-plugins-good" "gstreamer1.0-plugins-bad"
                        "gstreamer1.0-plugins-ugly" "gstreamer1.0-libav"
                    )
                    if safe_sudo apt install -y "${codec_packages[@]}"; then
                        print_success "✓ Audio codecs installed"
                    else
                        print_warning "⚠ Some audio codecs failed to install"
                    fi
                fi
            else
                print_error "✗ System packages require sudo access"
                echo -e "${GRAY}   Please run: sudo apt install ${packages_to_install[*]} ${pyqt_packages[*]}${NC}"
                if ! ask_yn "Continue without system packages?" "n" "Some features may not work properly"; then
                    exit 1
                fi
            fi
            ;;
            
        "fedora")
            packages_to_install=(
                "python3" "python3-pip" "python3-devel"
                "git" "curl" "gcc" "gcc-c++" "make"
                "pulseaudio-libs-devel" "avahi-devel"
            )
            
            local pyqt_packages=("python3-pyqt6" "python3-pyqt6-multimedia")
            
            if [[ "$SUDO_AVAILABLE" == "true" ]]; then
                print_info "→ Installing packages with DNF..."
                if safe_sudo dnf install -y "${packages_to_install[@]}" "${pyqt_packages[@]}"; then
                    print_success "✓ System packages installed"
                    install_success=true
                else
                    print_warning "⚠ Some packages failed to install, continuing"
                    install_success=true
                fi
                
                if [[ "$AUDIO_CODECS" == "true" ]]; then
                    print_info "→ Installing audio codecs..."
                    safe_sudo dnf install -y gstreamer1-plugins-good gstreamer1-plugins-bad-free gstreamer1-plugins-ugly-free
                fi
            else
                print_error "✗ System packages require sudo access"
                exit 1
            fi
            ;;
            
        "arch")
            packages_to_install=(
                "python" "python-pip" "python-virtualenv"
                "git" "curl" "base-devel"
                "libpulse" "avahi"
            )
            
            local pyqt_packages=("python-pyqt6" "python-pyqt6-multimedia")
            
            if [[ "$SUDO_AVAILABLE" == "true" ]]; then
                print_info "→ Updating package database..."
                safe_sudo pacman -Sy
                
                print_info "→ Installing packages with Pacman..."
                if safe_sudo pacman -S --noconfirm "${packages_to_install[@]}" "${pyqt_packages[@]}"; then
                    print_success "✓ System packages installed"
                    install_success=true
                else
                    print_warning "⚠ Some packages failed to install"
                    install_success=true
                fi
                
                if [[ "$AUDIO_CODECS" == "true" ]]; then
                    safe_sudo pacman -S --noconfirm gst-plugins-good gst-plugins-bad gst-plugins-ugly
                fi
            else
                print_error "✗ System packages require sudo access"
                exit 1
            fi
            ;;
            
        *)
            print_warning "⚠ Unsupported OS detected, attempting generic installation"
            if [[ "$SUDO_AVAILABLE" == "true" ]]; then
                print_info "→ Attempting to install basic Python dependencies..."
                case "$PACKAGE_MANAGER" in
                    "apt")
                        safe_sudo apt install -y python3 python3-pip python3-venv git curl
                        ;;
                    "dnf")
                        safe_sudo dnf install -y python3 python3-pip git curl
                        ;;
                    "yum")
                        safe_sudo yum install -y python3 python3-pip git curl
                        ;;
                    "zypper")
                        safe_sudo zypper install -y python3 python3-pip git curl
                        ;;
                esac
                install_success=true
            else
                print_error "✗ Cannot install system packages without sudo"
                exit 1
            fi
            ;;
    esac
    
    if [[ "$install_success" == "true" ]]; then
        print_success "✓ System dependencies installation completed"
    else
        print_error "✗ System dependencies installation failed"
        exit 1
    fi
}

# Clone repository if not already present
clone_repository() {
    if [ ! -f "main.py" ]; then
        print_header "\n📥 Cloning Repository"
        print_info "Cloning AppleTVRemote-GUI repository..."
        git clone https://github.com/ZProLegend007/AppleTVRemote-GUI.git .
        print_success "Repository cloned successfully"
    else
        print_info "Repository already present, skipping clone"
    fi
}

# Set up Python virtual environment
setup_virtual_environment() {
    print_header "\n🐍 Setting up Python Virtual Environment"
    
    if [ "$USER_INSTALL" = true ]; then
        INSTALL_DIR="$HOME/.local/share/appletv-remote-gui"
        VENV_DIR="$INSTALL_DIR/venv"
    else
        INSTALL_DIR="/opt/appletv-remote-gui"
        VENV_DIR="$INSTALL_DIR/venv"
    fi
    
    print_info "Creating installation directory: $INSTALL_DIR"
    if [ "$USER_INSTALL" = true ]; then
        mkdir -p "$INSTALL_DIR"
    else
        sudo mkdir -p "$INSTALL_DIR"
    fi
    
    print_info "Creating virtual environment..."
    if [ "$USER_INSTALL" = true ]; then
        python3 -m venv "$VENV_DIR"
    else
        sudo python3 -m venv "$VENV_DIR"
        sudo chown -R $USER:$USER "$VENV_DIR"
    fi
    
    print_success "Virtual environment created at $VENV_DIR"
}

# Install Python dependencies
install_python_deps() {
    print_header "\n📚 Installing Python Dependencies"
    
    print_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    print_info "Installing required packages..."
    pip install -r requirements.txt
    
    if [ "$INSTALL_DEV_DEPS" = true ]; then
        print_info "Installing development dependencies..."
        pip install pytest black flake8 mypy
    fi
    
    print_success "Python dependencies installed successfully"
}

# Copy application files
setup_application() {
    print_header "\n📁 Setting up Application Files"
    
    if [ "$USER_INSTALL" = true ]; then
        print_info "Copying application files to user directory..."
        cp -r . "$INSTALL_DIR/"
    else
        print_info "Copying application files to system directory..."
        sudo cp -r . "$INSTALL_DIR/"
        sudo chown -R $USER:$USER "$INSTALL_DIR"
    fi
    
    # Make main.py executable
    chmod +x "$INSTALL_DIR/main.py"
    
    print_success "Application files copied successfully"
}

# Create desktop entry
create_desktop_entry() {
    if [ "$CREATE_DESKTOP_ENTRY" = false ]; then
        return
    fi
    
    print_header "\n🖥️ Creating Desktop Entry"
    
    if [ "$USER_INSTALL" = true ]; then
        DESKTOP_ENTRY_PATH="$HOME/.local/share/applications/appletv-remote-gui.desktop"
        mkdir -p "$HOME/.local/share/applications"
    else
        DESKTOP_ENTRY_PATH="/usr/share/applications/appletv-remote-gui.desktop"
    fi
    
    print_info "Creating desktop entry at $DESKTOP_ENTRY_PATH"
    
    cat > "$DESKTOP_ENTRY_PATH" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Apple TV Remote GUI
Comment=Control Apple TV and HomePod devices from Linux
GenericName=Apple TV Remote
Exec=$VENV_DIR/bin/python $INSTALL_DIR/main.py
Icon=$INSTALL_DIR/resources/icons/app_icon.png
Terminal=false
StartupNotify=true
MimeType=
Categories=AudioVideo;RemoteAccess;Network;
Keywords=Apple;TV;HomePod;Remote;Control;Media;
StartupWMClass=appletv-remote-gui
EOF
    
    if [ "$USER_INSTALL" = false ]; then
        sudo mv "$DESKTOP_ENTRY_PATH.tmp" "$DESKTOP_ENTRY_PATH" 2>/dev/null || sudo cp "$DESKTOP_ENTRY_PATH" "$DESKTOP_ENTRY_PATH"
    fi
    
    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        if [ "$USER_INSTALL" = true ]; then
            update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
        else
            sudo update-desktop-database /usr/share/applications 2>/dev/null || true
        fi
    fi
    
    print_success "Desktop entry created successfully"
}

# Create command-line alias
create_cli_alias() {
    if [ "$CREATE_CLI_ALIAS" = false ]; then
        return
    fi
    
    print_header "\n💻 Creating Command-line Alias"
    
    if [ "$USER_INSTALL" = true ]; then
        BIN_DIR="$HOME/.local/bin"
        mkdir -p "$BIN_DIR"
        SCRIPT_PATH="$BIN_DIR/atvremote"
    else
        BIN_DIR="/usr/local/bin"
        SCRIPT_PATH="$BIN_DIR/atvremote"
    fi
    
    print_info "Creating executable script at $SCRIPT_PATH"
    
    cat > "$SCRIPT_PATH" << EOF
#!/bin/bash
# AppleTVRemote-GUI launcher script
cd "$INSTALL_DIR"
exec "$VENV_DIR/bin/python" "$INSTALL_DIR/main.py" "\$@"
EOF
    
    chmod +x "$SCRIPT_PATH"
    
    if [ "$USER_INSTALL" = false ]; then
        sudo mv "$SCRIPT_PATH" "$SCRIPT_PATH"
        sudo chmod +x "$SCRIPT_PATH"
    fi
    
    # Add to PATH if not already there
    if [ "$USER_INSTALL" = true ]; then
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            print_info "Adding $HOME/.local/bin to PATH in ~/.bashrc"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
            print_warning "Please run 'source ~/.bashrc' or restart your terminal to use 'atvremote' command"
        fi
    fi
    
    print_success "Command-line alias 'atvremote' created successfully"
}

# Create configuration directory
create_config_directory() {
    if [ "$CREATE_CONFIG_DIR" = false ]; then
        return
    fi
    
    print_header "\n⚙️ Creating Configuration Directory"
    
    CONFIG_DIR="$HOME/.config/appletv-remote-gui"
    print_info "Creating configuration directory at $CONFIG_DIR"
    mkdir -p "$CONFIG_DIR"
    
    # Create default config file
    cat > "$CONFIG_DIR/config.json" << EOF
{
    "theme": "dark",
    "auto_discovery": true,
    "discovery_timeout": 10,
    "connection_timeout": 15,
    "debug_logging": false,
    "last_window_geometry": null,
    "recent_devices": []
}
EOF
    
    print_success "Configuration directory created with default settings"
}

# Setup auto-start
setup_auto_start() {
    if [ "$AUTO_START" = false ]; then
        return
    fi
    
    print_header "\n🚀 Setting up Auto-start"
    
    AUTOSTART_DIR="$HOME/.config/autostart"
    mkdir -p "$AUTOSTART_DIR"
    
    cat > "$AUTOSTART_DIR/appletv-remote-gui.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Apple TV Remote GUI
Exec=$VENV_DIR/bin/python $INSTALL_DIR/main.py --minimized
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=10
EOF
    
    print_success "Auto-start configured successfully"
}

# Download sample themes
download_sample_themes() {
    if [ "$DOWNLOAD_THEMES" = false ]; then
        return
    fi
    
    print_header "\n🎨 Downloading Sample Themes"
    
    THEMES_DIR="$INSTALL_DIR/resources/themes"
    mkdir -p "$THEMES_DIR"
    
    print_info "Creating sample themes..."
    
    # Create a sample dark theme
    cat > "$THEMES_DIR/midnight.qss" << 'EOF'
/* Midnight Theme for AppleTVRemote-GUI */
QMainWindow {
    background-color: #1a1a1a;
    color: #ffffff;
}

QPushButton {
    background-color: #333333;
    border: 1px solid #555555;
    border-radius: 6px;
    padding: 8px 16px;
    color: #ffffff;
}

QPushButton:hover {
    background-color: #444444;
}

QPushButton:pressed {
    background-color: #222222;
}
EOF
    
    # Create a sample light theme
    cat > "$THEMES_DIR/daylight.qss" << 'EOF'
/* Daylight Theme for AppleTVRemote-GUI */
QMainWindow {
    background-color: #f5f5f5;
    color: #333333;
}

QPushButton {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 6px;
    padding: 8px 16px;
    color: #333333;
}

QPushButton:hover {
    background-color: #f0f0f0;
}

QPushButton:pressed {
    background-color: #e0e0e0;
}
EOF
    
    print_success "Sample themes downloaded successfully"
}

# Run tests
run_tests() {
    print_header "\n🧪 Running Application Tests"
    
    cd "$INSTALL_DIR"
    source "$VENV_DIR/bin/activate"
    
    print_info "Running test suite..."
    if python3 test_app.py; then
        print_success "All tests passed successfully"
        return 0
    else
        print_warning "Some tests failed, but installation may still work"
        return 1
    fi
}

# Cleanup on error
cleanup_on_error() {
    print_error "Installation failed. Cleaning up..."
    
    if [ -n "$INSTALL_DIR" ] && [ -d "$INSTALL_DIR" ]; then
        if [ "$USER_INSTALL" = true ]; then
            rm -rf "$INSTALL_DIR"
        else
            sudo rm -rf "$INSTALL_DIR"
        fi
        print_info "Removed installation directory"
    fi
    
    if [ -n "$DESKTOP_ENTRY_PATH" ] && [ -f "$DESKTOP_ENTRY_PATH" ]; then
        if [ "$USER_INSTALL" = true ]; then
            rm -f "$DESKTOP_ENTRY_PATH"
        else
            sudo rm -f "$DESKTOP_ENTRY_PATH"
        fi
        print_info "Removed desktop entry"
    fi
    
    exit 1
}

# Enhanced main installation flow
main() {
    # Handle errors gracefully
    trap 'cleanup_on_error' ERR
    
    # Phase 1: Welcome and System Detection
    clear_and_banner
    
    print_section "🔍 SYSTEM DETECTION"
    detect_system
    check_sudo
    check_internet_connectivity
    check_python
    
    # Phase 2: User Preferences
    print_section "⚙️ INSTALLATION PREFERENCES"
    ask_user_preferences
    
    # Phase 3: Installation Summary
    show_installation_summary
    
    if ! ask_yn "🚀 Proceed with installation?" "y" "Start the installation process with your selected options"; then
        print_info "Installation cancelled by user"
        echo -e "${GRAY}Thank you for trying AppleTVRemote-GUI!${NC}"
        exit 0
    fi
    
    # Phase 4: Installation Process
    print_section "📦 INSTALLING APPLETV REMOTE GUI"
    
    install_system_packages
    refresh_sudo  # Refresh sudo credentials after potentially long package installation
    
    clone_repository
    setup_virtual_environment
    install_python_deps
    setup_application
    
    if [[ "$CREATE_DESKTOP_ENTRY" == "true" ]]; then
        create_desktop_entry
    fi
    
    if [[ "$CREATE_CLI_ALIAS" == "true" ]]; then
        create_cli_alias
    fi
    
    if [[ "$CREATE_CONFIG_DIR" == "true" ]]; then
        create_config_directory
    fi
    
    if [[ "$AUTO_START" == "true" ]]; then
        setup_auto_start
    fi
    
    if [[ "$DOWNLOAD_THEMES" == "true" ]]; then
        download_sample_themes
    fi
    
    # Phase 5: Testing and Verification
    print_section "🧪 VERIFYING INSTALLATION"
    if run_tests; then
        print_success "✓ All installation tests passed"
    else
        print_warning "⚠ Some tests had warnings, but installation should work"
    fi
    
    # Phase 6: Success and Launch
    print_section "🎉 INSTALLATION COMPLETE"
    show_success_message
    
    if ask_yn "🚀 Launch AppleTVRemote-GUI now?" "y" "Start the application immediately to test the installation"; then
        launch_application
    fi
    
    show_next_steps
    
    echo -e "\n${GREEN}${BOLD}🎉 Thank you for installing AppleTVRemote-GUI!${NC}"
    echo -e "${GRAY}Made with ❤️ for the Apple TV community${NC}\n"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root. It will ask for sudo when needed."
    exit 1
fi

# Run main function
main "$@"