#!/bin/bash

# AppleTVRemote-GUI Automated Installer
# This script installs the AppleTVRemote-GUI application with all dependencies

set -e  # Exit on any error

# Color output for better UX
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Functions for colored output
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_header() { echo -e "${CYAN}${BOLD}$1${NC}"; }

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

# Detect OS and package manager
detect_os() {
    print_info "Detecting operating system..."
    
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_warning "This application is designed for Linux. Some features may not work properly."
    fi
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DETECTED_OS=$ID
    else
        print_error "Cannot detect OS. Please install dependencies manually."
        exit 1
    fi
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        PACKAGE_MANAGER="apt"
        print_success "Detected Debian/Ubuntu system with APT"
    elif command -v dnf &> /dev/null; then
        PACKAGE_MANAGER="dnf"
        print_success "Detected Fedora/RHEL system with DNF"
    elif command -v yum &> /dev/null; then
        PACKAGE_MANAGER="yum"
        print_success "Detected CentOS/RHEL system with YUM"
    elif command -v pacman &> /dev/null; then
        PACKAGE_MANAGER="pacman"
        print_success "Detected Arch Linux system with Pacman"
    elif command -v zypper &> /dev/null; then
        PACKAGE_MANAGER="zypper"
        print_success "Detected openSUSE system with Zypper"
    else
        print_error "Unsupported package manager. Please install dependencies manually."
        exit 1
    fi
}

# Check Python version
check_python() {
    print_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    required_version="3.8"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        print_error "Python 3.8+ is required. Found Python $python_version"
        exit 1
    fi
    
    print_success "Python $python_version found"
}

# Interactive prompts for optional features
ask_user_preferences() {
    print_header "\n🔧 Installation Options"
    echo "Please choose your installation preferences:"
    echo
    
    # System-wide vs user installation
    while true; do
        read -p "$(echo -e "${YELLOW}Install system-wide for all users? [y/N]:${NC} ")" yn
        case $yn in
            [Yy]* ) USER_INSTALL=false; break;;
            [Nn]* | "" ) USER_INSTALL=true; break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
    
    # Desktop entry
    while true; do
        read -p "$(echo -e "${YELLOW}Create desktop entry (system menu)? [Y/n]:${NC} ")" yn
        case $yn in
            [Yy]* | "" ) CREATE_DESKTOP_ENTRY=true; break;;
            [Nn]* ) CREATE_DESKTOP_ENTRY=false; break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
    
    # Command-line alias
    while true; do
        read -p "$(echo -e "${YELLOW}Create command-line alias 'atvremote'? [Y/n]:${NC} ")" yn
        case $yn in
            [Yy]* | "" ) CREATE_CLI_ALIAS=true; break;;
            [Nn]* ) CREATE_CLI_ALIAS=false; break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
    
    # Development dependencies
    while true; do
        read -p "$(echo -e "${YELLOW}Install development dependencies? [y/N]:${NC} ")" yn
        case $yn in
            [Yy]* ) INSTALL_DEV_DEPS=true; break;;
            [Nn]* | "" ) INSTALL_DEV_DEPS=false; break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
    
    # Auto-start service
    while true; do
        read -p "$(echo -e "${YELLOW}Auto-start on system boot? [y/N]:${NC} ")" yn
        case $yn in
            [Yy]* ) AUTO_START=true; break;;
            [Nn]* | "" ) AUTO_START=false; break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
    
    # Audio codecs
    while true; do
        read -p "$(echo -e "${YELLOW}Install optional audio codecs? [y/N]:${NC} ")" yn
        case $yn in
            [Yy]* ) INSTALL_AUDIO_CODECS=true; break;;
            [Nn]* | "" ) INSTALL_AUDIO_CODECS=false; break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
    
    # Configuration directory
    while true; do
        read -p "$(echo -e "${YELLOW}Create configuration directory? [Y/n]:${NC} ")" yn
        case $yn in
            [Yy]* | "" ) CREATE_CONFIG_DIR=true; break;;
            [Nn]* ) CREATE_CONFIG_DIR=false; break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
    
    # Sample themes
    while true; do
        read -p "$(echo -e "${YELLOW}Download sample themes? [y/N]:${NC} ")" yn
        case $yn in
            [Yy]* ) DOWNLOAD_THEMES=true; break;;
            [Nn]* | "" ) DOWNLOAD_THEMES=false; break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
    
    echo
    print_info "Installation preferences saved."
}

