"""Remote control widget for Apple TV interface."""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QPushButton, QLabel, QGroupBox, QSlider, QFrame)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
import asyncio

from backend.device_controller import DeviceController

class CircularButton(QPushButton):
    """Circular button for remote control."""
    
    def __init__(self, text: str = "", size: int = 60):
        super().__init__(text)
        self.setFixedSize(size, size)
        self._setup_style()
    
    def _setup_style(self):
        """Set up the circular button style."""
        self.setStyleSheet(f'''
        CircularButton {{
            border: 2px solid #555555;
            border-radius: {self.width() // 2}px;
            background-color: #404040;
            color: #ffffff;
            font-weight: bold;
            font-size: 12px;
        }}
        CircularButton:hover {{
            background-color: #505050;
            border-color: #666666;
        }}
        CircularButton:pressed {{
            background-color: #303030;
            border-color: #777777;
        }}
        CircularButton:disabled {{
            background-color: #2a2a2a;
            color: #666666;
            border-color: #444444;
        }}
        ''')

class DirectionalPad(QWidget):
    """Directional pad widget for Apple TV remote."""
    
    def __init__(self, device_controller: DeviceController):
        super().__init__()
        self.device_controller = device_controller
        self._setup_ui()
        self._setup_shortcuts()
    
    def _setup_ui(self):
        """Set up the directional pad UI."""
        layout = QGridLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(5)
        
        # Up button
        self.up_button = CircularButton("▲", 50)
        self.up_button.clicked.connect(lambda: asyncio.create_task(self.device_controller.remote_up()))
        layout.addWidget(self.up_button, 0, 1, Qt.AlignmentFlag.AlignCenter)
        
        # Left button
        self.left_button = CircularButton("◀", 50)
        self.left_button.clicked.connect(lambda: asyncio.create_task(self.device_controller.remote_left()))
        layout.addWidget(self.left_button, 1, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Select button (center)
        self.select_button = CircularButton("OK", 60)
        self.select_button.clicked.connect(lambda: asyncio.create_task(self.device_controller.remote_select()))
        layout.addWidget(self.select_button, 1, 1, Qt.AlignmentFlag.AlignCenter)
        
        # Right button
        self.right_button = CircularButton("▶", 50)
        self.right_button.clicked.connect(lambda: asyncio.create_task(self.device_controller.remote_right()))
        layout.addWidget(self.right_button, 1, 2, Qt.AlignmentFlag.AlignCenter)
        
        # Down button
        self.down_button = CircularButton("▼", 50)
        self.down_button.clicked.connect(lambda: asyncio.create_task(self.device_controller.remote_down()))
        layout.addWidget(self.down_button, 2, 1, Qt.AlignmentFlag.AlignCenter)
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts for directional pad."""
        # Arrow keys
        QShortcut(QKeySequence("Up"), self, lambda: asyncio.create_task(self.device_controller.remote_up()))
        QShortcut(QKeySequence("Down"), self, lambda: asyncio.create_task(self.device_controller.remote_down()))
        QShortcut(QKeySequence("Left"), self, lambda: asyncio.create_task(self.device_controller.remote_left()))
        QShortcut(QKeySequence("Right"), self, lambda: asyncio.create_task(self.device_controller.remote_right()))
        QShortcut(QKeySequence("Return"), self, lambda: asyncio.create_task(self.device_controller.remote_select()))
        QShortcut(QKeySequence("Enter"), self, lambda: asyncio.create_task(self.device_controller.remote_select()))
    
    def set_enabled(self, enabled: bool):
        """Enable or disable all directional pad buttons."""
        self.up_button.setEnabled(enabled)
        self.down_button.setEnabled(enabled)
        self.left_button.setEnabled(enabled)
        self.right_button.setEnabled(enabled)
        self.select_button.setEnabled(enabled)

class RemoteControlWidget(QWidget):
    """Widget for Apple TV remote control interface."""
    
    def __init__(self, device_controller: DeviceController):
        super().__init__()
        self.device_controller = device_controller
        self._setup_ui()
        self._setup_connections()
        self._setup_shortcuts()
        
        # Update UI state based on device connection
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui_state)
        self.update_timer.start(2000)  # Update every 2 seconds
        
        # Initial state update
        self._update_ui_state()
    
    def _setup_ui(self):
        """Set up the remote control UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Apple TV Remote")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Connection status
        self.connection_label = QLabel("No device connected")
        self.connection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connection_label.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(self.connection_label)
        
        # Main remote controls in a horizontal layout
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(30)
        
        # Left column - Directional pad
        left_column = QVBoxLayout()
        
        dpad_group = QGroupBox("Navigation")
        dpad_layout = QVBoxLayout(dpad_group)
        
        self.directional_pad = DirectionalPad(self.device_controller)
        dpad_layout.addWidget(self.directional_pad)
        
        left_column.addWidget(dpad_group)
        left_column.addStretch()
        
        # Right column - Control buttons
        right_column = QVBoxLayout()
        
        # Menu and Home buttons
        system_group = QGroupBox("System Controls")
        system_layout = QGridLayout(system_group)
        
        self.menu_button = QPushButton("Menu")
        self.menu_button.setFixedSize(80, 40)
        self.menu_button.clicked.connect(lambda: asyncio.create_task(self.device_controller.remote_menu()))
        system_layout.addWidget(self.menu_button, 0, 0)
        
        self.home_button = QPushButton("Home")
        self.home_button.setFixedSize(80, 40)
        self.home_button.clicked.connect(lambda: asyncio.create_task(self.device_controller.remote_home()))
        system_layout.addWidget(self.home_button, 0, 1)
        
        # Play/Pause button
        self.play_pause_button = QPushButton("Play/Pause")
        self.play_pause_button.setFixedSize(160, 40)
        self.play_pause_button.clicked.connect(lambda: asyncio.create_task(self.device_controller.remote_play_pause()))
        system_layout.addWidget(self.play_pause_button, 1, 0, 1, 2)
        
        right_column.addWidget(system_group)
        
        # Volume controls
        volume_group = QGroupBox("Volume")
        volume_layout = QVBoxLayout(volume_group)
        
        volume_buttons_layout = QHBoxLayout()
        
        self.volume_down_button = QPushButton("Vol -")
        self.volume_down_button.clicked.connect(lambda: asyncio.create_task(self.device_controller.remote_volume_down()))
        volume_buttons_layout.addWidget(self.volume_down_button)
        
        self.volume_up_button = QPushButton("Vol +")
        self.volume_up_button.clicked.connect(lambda: asyncio.create_task(self.device_controller.remote_volume_up()))
        volume_buttons_layout.addWidget(self.volume_up_button)
        
        volume_layout.addLayout(volume_buttons_layout)
        
        # Volume slider (for display/feedback)
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setEnabled(False)  # Read-only for now
        volume_layout.addWidget(self.volume_slider)
        
        volume_label = QLabel("Volume Control")
        volume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        volume_label.setStyleSheet("color: #888888; font-size: 10px;")
        volume_layout.addWidget(volume_label)
        
        right_column.addWidget(volume_group)
        right_column.addStretch()
        
        # Add columns to main layout
        controls_layout.addLayout(left_column)
        controls_layout.addLayout(right_column)
        
        layout.addLayout(controls_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #555555;")
        layout.addWidget(separator)
        
        # Shortcuts info
        shortcuts_group = QGroupBox("Keyboard Shortcuts")
        shortcuts_layout = QVBoxLayout(shortcuts_group)
        
        shortcuts_text = """
        Arrow Keys: Navigation
        Enter/Return: Select
        Space: Play/Pause
        M: Menu
        H: Home
        +/-: Volume Up/Down
        """
        
        shortcuts_label = QLabel(shortcuts_text)
        shortcuts_label.setStyleSheet("color: #888888; font-size: 10px;")
        shortcuts_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        shortcuts_layout.addWidget(shortcuts_label)
        
        layout.addWidget(shortcuts_group)
        
        layout.addStretch()
    
    def _setup_connections(self):
        """Set up signal connections."""
        self.device_controller.device_connected.connect(self._on_device_connected)
        self.device_controller.device_disconnected.connect(self._on_device_disconnected)
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # System controls
        QShortcut(QKeySequence("Space"), self, lambda: asyncio.create_task(self.device_controller.remote_play_pause()))
        QShortcut(QKeySequence("M"), self, lambda: asyncio.create_task(self.device_controller.remote_menu()))
        QShortcut(QKeySequence("H"), self, lambda: asyncio.create_task(self.device_controller.remote_home()))
        
        # Volume controls
        QShortcut(QKeySequence("+"), self, lambda: asyncio.create_task(self.device_controller.remote_volume_up()))
        QShortcut(QKeySequence("-"), self, lambda: asyncio.create_task(self.device_controller.remote_volume_down()))
        QShortcut(QKeySequence("="), self, lambda: asyncio.create_task(self.device_controller.remote_volume_up()))  # For keyboards without dedicated +
    
    def _update_ui_state(self):
        """Update UI state based on device connection."""
        connected_devices = self.device_controller.get_connected_devices()
        has_connection = len(connected_devices) > 0
        
        # Enable/disable controls
        self.directional_pad.set_enabled(has_connection)
        self.menu_button.setEnabled(has_connection)
        self.home_button.setEnabled(has_connection)
        self.play_pause_button.setEnabled(has_connection)
        self.volume_up_button.setEnabled(has_connection)
        self.volume_down_button.setEnabled(has_connection)
        
        # Update connection status
        if has_connection:
            device_info = next(iter(connected_devices.values()))
            device_name = device_info.get('name', 'Unknown Device')
            self.connection_label.setText(f"Connected to: {device_name}")
            self.connection_label.setStyleSheet("color: #00ff00; font-size: 12px; font-weight: bold;")
        else:
            self.connection_label.setText("No device connected")
            self.connection_label.setStyleSheet("color: #888888; font-size: 12px;")
    
    @pyqtSlot(str, dict)
    def _on_device_connected(self, device_id: str, device_info: dict):
        """Handle device connection."""
        self._update_ui_state()
    
    @pyqtSlot(str)
    def _on_device_disconnected(self, device_id: str):
        """Handle device disconnection."""
        self._update_ui_state()
    
    def set_volume_display(self, volume: int):
        """Set the volume slider display value."""
        self.volume_slider.setValue(volume)