"""Main application window for AppleTVRemote-GUI."""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTabWidget, QStatusBar, QMenuBar, QMessageBox,
                            QLabel, QPushButton, QSplitter)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QAction, QKeySequence, QPixmap
import asyncio

from ui.device_manager import DeviceManagerWidget
from ui.remote_control import RemoteControlWidget
from ui.now_playing import NowPlayingWidget
from ui.pairing_dialog import PairingDialogManager
from ui.settings import SettingsDialog
from backend.config_manager import ConfigManager
from backend.device_controller import DeviceController
from backend.pairing_manager import PairingManager

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, config_manager: ConfigManager, 
                 device_controller: DeviceController,
                 pairing_manager: PairingManager):
        super().__init__()
        
        self.config_manager = config_manager
        self.device_controller = device_controller
        self.pairing_manager = pairing_manager
        
        self.pairing_dialog_manager = PairingDialogManager(self.pairing_manager, self)
        
        self._setup_ui()
        self._setup_connections()
        self._apply_theme()
        
        # Update timer for UI refresh
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(5000)  # Update every 5 seconds
    
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Apple TV Remote")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create splitter for resizable layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Device Manager
        self.device_manager = DeviceManagerWidget(
            self.config_manager, 
            self.device_controller,
            self.pairing_manager
        )
        splitter.addWidget(self.device_manager)
        
        # Right panel - Control tabs
        self.tab_widget = QTabWidget()
        splitter.addWidget(self.tab_widget)
        
        # Remote Control tab
        self.remote_control = RemoteControlWidget(self.device_controller)
        self.tab_widget.addTab(self.remote_control, "Remote Control")
        
        # Now Playing tab
        self.now_playing = NowPlayingWidget(self.device_controller)
        self.tab_widget.addTab(self.now_playing, "Now Playing")
        
        # Set splitter proportions (30% device manager, 70% control tabs)
        splitter.setSizes([300, 700])
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Discover devices action
        discover_action = QAction("&Discover Devices", self)
        discover_action.setShortcut(QKeySequence("Ctrl+D"))
        discover_action.setStatusTip("Scan for Apple TV and HomePod devices")
        discover_action.triggered.connect(self._discover_devices)
        file_menu.addAction(discover_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("&Settings")
        
        # Preferences action
        preferences_action = QAction("&Preferences", self)
        preferences_action.setShortcut(QKeySequence("Ctrl+,"))
        preferences_action.setStatusTip("Open application preferences")
        preferences_action.triggered.connect(self._show_preferences)
        settings_menu.addAction(preferences_action)
        
        # Theme submenu
        theme_menu = settings_menu.addMenu("&Theme")
        
        dark_theme_action = QAction("&Dark", self)
        dark_theme_action.setCheckable(True)
        dark_theme_action.triggered.connect(lambda: self._set_theme('dark'))
        theme_menu.addAction(dark_theme_action)
        
        light_theme_action = QAction("&Light", self)
        light_theme_action.setCheckable(True)
        light_theme_action.triggered.connect(lambda: self._set_theme('light'))
        theme_menu.addAction(light_theme_action)
        
        # Set current theme
        current_theme = self.config_manager.get('theme', 'dark')
        if current_theme == 'dark':
            dark_theme_action.setChecked(True)
        else:
            light_theme_action.setChecked(True)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About AppleTVRemote-GUI")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Connection status label
        self.connection_status = QLabel("Not connected")
        self.status_bar.addWidget(self.connection_status)
        
        # Device count label
        self.device_count_label = QLabel("0 devices")
        self.status_bar.addPermanentWidget(self.device_count_label)
    
    def _setup_connections(self):
        """Set up signal connections."""
        # Device controller signals
        self.device_controller.device_connected.connect(self._on_device_connected)
        self.device_controller.device_disconnected.connect(self._on_device_disconnected)
        self.device_controller.devices_discovered.connect(self._on_devices_discovered)
        self.device_controller.connection_failed.connect(self._on_connection_failed)
        
        # Pairing manager signals
        self.pairing_manager.pairing_started.connect(self._on_pairing_started)
        self.pairing_manager.pairing_completed.connect(self._on_pairing_completed)
        self.pairing_manager.pairing_failed.connect(self._on_pairing_failed)
    
    def _apply_theme(self):
        """Apply the current theme."""
        theme = self.config_manager.get('theme', 'dark')
        
        if theme == 'dark':
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
    
    def _apply_dark_theme(self):
        """Apply dark theme."""
        dark_style = '''
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #3c3c3c;
        }
        QTabBar::tab {
            background-color: #404040;
            color: #ffffff;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #505050;
        }
        QPushButton {
            background-color: #404040;
            border: 1px solid #555555;
            padding: 8px 16px;
            border-radius: 4px;
            color: #ffffff;
        }
        QPushButton:hover {
            background-color: #505050;
        }
        QPushButton:pressed {
            background-color: #303030;
        }
        QPushButton:disabled {
            background-color: #2a2a2a;
            color: #666666;
        }
        QStatusBar {
            background-color: #404040;
            border-top: 1px solid #555555;
        }
        QMenuBar {
            background-color: #404040;
            color: #ffffff;
        }
        QMenuBar::item:selected {
            background-color: #505050;
        }
        QMenu {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #555555;
        }
        QMenu::item:selected {
            background-color: #505050;
        }
        '''
        self.setStyleSheet(dark_style)
    
    def _apply_light_theme(self):
        """Apply light theme."""
        # Use default system theme for light mode
        self.setStyleSheet("")
    
    @pyqtSlot(str, dict)
    def _on_device_connected(self, device_id: str, device_info: dict):
        """Handle device connection."""
        device_name = device_info.get('name', device_id)
        self.connection_status.setText(f"Connected to {device_name}")
        self.status_bar.showMessage(f"Connected to {device_name}", 3000)
    
    @pyqtSlot(str)
    def _on_device_disconnected(self, device_id: str):
        """Handle device disconnection."""
        self.connection_status.setText("Not connected")
        self.status_bar.showMessage("Device disconnected", 3000)
    
    @pyqtSlot(list)
    def _on_devices_discovered(self, devices: list):
        """Handle device discovery completion."""
        count = len(devices)
        self.device_count_label.setText(f"{count} device{'s' if count != 1 else ''}")
        self.status_bar.showMessage(f"Found {count} device{'s' if count != 1 else ''}", 3000)
    
    @pyqtSlot(str, str)
    def _on_connection_failed(self, device_id: str, error: str):
        """Handle connection failure."""
        QMessageBox.warning(self, "Connection Failed", 
                          f"Failed to connect to device: {error}")
    
    @pyqtSlot(str, dict)
    def _on_pairing_completed(self, device_id: str, credentials: dict):
        """Handle successful pairing."""
        self.status_bar.showMessage("Pairing completed successfully", 3000)
        # Try to connect to the newly paired device
        asyncio.create_task(self.device_controller.connect_device(device_id))
    
    @pyqtSlot(str)
    def _on_pairing_started(self, device_id: str):
        """Handle pairing started signal."""
        self.status_bar.showMessage(f"Starting pairing with device {device_id}...", 3000)
    
    @pyqtSlot(str, str)
    def _on_pairing_failed(self, device_id: str, error: str):
        """Handle pairing failure."""
        QMessageBox.warning(self, "Pairing Failed", 
                          f"Failed to pair with device: {error}")
    
    def _discover_devices(self):
        """Start device discovery."""
        timeout = self.config_manager.get('discovery_timeout', 10)
        asyncio.create_task(self.device_controller.discover_devices(timeout))
    
    def _show_preferences(self):
        """Show preferences dialog."""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            self._apply_theme()
    
    def _set_theme(self, theme: str):
        """Set the application theme."""
        self.config_manager.set('theme', theme)
        self._apply_theme()
    
    def _show_about(self):
        """Show about dialog."""
        about_text = '''
        <h2>AppleTVRemote-GUI</h2>
        <p>Version 1.0.0</p>
        <p>A modern Linux GUI application for controlling Apple TV and HomePod devices.</p>
        <p>Built with PyQt6 and pyatv library.</p>
        <p><b>Author:</b> Zac</p>
        <p><b>License:</b> MIT License</p>
        '''
        QMessageBox.about(self, "About AppleTVRemote-GUI", about_text)
    
    def _update_ui(self):
        """Periodic UI update."""
        # Update device count
        connected_devices = self.device_controller.get_connected_devices()
        if connected_devices:
            current_device = next(iter(connected_devices.values()))
            device_name = current_device.get('name', 'Unknown')
            self.connection_status.setText(f"Connected to {device_name}")
        else:
            self.connection_status.setText("Not connected")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save window geometry
        geometry = self.saveGeometry()
        self.config_manager.set('window_geometry', geometry.data().hex())
        
        # Disconnect all devices
        connected_devices = list(self.device_controller._connected_devices.keys())
        for device_id in connected_devices:
            asyncio.create_task(self.device_controller.disconnect_device(device_id))
        
        event.accept()