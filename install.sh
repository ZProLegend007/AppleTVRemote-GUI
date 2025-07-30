#!/bin/bash

# ApplerGUI Professional Installer
# One-line install: curl -fsSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/install.sh | bash

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

# Clean section display with proper clearing
show_section() {
    local title="$1"
    clear
    echo -e "${PURPLE}"
    cat << EOF
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║   🍎 ApplerGUI Professional Installer                                      ║
║                                                                            ║
║   Modern Linux GUI for Apple TV & HomePod Control                         ║
║                                                                            ║
║   ✨ Automated Installation with Smart Dependency Management               ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}\n"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE} $title${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Section header for prompts
show_section_header() {
    local title="$1"
    echo -e "${PURPLE}"
    cat << EOF
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
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE} $title${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Clear terminal and show fancy banner
clear_and_banner() {
    clear
    echo -e "${PURPLE}"
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║   🍎 ApplerGUI Professional Installer                                      ║
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
INSTALL_PYQT6_VIA_PIP=false

# Clean spinner animation that doesn't conflict with command output
show_spinner_clean() {
    local pid=$1
    local message="$2"
    local spin='⣾⣽⣻⢿⡿⣟⣯⣷'
    local i=0
    
    # Hide command output, show only spinner
    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) %8 ))
        printf "\r${BLUE}${spin:$i:1}${NC} $message"
        sleep .1
    done
    
    # Clear spinner line and show result
    printf "\r\033[K"
    
    # Check exit code and show appropriate message
    wait $pid
    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        printf "✓ $message\n"
    else
        printf "✗ $message (failed)\n"
    fi
    
    return $exit_code
}

# Progress bar for installations
show_progress() {
    local current=$1
    local total=$2
    local message="$3"
    local percent=$((current * 100 / total))
    local filled=$((percent / 5))
    local empty=$((20 - filled))
    
    printf "\r${BLUE}%s${NC} [" "$message"
    printf "%*s" $filled | tr ' ' '█'
    printf "%*s" $empty | tr ' ' '░'
    printf "] %d%%" $percent
}

# Animated dots for waiting states
show_waiting_dots() {
    local message="$1"
    local duration="${2:-3}"
    local dots=""
    
    for i in $(seq 1 $duration); do
        dots+="."
        echo -ne "\r${BLUE}$message$dots${NC}"
        sleep 1
    done
    echo
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
    show_section "⚙️ INSTALLATION PREFERENCES"
    echo -e "${GRAY}Configure your ApplerGUI installation with the options below.${NC}"
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
    
    if ask_yn "🖥️ Create desktop entry?" "y" "Add ApplerGUI to your application menu for easy access"; then
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
    
    if ask_yn "💻 Create command-line shortcut?" "y" "Add 'applergui' command to your PATH for terminal access"; then
        CLI_SHORTCUT=true
        CREATE_CLI_ALIAS=true
    fi
    
    if ask_yn "🔧 Install development tools?" "n" "Additional dependencies for contributing code (pytest, linting tools)"; then
        DEV_TOOLS=true
        INSTALL_DEV_DEPS=true
    fi
    
    if ask_yn "🚀 Enable auto-start?" "n" "Launch ApplerGUI automatically when you log in"; then
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
    
    clear
    echo -e "\n${GREEN}✓ Preferences configured successfully${NC}"
    show_waiting_dots "Processing your preferences" 2
}

