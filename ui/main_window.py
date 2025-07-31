"""Main application window for AppleTVRemote-GUI."""

import sys
import logging
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QSplitter, QFrame, QTabWidget, QLabel, QPushButton, 
                             QProgressBar, QTableWidget, QGroupBox, QGridLayout, 
                             QSlider, QTableWidgetItem, QLineEdit, QStatusBar, 
                             QMenuBar, QMessageBox, QApplication, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot, QThreadPool, QPropertyAnimation, QEasingCurve
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
    """Device discovery panel with real pyatv backend integration"""
    
    device_selected = pyqtSignal(dict)
    pairing_requested = pyqtSignal(dict)
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.discovered_devices = []
        self.selected_device = None
        self.current_device = None  # Currently connected device
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup discovery panel with current device status"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        
        # Ensure minimum size for visibility
        self.setMinimumSize(300, 400)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("Device Discovery")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Currently connected device section
        connected_group = QGroupBox("Currently Connected")
        connected_layout = QVBoxLayout(connected_group)
        
        self.connected_device_label = QLabel("No device connected")
        self.connected_device_label.setStyleSheet("font-weight: bold; color: #333;")
        connected_layout.addWidget(self.connected_device_label)
        
        self.connected_status_label = QLabel("Status: Disconnected")
        self.connected_status_label.setStyleSheet("color: #666; font-size: 11px;")
        connected_layout.addWidget(self.connected_status_label)
        
        # Disconnect button
        self.disconnect_btn = self._create_clean_button("Disconnect")
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.clicked.connect(self._disconnect_device)
        connected_layout.addWidget(self.disconnect_btn)
        
        layout.addWidget(connected_group)
        
        # Status label
        self.status_label = QLabel("Ready to discover devices...")
        layout.addWidget(self.status_label)
        
        # Discover button
        self.discover_btn = self._create_clean_button("Discover Apple TVs")
        self.discover_btn.clicked.connect(self._start_discovery)
        layout.addWidget(self.discover_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Device list group
        devices_group = QGroupBox("Available Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        # Device table
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(3)
        self.devices_table.setHorizontalHeaderLabels(["Device Name", "Model", "Address"])
        self.devices_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.devices_table.verticalHeader().setVisible(False)
        self.devices_table.setAlternatingRowColors(True)
        self.devices_table.itemSelectionChanged.connect(self._on_device_selected)
        self.devices_table.setMinimumHeight(150)
        devices_layout.addWidget(self.devices_table)
        
        # Connect button
        self.connect_btn = self._create_clean_button("Connect to Selected Device")
        self.connect_btn.setEnabled(False)
        self.connect_btn.clicked.connect(self._connect_device)
        devices_layout.addWidget(self.connect_btn)
        
        layout.addWidget(devices_group)
        layout.addStretch()
    
    def _create_clean_button(self, text):
        """Create clean button with consistent styling"""
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f0f0f0,
                    stop: 1 #e0e0e0
                );
                border: 1px solid #a0a0a0;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: normal;
                min-height: 28px;
                color: #333;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e8e8e8,
                    stop: 1 #d8d8d8
                );
                border-color: #808080;
            }
            QPushButton:pressed {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #d0d0d0,
                    stop: 1 #c0c0c0
                );
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #999;
                border-color: #ddd;
            }
        """)
        return button
    
    async def _start_discovery(self):
        """Start real device discovery using pyatv"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Scanning for Apple TV devices...")
        self.discover_btn.setEnabled(False)
        self.discovered_devices.clear()
        self._populate_device_table()
        
        try:
            import pyatv
            
            # Real device discovery
            devices = await pyatv.scan(timeout=5)
            
            self.discovered_devices = []
            for device in devices:
                device_info = {
                    "name": device.name,
                    "model": str(device.device_info.model) if device.device_info else "Unknown",
                    "address": str(device.address),
                    "device": device  # Store the actual pyatv device object
                }
                self.discovered_devices.append(device_info)
            
            self._populate_device_table()
            self.status_label.setText(f"Found {len(self.discovered_devices)} device(s)")
            
        except ImportError:
            self.status_label.setText("Error: pyatv not installed")
        except Exception as e:
            self.status_label.setText(f"Discovery error: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
            self.discover_btn.setEnabled(True)
    
    def _populate_device_table(self):
        """Populate device table with discovered devices"""
        self.devices_table.setRowCount(len(self.discovered_devices))
        for row, device in enumerate(self.discovered_devices):
            name_item = QTableWidgetItem(device['name'])
            model_item = QTableWidgetItem(device['model'])
            address_item = QTableWidgetItem(device['address'])
            
            self.devices_table.setItem(row, 0, name_item)
            self.devices_table.setItem(row, 1, model_item)
            self.devices_table.setItem(row, 2, address_item)
        
        self.devices_table.resizeColumnsToContents()
    
    def _on_device_selected(self):
        """Handle device selection"""
        selected_rows = self.devices_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_device = self.discovered_devices[row]
            self.connect_btn.setEnabled(True)
        else:
            self.selected_device = None
            self.connect_btn.setEnabled(False)
    
    async def _connect_device(self):
        """Connect to selected device"""
        if not self.selected_device:
            return
        
        try:
            import pyatv
            
            self.status_label.setText(f"Connecting to {self.selected_device['name']}...")
            self.connect_btn.setEnabled(False)
            
            # Connect to the device
            device = self.selected_device['device']
            atv = await pyatv.connect(device, loop=None)
            
            # Update current device status
            self.current_device = {
                'name': self.selected_device['name'],
                'model': self.selected_device['model'],
                'address': self.selected_device['address'],
                'atv': atv
            }
            
            self._update_connected_device_display()
            self.status_label.setText(f"Successfully connected to {self.selected_device['name']}")
            
        except Exception as e:
            self.status_label.setText(f"Connection failed: {str(e)}")
        finally:
            self.connect_btn.setEnabled(True)
    
    def _disconnect_device(self):
        """Disconnect from current device"""
        if self.current_device and 'atv' in self.current_device:
            try:
                self.current_device['atv'].close()
            except:
                pass
        
        self.current_device = None
        self._update_connected_device_display()
        self.status_label.setText("Disconnected from device")
    
    def _update_connected_device_display(self):
        """Update the connected device display"""
        if self.current_device:
            self.connected_device_label.setText(f"📺 {self.current_device['name']}")
            self.connected_status_label.setText(f"Status: Connected ({self.current_device['model']})")
            self.disconnect_btn.setEnabled(True)
        else:
            self.connected_device_label.setText("No device connected")
            self.connected_status_label.setText("Status: Disconnected")
            self.disconnect_btn.setEnabled(False)
    
    def get_current_device(self):
        """Get the currently connected device"""
        return self.current_device

class RemotePanel(QFrame):
    """Apple TV remote control panel with improved modern design"""
    
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
        self.button_animations = {}
        self._setup_ui()
        self._setup_shortcuts()
    
    def _setup_ui(self):
        """Setup remote control UI with improved modern design"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        
        # Ensure minimum size for visibility
        self.setMinimumSize(300, 500)  # Increased height for shortcuts
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Apple TV Remote")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Menu button - standard rounded button
        self.menu_btn = self._create_standard_button("MENU", (160, 40))
        self.menu_btn.clicked.connect(self._on_menu_pressed)
        layout.addWidget(self.menu_btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Directional pad - improved box layout
        dpad_frame = QFrame()
        dpad_layout = QGridLayout(dpad_frame)
        dpad_layout.setSpacing(12)  # More even spacing
        dpad_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create directional buttons with consistent sizing and modern layout
        button_size = 50
        
        self.up_btn = self._create_standard_button("↑", (button_size, button_size))
        self.up_btn.clicked.connect(self._on_up_pressed)
        dpad_layout.addWidget(self.up_btn, 0, 1, Qt.AlignmentFlag.AlignCenter)
        
        self.left_btn = self._create_standard_button("←", (button_size, button_size))
        self.left_btn.clicked.connect(self._on_left_pressed)
        dpad_layout.addWidget(self.left_btn, 1, 0, Qt.AlignmentFlag.AlignCenter)
        
        # OK button in center - standard rounded button (not circular)
        self.select_btn = self._create_standard_button("OK", (60, 60))
        self.select_btn.clicked.connect(self._on_select_pressed)
        dpad_layout.addWidget(self.select_btn, 1, 1, Qt.AlignmentFlag.AlignCenter)
        
        self.right_btn = self._create_standard_button("→", (button_size, button_size))
        self.right_btn.clicked.connect(self._on_right_pressed)
        dpad_layout.addWidget(self.right_btn, 1, 2, Qt.AlignmentFlag.AlignCenter)
        
        self.down_btn = self._create_standard_button("↓", (button_size, button_size))
        self.down_btn.clicked.connect(self._on_down_pressed)
        dpad_layout.addWidget(self.down_btn, 2, 1, Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(dpad_frame)
        
        # Media controls - evenly spaced
        media_frame = QFrame()
        media_layout = QHBoxLayout(media_frame)
        media_layout.setSpacing(20)
        media_layout.setContentsMargins(20, 10, 20, 10)
        
        self.play_pause_btn = self._create_standard_button("⏯", (50, 50))
        self.play_pause_btn.clicked.connect(self._on_play_pause_pressed)
        media_layout.addWidget(self.play_pause_btn)
        
        self.volume_up_btn = self._create_standard_button("🔊", (50, 50))
        self.volume_up_btn.clicked.connect(self._on_volume_up_pressed)
        media_layout.addWidget(self.volume_up_btn)
        
        self.volume_down_btn = self._create_standard_button("🔇", (50, 50))
        self.volume_down_btn.clicked.connect(self._on_volume_down_pressed)
        media_layout.addWidget(self.volume_down_btn)
        
        layout.addWidget(media_frame)
        
        # Home button
        self.home_btn = self._create_standard_button("HOME", (160, 40))
        self.home_btn.clicked.connect(self._on_home_pressed)
        layout.addWidget(self.home_btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Keyboard shortcuts info section
        shortcuts_group = QGroupBox("Keyboard Shortcuts")
        shortcuts_layout = QVBoxLayout(shortcuts_group)
        shortcuts_layout.setSpacing(5)
        
        shortcuts_text = [
            "Arrow Keys: Navigation",
            "Enter/Return: OK/Select",
            "Space: Play/Pause",
            "M: Menu",
            "H: Home",
            "+/-: Volume Up/Down"
        ]
        
        for shortcut in shortcuts_text:
            shortcut_label = QLabel(shortcut)
            shortcut_label.setStyleSheet("font-size: 11px; color: #666;")
            shortcuts_layout.addWidget(shortcut_label)
        
        layout.addWidget(shortcuts_group)
        layout.addStretch()
    
    def _create_standard_button(self, text, size=(50, 50)):
        """Create standard Qt button with consistent rounded styling"""
        button = QPushButton(text)
        button.setFixedSize(*size)
        
        # Set appropriate font size based on button size
        if size[0] >= 160:  # Large buttons (MENU, HOME)
            button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        elif size[0] >= 60:  # Medium buttons (OK)
            button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        else:  # Small buttons (arrows, media)
            button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        # Standard Qt button styling with consistent rounded corners
        button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f0f0f0,
                    stop: 1 #e0e0e0
                );
                border: 1px solid #a0a0a0;
                border-radius: 8px;
                color: #333;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e8e8e8,
                    stop: 1 #d8d8d8
                );
                border-color: #808080;
            }
            QPushButton:pressed {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #d0d0d0,
                    stop: 1 #c0c0c0
                );
                border-color: #606060;
            }
        """)
        return button
    
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
    
    def _animate_button_press(self, button):
        """Enhanced button press animation with visual feedback"""
        button_id = id(button)
        
        # Cancel existing animation
        if button_id in self.button_animations:
            animation = self.button_animations[button_id]
            if animation.state() == QPropertyAnimation.State.Running:
                animation.stop()
        
        # Create press animation with more obvious visual feedback
        original_style = button.styleSheet()
        
        # Highlight effect
        pressed_style = """
            QPushButton {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #b0b0ff,
                    stop: 1 #9090ff
                );
                border: 2px solid #6060ff;
                border-radius: 8px;
                color: #000;
                font-weight: bold;
            }
        """
        
        animation = QPropertyAnimation(button, b"styleSheet")
        animation.setDuration(150)
        animation.setStartValue(pressed_style)
        animation.setEndValue(original_style)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.button_animations[button_id] = animation
        animation.finished.connect(lambda: self.button_animations.pop(button_id, None))
        animation.start()
    
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

