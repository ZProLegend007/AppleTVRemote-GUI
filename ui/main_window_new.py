"""Modern three-section responsive main window for ApplerGUI."""

import sys
import logging
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QSplitter, QFrame, QTabWidget, QStackedWidget,
                             QLabel, QPushButton, QProgressBar, QTableWidget,
                             QGroupBox, QGridLayout, QSlider, QApplication,
                             QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QPalette, QIcon

class DiscoveryPanel(QFrame):
    """Integrated device discovery panel."""
    
    device_selected = pyqtSignal(dict)  # Device info
    pairing_requested = pyqtSignal(dict)  # Device to pair
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.discovered_devices = []
        self.selected_device = None
        
        self._setup_ui()
        self._setup_discovery()
    
    def _setup_ui(self):
        """Setup discovery panel UI."""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8f9fa,
                    stop: 1 #e9ecef
                );
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 5px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: rgba(255, 255, 255, 0.9);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #495057;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel("🔍 Device Discovery")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #495057; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Discovery status
        self.status_label = QLabel("Ready to discover devices...")
        self.status_label.setStyleSheet("color: #6c757d; margin-bottom: 10px;")
        layout.addWidget(self.status_label)
        
        # Discover button
        self.discover_btn = QPushButton("🔄 Discover Devices")
        self.discover_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #28a745,
                    stop: 1 #1e7e34
                );
                border: none;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1e7e34,
                    stop: 1 #155724
                );
            }
            QPushButton:pressed {
                background: #155724;
            }
        """)
        self.discover_btn.clicked.connect(self._start_discovery)
        layout.addWidget(self.discover_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #28a745;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #28a745,
                    stop: 1 #20c997
                );
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Device list
        devices_group = QGroupBox("📱 Discovered Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(2)
        self.devices_table.setHorizontalHeaderLabels(["Device Name", "Model"])
        self.devices_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.devices_table.verticalHeader().setVisible(False)
        self.devices_table.setAlternatingRowColors(True)
        self.devices_table.horizontalHeader().setStretchLastSection(True)
        self.devices_table.itemSelectionChanged.connect(self._on_device_selected)
        devices_layout.addWidget(self.devices_table)
        
        # Pair button
        self.pair_btn = QPushButton("📱 Pair Selected Device")
        self.pair_btn.setEnabled(False)
        self.pair_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #007bff,
                    stop: 1 #0056b3
                );
                border: none;
                color: white;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0056b3,
                    stop: 1 #004085
                );
            }
            QPushButton:disabled {
                background: #6c757d;
            }
        """)
        self.pair_btn.clicked.connect(self._request_pairing)
        devices_layout.addWidget(self.pair_btn)
        
        layout.addWidget(devices_group)
        layout.addStretch()
    
    def _setup_discovery(self):
        """Setup discovery functionality."""
        # Timer for simulated discovery
        self.discovery_timer = QTimer()
        self.discovery_timer.timeout.connect(self._discovery_progress)
        self.discovery_progress_value = 0
        
        # Add some sample devices for demo
        self._add_sample_devices()
    
    def _add_sample_devices(self):
        """Add sample devices for demonstration."""
        sample_devices = [
            {"name": "Apple TV 4K", "model": "Apple TV", "id": "appletv_1"},
            {"name": "Living Room HomePod", "model": "HomePod", "id": "homepod_1"},
            {"name": "Kitchen Apple TV", "model": "Apple TV HD", "id": "appletv_2"},
        ]
        
        self.discovered_devices = sample_devices
        self._update_device_table()
    
    def _update_device_table(self):
        """Update the device table with discovered devices."""
        self.devices_table.setRowCount(len(self.discovered_devices))
        
        for row, device in enumerate(self.discovered_devices):
            name_item = QTableWidgetItem(device.get('name', 'Unknown'))
            model_item = QTableWidgetItem(device.get('model', 'Unknown'))
            
            self.devices_table.setItem(row, 0, name_item)
            self.devices_table.setItem(row, 1, model_item)
    
    def _start_discovery(self):
        """Start device discovery."""
        self.status_label.setText("Discovering devices...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.discover_btn.setEnabled(False)
        
        self.discovery_progress_value = 0
        self.discovery_timer.start(100)  # Update every 100ms
    
    def _discovery_progress(self):
        """Update discovery progress."""
        self.discovery_progress_value += 2
        self.progress_bar.setValue(self.discovery_progress_value)
        
        if self.discovery_progress_value >= 100:
            self.discovery_timer.stop()
            self._discovery_complete()
    
    def _discovery_complete(self):
        """Complete discovery process."""
        self.status_label.setText(f"Found {len(self.discovered_devices)} devices")
        self.progress_bar.setVisible(False)
        self.discover_btn.setEnabled(True)
    
    def _on_device_selected(self):
        """Handle device selection."""
        current_row = self.devices_table.currentRow()
        if current_row >= 0:
            self.selected_device = self.discovered_devices[current_row]
            self.pair_btn.setEnabled(True)
            self.device_selected.emit(self.selected_device)
        else:
            self.selected_device = None
            self.pair_btn.setEnabled(False)
    
    def _request_pairing(self):
        """Request pairing with selected device."""
        if self.selected_device:
            self.pairing_requested.emit(self.selected_device)


class RemotePanel(QFrame):
    """Apple TV remote control panel."""
    
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
        """Setup remote control UI to look like actual Apple TV remote."""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2c3e50,
                    stop: 1 #34495e
                );
                border: 1px solid #1a252f;
                border-radius: 12px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("📺 Apple TV Remote")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: white; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Menu button (top)
        self.menu_btn = self._create_remote_button("MENU", "#e74c3c")
        self.menu_btn.clicked.connect(self._on_menu_pressed)
        layout.addWidget(self.menu_btn)
        
        # Directional pad + Select (center section)
        dpad_frame = QFrame()
        dpad_layout = QGridLayout(dpad_frame)
        dpad_layout.setSpacing(5)
        
        # Directional buttons
        self.up_btn = self._create_dpad_button("↑")
        self.up_btn.clicked.connect(self._on_up_pressed)
        dpad_layout.addWidget(self.up_btn, 0, 1)
        
        self.left_btn = self._create_dpad_button("←")
        self.left_btn.clicked.connect(self._on_left_pressed)
        dpad_layout.addWidget(self.left_btn, 1, 0)
        
        self.select_btn = self._create_dpad_button("SELECT", size=(80, 80))
        self.select_btn.clicked.connect(self._on_select_pressed)
        dpad_layout.addWidget(self.select_btn, 1, 1)
        
        self.right_btn = self._create_dpad_button("→")
        self.right_btn.clicked.connect(self._on_right_pressed)
        dpad_layout.addWidget(self.right_btn, 1, 2)
        
        self.down_btn = self._create_dpad_button("↓")
        self.down_btn.clicked.connect(self._on_down_pressed)
        dpad_layout.addWidget(self.down_btn, 2, 1)
        
        layout.addWidget(dpad_frame)
        
        # Media controls
        media_frame = QFrame()
        media_layout = QHBoxLayout(media_frame)
        media_layout.setSpacing(10)
        
        self.play_pause_btn = self._create_media_button("⏯")
        self.play_pause_btn.clicked.connect(self._on_play_pause_pressed)
        media_layout.addWidget(self.play_pause_btn)
        
        self.volume_up_btn = self._create_media_button("🔊")
        self.volume_up_btn.clicked.connect(self._on_volume_up_pressed)
        media_layout.addWidget(self.volume_up_btn)
        
        self.volume_down_btn = self._create_media_button("🔇")
        self.volume_down_btn.clicked.connect(self._on_volume_down_pressed)
        media_layout.addWidget(self.volume_down_btn)
        
        layout.addWidget(media_frame)
        
        # Home button (bottom)
        self.home_btn = self._create_remote_button("HOME", "#3498db")
        self.home_btn.clicked.connect(self._on_home_pressed)
        layout.addWidget(self.home_btn)
        
        layout.addStretch()
    
    def _create_remote_button(self, text: str, color: str) -> QPushButton:
        """Create styled remote button."""
        button = QPushButton(text)
        button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        button.setFixedSize(200, 45)
        button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {color},
                    stop: 1 {self._darken_color(color)}
                );
                border: none;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background: {self._darken_color(color, 0.3)};
            }}
        """)
        return button
    
    def _create_dpad_button(self, text: str, size: tuple = (60, 60)) -> QPushButton:
        """Create directional pad button."""
        button = QPushButton(text)
        button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        button.setFixedSize(*size)
        button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #95a5a6,
                    stop: 1 #7f8c8d
                );
                border: none;
                color: white;
                border-radius: 30px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
            QPushButton:pressed {
                background: #6c7b7d;
            }
        """)
        return button
    
    def _create_media_button(self, text: str) -> QPushButton:
        """Create media control button."""
        button = QPushButton(text)
        button.setFont(QFont("Arial", 16))
        button.setFixedSize(50, 50)
        button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f39c12,
                    stop: 1 #d68910
                );
                border: none;
                color: white;
                border-radius: 25px;
            }
            QPushButton:hover {
                background: #d68910;
            }
            QPushButton:pressed {
                background: #b7740f;
            }
        """)
        return button
    
    def _darken_color(self, color: str, factor: float = 0.2) -> str:
        """Darken a hex color by a factor."""
        # Simple darkening - remove # and convert to RGB, then darken
        if color.startswith('#'):
            color = color[1:]
        
        try:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Arrow keys for navigation
        QShortcut(QKeySequence("Up"), self, self._on_up_pressed)
        QShortcut(QKeySequence("Down"), self, self._on_down_pressed)
        QShortcut(QKeySequence("Left"), self, self._on_left_pressed)
        QShortcut(QKeySequence("Right"), self, self._on_right_pressed)
        
        # Enter/Return for select
        QShortcut(QKeySequence("Return"), self, self._on_select_pressed)
        QShortcut(QKeySequence("Enter"), self, self._on_select_pressed)
        
        # Space for play/pause
        QShortcut(QKeySequence("Space"), self, self._on_play_pause_pressed)
        
        # Escape for menu
        QShortcut(QKeySequence("Escape"), self, self._on_menu_pressed)
    
    def _on_menu_pressed(self):
        """Handle menu button press."""
        self.menu_pressed.emit()
        print("Menu pressed")
    
    def _on_home_pressed(self):
        """Handle home button press."""
        self.home_pressed.emit()
        print("Home pressed")
    
    def _on_select_pressed(self):
        """Handle select button press."""
        self.select_pressed.emit()
        print("Select pressed")
    
    def _on_up_pressed(self):
        """Handle up button press."""
        self.up_pressed.emit()
        print("Up pressed")
    
    def _on_down_pressed(self):
        """Handle down button press."""
        self.down_pressed.emit()
        print("Down pressed")
    
    def _on_left_pressed(self):
        """Handle left button press."""
        self.left_pressed.emit()
        print("Left pressed")
    
    def _on_right_pressed(self):
        """Handle right button press."""
        self.right_pressed.emit()
        print("Right pressed")
    
    def _on_play_pause_pressed(self):
        """Handle play/pause button press."""
        self.play_pause_pressed.emit()
        print("Play/Pause pressed")
    
    def _on_volume_up_pressed(self):
        """Handle volume up button press."""
        self.volume_up_pressed.emit()
        print("Volume up pressed")
    
    def _on_volume_down_pressed(self):
        """Handle volume down button press."""
        self.volume_down_pressed.emit()
        print("Volume down pressed")


class NowPlayingPanel(QFrame):
    """Now playing information panel."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_track = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup now playing panel UI."""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #8e44ad,
                    stop: 1 #9b59b6
                );
                border: 1px solid #7d3c98;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel("🎵 Now Playing")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: white; margin-bottom: 15px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Album artwork placeholder
        artwork_frame = QFrame()
        artwork_frame.setFixedSize(200, 200)
        artwork_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
            }
        """)
        artwork_layout = QVBoxLayout(artwork_frame)
        artwork_label = QLabel("🎵")
        artwork_label.setFont(QFont("Arial", 48))
        artwork_label.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        artwork_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        artwork_layout.addWidget(artwork_label)
        layout.addWidget(artwork_frame, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Track info
        self.title_label = QLabel("No track playing")
        self.title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: white; margin: 10px 0 5px 0;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)
        
        self.artist_label = QLabel("")
        self.artist_label.setFont(QFont("Arial", 10))
        self.artist_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); margin-bottom: 5px;")
        self.artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artist_label.setWordWrap(True)
        layout.addWidget(self.artist_label)
        
        self.album_label = QLabel("")
        self.album_label.setFont(QFont("Arial", 9))
        self.album_label.setStyleSheet("color: rgba(255, 255, 255, 0.6); margin-bottom: 15px;")
        self.album_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.album_label.setWordWrap(True)
        layout.addWidget(self.album_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #e74c3c,
                    stop: 1 #c0392b
                );
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Time labels
        time_frame = QFrame()
        time_layout = QHBoxLayout(time_frame)
        time_layout.setContentsMargins(0, 5, 0, 0)
        
        self.current_time_label = QLabel("0:00")
        self.current_time_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 10px;")
        time_layout.addWidget(self.current_time_label)
        
        time_layout.addStretch()
        
        self.total_time_label = QLabel("0:00")
        self.total_time_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 10px;")
        time_layout.addWidget(self.total_time_label)
        
        layout.addWidget(time_frame)
        
        # Volume control
        volume_frame = QFrame()
        volume_layout = QVBoxLayout(volume_frame)
        volume_layout.setContentsMargins(0, 15, 0, 0)
        
        volume_label = QLabel("🔊 Volume")
        volume_label.setStyleSheet("color: white; font-weight: bold; margin-bottom: 5px;")
        volume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid rgba(255, 255, 255, 0.3);
                height: 8px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 2px solid #8e44ad;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -5px 0;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #e74c3c,
                    stop: 1 #c0392b
                );
                border-radius: 4px;
            }
        """)
        volume_layout.addWidget(self.volume_slider)
        
        layout.addWidget(volume_frame)
        layout.addStretch()
        
        # Set demo data
        self._set_demo_data()
    
    def _set_demo_data(self):
        """Set demo playing data."""
        self.title_label.setText("Shake It Off")
        self.artist_label.setText("Taylor Swift")
        self.album_label.setText("1989")
        self.progress_bar.setRange(0, 219)  # 3:39 in seconds
        self.progress_bar.setValue(95)  # 1:35 played
        self.current_time_label.setText("1:35")
        self.total_time_label.setText("3:39")