# Launch application after installation
launch_application() {
    print_info "🚀 Starting ApplerGUI..."
    cd "$INSTALL_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Launch in background to not block terminal
    nohup python3 main.py > /dev/null 2>&1 &
    sleep 2
    
    if pgrep -f "python3 main.py" > /dev/null; then
        print_success "✓ ApplerGUI launched successfully!"
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
        clear
        show_section "⚙️ INSTALLATION PREFERENCES"
        
        echo -e "\n${BLUE}┌─────────────────────────────────────────────────────────────────────────┐${NC}"
        echo -e "${BLUE}│${NC} $prompt"
        [[ -n "$explanation" ]] && echo -e "${BLUE}│${NC} ${GRAY}$explanation${NC}"
        echo -e "${BLUE}└─────────────────────────────────────────────────────────────────────────┘${NC}"
        
        if [[ "$default" == "y" ]]; then
            echo -en "${GREEN}[Y/n]${NC} (default: Yes): "
        else
            echo -en "${YELLOW}[y/N]${NC} (default: No): "
        fi
        
        # CRITICAL: Actually wait for user input from terminal
        read -r response < /dev/tty
        
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
                echo -e "\n${RED}⚠ Please enter 'y' for yes or 'n' for no${NC}"
                echo -e "${GRAY}Press Enter to continue...${NC}"
                read -r < /dev/tty
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
    echo -e "├─ CLI Shortcut: $([ "$CLI_SHORTCUT" = true ] && echo "Yes ('applergui')" || echo "No")"
    echo -e "├─ Development Tools: $([ "$DEV_TOOLS" = true ] && echo "Yes" || echo "No")"
    echo -e "├─ Auto-start: $([ "$AUTO_START" = true ] && echo "Yes" || echo "No")"
    echo -e "├─ Audio Codecs: $([ "$AUDIO_CODECS" = true ] && echo "Yes" || echo "No")"
    echo -e "├─ Sample Config: $([ "$SAMPLE_CONFIG" = true ] && echo "Yes" || echo "No")"
    echo -e "└─ Extra Themes: $([ "$EXTRA_THEMES" = true ] && echo "Yes" || echo "No")"
    
    echo -e "\n${BOLD}System Information:${NC}"
    echo -e "├─ OS: $OS_TYPE ($DETECTED_OS)"
    echo -e "├─ Package Manager: $PACKAGE_MANAGER"
    echo -e "├─ Sudo Access: $([ "$SUDO_AVAILABLE" = true ] && echo "Available" || echo "Not available")"
    echo -e "└─ Install Location: $([ "$SYSTEM_WIDE" = true ] && echo "/opt/applergui" || echo "~/.local/share/applergui")"
}

# Show success message and next steps
show_success_message() {
    echo -e "${GREEN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🎉 Installation Complete! ApplerGUI is ready to use.                      ║
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
        echo -e "• ${GREEN}GUI:${NC} Find 'ApplerGUI' in your application menu"
    fi
    if [[ "$CLI_SHORTCUT" == "true" ]]; then
        echo -e "• ${BLUE}Terminal:${NC} Run ${CYAN}applergui${NC} command"
    fi
    
    echo -e "\n${BOLD}Installation Details:${NC}"
    echo -e "• Location: ${CYAN}$INSTALL_DIR${NC}"
    echo -e "• Command: ${CYAN}applergui${NC}"
    echo -e "• Update: ${CYAN}applergui --update${NC}"
    
    echo -e "\n${BOLD}First Time Setup:${NC}"
    echo -e "1. Launch the application"
    echo -e "2. Click '${CYAN}Discover Devices${NC}' to find your Apple TV/HomePod"
    echo -e "3. Click '${CYAN}Pair${NC}' next to your device"
    echo -e "4. Follow the on-screen pairing instructions"
    echo -e "5. Start controlling your Apple TV!"
    
    echo -e "\n${BOLD}Support & Resources:${NC}"
    echo -e "• Documentation: ${CYAN}https://github.com/ZProLegend007/ApplerGUI${NC}"
    echo -e "• Report Issues: ${CYAN}https://github.com/ZProLegend007/ApplerGUI/issues${NC}"
    echo -e "• Configuration: ${CYAN}~/.config/applergui/${NC}"
    
    if [[ "$CLI_SHORTCUT" == "true" ]]; then
        echo -e "\n${GRAY}💡 Tip: You may need to restart your terminal or run 'source ~/.bashrc' to use the 'applergui' command${NC}"
    fi
}

