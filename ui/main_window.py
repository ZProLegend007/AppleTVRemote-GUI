#!/usr/bin/env python3
import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QApplication)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
import subprocess

class DiscoveryWorker(QThread):
    """Worker thread for device discovery"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def run(self):
        try:
            result = subprocess.run(['atvremote', 'scan'], 
                                  capture_output=True, text=True, timeout=15)
            devices = self.parse_scan_output(result.stdout)
            self.finished.emit(devices)
        except Exception as e:
            self.error.emit(str(e))
    
    def parse_scan_output(self, output):
        """Parse atvremote scan output"""
        devices = []
        current_device = {}
        
        for line in output.strip().split('\n'):
            line = line.strip()
            if line == '----' or line == '':
                if current_device:
                    devices.append(current_device)
                    current_device = {}
            elif ':' in line:
                key, value = line.split(':', 1)
                current_device[key.strip()] = value.strip()
        
        if current_device:
            devices.append(current_device)
        
        return devices

class MainWindow(QMainWindow):
    def __init__(self, config_manager, device_controller, pairing_manager):
        super().__init__()
        self.config_manager = config_manager
        self.device_controller = device_controller
        self.pairing_manager = pairing_manager
        
        self.setWindowTitle("Apple TV Remote GUI")
        self.setFixedSize(300, 500)
        
        # Apply black styling IMMEDIATELY
        self._apply_black_styling()
        
        self._setup_ui()
        self._setup_discovery()
        self._setup_keyboard_shortcuts()
        
        # Force black styling repeatedly to ensure it sticks
        QTimer.singleShot(10, self._apply_black_styling)
        QTimer.singleShot(100, self._apply_black_styling)
        QTimer.singleShot(500, self._apply_black_styling)
    
    def _apply_black_styling(self):
        """Apply black styling to the window"""
        black_style = """
            QMainWindow {
                background-color: #000000;
                border: 2px solid #000000;
                color: #ffffff;
            }
            QWidget {
                background-color: #000000;
                color: #ffffff;
            }
            QPushButton {
                background-color: #2a2a2a;
                border: 2px solid #444444;
                color: #ffffff;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 2px solid #555555;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
                border: 2px solid #666666;
            }
            QPushButton:disabled {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                color: #666666;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
        """
        
        self.setStyleSheet(black_style)
        
        # Apply to volume container if it exists
        if hasattr(self, 'volume_container'):
            volume_style = """
                QWidget {
                    background-color: transparent;
                    border: 3px solid #444444;
                    border-radius: 40px;
                }
            """
            self.volume_container.setStyleSheet(volume_style)
        
        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
    
    def _setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Discovery section
        self.discover_btn = QPushButton("Discover Apple TVs")
        self.discover_btn.clicked.connect(self._start_discovery)
        layout.addWidget(self.discover_btn)
        
        # Device info label
        self.device_label = QLabel("No devices found")
        self.device_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.device_label)
        
        # Directional buttons
        nav_layout = QVBoxLayout()
        
        # Up button
        self.up_btn = QPushButton("↑")
        self.up_btn.setFixedSize(60, 40)
        up_layout = QHBoxLayout()
        up_layout.addStretch()
        up_layout.addWidget(self.up_btn)
        up_layout.addStretch()
        nav_layout.addLayout(up_layout)
        
        # Left, Select, Right buttons
        middle_layout = QHBoxLayout()
        self.left_btn = QPushButton("←")
        self.left_btn.setFixedSize(60, 40)
        self.select_btn = QPushButton("Select")
        self.select_btn.setFixedSize(80, 40)
        self.right_btn = QPushButton("→")
        self.right_btn.setFixedSize(60, 40)
        
        middle_layout.addWidget(self.left_btn)
        middle_layout.addWidget(self.select_btn)
        middle_layout.addWidget(self.right_btn)
        nav_layout.addLayout(middle_layout)
        
        # Down button
        self.down_btn = QPushButton("↓")
        self.down_btn.setFixedSize(60, 40)
        down_layout = QHBoxLayout()
        down_layout.addStretch()
        down_layout.addWidget(self.down_btn)
        down_layout.addStretch()
        nav_layout.addLayout(down_layout)
        
        layout.addLayout(nav_layout)
        
        # Control buttons
        control_layout = QVBoxLayout()
        
        self.play_pause_btn = QPushButton("⏯")
        self.menu_btn = QPushButton("Menu")
        self.home_btn = QPushButton("Home")
        
        control_layout.addWidget(self.play_pause_btn)
        control_layout.addWidget(self.menu_btn)
        control_layout.addWidget(self.home_btn)
        
        layout.addLayout(control_layout)
        
        # Volume control (pill shape)
        self.volume_container = QWidget()
        self.volume_container.setFixedSize(80, 120)
        volume_layout = QVBoxLayout()
        volume_layout.setSpacing(5)
        volume_layout.setContentsMargins(10, 10, 10, 10)
        
        self.volume_up_btn = QPushButton("🔊")
        self.volume_down_btn = QPushButton("🔉")
        
        volume_layout.addWidget(self.volume_up_btn)
        volume_layout.addWidget(self.volume_down_btn)
        self.volume_container.setLayout(volume_layout)
        
        volume_container_layout = QHBoxLayout()
        volume_container_layout.addStretch()
        volume_container_layout.addWidget(self.volume_container)
        volume_container_layout.addStretch()
        
        layout.addLayout(volume_container_layout)
        
        # Connect device controller buttons
        self._connect_device_buttons()
    
    def _connect_device_buttons(self):
        """Connect buttons to device controller"""
        self.up_btn.clicked.connect(self.device_controller.navigate_up)
        self.down_btn.clicked.connect(self.device_controller.navigate_down)
        self.left_btn.clicked.connect(self.device_controller.navigate_left)
        self.right_btn.clicked.connect(self.device_controller.navigate_right)
        self.select_btn.clicked.connect(self.device_controller.select)
        self.play_pause_btn.clicked.connect(self.device_controller.play_pause)
        self.menu_btn.clicked.connect(self.device_controller.menu)
        self.home_btn.clicked.connect(self.device_controller.home)
        self.volume_up_btn.clicked.connect(self.device_controller.volume_up)
        self.volume_down_btn.clicked.connect(self.device_controller.volume_down)
    
    def _setup_discovery(self):
        """Setup device discovery"""
        self.discovery_worker = None
        self.loading_timer = QTimer()
        self.loading_dots = 0
        self.loading_timer.timeout.connect(self._update_loading_dots)
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        shortcuts = {
            Qt.Key.Key_Up: self.up_btn,
            Qt.Key.Key_Down: self.down_btn,
            Qt.Key.Key_Left: self.left_btn,
            Qt.Key.Key_Right: self.right_btn,
            Qt.Key.Key_Return: self.select_btn,
            Qt.Key.Key_Space: self.play_pause_btn,
            Qt.Key.Key_M: self.menu_btn,
            Qt.Key.Key_H: self.home_btn,
            Qt.Key.Key_Plus: self.volume_up_btn,
            Qt.Key.Key_Minus: self.volume_down_btn,
        }
        
        for key, button in shortcuts.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(lambda btn=button: self._animate_button_press(btn))
    
    def _animate_button_press(self, button):
        """Animate button press for visual feedback"""
        try:
            original_style = button.styleSheet()
            button.setStyleSheet(original_style + """
                QPushButton {
                    background-color: #0a0a0a !important;
                    border: 2px solid #ffffff !important;
                }
            """)
            button.click()
            QTimer.singleShot(200, lambda: button.setStyleSheet(original_style))
        except Exception as e:
            print(f"Button animation error: {e}")
    
    def _start_discovery(self):
        """Start device discovery"""
        try:
            print("🔍 Starting discovery scan...")
            
            self.discover_btn.setText("Discovering")
            self.discover_btn.setEnabled(False)
            self.device_label.setText("Scanning for devices...")
            
            self.loading_dots = 0
            self.loading_timer.start(500)
            
            # Create and start worker thread
            self.discovery_worker = DiscoveryWorker()
            self.discovery_worker.finished.connect(self._on_discovery_finished)
            self.discovery_worker.error.connect(self._on_discovery_error)
            self.discovery_worker.start()
            
        except Exception as e:
            print(f"Discovery start error: {e}")
            self._stop_discovery_animation()
    
    def _on_discovery_finished(self, devices):
        """Handle discovery completion"""
        try:
            device_count = len(devices)
            print(f"✅ Found {device_count} Apple TV devices")
            
            if device_count == 0:
                self.device_label.setText("No devices found")
            elif device_count == 1:
                device = devices[0]
                device_name = device.get('Name', 'Unknown Device')
                self.device_label.setText(f"Found: {device_name}")
                print(f"  - {device_name} ({device.get('Address', 'No address')})")
            else:
                self.device_label.setText(f"Found {device_count} devices")
                for device in devices:
                    device_name = device.get('Name', 'Unknown Device')
                    print(f"  - {device_name} ({device.get('Address', 'No address')})")
                    
        except Exception as e:
            print(f"Discovery parsing error: {e}")
            self.device_label.setText("Discovery error")
        finally:
            self._stop_discovery_animation()
    
    def _on_discovery_error(self, error):
        """Handle discovery error"""
        print(f"❌ Discovery error: {error}")
        self.device_label.setText("Discovery failed")
        self._stop_discovery_animation()
    
    def _stop_discovery_animation(self):
        """Stop loading animation"""
        try:
            if hasattr(self, 'loading_timer'):
                self.loading_timer.stop()
            if hasattr(self, 'discover_btn'):
                self.discover_btn.setText("Discover Apple TVs")
                self.discover_btn.setEnabled(True)
        except Exception as e:
            print(f"Stop animation error: {e}")
    
    def _update_loading_dots(self):
        """Update loading dots animation"""
        try:
            dots = "." * (self.loading_dots % 4)
            self.discover_btn.setText(f"Discovering{dots}")
            self.loading_dots += 1
        except Exception as e:
            print(f"Loading dots error: {e}")
    
    def showEvent(self, event):
        """Override show event to force black styling"""
        super().showEvent(event)
        # Force black styling when window is shown
        QTimer.singleShot(1, self._apply_black_styling)