class ResponsiveMainWindow(QMainWindow):
    """Main window with responsive three-section layout."""
    
    def __init__(self, config_manager=None, device_controller=None, pairing_manager=None):
        super().__init__()
        self.config_manager = config_manager
        self.device_controller = device_controller
        self.pairing_manager = pairing_manager
        
        # Layout mode tracking
        self.is_compact_mode = False
        self.min_width_for_sections = 1200  # Minimum width for three sections
        
        self._setup_ui()
        self._setup_responsive_behavior()
        
    def _setup_ui(self):
        """Setup main window UI."""
        self.setWindowTitle("ApplerGUI - Apple TV Remote Control")
        self.setMinimumSize(400, 600)
        self.resize(1400, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout container
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget (hidden initially)
        self.tab_widget = QTabWidget()
        self.tab_widget.setVisible(False)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background: white;
            }
            QTabBar::tab {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background: #e9ecef;
            }
        """)
        self.main_layout.addWidget(self.tab_widget)
        
        # Three-section splitter (visible initially)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # Create panels
        self.discovery_panel = DiscoveryPanel(self.config_manager)
        self.remote_panel = RemotePanel()
        self.now_playing_panel = NowPlayingPanel()
        
        # Add panels to splitter
        self.splitter.addWidget(self.discovery_panel)
        self.splitter.addWidget(self.remote_panel)
        self.splitter.addWidget(self.now_playing_panel)
        
        # Set equal sizes
        self.splitter.setSizes([400, 400, 400])
        
        # Add panels to tab widget (for later use)
        self.tab_widget.addTab(self.discovery_panel, "🔍 Discovery")
        self.tab_widget.addTab(self.remote_panel, "📺 Remote")
        self.tab_widget.addTab(self.now_playing_panel, "🎵 Now Playing")
        
        # Connect signals
        self.discovery_panel.pairing_requested.connect(self._handle_pairing_request)
        
    def _setup_responsive_behavior(self):
        """Setup responsive window behavior."""
        # Window resize timer for smooth responsive transitions
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._update_layout_mode)
        
    def resizeEvent(self, event):
        """Handle window resize for responsive layout."""
        super().resizeEvent(event)
        # Debounce resize events
        self.resize_timer.start(100)
        
    def _update_layout_mode(self):
        """Update layout based on window size."""
        current_width = self.width()
        should_be_compact = current_width < self.min_width_for_sections
        
        if should_be_compact != self.is_compact_mode:
            self.is_compact_mode = should_be_compact
            self._switch_layout_mode()
    
    def _switch_layout_mode(self):
        """Switch between compact and expanded layout modes."""
        if self.is_compact_mode:
            # Switch to compact mode (tabs)
            self.splitter.setVisible(False)
            self.tab_widget.setVisible(True)
            
            # Move current panels to tab widget if not already there
            self._move_panels_to_tabs()
            
        else:
            # Switch to expanded mode (three sections)
            self.tab_widget.setVisible(False)
            self.splitter.setVisible(True)
            
            # Move panels back to splitter
            self._move_panels_to_splitter()
    
    def _move_panels_to_tabs(self):
        """Move panels from splitter to tab widget."""
        # Remove from splitter (if present)
        for i in range(self.splitter.count()):
            widget = self.splitter.widget(0)
            if widget:
                widget.setParent(None)
        
        # Clear and re-add to tabs
        self.tab_widget.clear()
        self.tab_widget.addTab(self.discovery_panel, "🔍 Discovery")
        self.tab_widget.addTab(self.remote_panel, "📺 Remote")
        self.tab_widget.addTab(self.now_playing_panel, "🎵 Now Playing")
    
    def _move_panels_to_splitter(self):
        """Move panels from tab widget to splitter."""
        # Remove from tabs
        self.tab_widget.clear()
        
        # Add back to splitter
        self.splitter.addWidget(self.discovery_panel)
        self.splitter.addWidget(self.remote_panel)
        self.splitter.addWidget(self.now_playing_panel)
        
        # Restore sizes
        self.splitter.setSizes([400, 400, 400])
    
    def _handle_pairing_request(self, device_info):
        """Handle device pairing request with overlay."""
        # Create darkened overlay for PIN entry
        from ui.pin_overlay import PinOverlay
        
        overlay = PinOverlay(device_info, parent=self)
        overlay.pin_entered.connect(self._handle_pin_entry)
        overlay.overlay_closed.connect(lambda: print("PIN overlay closed"))
        overlay.show_overlay()
    
    def _handle_pin_entry(self, device_info, pin):
        """Handle PIN entry for device pairing."""
        # Implement PIN-based pairing logic
        logging.info(f"PIN entered for {device_info['name']}: {pin}")
        QMessageBox.information(self, "Pairing", 
                                f"PIN entered for {device_info['name']}: {pin}\n(Demo mode)")