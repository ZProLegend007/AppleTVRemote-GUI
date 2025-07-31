"""Main application window for AppleTVRemote-GUI."""

import sys
import logging
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QSplitter, QFrame, QTabWidget, QLabel, QPushButton, 
                             QProgressBar, QTableWidget, QGroupBox, QGridLayout, 
                             QSlider, QTableWidgetItem, QLineEdit, QStatusBar, 
                             QMenuBar, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot, QThreadPool
from PyQt6.QtGui import QFont, QAction, QKeySequence, QPixmap
import asyncio
import qasync

from ui.device_manager import DeviceManagerWidget
from ui.remote_control import RemoteControlWidget
from ui.now_playing import NowPlayingWidget
from ui.pairing_dialog import PairingDialogManager
from ui.settings import SettingsDialog
from ui.pin_dialog import PinDialog
from backend.config_manager import ConfigManager
from backend.device_controller import DeviceController
from backend.pairing_manager import PairingManager

class DiscoveryPanel(QFrame):
    """Integrated device discovery panel with current main window styling"""
    
    device_selected = pyqtSignal(dict)
    pairing_requested = pyqtSignal(dict)
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.discovered_devices = []
        self.selected_device = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup discovery panel with consistent main window styling"""
        # Use existing main window frame styling
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header - match existing style
        header = QLabel("Device Discovery")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Status label
        self.status_label = QLabel("Ready to discover devices...")
        layout.addWidget(self.status_label)
        
        # Discover button - match existing button style
        self.discover_btn = QPushButton("Discover Apple TVs")
        self.discover_btn.clicked.connect(self._start_discovery)
        layout.addWidget(self.discover_btn)
        
        # Progress bar - match existing style
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Device list group
        devices_group = QGroupBox("Discovered Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        # Device table - match existing table styling
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(2)
        self.devices_table.setHorizontalHeaderLabels(["Device Name", "Model"])
        self.devices_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.devices_table.verticalHeader().setVisible(False)
        self.devices_table.setAlternatingRowColors(True)
        self.devices_table.itemSelectionChanged.connect(self._on_device_selected)
        devices_layout.addWidget(self.devices_table)
        
        # Pair button
        self.pair_btn = QPushButton("Pair Selected Device")
        self.pair_btn.setEnabled(False)
        self.pair_btn.clicked.connect(self._request_pairing)
        devices_layout.addWidget(self.pair_btn)
        
        layout.addWidget(devices_group)
        layout.addStretch()
    
    def _start_discovery(self):
        """Start device discovery"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Scanning for Apple TV devices...")
        self.discover_btn.setEnabled(False)
        
        # TODO: Implement actual discovery logic
        # For now, simulate discovery
        QTimer.singleShot(2000, self._simulate_discovery_complete)
    
    def _simulate_discovery_complete(self):
        """Simulate discovery completion"""
        # Add sample devices
        sample_devices = [
            {"name": "Living Room Apple TV", "model": "Apple TV 4K"},
            {"name": "Bedroom Apple TV", "model": "Apple TV HD"},
            {"name": "Kitchen HomePod", "model": "HomePod Mini"}
        ]
        
        self.discovered_devices = sample_devices
        self._populate_device_table()
        
        self.progress_bar.setVisible(False)
        self.discover_btn.setEnabled(True)
        self.status_label.setText(f"Found {len(sample_devices)} device(s)")
    
    def _populate_device_table(self):
        """Populate device table"""
        self.devices_table.setRowCount(len(self.discovered_devices))
        for row, device in enumerate(self.discovered_devices):
            name_item = QTableWidgetItem(device['name'])
            model_item = QTableWidgetItem(device['model'])
            self.devices_table.setItem(row, 0, name_item)
            self.devices_table.setItem(row, 1, model_item)
        
        self.devices_table.resizeColumnsToContents()
    
    def _on_device_selected(self):
        """Handle device selection"""
        selected_rows = self.devices_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_device = self.discovered_devices[row]
            self.pair_btn.setEnabled(True)
        else:
            self.selected_device = None
            self.pair_btn.setEnabled(False)
    
    def _request_pairing(self):
        """Request device pairing"""
        if self.selected_device:
            self.pairing_requested.emit(self.selected_device)