# Helper function for package installation with proper error handling
install_packages_with_spinner() {
    local packages=("$@")
    
    {
        safe_sudo apt install -y "${packages[@]}" 2>&1
    } &
    local apt_pid=$!
    
    show_spinner_clean $apt_pid "Installing ${packages[*]}"
    wait $apt_pid
    local exit_code=$?
    
    return $exit_code
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
                {
                    safe_sudo apt update -qq 2>&1
                } &
                show_spinner_clean $! "Updating package cache"
                wait $!
                if [[ $? -eq 0 ]]; then
                    print_success "✓ Package cache updated"
                else
                    print_warning "⚠ Failed to update package cache, continuing anyway"
                fi
                
                print_info "→ Installing base packages..."
                {
                    safe_sudo apt install -y "${packages_to_install[@]}" 2>&1
                } &
                show_spinner_clean $! "Installing base system packages"
                wait $!
                if [[ $? -eq 0 ]]; then
                    print_success "✓ Base packages installed"
                    install_success=true
                else
                    print_error "✗ Failed to install base packages"
                    exit 1
                fi
                
                print_info "→ Installing PyQt6 packages..."
                if install_packages_with_spinner "${pyqt_packages[@]}"; then
                    print_success "✓ ✓ PyQt6 system packages installed"
                else
                    print_warning "⚠ ⚠ PyQt6 system packages not available"
                    print_info "ℹ ℹ Will install PyQt6 via pip instead"
                    INSTALL_PYQT6_VIA_PIP=true
                fi
                
                if [[ "$AUDIO_CODECS" == "true" ]]; then
                    print_info "→ Installing additional audio codecs..."
                    local codec_packages=(
                        "gstreamer1.0-plugins-good" "gstreamer1.0-plugins-bad"
                        "gstreamer1.0-plugins-ugly" "gstreamer1.0-libav"
                    )
                    {
                        safe_sudo apt install -y "${codec_packages[@]}" 2>&1
                    } &
                    show_spinner_clean $! "Installing audio codecs"
                    wait $!
                    if [[ $? -eq 0 ]]; then
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
                {
                    safe_sudo dnf install -y "${packages_to_install[@]}" "${pyqt_packages[@]}" 2>&1
                } &
                show_spinner_clean $! "Installing packages with DNF"
                wait $!
                if [[ $? -eq 0 ]]; then
                    print_success "✓ System packages installed"
                    install_success=true
                else
                    print_warning "⚠ Some packages failed to install, continuing"
                    install_success=true
                fi
                
                if [[ "$AUDIO_CODECS" == "true" ]]; then
                    print_info "→ Installing audio codecs..."
                    {
                        safe_sudo dnf install -y gstreamer1-plugins-good gstreamer1-plugins-bad-free gstreamer1-plugins-ugly-free 2>&1
                    } &
                    show_spinner_clean $! "Installing audio codecs"
                    wait $!
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
                {
                    safe_sudo pacman -Sy 2>&1
                } &
                show_spinner_clean $! "Updating package database"
                wait $!
                
                print_info "→ Installing packages with Pacman..."
                {
                    safe_sudo pacman -S --noconfirm "${packages_to_install[@]}" "${pyqt_packages[@]}" 2>&1
                } &
                show_spinner_clean $! "Installing packages with Pacman"
                wait $!
                if [[ $? -eq 0 ]]; then
                    print_success "✓ System packages installed"
                    install_success=true
                else
                    print_warning "⚠ Some packages failed to install"
                    install_success=true
                fi
                
                if [[ "$AUDIO_CODECS" == "true" ]]; then
                    {
                        safe_sudo pacman -S --noconfirm gst-plugins-good gst-plugins-bad gst-plugins-ugly 2>&1
                    } &
                    show_spinner_clean $! "Installing audio codecs"
                    wait $!
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
                        {
                            safe_sudo apt install -y python3 python3-pip python3-venv git curl 2>&1
                        } &
                        show_spinner_clean $! "Installing basic dependencies"
                        wait $!
                        ;;
                    "dnf")
                        {
                            safe_sudo dnf install -y python3 python3-pip git curl 2>&1
                        } &
                        show_spinner_clean $! "Installing basic dependencies"
                        wait $!
                        ;;
                    "yum")
                        {
                            safe_sudo yum install -y python3 python3-pip git curl 2>&1
                        } &
                        show_spinner_clean $! "Installing basic dependencies"
                        wait $!
                        ;;
                    "zypper")
                        {
                            safe_sudo zypper install -y python3 python3-pip git curl 2>&1
                        } &
                        show_spinner_clean $! "Installing basic dependencies"
                        wait $!
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
        print_success "✓ ✓ System dependencies installation completed"
        
        # Show installation summary
        local success_packages=("base system packages")
        local failed_packages=()
        
        if [[ "$INSTALL_PYQT6_VIA_PIP" == "true" ]]; then
            failed_packages+=("PyQt6 system packages")
            print_info "   ℹ Successfully installed: ${success_packages[*]}"
            print_warning "   ⚠ Failed to install: ${failed_packages[*]} (will use pip fallback)"
        else
            success_packages+=("PyQt6 system packages")
            print_info "   ℹ Successfully installed: ${success_packages[*]}"
        fi
        
        sleep 2  # Let user see the summary
    else
        print_error "✗ System dependencies installation failed"
        exit 1
    fi
}

