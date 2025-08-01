#!/usr/bin/env python3
"""
Shared Launcher Module for Apple TV Remote GUI
This module provides unified launch functionality for both desktop and terminal entry points.
Ensures IDENTICAL behavior regardless of launch method.
"""

import os
import sys
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

def setup_environment():
    """Setup IDENTICAL environment for ALL launch methods"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Force IDENTICAL environment variables
    os.environ['PYTHONPATH'] = script_dir
    os.environ['QT_QPA_PLATFORM'] = 'xcb'
    os.environ['DISPLAY'] = ':0'
    
    # Force Python path consistency
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

class DiscoveryWorker(QThread):
    """Proper QThread for discovery"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def run(self):
        try:
            result = subprocess.run(
                ['atvremote', 'scan'],
                capture_output=True,
                text=True,
                timeout=15
            )
            self.finished.emit(result.stdout)
        except Exception as e:
            self.error.emit(str(e))

class AppleTVRemoteGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        print("🍎 Initializing Apple TV Remote GUI...")
        try:
            self._setup_ui()
            self._setup_discovery()
            self._setup_keyboard_shortcuts()
            self._setup_error_handling()
            # FORCE black styling immediately and repeatedly
            self._apply_black_styling_force()
        except Exception as e:
            print(f"Initialization error: {e}")
    
    def _setup_ui(self):
        """Setup main UI"""
        self.setWindowTitle("Apple TV Remote GUI")
        self.setFixedSize(300, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Create buttons
        self.discover_btn = QPushButton("Discover Apple TVs")
        self.up_btn = QPushButton("↑")
        self.down_btn = QPushButton("↓")
        self.left_btn = QPushButton("←")
        self.right_btn = QPushButton("→")
        self.select_btn = QPushButton("Select")
        self.play_pause_btn = QPushButton("⏯")
        self.menu_btn = QPushButton("Menu")
        self.home_btn = QPushButton("Home")
        
        # Volume pill container
        self.volume_container = QWidget()
        self.volume_container.setFixedSize(80, 120)
        volume_layout = QVBoxLayout()
        volume_layout.setSpacing(0)
        volume_layout.setContentsMargins(3, 3, 3, 3)
        
        self.volume_up_btn = QPushButton("🔊")
        self.volume_down_btn = QPushButton("🔉")
        
        volume_layout.addWidget(self.volume_up_btn)
        volume_layout.addWidget(self.volume_down_btn)
        self.volume_container.setLayout(volume_layout)
        
        # Add to main layout
        layout.addWidget(self.discover_btn)
        layout.addWidget(self.up_btn)
        layout.addWidget(self.down_btn)
        layout.addWidget(self.left_btn)
        layout.addWidget(self.right_btn)
        layout.addWidget(self.select_btn)
        layout.addWidget(self.play_pause_btn)
        layout.addWidget(self.menu_btn)
        layout.addWidget(self.home_btn)
        layout.addWidget(self.volume_container)
    
    def _setup_discovery(self):
        """Setup discovery functionality"""
        self.discovery_worker = None
        self.loading_timer = QTimer()
        self.loading_dots = 0
        self.loading_timer.timeout.connect(self._update_loading_dots)
        self.discover_btn.clicked.connect(self._safe_start_discovery)
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts with visual feedback"""
        shortcuts = {
            Qt.Key_Up: self.up_btn,
            Qt.Key_Down: self.down_btn,
            Qt.Key_Left: self.left_btn,
            Qt.Key_Right: self.right_btn,
            Qt.Key_Return: self.select_btn,
            Qt.Key_Space: self.play_pause_btn,
            Qt.Key_M: self.menu_btn,
            Qt.Key_H: self.home_btn,
            Qt.Key_Plus: self.volume_up_btn,
            Qt.Key_Minus: self.volume_down_btn,
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
    
    def _safe_start_discovery(self):
        """FIXED discovery start with proper error handling"""
        try:
            print("🔍 Starting discovery scan...")
            
            self.discover_btn.setText("Discovering")
            self.discover_btn.setEnabled(False)
            
            self.loading_dots = 0
            self.loading_timer.start(500)
            
            # Create new worker thread
            self.discovery_worker = DiscoveryWorker()
            self.discovery_worker.finished.connect(self._on_discovery_finished)
            self.discovery_worker.error.connect(self._on_discovery_error)
            self.discovery_worker.start()
            
        except Exception as e:
            print(f"Discovery start error: {e}")
            self._stop_discovery_animation()
    
    def _on_discovery_finished(self, output):
        """Handle discovery completion"""
        try:
            devices = self._parse_atvremote_scan_output(output)
            print(f"✅ Found {len(devices)} Apple TV devices")
            for device in devices:
                print(f"  - {device.get('Name', 'Unknown')} ({device.get('Address', 'No address')})")
        except Exception as e:
            print(f"Discovery parsing error: {e}")
        finally:
            self._stop_discovery_animation()
    
    def _on_discovery_error(self, error):
        """Handle discovery error"""
        print(f"❌ Discovery error: {error}")
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
    
    def _parse_atvremote_scan_output(self, output):
        """Parse atvremote scan output properly"""
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
    
    def _apply_black_styling_force(self):
        """FORCE black styling regardless of launch method"""
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
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """
        
        # Volume pill styling
        volume_style = """
            QWidget {
                background-color: transparent;
                border: 3px solid #444444;
                border-radius: 40px;
            }
        """
        
        # Apply styling IMMEDIATELY
        self.setStyleSheet(black_style)
        if hasattr(self, 'volume_container'):
            self.volume_container.setStyleSheet(volume_style)
        
        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        
        # Apply styling AGAIN after delays to ensure it sticks
        QTimer.singleShot(10, lambda: self._reapply_black_styling(black_style, volume_style))
        QTimer.singleShot(100, lambda: self._reapply_black_styling(black_style, volume_style))
        QTimer.singleShot(500, lambda: self._reapply_black_styling(black_style, volume_style))
    
    def _reapply_black_styling(self, black_style, volume_style):
        """Reapply black styling to ensure it sticks"""
        try:
            self.setStyleSheet(black_style)
            if hasattr(self, 'volume_container'):
                self.volume_container.setStyleSheet(volume_style)
            self.style().unpolish(self)
            self.style().polish(self)
            self.update()
        except Exception as e:
            print(f"Style reapply error: {e}")
    
    def _setup_error_handling(self):
        """Setup error handling to prevent crashes"""
        original_resize = self.resizeEvent
        def safe_resize(event):
            try:
                original_resize(event)
            except Exception as e:
                print(f"Resize error handled: {e}")
        self.resizeEvent = safe_resize
    
    def showEvent(self, event):
        """Override show event to force styling"""
        super().showEvent(event)
        # Force black styling when window is shown
        QTimer.singleShot(1, self._apply_black_styling_force)

def unified_main():
    """UNIFIED main function used by BOTH launch methods"""
    print("🍎 Apple TV Remote GUI Starting (Unified Launch)...")
    
    # Setup IDENTICAL environment
    setup_environment()
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Apple TV Remote GUI")
        
        # Create main window
        window = AppleTVRemoteGUI()
        window.show()
        
        # Force styling after show
        QTimer.singleShot(1, window._apply_black_styling_force)
        
        # Run application
        print("🍎 Application started successfully")
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)