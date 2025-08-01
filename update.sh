#!/bin/bash
# ApplerGUI Professional Update Script - Matching installer design

set -e  # Exit on error, but handle gracefully

# Enhanced color palette for professional UI (matching install.sh)
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

# Functions for enhanced colored output (matching install.sh)
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

# Clean section display with proper clearing (matching install.sh)
show_section() {
    local title="$1"
    clear
    echo -e "${PURPLE}"
    cat << EOF
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║   🍎 ApplerGUI Professional Update Manager                                 ║
║                                                                            ║
║   Modern Linux GUI for Apple TV & HomePod Control                         ║
║                                                                            ║
║   ✨ Automated Update with Smart Dependency Management                     ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}\n"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE} $title${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Clear terminal and show fancy banner (matching install.sh)
clear_and_banner() {
    clear
    echo -e "${PURPLE}"
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║   🍎 ApplerGUI Professional Update Manager                                 ║
║                                                                            ║
║   Modern Linux GUI for Apple TV & HomePod Control                         ║
║                                                                            ║
║   ✨ Automated Update with Smart Dependency Management                     ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}\n"
    echo -e "${GRAY}Version 2.0 • Professional Update Experience${NC}"
    echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Enhanced spinner with complete output isolation and logging (matching install.sh style)
show_spinner_isolated() {
    local pid=$1
    local message="$2"
    local spin='⣾⣽⣻⢿⡿⣟⣯⣷'
    local i=0
    local start_time=$(date +%s)
    
    # Clear any existing line content
    printf "\r\033[K"
    
    # Show spinner while process runs
    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) %8 ))
        printf "\r\033[K${BLUE}${spin:$i:1}${NC} $message"
        sleep 0.15
    done
    
    # Clear spinner line completely
    printf "\r\033[K"
    
    # Wait for process and get exit code
    wait $pid  
    local exit_code=$?
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Show final result on clean line
    if [[ $exit_code -eq 0 ]]; then
        printf "${GREEN}✓${NC} $message ${GRAY}(${duration}s)${NC}\n"
    else
        printf "${RED}✗${NC} $message ${GRAY}(failed after ${duration}s)${NC}\n"
    fi
    
    return $exit_code
}

ask_yn() {
    local question="$1"
    local default="$2"
    local description="$3"
    
    while true; do
        if [[ "$default" == "y" ]]; then
            printf "${BLUE}$question${NC} [Y/n]: "
        else
            printf "${BLUE}$question${NC} [y/N]: "
        fi
        
        read -r response
        
        if [[ -z "$response" ]]; then
            response="$default"
        fi
        
        case "$response" in
            [Yy]|[Yy][Ee][Ss]) return 0 ;;
            [Nn]|[Nn][Oo]) return 1 ;;
            *) print_warning "Please answer yes or no." ;;
        esac
    done
}

# Self-update functionality
self_update() {
    clear_and_banner
    show_section "🔄 SELF-UPDATE"
    
    print_info "Updating the update script itself..."
    
    local script_url="https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/update.sh"
    local temp_script="/tmp/update_new.sh"
    
    # Download new script
    {
        curl -fsSL "$script_url" > "$temp_script"
    } &
    local download_pid=$!
    
    show_spinner_isolated $download_pid "Downloading latest update script"
    
    if [[ $? -eq 0 && -s "$temp_script" ]]; then
        # Replace current script
        chmod +x "$temp_script"
        mv "$temp_script" "$0"
        
        print_success "✅ Update script updated successfully!"
        print_info "🚀 Restart the update to use the new version"
        exit 0
    else
        print_error "✗ Failed to download update script"
        rm -f "$temp_script"
        exit 1
    fi
}

