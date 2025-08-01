#!/bin/bash
# ApplerGUI Clean Launcher

INSTALL_DIR="$HOME/.local/share/applergui"
VENV_DIR="$INSTALL_DIR/venv"

# Function to launch with clean environment
launch_clean() {
    cd "$INSTALL_DIR" || {
        echo "✗ Error: Installation directory not found: $INSTALL_DIR"
        exit 1
    }
    
    # Set clean GTK environment
    export GTK_THEME="Adwaita"  
    export GDK_BACKEND=x11
    unset GTK_CSS_PATH
    unset GTK_THEME_PATH
    
    # Set clean Qt environment
    export QT_STYLE_OVERRIDE=""
    export QT_QPA_PLATFORMTHEME=""
    export QT_QPA_PLATFORM_PLUGIN_PATH=""
    export QT_LOGGING_RULES="*.debug=false"
    
    # Activate virtual environment
    if [[ -f "$VENV_DIR/bin/activate" ]]; then
        source "$VENV_DIR/bin/activate"
    else
        echo "✗ Error: Virtual environment not found"
        exit 1
    fi
    
    # Create logs directory
    mkdir -p "$INSTALL_DIR/logs"
    
    # Launch application with clean environment and error handling
    echo "🚀 Starting ApplerGUI..."
    
    # Try to launch the application
    python3 -c "
import sys
import os
sys.path.insert(0, '.')

try:
    from ui.main_window import MainWindow
    from backend.config_manager import ConfigManager
    from backend.device_controller import DeviceController  
    from backend.pairing_manager import PairingManager
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Setup backend components
    config_manager = ConfigManager()
    device_controller = DeviceController(config_manager)
    pairing_manager = PairingManager(config_manager)
    
    # Create main window
    window = MainWindow(config_manager, device_controller, pairing_manager)
    window.show()
    
    print('✓ ApplerGUI launched successfully')
    sys.exit(app.exec())
    
except Exception as e:
    print(f'✗ Failed to start ApplerGUI: {e}')
    print('💡 Run with --debug for detailed error information')
    sys.exit(1)
"
}

# Handle command line arguments
case "$1" in
    --update)
        echo "🔄 Updating ApplerGUI..."
        if [[ -f "$INSTALL_DIR/update.sh" ]]; then
            bash "$INSTALL_DIR/update.sh"
        else
            echo "✗ Update script not found, please reinstall"
            exit 1
        fi
        ;;
    --version)
        cd "$INSTALL_DIR"
        git describe --tags --always 2>/dev/null || echo "unknown"
        ;;
    --debug)
        # Debug launch function here
        echo "🐛 Debug mode not implemented yet"
        launch_clean
        ;;
    --help)
        echo "ApplerGUI - Apple TV & HomePod Control"
        echo "Usage:"
        echo "  applergui         Launch GUI application"
        echo "  applergui --update    Update to latest version"
        echo "  applergui --version   Show version information"
        echo "  applergui --debug     Launch with debug output"
        echo "  applergui --help      Show this help"
        ;;
    *)
        launch_clean
        ;;
esac