class NowPlayingPanel(QFrame):
    """Now playing information panel with consistent styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_track = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup now playing panel with modern styling"""
        # Use existing main window frame styling
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        
        # Ensure minimum size for visibility
        self.setMinimumSize(250, 400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("Now Playing")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Album artwork placeholder with modern styling
        artwork_frame = QFrame()
        artwork_frame.setFrameStyle(QFrame.Shape.Box)
        artwork_frame.setFixedSize(180, 180)
        artwork_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8f8f8,
                    stop: 1 #e8e8e8
                );
                border: 1px solid #ccc;
                border-radius: 8px;
            }
        """)
        artwork_layout = QVBoxLayout(artwork_frame)
        
        artwork_label = QLabel("🎵")
        artwork_label.setFont(QFont("Arial", 36))
        artwork_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        artwork_label.setStyleSheet("color: #666;")
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
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #999;
                border-radius: 6px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # Time labels
        time_frame = QFrame()
        time_layout = QHBoxLayout(time_frame)
        time_layout.setContentsMargins(0, 0, 0, 0)
        
        self.current_time_label = QLabel("0:00")
        self.current_time_label.setStyleSheet("color: #666; font-size: 11px;")
        time_layout.addWidget(self.current_time_label)
        
        time_layout.addStretch()
        
        self.total_time_label = QLabel("0:00")
        self.total_time_label.setStyleSheet("color: #666; font-size: 11px;")
        time_layout.addWidget(self.total_time_label)
        
        progress_layout.addWidget(time_frame)
        layout.addWidget(progress_group)
        
        # Volume control
        volume_group = QGroupBox("Volume Control")
        volume_layout = QVBoxLayout(volume_group)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #ccc;
                height: 8px;
                background: #f0f0f0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #999;
                border: 2px solid #777;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -5px 0;
            }
            QSlider::sub-page:horizontal {
                background-color: #999;
                border-radius: 4px;
            }
        """)
        volume_layout.addWidget(self.volume_slider)
        
        volume_value_frame = QFrame()
        volume_value_layout = QHBoxLayout(volume_value_frame)
        volume_value_layout.setContentsMargins(0, 0, 0, 0)
        
        volume_value_layout.addWidget(QLabel("🔇"))
        volume_value_layout.addStretch()
        self.volume_value_label = QLabel("50%")
        self.volume_value_label.setStyleSheet("color: #666; font-weight: bold;")
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