main() {
    # Check for self-update flag first
    if [[ "$1" == "--self-update" ]]; then
        self_update
        return
    fi
    
    clear_and_banner
    
    APP_DIR="$(cd "$(dirname "$0")" && pwd)"
    REPO_URL="https://github.com/ZProLegend007/ApplerGUI.git"
    LOG_DIR="$APP_DIR/logs"
    
    # Setup logging
    mkdir -p "$LOG_DIR"
    UPDATE_LOG="$LOG_DIR/update.log"
    
    # Initialize log
    echo "ApplerGUI Update Log - $(date)" > "$UPDATE_LOG"
    
    show_section "🔍 CHECKING FOR UPDATES"
    
    cd "$APP_DIR" || {
        print_error "✗ ApplerGUI installation directory not found"
        exit 1
    }
    
    # Check if we're in a git repository
    if [[ ! -d ".git" ]]; then
        print_error "✗ Not a git repository - cannot update"
        print_info "💡 Please reinstall ApplerGUI using the installer script"
        exit 1
    fi
    
    print_info "🔍 Fetching latest version information..."
    
    # Fetch with hidden output
    {
        git fetch origin main >>"$UPDATE_LOG" 2>&1
    } &
    local fetch_pid=$!
    
    show_spinner_isolated $fetch_pid "Checking for updates"
    
    if [[ $? -ne 0 ]]; then
        print_error "✗ Failed to check for updates"
        print_info "💡 Check your internet connection"
        exit 1
    fi
    
    # Check if update available
    LOCAL_COMMIT=$(git rev-parse HEAD 2>/dev/null)
    REMOTE_COMMIT=$(git rev-parse origin/main 2>/dev/null)
    
    if [[ "$LOCAL_COMMIT" == "$REMOTE_COMMIT" ]]; then
        print_success "✅ ApplerGUI is already up to date!"
        print_info "📦 Current version: $(git describe --tags --always 2>/dev/null || echo 'unknown')"
        print_info ""
        print_info "💡 To update the update script itself, run: ./update.sh --self-update"
        exit 0
    fi
    
    show_section "📦 UPDATE AVAILABLE"
    
    print_info "📦 Update available for ApplerGUI!"
    print_info "🔄 Current: $(git describe --tags --always 2>/dev/null || echo 'unknown')"
    print_info "🆕 Latest:  $(git describe --tags --always origin/main 2>/dev/null || echo 'latest')"
    
    if ! ask_yn "🚀 Update ApplerGUI now?" "y" "Download and install the latest version"; then
        print_info "Update cancelled by user"
        exit 0
    fi
    
    show_section "🔄 UPDATING APPLICATION"
    
    # Backup current installation
    print_info "💾 Creating backup..."
    BACKUP_DIR="$APP_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    
    {
        cp -r "$APP_DIR" "$BACKUP_DIR" >>"$UPDATE_LOG" 2>&1
    } &
    local backup_pid=$!
    
    show_spinner_isolated $backup_pid "Creating backup"
    
    # Pull latest changes
    print_info "📥 Downloading updates..."
    
    {
        git pull origin main >>"$UPDATE_LOG" 2>&1
    } &
    local pull_pid=$!
    
    show_spinner_isolated $pull_pid "Downloading updates"
    
    if [[ $? -ne 0 ]]; then
        print_error "✗ Failed to download updates"
        print_info "🔄 Restoring from backup..."
        
        rm -rf "$APP_DIR"
        mv "$BACKUP_DIR" "$APP_DIR"
        
        print_error "✗ Update failed, installation restored"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [[ ! -d "venv" ]]; then
        print_error "✗ Virtual environment not found"
        print_info "💡 Please reinstall ApplerGUI using the installer script"
        exit 1
    fi
    
    # Reinstall dependencies
    print_info "📦 Updating dependencies..."
    
    source venv/bin/activate || {
        print_error "✗ Failed to activate virtual environment"
        exit 1
    }
    
    {
        pip install --quiet --upgrade -r requirements.txt >>"$UPDATE_LOG" 2>&1
        pip install --quiet -e . >>"$UPDATE_LOG" 2>&1
    } &
    local deps_pid=$!
    
    show_spinner_isolated $deps_pid "Updating dependencies"
    
    if [[ $? -eq 0 ]]; then
        # Run Qt connection check
        print_info "🔧 Verifying Qt connections..."
        
        {
            python3 qt_connection_fix.py >>"$UPDATE_LOG" 2>&1
        } &
        local qt_pid=$!
        
        show_spinner_isolated $qt_pid "Checking Qt connections"
        
        # Remove backup on success
        rm -rf "$BACKUP_DIR"
        
        show_section "🎉 UPDATE COMPLETE"
        
        print_success "✅ ApplerGUI updated successfully!"
        print_info "📦 New version: $(git describe --tags --always 2>/dev/null || echo 'latest')"
        print_info "🚀 Launch with: applergui"
        print_info "📊 Update log: $UPDATE_LOG"
        print_info ""
        print_info "💡 To update this script: ./update.sh --self-update"
        
    else
        print_error "✗ Failed to update dependencies"
        print_info "🔄 Restoring from backup..."
        
        rm -rf "$APP_DIR"
        mv "$BACKUP_DIR" "$APP_DIR"
        
        print_error "✗ Update failed, installation restored"
        print_info "💡 Check update log: $UPDATE_LOG"
        exit 1
    fi
}
}

main "$@"