class RemotePanel(QFrame):
    """Apple TV remote control panel with consistent styling"""
    
    # Remote control signals
    menu_pressed = pyqtSignal()
    home_pressed = pyqtSignal()
    select_pressed = pyqtSignal()
    up_pressed = pyqtSignal()
    down_pressed = pyqtSignal()
    left_pressed = pyqtSignal()
    right_pressed = pyqtSignal()
    play_pause_pressed = pyqtSignal()
    volume_up_pressed = pyqtSignal()
    volume_down_pressed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_shortcuts()
    
    def _setup_ui(self):
        """Setup remote control UI with consistent styling"""
        # Use existing main window frame styling
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("Apple TV Remote")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Menu button
        self.menu_btn = QPushButton("MENU")
        self.menu_btn.setMinimumHeight(40)
        self.menu_btn.clicked.connect(self._on_menu_pressed)
        layout.addWidget(self.menu_btn)
        
        # Directional pad
        dpad_frame = QFrame()
        dpad_layout = QGridLayout(dpad_frame)
        dpad_layout.setSpacing(5)
        
        # Create directional buttons with consistent styling
        self.up_btn = QPushButton("↑")
        self.up_btn.setFixedSize(50, 50)
        self.up_btn.clicked.connect(self._on_up_pressed)
        dpad_layout.addWidget(self.up_btn, 0, 1)
        
        self.left_btn = QPushButton("←")
        self.left_btn.setFixedSize(50, 50)
        self.left_btn.clicked.connect(self._on_left_pressed)
        dpad_layout.addWidget(self.left_btn, 1, 0)
        
        self.select_btn = QPushButton("SELECT")
        self.select_btn.setFixedSize(70, 70)
        self.select_btn.clicked.connect(self._on_select_pressed)
        dpad_layout.addWidget(self.select_btn, 1, 1)
        
        self.right_btn = QPushButton("→")
        self.right_btn.setFixedSize(50, 50)
        self.right_btn.clicked.connect(self._on_right_pressed)
        dpad_layout.addWidget(self.right_btn, 1, 2)
        
        self.down_btn = QPushButton("↓")
        self.down_btn.setFixedSize(50, 50)
        self.down_btn.clicked.connect(self._on_down_pressed)
        dpad_layout.addWidget(self.down_btn, 2, 1)
        
        layout.addWidget(dpad_frame)
        
        # Media controls
        media_frame = QFrame()
        media_layout = QHBoxLayout(media_frame)
        media_layout.setSpacing(10)
        
        self.play_pause_btn = QPushButton("⏯")
        self.play_pause_btn.setFixedSize(45, 45)
        self.play_pause_btn.clicked.connect(self._on_play_pause_pressed)
        media_layout.addWidget(self.play_pause_btn)
        
        self.volume_up_btn = QPushButton("🔊")
        self.volume_up_btn.setFixedSize(45, 45)
        self.volume_up_btn.clicked.connect(self._on_volume_up_pressed)
        media_layout.addWidget(self.volume_up_btn)
        
        self.volume_down_btn = QPushButton("🔇")
        self.volume_down_btn.setFixedSize(45, 45)
        self.volume_down_btn.clicked.connect(self._on_volume_down_pressed)
        media_layout.addWidget(self.volume_down_btn)
        
        layout.addWidget(media_frame)
        
        # Home button
        self.home_btn = QPushButton("HOME")
        self.home_btn.setMinimumHeight(40)
        self.home_btn.clicked.connect(self._on_home_pressed)
        layout.addWidget(self.home_btn)
        
        layout.addStretch()
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        from PyQt6.QtGui import QShortcut, QKeySequence
        
        # Arrow keys for navigation
        QShortcut(QKeySequence(Qt.Key.Key_Up), self, self._on_up_pressed)
        QShortcut(QKeySequence(Qt.Key.Key_Down), self, self._on_down_pressed)
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self._on_left_pressed)
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self._on_right_pressed)
        
        # Enter/Return for select
        QShortcut(QKeySequence(Qt.Key.Key_Return), self, self._on_select_pressed)
        QShortcut(QKeySequence(Qt.Key.Key_Enter), self, self._on_select_pressed)
        
        # Space for play/pause
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self._on_play_pause_pressed)
        
        # M for menu, H for home
        QShortcut(QKeySequence(Qt.Key.Key_M), self, self._on_menu_pressed)
        QShortcut(QKeySequence(Qt.Key.Key_H), self, self._on_home_pressed)
        
        # Plus/Minus for volume
        QShortcut(QKeySequence(Qt.Key.Key_Plus), self, self._on_volume_up_pressed)
        QShortcut(QKeySequence(Qt.Key.Key_Minus), self, self._on_volume_down_pressed)
    
    def _on_menu_pressed(self):
        """Handle menu button press"""
        self._animate_button_press(self.menu_btn)
        self.menu_pressed.emit()
    
    def _on_home_pressed(self):
        """Handle home button press"""
        self._animate_button_press(self.home_btn)
        self.home_pressed.emit()
    
    def _on_select_pressed(self):
        """Handle select button press"""
        self._animate_button_press(self.select_btn)
        self.select_pressed.emit()
    
    def _on_up_pressed(self):
        """Handle up button press"""
        self._animate_button_press(self.up_btn)
        self.up_pressed.emit()
    
    def _on_down_pressed(self):
        """Handle down button press"""
        self._animate_button_press(self.down_btn)
        self.down_pressed.emit()
    
    def _on_left_pressed(self):
        """Handle left button press"""
        self._animate_button_press(self.left_btn)
        self.left_pressed.emit()
    
    def _on_right_pressed(self):
        """Handle right button press"""
        self._animate_button_press(self.right_btn)
        self.right_pressed.emit()
    
    def _on_play_pause_pressed(self):
        """Handle play/pause button press"""
        self._animate_button_press(self.play_pause_btn)
        self.play_pause_pressed.emit()
    
    def _on_volume_up_pressed(self):
        """Handle volume up button press"""
        self._animate_button_press(self.volume_up_btn)
        self.volume_up_pressed.emit()
    
    def _on_volume_down_pressed(self):
        """Handle volume down button press"""
        self._animate_button_press(self.volume_down_btn)
        self.volume_down_pressed.emit()
    
    def _animate_button_press(self, button):
        """Animate button press for visual feedback"""
        # Simple style-based animation
        original_style = button.styleSheet()
        button.setStyleSheet("QPushButton { background-color: #0078d4; }")
        QTimer.singleShot(100, lambda: button.setStyleSheet(original_style))