# Install system dependencies
install_system_deps() {
    print_header "\n📦 Installing System Dependencies"
    
    case $PACKAGE_MANAGER in
        "apt")
            print_info "Updating package lists..."
            sudo apt-get update -qq
            
            print_info "Installing base dependencies..."
            sudo apt-get install -y python3-pip python3-venv python3-dev git curl
            
            print_info "Installing PyQt6 and multimedia dependencies..."
            sudo apt-get install -y python3-pyqt6 python3-pyqt6.qtmultimedia || {
                print_warning "PyQt6 system packages not available, will install via pip"
            }
            
            if [ "$INSTALL_AUDIO_CODECS" = true ]; then
                print_info "Installing additional audio codecs..."
                sudo apt-get install -y gstreamer1.0-plugins-good \
                    gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
                    gstreamer1.0-libav
            fi
            ;;
        "dnf")
            print_info "Installing base dependencies..."
            sudo dnf install -y python3-pip python3-devel git curl
            
            print_info "Installing PyQt6 dependencies..."
            sudo dnf install -y python3-PyQt6 python3-PyQt6-devel
            
            if [ "$INSTALL_AUDIO_CODECS" = true ]; then
                print_info "Installing additional audio codecs..."
                sudo dnf install -y gstreamer1-plugins-good \
                    gstreamer1-plugins-bad-free gstreamer1-plugins-ugly-free
            fi
            ;;
        "yum")
            print_info "Installing base dependencies..."
            sudo yum install -y python3-pip python3-devel git curl
            
            print_info "Installing PyQt6 dependencies..."
            sudo yum install -y python36-PyQt6 || sudo yum install -y python3-PyQt6
            
            if [ "$INSTALL_AUDIO_CODECS" = true ]; then
                print_info "Installing additional audio codecs..."
                sudo yum install -y gstreamer1-plugins-good \
                    gstreamer1-plugins-bad-free gstreamer1-plugins-ugly-free
            fi
            ;;
        "pacman")
            print_info "Updating package database..."
            sudo pacman -Sy
            
            print_info "Installing base dependencies..."
            sudo pacman -S --noconfirm python-pip python-virtualenv git curl
            
            print_info "Installing PyQt6 dependencies..."
            sudo pacman -S --noconfirm python-pyqt6 python-pyqt6-multimedia
            
            if [ "$INSTALL_AUDIO_CODECS" = true ]; then
                print_info "Installing additional audio codecs..."
                sudo pacman -S --noconfirm gst-plugins-good gst-plugins-bad gst-plugins-ugly
            fi
            ;;
        "zypper")
            print_info "Installing base dependencies..."
            sudo zypper install -y python3-pip python3-devel git curl
            
            print_info "Installing PyQt6 dependencies..."
            sudo zypper install -y python3-qt6 python3-qt6-devel
            
            if [ "$INSTALL_AUDIO_CODECS" = true ]; then
                print_info "Installing additional audio codecs..."
                sudo zypper install -y gstreamer-plugins-good \
                    gstreamer-plugins-bad gstreamer-plugins-ugly
            fi
            ;;
    esac
    
    print_success "System dependencies installed successfully"
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

# Main installation flow
main() {
    trap cleanup_on_error ERR
    
    print_header "🍎 AppleTVRemote-GUI Automated Installer"
    echo -e "${CYAN}===============================================${NC}"
    echo
    print_info "This installer will set up AppleTVRemote-GUI on your system"
    echo
    
    detect_os
    check_python
    ask_user_preferences
    
    print_header "\n🚀 Starting Installation Process"
    
    install_system_deps
    clone_repository
    setup_virtual_environment
    install_python_deps
    setup_application
    create_desktop_entry
    create_cli_alias
    create_config_directory
    setup_auto_start
    download_sample_themes
    
    if run_tests; then
        print_header "\n🎉 Installation Completed Successfully!"
    else
        print_header "\n⚠️ Installation Completed with Warnings"
    fi
    
    echo
    print_info "Installation Summary:"
    echo "  📍 Install Location: $INSTALL_DIR"
    echo "  🐍 Virtual Environment: $VENV_DIR"
    if [ "$CREATE_DESKTOP_ENTRY" = true ]; then
        echo "  🖥️ Desktop Entry: $DESKTOP_ENTRY_PATH"
    fi
    if [ "$CREATE_CLI_ALIAS" = true ]; then
        echo "  💻 Command: atvremote"
    fi
    echo
    
    print_header "🎯 Next Steps:"
    echo "1. Run the application:"
    if [ "$CREATE_CLI_ALIAS" = true ]; then
        echo "   atvremote"
    else
        echo "   $VENV_DIR/bin/python $INSTALL_DIR/main.py"
    fi
    echo
    echo "2. Or launch from your application menu (if desktop entry was created)"
    echo
    echo "3. For troubleshooting, check the README.md file"
    echo
    
    # Offer to launch the application
    echo
    while true; do
        read -p "$(echo -e "${YELLOW}Would you like to launch the application now? [Y/n]:${NC} ")" yn
        case $yn in
            [Yy]* | "" )
                print_info "Launching AppleTVRemote-GUI..."
                cd "$INSTALL_DIR"
                source "$VENV_DIR/bin/activate"
                python3 main.py &
                print_success "Application launched successfully!"
                break;;
            [Nn]* ) 
                print_info "You can launch the application later using the instructions above."
                break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
    
    echo
    print_success "Thank you for installing AppleTVRemote-GUI! 🎉"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root. It will ask for sudo when needed."
    exit 1
fi

# Run main function
main "$@"