# Enhanced installation directory management
setup_installation_directory() {
    print_info "→ 📁 Setting up installation directory..."
    
    # User-specific installation path
    local install_dir="$HOME/.local/share/applergui"
    
    # Create directory structure
    mkdir -p "$install_dir"
    cd "$install_dir" || {
        print_error "✗ Cannot access installation directory"
        exit 1
    }
    
    # Set global variable for other functions
    export INSTALL_DIR="$install_dir"
    export VENV_DIR="$install_dir/venv"
    
    print_success "✓ Installation directory: $install_dir"
}

# Proper directory and repository management
setup_repository() {
    show_section "📥 DOWNLOADING APPLICATION"
    
    # Setup installation directory first
    setup_installation_directory
    
    print_info "→ Cloning repository..."
    {
        git clone --depth 1 https://github.com/ZProLegend007/ApplerGUI.git "$INSTALL_DIR" 2>&1
    } &
    show_spinner_clean $! "Downloading ApplerGUI"
    
    wait $!
    if [[ $? -eq 0 ]]; then
        print_success "✓ Repository cloned successfully"
    else
        print_error "✗ Failed to clone repository"
        exit 1
    fi
}

# Set up Python virtual environment
setup_virtual_environment() {
    print_info "🐍 Creating Python virtual environment..."
    
    # CRITICAL FIX: Ensure INSTALL_DIR is set before proceeding
    if [[ -z "$INSTALL_DIR" ]]; then
        print_error "✗ Installation directory not set. Cannot create virtual environment."
        exit 1
    fi
    
    # FIXED: Use proper user directory path within the installation directory
    VENV_DIR="$INSTALL_DIR/venv"
    
    # Ensure we're in the correct directory
    cd "$INSTALL_DIR" || {
        print_error "✗ Installation directory not found: $INSTALL_DIR"
        exit 1
    }
    
    print_info "→ Creating virtual environment..."
    {
        python3 -m venv "$VENV_DIR" 2>&1
    } &
    local venv_pid=$!
    
    show_spinner_clean $venv_pid "Creating Python virtual environment"
    wait $venv_pid
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        print_success "✓ ✓ Virtual environment created successfully"
    else
        print_error "✗ ✗ Failed to create virtual environment"
        exit 1
    fi
    
    # Activate virtual environment
    print_info "→ Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    if [[ "$VIRTUAL_ENV" == "$VENV_DIR" ]]; then
        print_success "✓ ✓ Virtual environment activated"
    else
        print_error "✗ ✗ Failed to activate virtual environment"
        exit 1
    fi
    
    # Upgrade pip in virtual environment
    print_info "→ Upgrading pip..."
    {
        pip install --upgrade pip 2>&1
    } &
    local pip_pid=$!
    
    show_spinner_clean $pip_pid "Upgrading pip"
    wait $pip_pid
    
    if [[ $? -eq 0 ]]; then
        print_success "✓ ✓ Pip upgraded successfully"
    else
        print_warning "⚠ ⚠ Pip upgrade failed - continuing anyway"
    fi
    
    sleep 1
}

