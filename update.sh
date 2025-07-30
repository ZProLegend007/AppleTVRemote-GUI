#!/bin/bash
# ApplerGUI Update Script with matching terminal design

# Import color definitions and functions
source "$(dirname "$0")/installer_functions.sh" 2>/dev/null || {
    # Fallback color definitions
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    PURPLE='\033[0;35m'
    GRAY='\033[90m'
    BOLD='\033[1m'
    NC='\033[0m'
    
    print_info() { echo -e "${BLUE}→${NC} $1"; }
    print_success() { echo -e "${GREEN}✓${NC} $1"; }
    print_error() { echo -e "${RED}✗${NC} $1"; }
    print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
}

show_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Enhanced spinner with complete output isolation and logging
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

main() {
    clear
    
    # Show update header
    echo -e "${GREEN}"
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║   🔄 ApplerGUI Update Manager                                              ║
║                                                                            ║
║   Keeping your Apple TV & HomePod Control up to date                      ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
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
    
    print_info "→ 🔍 Fetching latest version information..."
    
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
    print_info "→ 💾 Creating backup..."
    BACKUP_DIR="$APP_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    
    {
        cp -r "$APP_DIR" "$BACKUP_DIR" >>"$UPDATE_LOG" 2>&1
    } &
    local backup_pid=$!
    
    show_spinner_isolated $backup_pid "Creating backup"
    
    # Pull latest changes
    print_info "→ 📥 Downloading updates..."
    
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
    print_info "→ 📦 Updating dependencies..."
    
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
        print_info "→ 🔧 Verifying Qt connections..."
        
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
        print_info "💡 Launch with: applergui"
        print_info "📊 Update log: $UPDATE_LOG"
        
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

main "$@"