class NowPlayingPanel(QFrame):
    """Now playing information panel with consistent styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_track = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup now playing panel with consistent styling"""
        # Use existing main window frame styling
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("Now Playing")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Album artwork placeholder
        artwork_frame = QFrame()
        artwork_frame.setFrameStyle(QFrame.Shape.Box)
        artwork_frame.setFixedSize(180, 180)
        artwork_layout = QVBoxLayout(artwork_frame)
        
        artwork_label = QLabel("🎵")
        artwork_label.setFont(QFont("Arial", 36))
        artwork_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        artwork_layout.addWidget(artwork_label)
        
        layout.addWidget(artwork_frame, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Track information
        track_info_group = QGroupBox("Track Information")
        track_info_layout = QVBoxLayout(track_info_group)
        
        self.title_label = QLabel("No track playing")
        self.title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        track_info_layout.addWidget(self.title_label)
        
        self.artist_label = QLabel("")
        self.artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artist_label.setWordWrap(True)
        track_info_layout.addWidget(self.artist_label)
        
        self.album_label = QLabel("")
        self.album_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.album_label.setWordWrap(True)
        track_info_layout.addWidget(self.album_label)
        
        layout.addWidget(track_info_group)
        
        # Progress section
        progress_group = QGroupBox("Playback Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        # Time labels
        time_frame = QFrame()
        time_layout = QHBoxLayout(time_frame)
        time_layout.setContentsMargins(0, 0, 0, 0)
        
        self.current_time_label = QLabel("0:00")
        time_layout.addWidget(self.current_time_label)
        
        time_layout.addStretch()
        
        self.total_time_label = QLabel("0:00")
        time_layout.addWidget(self.total_time_label)
        
        progress_layout.addWidget(time_frame)
        layout.addWidget(progress_group)
        
        # Volume control
        volume_group = QGroupBox("Volume Control")
        volume_layout = QVBoxLayout(volume_group)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        volume_layout.addWidget(self.volume_slider)
        
        volume_value_frame = QFrame()
        volume_value_layout = QHBoxLayout(volume_value_frame)
        volume_value_layout.setContentsMargins(0, 0, 0, 0)
        
        volume_value_layout.addWidget(QLabel("🔇"))
        volume_value_layout.addStretch()
        self.volume_value_label = QLabel("50%")
        volume_value_layout.addWidget(self.volume_value_label)
        volume_value_layout.addStretch()
        volume_value_layout.addWidget(QLabel("🔊"))
        
        volume_layout.addWidget(volume_value_frame)
        layout.addWidget(volume_group)
        
        # Connect volume slider
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        
        layout.addStretch()
    
    def _on_volume_changed(self, value):
        """Handle volume slider change"""
        self.volume_value_label.setText(f"{value}%")
    
    def update_track_info(self, title="", artist="", album=""):
        """Update track information"""
        self.title_label.setText(title if title else "No track playing")
        self.artist_label.setText(artist)
        self.album_label.setText(album)

class MainWindow(QMainWindow):
    """Main window with responsive layout maintaining current aesthetic"""
    
    def __init__(self, config_manager: ConfigManager, 
                 device_controller: DeviceController,
                 pairing_manager: PairingManager):
        super().__init__()
        
        self.config_manager = config_manager
        self.device_controller = device_controller
        self.pairing_manager = pairing_manager
        
        # Enable multithreading
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(4)  # Allow multiple background tasks
        
        self.pairing_dialog_manager = PairingDialogManager(self.pairing_manager, self)
        
        # Responsive settings - more conservative breakpoint
        self.is_compact_mode = False
        self.min_width_for_sections = 800  # More reasonable breakpoint
        
        self._setup_ui()
        self._setup_connections()
        self._apply_theme()
        self._setup_smooth_transitions()
        self._setup_responsive_behavior()
        
        # Update timer for UI refresh
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(5000)  # Update every 5 seconds
    
    def _setup_ui(self):
        """Setup main window UI maintaining current aesthetic"""
        self.setWindowTitle("Apple TV Remote")
        self.setMinimumSize(600, 500)  # Reasonable minimum size
        self.resize(1000, 700)  # Good default size for three sections
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout container
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Tab widget (hidden initially) - use existing styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setVisible(False)
        self.main_layout.addWidget(self.tab_widget)
        
        # Three-section splitter (visible initially)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # Create panels with consistent styling
        self.discovery_panel = DiscoveryPanel(self.config_manager)
        self.remote_panel = RemotePanel()
        self.now_playing_panel = NowPlayingPanel()
        
        # Add panels to splitter with reasonable proportions
        self.splitter.addWidget(self.discovery_panel)
        self.splitter.addWidget(self.remote_panel)
        self.splitter.addWidget(self.now_playing_panel)
        
        # Set reasonable sizes that work at default window size
        self.splitter.setSizes([300, 300, 300])  # Equal distribution
        
        # Add panels to tab widget for mobile view
        self.tab_widget.addTab(self.discovery_panel, "Discovery")
        self.tab_widget.addTab(self.remote_panel, "Remote")
        self.tab_widget.addTab(self.now_playing_panel, "Now Playing")
        
        # Connect signals
        if self.discovery_panel:
            self.discovery_panel.pairing_requested.connect(self._handle_pairing_request)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create status bar
        self._create_status_bar()
    
    def _setup_responsive_behavior(self):
        """Setup responsive window behavior"""
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._update_layout_mode)
    
    def resizeEvent(self, event):
        """Handle window resize for responsive layout"""
        super().resizeEvent(event)
        self.resize_timer.start(100)  # Debounce resize events
    
    def _update_layout_mode(self):
        """Update layout based on window size"""
        current_width = self.width()
        should_be_compact = current_width < self.min_width_for_sections
        
        if should_be_compact != self.is_compact_mode:
            self.is_compact_mode = should_be_compact
            self._switch_layout_mode()
    
    def _switch_layout_mode(self):
        """Switch between compact and expanded layout modes"""
        if self.is_compact_mode:
            # Switch to compact mode (tabs) for phone-like sizes
            self.splitter.setVisible(False)
            self.tab_widget.setVisible(True)
            self._move_panels_to_tabs()
        else:
            # Switch to expanded mode (three sections) for normal sizes
            self.tab_widget.setVisible(False)
            self.splitter.setVisible(True)
            self._move_panels_to_splitter()
    
    def _move_panels_to_tabs(self):
        """Move panels from splitter to tab widget"""
        # Clear existing tabs
        self.tab_widget.clear()
        
        # Re-add panels to tabs
        self.tab_widget.addTab(self.discovery_panel, "Discovery")
        self.tab_widget.addTab(self.remote_panel, "Remote") 
        self.tab_widget.addTab(self.now_playing_panel, "Now Playing")
    
    def _move_panels_to_splitter(self):
        """Move panels from tab widget to splitter"""
        # Clear tabs
        self.tab_widget.clear()
        
        # Re-add to splitter
        self.splitter.addWidget(self.discovery_panel)
        self.splitter.addWidget(self.remote_panel)
        self.splitter.addWidget(self.now_playing_panel)
        
        # Restore reasonable sizes
        self.splitter.setSizes([300, 300, 300])
    
    def _handle_pairing_request(self, device_info):
        """Handle device pairing request"""
        # Create simple PIN dialog that matches current aesthetic
        dialog = PinDialog(device_info, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            pin = dialog.get_pin()
            self._handle_pin_entry(device_info, pin)
    
    def _handle_pin_entry(self, device_info, pin):
        """Handle PIN entry for device pairing"""
        logging.info(f"PIN entered for {device_info['name']}: {pin}")
        # TODO: Integrate with actual pairing logic

    def _setup_smooth_transitions(self):
        """Enable smooth toolbar transitions."""
        self.setAnimated(True)
        
        # Process events regularly to prevent lag
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(lambda: QApplication.processEvents())
        self.ui_timer.start(16)  # ~60 FPS refresh rate
    
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
        # Try to connect to the newly paired device using QTimer to schedule it
        QTimer.singleShot(0, lambda: asyncio.create_task(self.device_controller.connect_device(device_id)))
    
    @pyqtSlot(str)
    def _on_pairing_started(self, device_id: str):
        """Handle pairing started signal."""
        self.status_bar.showMessage(f"Starting pairing with device {device_id}...", 3000)
    
    @pyqtSlot(str, str)
    def _on_pairing_failed(self, device_id: str, error: str):
        """Handle pairing failure."""
        QMessageBox.warning(self, "Pairing Failed", 
                          f"Failed to pair with device: {error}")
    
    @qasync.asyncSlot()
    async def _discover_devices(self):
        """Start device discovery."""
        try:
            timeout = self.config_manager.get('discovery_timeout', 10)
            await self.device_controller.discover_devices(timeout)
        except Exception as e:
            print(f"Device discovery failed: {e}")
            QMessageBox.warning(self, "Discovery Failed", f"Device discovery failed: {e}")
    
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
        
        # Schedule disconnection of all devices
        connected_devices = list(self.device_controller._connected_devices.keys())
        if connected_devices:
            # Create a coroutine to disconnect all devices
            async def disconnect_all():
                for device_id in connected_devices:
                    await self.device_controller.disconnect_device(device_id)
            
            # Use QTimer to run the disconnection after the event loop continues
            QTimer.singleShot(0, lambda: asyncio.create_task(disconnect_all()))
        
        event.accept()