# Install Python dependencies
install_python_deps() {
    show_section "📦 INSTALLING PYTHON DEPENDENCIES"
    
    print_info "→ 📦 Installing Python packages..."
    
    # Ensure virtual environment is activated
    if [[ -z "$VIRTUAL_ENV" ]]; then
        source "$VENV_DIR/bin/activate"
    fi
    
    # Install PyQt6 via pip if system packages weren't available
    if [[ "${INSTALL_PYQT6_VIA_PIP:-false}" == "true" ]]; then
        print_info "→ → Installing PyQt6 via pip..."
        {
            pip install PyQt6 PyQt6-Qt6 2>&1
        } &
        show_spinner_clean $! "Installing PyQt6 via pip"
        
        if [[ $? -eq 0 ]]; then
            print_success "✓ ✓ PyQt6 installed via pip"
        else
            print_error "✗ ✗ Failed to install PyQt6 via pip"
            exit 1
        fi
    fi
    
    # Install application dependencies
    if [[ -f "$INSTALL_DIR/requirements.txt" ]]; then
        print_info "→ → Installing application dependencies..."
        {
            pip install -r "$INSTALL_DIR/requirements.txt" 2>&1
        } &
        show_spinner_clean $! "Installing application dependencies"
        
        if [[ $? -eq 0 ]]; then
            print_success "✓ ✓ Application dependencies installed"
        else
            print_error "✗ ✗ Failed to install application dependencies"
            exit 1
        fi
    fi
    
    # Install in development mode
    print_info "→ → Installing ApplerGUI..."
    {
        pip install -e "$INSTALL_DIR" 2>&1
    } &
    show_spinner_clean $! "Installing ApplerGUI"
    
    if [[ $? -eq 0 ]]; then
        print_success "✓ ✓ ApplerGUI installed successfully"
    else
        print_error "✗ ✗ Failed to install ApplerGUI"
        exit 1
    fi
    
    if [ "$INSTALL_DEV_DEPS" = true ]; then
        print_info "→ → Installing development dependencies..."
        {
            pip install pytest black flake8 mypy 2>&1
        } &
        show_spinner_clean $! "Installing development tools"
        wait $!
        
        if [[ $? -eq 0 ]]; then
            print_success "✓ ✓ Development dependencies installed"
        else
            print_warning "⚠ ⚠ Some development dependencies failed to install"
        fi
    fi
    
    print_success "✓ Python environment setup completed"
}

# Copy application files
setup_application() {
    print_info "📁 Configuring application files..."
    
    # Files are already in INSTALL_DIR from git clone, just need to set permissions
    print_info "→ Setting file permissions..."
    
    # Make main.py executable
    chmod +x "$INSTALL_DIR/main.py"
    
    # Set proper ownership if system-wide install
    if [ "$USER_INSTALL" = false ]; then
        sudo chown -R $USER:$USER "$INSTALL_DIR"
    fi
    
    print_success "✓ Application files configured successfully"
}

# Create desktop entry
create_desktop_entry() {
    if [ "$CREATE_DESKTOP_ENTRY" = false ]; then
        return
    fi
    
    print_header "\n🖥️ Creating Desktop Entry"
    
    if [ "$USER_INSTALL" = true ]; then
        DESKTOP_ENTRY_PATH="$HOME/.local/share/applications/applergui.desktop"
        mkdir -p "$HOME/.local/share/applications"
    else
        DESKTOP_ENTRY_PATH="/usr/share/applications/applergui.desktop"
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
StartupWMClass=applergui
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
    
    # Use the enhanced CLI command instead of simple script
    create_enhanced_cli_command
    
    print_success "Command-line alias 'applergui' created successfully"
}

# Create configuration directory
create_config_directory() {
    if [ "$CREATE_CONFIG_DIR" = false ]; then
        return
    fi
    
    print_header "\n⚙️ Creating Configuration Directory"
    
    CONFIG_DIR="$HOME/.config/applergui"
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
    
    cat > "$AUTOSTART_DIR/applergui.desktop" << EOF
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
/* Dark Theme for ApplerGUI */
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
/* Light Theme for ApplerGUI */
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
    show_waiting_dots "Initializing installer" 2
    
    show_section "🔍 SYSTEM DETECTION"
    detect_system
    check_sudo
    check_internet_connectivity
    check_python
    
    show_waiting_dots "System detection complete" 2
    
    # Phase 2: User Preferences (with proper clearing)
    ask_user_preferences
    
    # Phase 3: Installation Summary
    show_section "📋 INSTALLATION SUMMARY"
    show_installation_summary
    
    if ! ask_yn "🚀 Proceed with installation?" "y" "Start the installation process with your selected options"; then
        clear
        print_info "Installation cancelled by user"
        echo -e "${GRAY}Thank you for trying ApplerGUI!${NC}"
        exit 0
    fi
    
    # Phase 4: Installation Process
    show_section "📦 INSTALLING SYSTEM PACKAGES"
    install_system_packages
    refresh_sudo  # Refresh sudo credentials after potentially long package installation
    
    # CRITICAL FIX: Setup repository BEFORE Python environment to ensure INSTALL_DIR is set
    show_section "📥 DOWNLOADING APPLICATION"
    setup_repository
    
    show_section "🐍 SETTING UP PYTHON ENVIRONMENT"
    setup_virtual_environment
    install_python_deps
    
    show_section "⚙️ CONFIGURING APPLICATION"
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
    show_section "🧪 VERIFYING INSTALLATION"
    if run_tests; then
        print_success "✓ All installation tests passed"
    else
        print_warning "⚠ Some tests had warnings, but installation should work"
    fi
    
    # Phase 6: Success and Launch
    show_section "🎉 INSTALLATION COMPLETE"
    show_success_message
    
    if ask_yn "🚀 Launch ApplerGUI now?" "y" "Start the application immediately to test the installation"; then
        launch_application
    fi
    
    clear
    show_next_steps
    
    echo -e "\n${GREEN}${BOLD}🎉 Thank you for installing ApplerGUI!${NC}"
    
    # Create update functionality
    create_update_functionality
}

