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

from .device_manager import DeviceManagerWidget
from .remote_control import RemoteControlWidget
from .now_playing import NowPlayingWidget
from .pairing_dialog import PairingDialogManager
from .settings import SettingsDialog
from .pin_dialog import PinDialog
from ..backend.config_manager import ConfigManager
from ..backend.device_controller import DeviceController
from ..backend.pairing_manager import PairingManager

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
        
        # Add environment debugging
        self._debug_launch_environment()
        
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
        
        # Discover button with safe connection
        self.discover_btn = self._create_clean_button("Discover Apple TVs")
        self.discover_btn.clicked.connect(self._safe_start_discovery)
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
    
    def _debug_launch_environment(self):
        """Debug environment differences between desktop and terminal launch"""
        import sys
        import os
        
        print("🔍 === ENVIRONMENT DEBUG ===")
        print(f"Launch method: {sys.argv}")
        print(f"Working directory: {os.getcwd()}")
        print(f"Python executable: {sys.executable}")
        print(f"DISPLAY environment: {os.environ.get('DISPLAY', 'Not set')}")
        print(f"XDG_SESSION_TYPE: {os.environ.get('XDG_SESSION_TYPE', 'Not set')}")
        print(f"DESKTOP_SESSION: {os.environ.get('DESKTOP_SESSION', 'Not set')}")
        print(f"PATH: {os.environ.get('PATH', 'Not set')[:100]}...")
        
        # Check if launched from desktop or terminal
        if os.isatty(sys.stdout.fileno()):
            print("🖥️ Launched from TERMINAL")
            launch_method = "terminal"
        else:
            print("🖱️ Launched from DESKTOP")
            launch_method = "desktop"
        
        # Store launch method for styling decisions
        self.launch_method = launch_method
        
        # Check for common styling issues
        qt_style_override = os.environ.get('QT_STYLE_OVERRIDE', 'Not set')
        qt_theme = os.environ.get('QT_QPA_PLATFORMTHEME', 'Not set')
        print(f"QT_STYLE_OVERRIDE: {qt_style_override}")
        print(f"QT_QPA_PLATFORMTHEME: {qt_theme}")
        print("🔍 ==========================")
    
    def _create_clean_button(self, text):
        """Create clean button with consistent styling"""
        button = QPushButton(text)
        # Remove custom light styling - let the global dark theme apply
        return button
    
    def _safe_start_discovery(self):
        """Safe discovery start with error handling"""
        try:
            # Use asyncio to run the async discovery method
            import qasync
            import asyncio
            
            # Get current event loop or create new one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Schedule the async discovery
            asyncio.create_task(self._start_discovery())
            
        except Exception as e:
            print(f"❌ Discovery start error: {e}")
            self.status_label.setText(f"❌ Discovery start error: {e}")
            self._cleanup_discovery_state()
    
    def resizeEvent(self, event):
        """Safe resize event handler"""
        try:
            super().resizeEvent(event)
        except Exception as e:
            print(f"⚠️ Resize error handled safely: {e}")
            # Continue without crashing
    
    @qasync.asyncSlot()
    async def _start_discovery(self):
        """CRASH-PROOF device discovery with comprehensive error handling"""
        print("🔍 Starting SAFE Apple TV discovery...")
        
        # Safety check - prevent multiple discoveries
        if hasattr(self, '_discovery_running') and self._discovery_running:
            print("⚠️ Discovery already running, ignoring request")
            return
        
        self._discovery_running = True
        
        try:
            # Start enhanced loading animation with crash protection
            self._setup_safe_discovery_ui()
            
            # Run actual discovery with comprehensive error handling
            await self._run_safe_discovery()
                
        except Exception as e:
            error_msg = f"❌ Critical discovery error: {str(e)}"
            self.status_label.setText(error_msg)
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean up timers and state SAFELY
            self._cleanup_discovery_state()
    
    def _setup_safe_discovery_ui(self):
        """Setup discovery UI with crash protection"""
        try:
            # Start enhanced loading animation
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress bar
            self.status_label.setText("Discovering Apple TV devices...")
            self.discover_btn.setEnabled(False)
            self.discover_btn.setText("Scanning...")
            self.discovered_devices.clear()
            self._populate_device_table()
            
            # Setup animated loading dots for button text with crash protection
            if hasattr(self, 'loading_timer'):
                self.loading_timer.stop()
            
            self.loading_timer = QTimer()
            self.loading_timer.timeout.connect(self._update_discovery_loading_animation)
            self.loading_timer.start(500)  # Update every 500ms
            
            # Safety timeout to prevent hanging (15 seconds max)
            if hasattr(self, 'discovery_timeout_timer'):
                self.discovery_timeout_timer.stop()
                
            self.discovery_timeout_timer = QTimer()
            self.discovery_timeout_timer.timeout.connect(self._handle_discovery_timeout)
            self.discovery_timeout_timer.start(15000)  # 15 second timeout
            
            print("🎬 Discovery UI setup complete with safety timers")
            
        except Exception as e:
            print(f"⚠️ Error setting up discovery UI: {e}")
            # Continue anyway, don't crash
    
    async def _run_safe_discovery(self):
        """ACTUALLY run discovery with comprehensive crash protection"""
        try:
            # Try pyatv first with crash protection
            try:
                import pyatv
                
                # Real device discovery with terminal output and crash protection
                print("📡 Scanning for Apple TV devices with timeout protection...")
                
                # Use asyncio.wait_for for additional timeout protection
                import asyncio
                devices = await asyncio.wait_for(pyatv.scan(timeout=8), timeout=12)
                
                self.discovered_devices = []
                for device in devices:
                    try:
                        device_info = {
                            "name": device.name,
                            "model": str(device.device_info.model) if device.device_info else "Unknown",
                            "address": str(device.address),
                            "device": device  # Store the actual pyatv device object
                        }
                        self.discovered_devices.append(device_info)
                        
                        # Real-time terminal output of discovered devices
                        print(f"📺 Found device: {device.name} ({device_info['model']}) at {device_info['address']}")
                    except Exception as device_error:
                        print(f"⚠️ Error processing device: {device_error}")
                        continue
                
                self._populate_device_table()
                device_count = len(self.discovered_devices)
                
                if device_count > 0:
                    self.status_label.setText(f"✅ Found {device_count} device(s)")
                else:
                    self.status_label.setText("No Apple TV devices found")
                
                # Terminal output summary
                print(f"✅ Safe discovery completed: {device_count} device(s) found")
                
            except ImportError:
                # Fallback to atvremote command with crash protection
                await self._safe_atvremote_discovery()
            except asyncio.TimeoutError:
                error_msg = "❌ Discovery timed out for safety"
                self.status_label.setText(error_msg)
                print(f"❌ {error_msg}")
            except Exception as pyatv_error:
                error_msg = f"❌ pyatv discovery error: {str(pyatv_error)}"
                self.status_label.setText(error_msg)
                print(f"❌ {error_msg}")
                # Try fallback
                await self._safe_atvremote_discovery()
                
        except Exception as e:
            error_msg = f"❌ Critical discovery error: {str(e)}"
            self.status_label.setText(error_msg)
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            if hasattr(self, 'loading_timer'):
                self.loading_timer.stop()
            self.loading_timer = QTimer()
            self.loading_dots = 0
            self.loading_timer.timeout.connect(self._update_discovery_loading_animation)
            self.loading_timer.start(500)  # Update every 500ms
            
            # Crash protection timeout
            self.discovery_timeout_timer = QTimer()
            self.discovery_timeout_timer.setSingleShot(True)
            self.discovery_timeout_timer.timeout.connect(self._handle_discovery_timeout)
            self.discovery_timeout_timer.start(20000)  # 20 second timeout
            
            # Terminal output for debugging
            print("Running: SAFE pyatv scan with crash protection")
            
            try:
                import pyatv
                
                # Real device discovery with terminal output and crash protection
                print("📡 Scanning for Apple TV devices with timeout protection...")
                
                # Use asyncio.wait_for for additional timeout protection
                import asyncio
                devices = await asyncio.wait_for(pyatv.scan(timeout=8), timeout=12)
                
                self.discovered_devices = []
                for device in devices:
                    try:
                        device_info = {
                            "name": device.name,
                            "model": str(device.device_info.model) if device.device_info else "Unknown",
                            "address": str(device.address),
                            "device": device  # Store the actual pyatv device object
                        }
                        self.discovered_devices.append(device_info)
                        
                        # Real-time terminal output of discovered devices
                        print(f"📺 Found device: {device.name} ({device_info['model']}) at {device_info['address']}")
                    except Exception as device_error:
                        print(f"⚠️ Error processing device: {device_error}")
                        continue
                
                self._populate_device_table()
                device_count = len(self.discovered_devices)
                
                if device_count > 0:
                    self.status_label.setText(f"✅ Found {device_count} device(s)")
                else:
                    self.status_label.setText("No Apple TV devices found")
                
                # Terminal output summary
                print(f"✅ Safe discovery completed: {device_count} device(s) found")
                
            except ImportError:
                # Fallback to atvremote command with crash protection
                await self._safe_atvremote_discovery()
            except asyncio.TimeoutError:
                error_msg = "❌ Discovery timed out for safety"
                self.status_label.setText(error_msg)
                print(f"❌ {error_msg}")
            except Exception as pyatv_error:
                error_msg = f"❌ pyatv discovery error: {str(pyatv_error)}"
                self.status_label.setText(error_msg)
                print(f"❌ {error_msg}")
                # Try fallback
                await self._safe_atvremote_discovery()
                
        except Exception as e:
            error_msg = f"❌ Critical discovery error: {str(e)}"
            self.status_label.setText(error_msg)
            print(f"❌ {error_msg}")
        finally:
            # Clean up timers and state SAFELY
            self._cleanup_discovery_state()
    
    async def _safe_atvremote_discovery(self):
        """Safe atvremote fallback discovery with PROPER parsing"""
        try:
            import subprocess
            import asyncio
            
            print("📡 Fallback: Using SAFE atvremote scan with correct parsing...")
            
            # Run subprocess in executor to prevent blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: subprocess.run(
                    ['atvremote', 'scan'], 
                    capture_output=True, 
                    text=True, 
                    timeout=10,
                    cwd=os.path.dirname(os.path.abspath(__file__))  # Consistent working dir
                )
            )
            
            print(f"Scan output: {result.stdout}")
            if result.stderr:
                print(f"Scan errors: {result.stderr}")
            
            # PROPER atvremote output parsing
            self.discovered_devices = self._parse_atvremote_scan_output(result.stdout)
            
            self._populate_device_table()
            device_count = len(self.discovered_devices)
            
            if device_count > 0:
                self.status_label.setText(f"✅ Found {device_count} device(s) via atvremote")
                print(f"✅ Found {device_count} Apple TV devices:")
                for device in self.discovered_devices:
                    print(f"  - {device.get('name', 'Unknown')} ({device.get('address', 'No address')})")
            else:
                self.status_label.setText("No Apple TV devices found via atvremote")
                print("ℹ️ No Apple TV devices found")
            
            print(f"✅ Safe atvremote discovery completed: {device_count} device(s) found")
            
        except subprocess.TimeoutExpired:
            error_msg = "❌ atvremote scan timed out safely"
            self.status_label.setText(error_msg)
            print(f"⏱️ {error_msg}")
        except FileNotFoundError:
            error_msg = "❌ Error: neither pyatv nor atvremote available"
            self.status_label.setText(error_msg)
            print(f"❌ {error_msg}")
        except Exception as e:
            error_msg = f"❌ Safe atvremote error: {str(e)}"
            self.status_label.setText(error_msg)
            print(f"❌ {error_msg}")
    
    def _parse_atvremote_scan_output(self, output):
        """PROPERLY parse atvremote scan output"""
        devices = []
        
        if not output or not output.strip():
            return devices
        
        # atvremote scan output format:
        # Name: Apple TV
        # Model: Apple TV 4K
        # Address: 192.168.1.100
        # Identifier: XXXX-XXXX-XXXX
        # ----
        
        current_device = {}
        for line in output.strip().split('\n'):
            line = line.strip()
            
            if line == '----' or line == '':
                if current_device:
                    # Convert to expected format
                    device_info = {
                        "name": current_device.get('Name', 'Unknown Apple TV'),
                        "model": current_device.get('Model', 'Apple TV'),
                        "address": current_device.get('Address', 'Unknown'),
                        "identifier": current_device.get('Identifier', 'Unknown'),
                        "device": None
                    }
                    devices.append(device_info)
                    current_device = {}
            elif ':' in line:
                key, value = line.split(':', 1)
                current_device[key.strip()] = value.strip()
        
        # Add last device if exists
        if current_device:
            device_info = {
                "name": current_device.get('Name', 'Unknown Apple TV'),
                "model": current_device.get('Model', 'Apple TV'),
                "address": current_device.get('Address', 'Unknown'),
                "identifier": current_device.get('Identifier', 'Unknown'),
                "device": None
            }
            devices.append(device_info)
        
        return devices
    
    def _handle_discovery_timeout(self):
        """Handle discovery timeout safely"""
        print("⏰ Discovery timeout reached - stopping safely")
        self.status_label.setText("❌ Discovery timed out for safety")
        self._cleanup_discovery_state()
    
    def _cleanup_discovery_state(self):
        """Clean up discovery state safely"""
        try:
            # Stop all timers safely
            if hasattr(self, 'loading_timer') and self.loading_timer:
                self.loading_timer.stop()
            if hasattr(self, 'discovery_timeout_timer') and self.discovery_timeout_timer:
                self.discovery_timeout_timer.stop()
            
            # Reset UI state
            self.progress_bar.setVisible(False)
            self.discover_btn.setText("Discover Apple TVs")  # Reset button text
            self.discover_btn.setEnabled(True)
            
            # Clear running flag
            self._discovery_running = False
            
            print("🧹 Discovery state cleaned up safely")
        except Exception as cleanup_error:
            print(f"⚠️ Error during cleanup: {cleanup_error}")
    
    def _update_discovery_loading_animation(self):
        """Update discovery loading dots animation"""
        dots = "." * (self.loading_dots % 4)
        self.discover_btn.setText(f"Discovering{dots}")
        self.loading_dots += 1
    
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
    
    @qasync.asyncSlot()
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
        
        # Directional pad - responsive arrow layout with even spacing
        dpad_frame = QFrame()
        dpad_layout = QGridLayout(dpad_frame)
        dpad_layout.setSpacing(20)  # Even spacing between buttons
        dpad_layout.setContentsMargins(40, 40, 40, 40)  # Larger margins for better centering
        
        # Create directional buttons with consistent sizing and modern layout
        button_size = 50
        
        self.up_btn = self._create_standard_button("↑", (button_size, button_size))
        self.up_btn.clicked.connect(self._on_up_pressed)
        dpad_layout.addWidget(self.up_btn, 0, 1, Qt.AlignmentFlag.AlignCenter)  # Top center
        
        self.left_btn = self._create_standard_button("←", (button_size, button_size))
        self.left_btn.clicked.connect(self._on_left_pressed)
        dpad_layout.addWidget(self.left_btn, 1, 0, Qt.AlignmentFlag.AlignCenter)  # Middle left
        
        # OK button in center - standard rounded button (not circular)
        self.select_btn = self._create_standard_button("OK", (60, 60))
        self.select_btn.clicked.connect(self._on_select_pressed)
        dpad_layout.addWidget(self.select_btn, 1, 1, Qt.AlignmentFlag.AlignCenter)  # Middle center
        
        self.right_btn = self._create_standard_button("→", (button_size, button_size))
        self.right_btn.clicked.connect(self._on_right_pressed)
        dpad_layout.addWidget(self.right_btn, 1, 2, Qt.AlignmentFlag.AlignCenter)  # Middle right
        
        self.down_btn = self._create_standard_button("↓", (button_size, button_size))
        self.down_btn.clicked.connect(self._on_down_pressed)
        dpad_layout.addWidget(self.down_btn, 2, 1, Qt.AlignmentFlag.AlignCenter)  # Bottom center
        
        # Make layout responsive with equal stretch factors for proportional scaling
        dpad_layout.setColumnStretch(0, 1)  # Left column
        dpad_layout.setColumnStretch(1, 1)  # Center column  
        dpad_layout.setColumnStretch(2, 1)  # Right column
        dpad_layout.setRowStretch(0, 1)     # Top row
        dpad_layout.setRowStretch(1, 1)     # Middle row
        dpad_layout.setRowStretch(2, 1)     # Bottom row
        
        layout.addWidget(dpad_frame)
        
        # Menu button - positioned above play/pause button
        self.menu_btn = self._create_standard_button("MENU", (160, 40))
        self.menu_btn.clicked.connect(self._on_menu_pressed)
        layout.addWidget(self.menu_btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Media controls layout with volume pill on the right
        media_frame = QFrame()
        media_layout = QHBoxLayout(media_frame)
        media_layout.setSpacing(20)
        media_layout.setContentsMargins(20, 10, 20, 10)
        
        # Play/Pause button on the left
        self.play_pause_btn = self._create_standard_button("⏯", (50, 50))
        self.play_pause_btn.clicked.connect(self._on_play_pause_pressed)
        media_layout.addWidget(self.play_pause_btn)
        
        # Add stretch to push volume pill to the right
        media_layout.addStretch()
        
        # Create Apple TV style volume pill (vertical arrangement)
        volume_pill_container = self._create_volume_pill()
        media_layout.addWidget(volume_pill_container)
        
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
        
        # Remove custom light styling - let the global dark theme apply
        return button
    
    def _create_volume_pill(self):
        """Create PERMANENT Apple TV style volume pill that NEVER loses its shape"""
        print("🎛️ Creating permanent volume pill container...")
        
        # Create permanent pill frame that maintains shape ALWAYS
        pill_frame = QFrame()
        pill_frame.setFixedSize(70, 90)  # Fixed size pill container
        pill_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 3px solid #555555;
                border-radius: 35px;  /* Perfect pill shape */
            }
        """)
        
        # Internal layout for buttons
        pill_layout = QVBoxLayout(pill_frame)
        pill_layout.setSpacing(0)  # No gap between buttons
        pill_layout.setContentsMargins(3, 3, 3, 3)  # Small margin inside pill
        
        # Volume Up (top half of pill) - NO BORDER
        self.volume_up_btn = QPushButton("🔊")
        self.volume_up_btn.setFixedSize(60, 40)
        self.volume_up_btn.clicked.connect(self._on_volume_up_pressed)
        
        # Volume Down (bottom half of pill) - NO BORDER
        self.volume_down_btn = QPushButton("🔉")
        self.volume_down_btn.setFixedSize(60, 40)
        self.volume_down_btn.clicked.connect(self._on_volume_down_pressed)
        
        # Button styling that fits INSIDE the pill frame
        volume_button_style = """
            QPushButton {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2a2a2a,
                    stop: 1 #1a1a1a
                );
                border: none;  /* NO BORDER - pill frame provides the border */
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3a3a3a,
                    stop: 1 #2a2a2a
                );
            }
            QPushButton:pressed {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1a1a1a,
                    stop: 1 #0a0a0a
                );
            }
        """
        
        # Apply rounded corners ONLY to top and bottom buttons
        self.volume_up_btn.setStyleSheet(volume_button_style + """
            QPushButton {
                border-top-left-radius: 30px;
                border-top-right-radius: 30px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)
        
        self.volume_down_btn.setStyleSheet(volume_button_style + """
            QPushButton {
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 30px;
                border-bottom-right-radius: 30px;
            }
        """)
        
        pill_layout.addWidget(self.volume_up_btn)
        pill_layout.addWidget(self.volume_down_btn)
        
        print("✅ Permanent volume pill created - shape will NEVER change!")
        return pill_frame
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts with GUARANTEED visual feedback"""
        from PyQt6.QtGui import QShortcut, QKeySequence
        
        print("🔧 Setting up keyboard shortcuts with visual feedback...")
        
        # Store original styles for animation reset
        self.original_styles = {}
        for button in [self.up_btn, self.down_btn, self.left_btn, self.right_btn, 
                      self.select_btn, self.play_pause_btn, self.menu_btn, 
                      self.home_btn, self.volume_up_btn, self.volume_down_btn]:
            self.original_styles[button] = button.styleSheet()
        
        # Arrow keys for navigation - with GUARANTEED visual feedback
        QShortcut(QKeySequence(Qt.Key.Key_Up), self, lambda: self._guaranteed_keyboard_animation(self.up_btn, self.up_pressed))
        QShortcut(QKeySequence(Qt.Key.Key_Down), self, lambda: self._guaranteed_keyboard_animation(self.down_btn, self.down_pressed))
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, lambda: self._guaranteed_keyboard_animation(self.left_btn, self.left_pressed))
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, lambda: self._guaranteed_keyboard_animation(self.right_btn, self.right_pressed))
        
        # Enter/Return for select - with GUARANTEED visual feedback
        QShortcut(QKeySequence(Qt.Key.Key_Return), self, lambda: self._guaranteed_keyboard_animation(self.select_btn, self.select_pressed))
        QShortcut(QKeySequence(Qt.Key.Key_Enter), self, lambda: self._guaranteed_keyboard_animation(self.select_btn, self.select_pressed))
        
        # Space for play/pause - with GUARANTEED visual feedback
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, lambda: self._guaranteed_keyboard_animation(self.play_pause_btn, self.play_pause_pressed))
        
        # M for menu, H for home - with GUARANTEED visual feedback
        QShortcut(QKeySequence(Qt.Key.Key_M), self, lambda: self._guaranteed_keyboard_animation(self.menu_btn, self.menu_pressed))
        QShortcut(QKeySequence(Qt.Key.Key_H), self, lambda: self._guaranteed_keyboard_animation(self.home_btn, self.home_pressed))
        
        # Plus/Minus for volume - with GUARANTEED visual feedback
        QShortcut(QKeySequence(Qt.Key.Key_Plus), self, lambda: self._guaranteed_keyboard_animation(self.volume_up_btn, self.volume_up_pressed))
        QShortcut(QKeySequence(Qt.Key.Key_Minus), self, lambda: self._guaranteed_keyboard_animation(self.volume_down_btn, self.volume_down_pressed))
        
        print(f"✅ Registered {10} keyboard shortcuts with visual feedback")
    
    def _guaranteed_keyboard_animation(self, button, signal):
        """GUARANTEED visual feedback for keyboard shortcuts"""
        print(f"🎯 Keyboard shortcut triggered for button: {button.text()}")
        
        # Apply immediate visual feedback - this WILL work
        pressed_style = """
            QPushButton {
                background-color: #ff6600 !important;
                border: 3px solid #ffaa00 !important;
                border-radius: 8px !important;
                color: #ffffff !important;
                font-weight: bold !important;
            }
        """
        
        # Apply pressed style immediately
        original_style = self.original_styles.get(button, "")
        button.setStyleSheet(pressed_style)
        print(f"✅ Applied pressed style to {button.text()}")
        
        # Emit the signal for functionality
        signal.emit()
        
        # Reset style after delay using QTimer (more reliable than animation)
        def reset_style():
            button.setStyleSheet(original_style)
            print(f"🔄 Reset style for {button.text()}")
        
        QTimer.singleShot(200, reset_style)
    
    def _handle_keyboard_with_animation(self, button, action_method):
        """Handle keyboard press with visual button animation - DEPRECATED"""
        # This method is now deprecated in favor of _guaranteed_keyboard_animation
        self._guaranteed_keyboard_animation(button, None)
        
        # Execute the original action method without calling it again
        # Since action_method already includes the animation, we need to call the signal emission directly
        if button == self.up_btn:
            self.up_pressed.emit()
        elif button == self.down_btn:
            self.down_pressed.emit()
        elif button == self.left_btn:
            self.left_pressed.emit()
        elif button == self.right_btn:
            self.right_pressed.emit()
        elif button == self.select_btn:
            self.select_pressed.emit()
        elif button == self.play_pause_btn:
            self.play_pause_pressed.emit()
        elif button == self.menu_btn:
            self.menu_pressed.emit()
        elif button == self.home_btn:
            self.home_pressed.emit()
        elif button == self.volume_up_btn:
            self.volume_up_pressed.emit()
        elif button == self.volume_down_btn:
            self.volume_down_pressed.emit()
    
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
        
        # Store last known good splitter sizes for layout recovery
        self._last_splitter_sizes = [400, 400, 400]
        self._default_splitter_sizes = [400, 400, 400]
        
        try:
            self._setup_ui()
            self._apply_consistent_styling()
            self._apply_dark_oled_theme()
            self._setup_responsive_behavior()
            self._setup_error_handling()
            
            # Critical: Force initial layout check AFTER panels are created
            QTimer.singleShot(100, self._force_initial_layout)
        except Exception as e:
            print(f"❌ Main window initialization error: {e}")
            # Try to continue with minimal setup
            self._setup_minimal_ui()
    
    def _setup_error_handling(self):
        """Setup comprehensive error handling"""
        # Handle resize events safely
        self.resizeEvent = self._safe_resize_event
    
    def _safe_resize_event(self, event):
        """Safe resize event handler"""
        try:
            super().resizeEvent(event)
        except Exception as e:
            print(f"⚠️ Resize error handled safely: {e}")
    
    def _apply_consistent_styling(self):
        """Apply consistent styling regardless of launch method"""
        # Force black borders and consistent appearance always
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
                border: 2px solid #000000;
                color: #ffffff;
            }
            QWidget {
                background-color: #000000;
                color: #ffffff;
            }
        """)
        
        # Force style update
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
    
    def _setup_minimal_ui(self):
        """Setup minimal UI in case of errors"""
        try:
            self.setWindowTitle("ApplerGUI - Apple TV Remote Control")
            self.setMinimumSize(700, 500)
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            layout.addWidget(QLabel("ApplerGUI - Error Recovery Mode"))
        except Exception as e:
            print(f"❌ Even minimal UI setup failed: {e}")
    
    def _setup_ui(self):
        """Setup main window UI with backend integration"""
        self.setWindowTitle("ApplerGUI - Apple TV Remote Control")
        self.setMinimumSize(700, 500)
        self.resize(1200, 800)
        
        # Set up application logo/icon
        self._setup_application_logo()
        
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
    
    def _setup_application_logo(self):
        """Setup application logo integration"""
        from PyQt6.QtGui import QIcon
        import os
        
        # Set window icon using the existing app icon
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'app_icon.png')
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
            
            # Also set for the application instance
            app = QApplication.instance()
            if app:
                app.setWindowIcon(app_icon)
            
            print(f"✅ Application logo loaded from: {icon_path}")
        else:
            print(f"⚠️ Application icon not found at: {icon_path}")
    
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
    
    @qasync.asyncSlot()
    async def _send_menu_command(self):
        """Send menu command to connected device"""
        await self._send_remote_command("menu")
    
    @qasync.asyncSlot()
    async def _send_home_command(self):
        """Send home command to connected device"""
        await self._send_remote_command("home")
    
    @qasync.asyncSlot()
    async def _send_select_command(self):
        """Send select command to connected device"""
        await self._send_remote_command("select")
    
    @qasync.asyncSlot()
    async def _send_up_command(self):
        """Send up command to connected device"""
        await self._send_remote_command("up")
    
    @qasync.asyncSlot()
    async def _send_down_command(self):
        """Send down command to connected device"""
        await self._send_remote_command("down")
    
    @qasync.asyncSlot()
    async def _send_left_command(self):
        """Send left command to connected device"""
        await self._send_remote_command("left")
    
    @qasync.asyncSlot()
    async def _send_right_command(self):
        """Send right command to connected device"""
        await self._send_remote_command("right")
    
    @qasync.asyncSlot()
    async def _send_play_pause_command(self):
        """Send play/pause command to connected device"""
        await self._send_remote_command("play_pause")
    
    @qasync.asyncSlot()
    async def _send_volume_up_command(self):
        """Send volume up command to connected device"""
        await self._send_remote_command("volume_up")
    
    @qasync.asyncSlot()
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
    
    def _apply_dark_oled_theme(self):
        """Apply UNIVERSAL dark OLED theme with CONSISTENT borders regardless of launch method"""
        print("🎨 Applying universal dark OLED theme...")
        
        # Get absolute path for any potential resource references
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Force environment-independent styling
        universal_dark_style = f"""
        /* UNIVERSAL MAIN WINDOW - ALWAYS BLACK BORDER */
        QMainWindow {{
            background-color: #000000;
            color: #ffffff;
            border: 2px solid #000000 !important;  /* FORCE BLACK border */
        }}
        
        /* UNIVERSAL WIDGET BASE */
        QWidget {{
            background-color: #000000;
            color: #ffffff;
        }}
        
        /* UNIVERSAL FRAME STYLING */
        QFrame {{
            background-color: #000000;
            border: 1px solid #000000 !important;  /* FORCE BLACK frames */
            border-radius: 8px;
        }}
        
        /* UNIVERSAL BUTTON STYLING */
        QPushButton {{
            background-color: qlineargradient(
                x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #2a2a2a,
                stop: 1 #1a1a1a
            );
            border: 1px solid #000000 !important;  /* FORCE BLACK border */
            border-radius: 8px;
            color: #ffffff !important;
            font-weight: bold;
            padding: 8px;
            min-height: 20px;
        }}
        QPushButton:hover {{
            background-color: qlineargradient(
                x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #3a3a3a,
                stop: 1 #2a2a2a
            );
            border-color: #000000 !important;  /* FORCE BLACK border */
        }}
        QPushButton:pressed {{
            background-color: qlineargradient(
                x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #1a1a1a,
                stop: 1 #0a0a0a
            );
            border-color: #000000 !important;  /* FORCE BLACK border */
        }}
        QPushButton:disabled {{
            background-color: #1a1a1a;
            color: #666666;
            border-color: #000000 !important;  /* FORCE BLACK border */
        }}
        
        /* UNIVERSAL LABEL STYLING */
        QLabel {{
            color: #ffffff !important;
            background: transparent;
        }}
        
        /* UNIVERSAL GROUP BOX STYLING */
        QGroupBox {{
            color: #ffffff !important;
            border: 1px solid #000000 !important;  /* FORCE BLACK border */
            border-radius: 6px;
            margin-top: 10px;
            background-color: #0a0a0a;
            font-weight: bold;
        }}
        QGroupBox::title {{
            color: #ffffff !important;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}
        
        /* UNIVERSAL TABLE STYLING */
        QTableWidget {{
            background-color: #000000;
            color: #ffffff !important;
            border: 1px solid #000000 !important;  /* FORCE BLACK border */
            selection-background-color: #444444;
            alternate-background-color: #0a0a0a;
            gridline-color: #000000 !important;  /* FORCE BLACK gridlines */
        }}
        QTableWidget::item {{
            border-bottom: 1px solid #000000 !important;  /* FORCE BLACK border */
            padding: 5px;
            color: #ffffff !important;
        }}
        QTableWidget::item:selected {{
            background-color: #444444;
            color: #ffffff !important;
        }}
        QHeaderView::section {{
            background-color: #222222;
            color: #ffffff !important;
            border: 1px solid #000000 !important;  /* FORCE BLACK border */
            padding: 5px;
            font-weight: bold;
        }}
        
        /* UNIVERSAL PROGRESS BAR STYLING */
        QProgressBar {{
            border: 1px solid #000000 !important;  /* FORCE BLACK border */
            border-radius: 3px;
            background-color: #000000;
            color: #ffffff !important;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: #007acc;
            border-radius: 2px;
        }}
        
        /* UNIVERSAL TAB STYLING */
        QTabWidget::pane {{
            border: 1px solid #000000 !important;  /* FORCE BLACK border */
            background-color: #000000;
        }}
        QTabBar::tab {{
            background-color: #222222;
            color: #ffffff !important;
            border: 1px solid #000000 !important;  /* FORCE BLACK border */
            padding: 8px 16px;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background-color: #007acc;
            border-bottom-color: #007acc;
        }}
        QTabBar::tab:hover {{
            background-color: #333333;
        }}
        
        /* UNIVERSAL SLIDER STYLING */
        QSlider::groove:horizontal {{
            border: 1px solid #000000 !important;  /* FORCE BLACK border */
            height: 4px;
            background-color: #222222;
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background-color: #007acc;
            border: 1px solid #000000 !important;  /* FORCE BLACK border */
            width: 16px;
            border-radius: 8px;
            margin: -6px 0;
        }}
        QSlider::handle:horizontal:hover {{
            background-color: #0099ff;
        }}
        
        /* UNIVERSAL SPLITTER STYLING */
        QSplitter::handle {{
            background-color: #000000 !important;  /* FORCE BLACK handle */
        }}
        QSplitter::handle:horizontal {{
            width: 3px;
        }}
        QSplitter::handle:vertical {{
            height: 3px;
        }}
        
        /* UNIVERSAL LINE EDIT STYLING */
        QLineEdit {{
            background-color: #222222;
            border: 1px solid #000000 !important;  /* FORCE BLACK border */
            border-radius: 4px;
            color: #ffffff !important;
            padding: 5px;
        }}
        QLineEdit:focus {{
            border-color: #007acc !important;
        }}
        
        /* UNIVERSAL STATUS BAR STYLING */
        QStatusBar {{
            background-color: #000000;
            color: #ffffff !important;
            border-top: 1px solid #000000 !important;  /* FORCE BLACK border */
        }}
        
        /* UNIVERSAL MENU STYLING */
        QMenuBar {{
            background-color: #222222;
            color: #ffffff !important;
            border-bottom: 1px solid #000000 !important;  /* FORCE BLACK border */
        }}
        QMenuBar::item {{
            background-color: transparent;
            padding: 5px 10px;
            color: #ffffff !important;
        }}
        QMenuBar::item:selected {{
            background-color: #333333;
        }}
        QMenu {{
            background-color: #222222;
            color: #ffffff !important;
            border: 1px solid #000000 !important;  /* FORCE BLACK border */
        }}
        QMenu::item {{
            padding: 5px 20px;
            color: #ffffff !important;
        }}
        QMenu::item:selected {{
            background-color: #333333;
        }}
        
        /* CIRCULAR BUTTON SPECIFIC STYLING */
        CircularButton {{
            border: 2px solid #555555 !important;
            border-radius: 25px;
            background-color: qlineargradient(
                x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #404040,
                stop: 1 #202020
            );
            color: #ffffff !important;
            font-weight: bold;
            font-size: 12px;
        }}
        CircularButton:hover {{
            background-color: qlineargradient(
                x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #505050,
                stop: 1 #303030
            );
            border-color: #777777 !important;
        }}
        CircularButton:pressed {{
            background-color: qlineargradient(
                x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #202020,
                stop: 1 #101010
            );
            border-color: #999999 !important;
        }}
        CircularButton:disabled {{
            background-color: #2a2a2a;
            color: #666666;
            border-color: #444444 !important;
        }}
        """
        
        # Apply the universal styling
        self.setStyleSheet(universal_dark_style)
        
        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)
        
        print(f"✅ Universal dark OLED theme applied (launch method: {getattr(self, 'launch_method', 'unknown')})")
    
    def _setup_responsive_behavior(self):
        """Setup responsive window behavior"""
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._update_layout_mode)
    
    def resizeEvent(self, event):
        """Handle window resize for responsive layout with CRASH PROTECTION"""
        try:
            print(f"🔄 Resize event: {event.size().width()}x{event.size().height()}")
            super().resizeEvent(event)
            
            # Only proceed if resize timer exists and is not already running
            if hasattr(self, 'resize_timer') and self.resize_timer:
                # Stop any existing timer to prevent accumulation
                self.resize_timer.stop()
                self.resize_timer.start(150)  # Slightly longer debounce
            else:
                print("⚠️ Resize timer not available, skipping responsive layout")
                
        except Exception as resize_error:
            print(f"❌ Resize event error (safely handled): {resize_error}")
            # Continue execution - don't let resize errors crash the app
    
    def _update_layout_mode(self):
        """Update layout based on window size with CRASH PROTECTION"""
        try:
            current_width = self.width()
            should_be_compact = current_width < self.min_width_for_sections
            
            print(f"🔄 Layout check: width={current_width}, compact={should_be_compact}, current_mode={self.is_compact_mode}")
            
            if should_be_compact != self.is_compact_mode:
                print(f"🔄 Switching layout mode: {self.is_compact_mode} -> {should_be_compact}")
                self.is_compact_mode = should_be_compact
                self._switch_layout_mode()
                
        except Exception as layout_error:
            print(f"❌ Layout mode error (safely handled): {layout_error}")
            # Continue execution - don't let layout errors crash the app
    
    def _switch_layout_mode(self):
        """Switch between compact and expanded layout modes"""
        if self.is_compact_mode:
            # Store current splitter sizes before switching to compact mode
            current_sizes = self.splitter.sizes()
            if sum(current_sizes) > 0:  # Only store if sizes are valid
                self._last_splitter_sizes = current_sizes
            
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
        
        # CRITICAL: Restore last known good sizes or use defaults
        sizes_to_restore = self._last_splitter_sizes if sum(self._last_splitter_sizes) > 0 else self._default_splitter_sizes
        
        # Force layout update multiple times to ensure proper sizing
        def restore_sizes():
            self.splitter.setSizes(sizes_to_restore)
            print(f"Restored splitter sizes to: {sizes_to_restore}")
            print(f"Actual splitter sizes: {self.splitter.sizes()}")
        
        # Apply sizes immediately and again after a short delay
        restore_sizes()
        QTimer.singleShot(10, restore_sizes)
        QTimer.singleShot(50, restore_sizes)
        
        # Force widget updates
        self.splitter.update()
        for i in range(self.splitter.count()):
            widget = self.splitter.widget(i)
            if widget:
                widget.show()
                widget.update()
        
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