class ResponsiveMainWindow(QMainWindow):
    """Main window with backend integration"""
    
    def __init__(self, config_manager=None, device_controller=None, pairing_manager=None):
        super().__init__()
        self.config_manager = config_manager
        self.device_controller = device_controller
        self.pairing_manager = pairing_manager
        
        # Responsive settings
        self.is_compact_mode = False
        self.min_width_for_sections = 900
        
        self._setup_ui()
        self._setup_responsive_behavior()
        
        # Critical: Force initial layout check AFTER panels are created
        QTimer.singleShot(100, self._force_initial_layout)
    
    def _setup_ui(self):
        """Setup main window UI with backend integration"""
        self.setWindowTitle("ApplerGUI - Apple TV Remote Control")
        self.setMinimumSize(700, 500)
        self.resize(1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(5)
        
        # Create panels FIRST
        self.discovery_panel = DiscoveryPanel(self.config_manager)
        self.remote_panel = RemotePanel()
        self.now_playing_panel = NowPlayingPanel()
        
        # Connect remote buttons to device actions
        self._connect_remote_signals()
        
        # Tab widget (hidden initially)
        self.tab_widget = QTabWidget()
        self.tab_widget.setVisible(False)
        self.main_layout.addWidget(self.tab_widget)
        
        # Three-section splitter (visible initially)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(4)
        self.main_layout.addWidget(self.splitter)
        
        # Add panels to splitter IMMEDIATELY
        self.splitter.addWidget(self.discovery_panel)
        self.splitter.addWidget(self.remote_panel)
        self.splitter.addWidget(self.now_playing_panel)
        
        # Set sizes IMMEDIATELY after adding widgets
        self.splitter.setSizes([400, 400, 400])
        
        # Configure stretch factors
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 1)
    
    def _connect_remote_signals(self):
        """Connect remote button signals to device actions"""
        self.remote_panel.menu_pressed.connect(self._send_menu_command)
        self.remote_panel.home_pressed.connect(self._send_home_command)
        self.remote_panel.select_pressed.connect(self._send_select_command)
        self.remote_panel.up_pressed.connect(self._send_up_command)
        self.remote_panel.down_pressed.connect(self._send_down_command)
        self.remote_panel.left_pressed.connect(self._send_left_command)
        self.remote_panel.right_pressed.connect(self._send_right_command)
        self.remote_panel.play_pause_pressed.connect(self._send_play_pause_command)
        self.remote_panel.volume_up_pressed.connect(self._send_volume_up_command)
        self.remote_panel.volume_down_pressed.connect(self._send_volume_down_command)
    
    async def _send_menu_command(self):
        """Send menu command to connected device"""
        await self._send_remote_command("menu")
    
    async def _send_home_command(self):
        """Send home command to connected device"""
        await self._send_remote_command("home")
    
    async def _send_select_command(self):
        """Send select command to connected device"""
        await self._send_remote_command("select")
    
    async def _send_up_command(self):
        """Send up command to connected device"""
        await self._send_remote_command("up")
    
    async def _send_down_command(self):
        """Send down command to connected device"""
        await self._send_remote_command("down")
    
    async def _send_left_command(self):
        """Send left command to connected device"""
        await self._send_remote_command("left")
    
    async def _send_right_command(self):
        """Send right command to connected device"""
        await self._send_remote_command("right")
    
    async def _send_play_pause_command(self):
        """Send play/pause command to connected device"""
        await self._send_remote_command("play_pause")
    
    async def _send_volume_up_command(self):
        """Send volume up command to connected device"""
        await self._send_remote_command("volume_up")
    
    async def _send_volume_down_command(self):
        """Send volume down command to connected device"""
        await self._send_remote_command("volume_down")
    
    async def _send_remote_command(self, command):
        """Send command to the connected Apple TV device"""
        current_device = self.discovery_panel.get_current_device()
        if not current_device or 'atv' not in current_device:
            print(f"No device connected - cannot send {command}")
            return
        
        try:
            atv = current_device['atv']
            remote_control = atv.remote_control
            
            command_map = {
                "menu": remote_control.menu,
                "home": remote_control.home,
                "select": remote_control.select,
                "up": remote_control.up,
                "down": remote_control.down,
                "left": remote_control.left,
                "right": remote_control.right,
                "play_pause": remote_control.play_pause,
                "volume_up": remote_control.volume_up,
                "volume_down": remote_control.volume_down,
            }
            
            if command in command_map:
                await command_map[command]()
                print(f"Sent {command} command to {current_device['name']}")
            else:
                print(f"Unknown command: {command}")
                
        except Exception as e:
            print(f"Error sending {command} command: {str(e)}")
    
    def _setup_responsive_behavior(self):
        """Setup responsive window behavior"""
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._update_layout_mode)
    
    def resizeEvent(self, event):
        """Handle window resize for responsive layout"""
        super().resizeEvent(event)
        self.resize_timer.start(150)  # Slightly longer debounce
    
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
        """Move panels to tab widget"""
        print("Moving panels to tabs")
        
        # Clear tabs
        self.tab_widget.clear()
        
        # Add panels to tabs
        self.tab_widget.addTab(self.discovery_panel, "🔍 Discovery")
        self.tab_widget.addTab(self.remote_panel, "📺 Remote")
        self.tab_widget.addTab(self.now_playing_panel, "🎵 Now Playing")
    
    def _move_panels_to_splitter(self):
        """Move panels from tab widget to splitter with PROPER size management"""
        print("Moving panels to splitter")
        
        # Clear tabs first
        self.tab_widget.clear()
        
        # Add panels back to splitter
        self.splitter.addWidget(self.discovery_panel)
        self.splitter.addWidget(self.remote_panel)
        self.splitter.addWidget(self.now_playing_panel)
        
        # CRITICAL: Set sizes IMMEDIATELY after adding
        self.splitter.setSizes([400, 400, 400])
        
        # Force refresh
        QTimer.singleShot(10, lambda: self.splitter.setSizes([400, 400, 400]))
        
        print(f"After moving to splitter - sizes: {self.splitter.sizes()}")
    
    def _force_initial_layout(self):
        """Force initial layout mode to ensure visibility"""
        self._update_layout_mode()
        
        # Enhanced debugging
        print(f"=== LAYOUT DEBUG ===")
        print(f"Window size: {self.width()}x{self.height()}")
        print(f"Compact mode: {self.is_compact_mode}")
        print(f"Splitter visible: {self.splitter.isVisible()}")
        print(f"Tab widget visible: {self.tab_widget.isVisible()}")
        print(f"Splitter sizes: {self.splitter.sizes()}")
        print(f"Splitter count: {self.splitter.count()}")
        print(f"Discovery panel size: {self.discovery_panel.size()}")
        print(f"Remote panel size: {self.remote_panel.size()}")
        print(f"Now playing panel size: {self.now_playing_panel.size()}")
        print(f"===================")
        
        # Force repaint
        self.update()
        self.repaint()

# Backward compatibility alias
MainWindow = ResponsiveMainWindow

# Ensure proper exports
__all__ = ['ResponsiveMainWindow', 'MainWindow', 'DiscoveryPanel', 'RemotePanel', 'NowPlayingPanel']