# Create update script and functionality
create_update_functionality() {
    local install_dir="$INSTALL_DIR"
    
    # Create update script
    cat > "$install_dir/update.sh" << 'EOF'
#!/bin/bash
# ApplerGUI Update Script

APP_DIR="$HOME/.local/share/applergui"
REPO_URL="https://github.com/ZProLegend007/ApplerGUI.git"

echo "🔄 Checking for ApplerGUI updates..."

cd "$APP_DIR" || exit 1

# Fetch latest changes
git fetch origin main

# Check if update available
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)

if [[ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]]; then
    echo "📦 Update available! Updating ApplerGUI..."
    
    # Backup current installation
    cp -r "$APP_DIR" "$APP_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Pull latest changes
    git pull origin main
    
    # Reinstall dependencies
    source venv/bin/activate
    pip install -r requirements.txt
    pip install -e .
    
    echo "✅ ApplerGUI updated successfully!"
else
    echo "✅ ApplerGUI is already up to date!"
fi
EOF
    
    chmod +x "$install_dir/update.sh"
    
    # Add update check to application startup
    cat > "$install_dir/check_updates.py" << 'EOF'
import subprocess
import sys
import os
from pathlib import Path

def check_for_updates():
    """Check for updates on application startup"""
    try:
        app_dir = Path.home() / ".local" / "share" / "applergui"
        os.chdir(app_dir)
        
        # Fetch latest commit info
        result = subprocess.run(
            ["git", "fetch", "origin", "main"],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            # Check if update available
            local = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True
            ).stdout.strip()
            
            remote = subprocess.run(
                ["git", "rev-parse", "origin/main"],
                capture_output=True, text=True
            ).stdout.strip()
            
            if local != remote:
                print("📦 Update available for ApplerGUI!")
                print("💡 Run 'applergui --update' to update")
                
    except Exception as e:
        # Silently handle update check failures
        pass

if __name__ == "__main__":
    check_for_updates()
EOF
}

# Create enhanced CLI command with update functionality
create_enhanced_cli_command() {
    local bin_dir="$HOME/.local/bin"
    mkdir -p "$bin_dir"
    
    cat > "$bin_dir/applergui" << EOF
#!/bin/bash
# ApplerGUI Command Line Interface

INSTALL_DIR="$HOME/.local/share/applergui"
VENV_DIR="\$INSTALL_DIR/venv"

case "\$1" in
    --update)
        echo "🔄 Updating ApplerGUI..."
        bash "\$INSTALL_DIR/update.sh"
        ;;
    --version)
        cd "\$INSTALL_DIR"
        git describe --tags --always 2>/dev/null || echo "unknown"
        ;;
    --help)
        echo "ApplerGUI - Apple TV & HomePod Control"
        echo "Usage:"
        echo "  applergui         Launch GUI application"
        echo "  applergui --update    Update to latest version"
        echo "  applergui --version   Show version information"
        echo "  applergui --help      Show this help"
        ;;
    *)
        # Launch GUI application
        cd "\$INSTALL_DIR"
        source "\$VENV_DIR/bin/activate"
        python3 check_updates.py
        python3 main.py
        ;;
esac
EOF
    
    chmod +x "$bin_dir/applergui"
    
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    fi
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root. It will ask for sudo when needed."
    exit 1
fi

# Run main function
main "$@"