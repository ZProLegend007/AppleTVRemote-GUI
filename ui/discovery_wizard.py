import asyncio
import logging
import subprocess
import re
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QProgressBar, QTextEdit, QGroupBox, QLineEdit,
                             QMessageBox, QDialogButtonBox, QFrame)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPalette
from datetime import datetime

class AnimatedProgressBar(QProgressBar):
    """Custom progress bar with smooth animations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3498db,
                    stop: 1 #2980b9
                );
                border-radius: 6px;
            }
        """)
        
        # Animation for indeterminate progress
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(2000)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def start_animation(self):
        """Start smooth indeterminate animation"""
        self.setRange(0, 100)
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        self.animation.setLoopCount(-1)  # Infinite loop
        self.animation.start()
    
    def stop_animation(self):
        """Stop animation and hide"""
        self.animation.stop()
        self.setVisible(False)

class DeviceDiscoveryThread(QThread):
    """Thread for running atvremote scan command"""
    
    devices_found = pyqtSignal(list)  # List of discovered devices
    error_occurred = pyqtSignal(str)  # Error message
    progress_update = pyqtSignal(str)  # Progress message
    
    def run(self):
        """Run device discovery"""
        try:
            self.progress_update.emit("Initializing discovery...")
            
            # Run atvremote scan for device discovery (non-interactive)
            process = subprocess.Popen(
                ['atvremote', 'scan'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.progress_update.emit("Scanning network for Apple TV devices...")
            
            output, error = process.communicate(timeout=30)
            
            if process.returncode != 0:
                self.error_occurred.emit(f"Command failed: {error}")
                return
            
            self.progress_update.emit("Parsing discovered devices...")
            
            # Parse the output to extract device information
            devices = self._parse_scan_output(output)
            self.devices_found.emit(devices)
            
        except subprocess.TimeoutExpired:
            self.error_occurred.emit("Device discovery timed out after 30 seconds")
        except FileNotFoundError:
            self.error_occurred.emit("atvremote command not found. Please install pyatv:\npip install pyatv")
        except Exception as e:
            self.error_occurred.emit(f"Discovery failed: {str(e)}")
    
    def _parse_scan_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse atvremote scan output to extract device information"""
        devices = []
        
        # Look for device entries in the scan output
        lines = output.split('\n')
        current_device = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_device and 'name' in current_device:
                    devices.append(current_device)
                    current_device = {}
                continue
            
            if line.startswith('Name: '):
                current_device['name'] = line[6:].strip()
            elif line.startswith('Model: '):
                current_device['model'] = line[7:].strip()
            elif line.startswith('Address: '):
                current_device['address'] = line[9:].strip()
            elif line.startswith('Services: '):
                services_str = line[10:].strip()
                current_device['services'] = self._parse_services(services_str)
        
        # Add the last device if exists
        if current_device and 'name' in current_device:
            devices.append(current_device)
        
        return devices
    
    def _parse_services(self, services_str: str) -> List[str]:
        """Parse services string into list"""
        # Remove brackets and split by comma
        services_str = services_str.strip('[]')
        if not services_str:
            return []
        return [s.strip().strip("'\"") for s in services_str.split(',')]

class DevicePairingThread(QThread):
    """Thread for pairing with a specific device"""
    
    pairing_started = pyqtSignal(str)  # Device name
    pin_required = pyqtSignal(str, str)  # Service name, prompt
    pairing_progress = pyqtSignal(str)  # Progress message
    pairing_completed = pyqtSignal(dict)  # Device info
    pairing_failed = pyqtSignal(str)  # Error message
    
    def __init__(self, device_info: Dict[str, Any]):
        super().__init__()
        self.device_info = device_info
        self.pin_responses = {}
        self.waiting_for_pin = False
    
    def set_pin_response(self, service: str, pin: str):
        """Set PIN response for a service"""
        self.pin_responses[service] = pin
        self.waiting_for_pin = False
    
    def run(self):
        """Run device pairing process"""
        try:
            device_name = self.device_info['name']
            device_address = self.device_info['address']
            
            self.pairing_started.emit(device_name)
            
            # Check if device needs pairing
            services = self.device_info.get('services', [])
            pairing_services = [s for s in services if s.lower() in ['companion', 'airplay', 'raop']]
            
            if not pairing_services:
                self.pairing_progress.emit("No pairing required for this device")
            else:
                for service in pairing_services:
                    self._pair_service(device_address, service)
            
            # Test connection after pairing
            self.pairing_progress.emit("Testing connection...")
            if self._test_connection(device_address):
                self.pairing_completed.emit(self.device_info)
            else:
                self.pairing_failed.emit("Connection test failed")
                
        except Exception as e:
            self.pairing_failed.emit(f"Pairing failed: {str(e)}")
    
    def _pair_service(self, address: str, service: str):
        """Pair with a specific service"""
        try:
            self.pairing_progress.emit(f"Pairing {service} protocol...")
            
            # Run pairing command
            process = subprocess.Popen(
                ['atvremote', '--address', address, 'pair', '--protocol', service.lower()],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check if PIN entry is needed
            if service.lower() in ['companion', 'airplay'] and service not in self.pin_responses:
                self.pin_required.emit(service, f"Enter PIN displayed on {self.device_info['name']} for {service}")
                self.waiting_for_pin = True
                
                # Wait for PIN response
                while self.waiting_for_pin:
                    self.msleep(100)
            
            # Provide PIN if available
            if service in self.pin_responses:
                pin = self.pin_responses[service]
                process.stdin.write(f"{pin}\n")
                process.stdin.flush()
            
            output, error = process.communicate(timeout=60)
            
            if process.returncode != 0:
                if "already paired" not in error.lower() and "credentials already exists" not in error.lower():
                    raise Exception(f"{service} pairing failed: {error}")
                else:
                    self.pairing_progress.emit(f"{service} already paired")
            else:
                self.pairing_progress.emit(f"{service} pairing completed")
            
        except subprocess.TimeoutExpired:
            raise Exception(f"{service} pairing timed out")
    
    def _test_connection(self, address: str) -> bool:
        """Test connection to device"""
        try:
            process = subprocess.run(
                ['atvremote', '--address', address, 'playing'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return process.returncode == 0
        except:
            return False

class DiscoveryWizard(QDialog):
    """Apple TV Discovery and Pairing Wizard with Animations"""
    
    device_paired = pyqtSignal(dict)  # Device info
    discovery_finished = pyqtSignal()  # Discovery completed
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.discovered_devices = []
        self.selected_device = None
        self.pairing_thread = None
        
        self._setup_ui()
        self._setup_animations()
        self._start_discovery()
    
    def _setup_ui(self):
        """Setup the wizard UI with modern styling"""
        self.setWindowTitle("🍎 Apple TV Discovery & Pairing Wizard")
        self.setModal(True)
        self.resize(900, 700)
        
        # Modern styling
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8f9fa,
                    stop: 1 #e9ecef
                );
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: rgba(255, 255, 255, 0.8);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #495057;
            }
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #007bff,
                    stop: 1 #0056b3
                );
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0056b3,
                    stop: 1 #004085
                );
            }
            QPushButton:pressed {
                background: #004085;
            }
            QPushButton:disabled {
                background: #6c757d;
            }
            QTableWidget {
                gridline-color: #dee2e6;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ced4da;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header with animation
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        
        self.header_label = QLabel("🍎 Apple TV Discovery & Pairing")
        self.header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setStyleSheet("color: #495057; margin: 10px;")
        header_layout.addWidget(self.header_label)
        
        self.subtitle_label = QLabel("Discover and pair with Apple TV devices on your network")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("color: #6c757d; font-size: 14px; margin-bottom: 10px;")
        header_layout.addWidget(self.subtitle_label)
        
        layout.addWidget(header_frame)
        
        # Discovery section
        discovery_group = QGroupBox("🔍 Device Discovery")
        discovery_layout = QVBoxLayout(discovery_group)
        
        self.progress_bar = AnimatedProgressBar()
        discovery_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Initializing discovery...")
        self.status_label.setStyleSheet("color: #495057; font-weight: normal; padding: 5px;")
        discovery_layout.addWidget(self.status_label)
        
        layout.addWidget(discovery_group)
        
        # Device list section
        devices_group = QGroupBox("📱 Discovered Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(3)
        self.devices_table.setHorizontalHeaderLabels(["Device Name", "Model", "IP Address"])
        self.devices_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.devices_table.setAlternatingRowColors(True)
        self.devices_table.itemSelectionChanged.connect(self._on_device_selected)
        devices_layout.addWidget(self.devices_table)
        
        layout.addWidget(devices_group)
        
        # Pairing section
        self.pairing_group = QGroupBox("🔗 Device Pairing")
        self.pairing_group.setVisible(False)
        pairing_layout = QVBoxLayout(self.pairing_group)
        
        self.pairing_status = QLabel("Select a device to begin pairing")
        self.pairing_status.setStyleSheet("color: #495057; font-weight: normal; padding: 5px;")
        pairing_layout.addWidget(self.pairing_status)
        
        self.pairing_progress = AnimatedProgressBar()
        self.pairing_progress.setVisible(False)
        pairing_layout.addWidget(self.pairing_progress)
        
        # PIN entry section
        self.pin_group = QGroupBox("🔐 PIN Entry")
        self.pin_group.setVisible(False)
        pin_layout = QVBoxLayout(self.pin_group)
        
        self.pin_label = QLabel("Enter PIN shown on device:")
        self.pin_label.setStyleSheet("color: #495057; font-weight: bold; margin: 5px;")
        pin_layout.addWidget(self.pin_label)
        
        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("Enter 4-digit PIN from Apple TV screen")
        self.pin_input.setMaxLength(4)
        self.pin_input.returnPressed.connect(self._submit_pin)
        pin_layout.addWidget(self.pin_input)
        
        pin_button_layout = QHBoxLayout()
        self.submit_pin_btn = QPushButton("✓ Submit PIN")
        self.submit_pin_btn.clicked.connect(self._submit_pin)
        self.skip_pin_btn = QPushButton("⏭ Skip")
        self.skip_pin_btn.clicked.connect(self._skip_pin)
        
        pin_button_layout.addWidget(self.submit_pin_btn)
        pin_button_layout.addWidget(self.skip_pin_btn)
        pin_layout.addLayout(pin_button_layout)
        
        pairing_layout.addWidget(self.pin_group)
        layout.addWidget(self.pairing_group)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self._refresh_discovery)
        button_layout.addWidget(self.refresh_btn)
        
        self.pair_btn = QPushButton("📱 Pair Device")
        self.pair_btn.setEnabled(False)
        self.pair_btn.clicked.connect(self._start_pairing)
        button_layout.addWidget(self.pair_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("✕ Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def _setup_animations(self):
        """Setup UI animations"""
        # Fade in animation for main dialog
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Start fade in
        self.setWindowOpacity(0.0)
        self.fade_animation.start()
    
    def _start_discovery(self):
        """Start device discovery with animation"""
        self.progress_bar.setVisible(True)
        self.progress_bar.start_animation()
        self.status_label.setText("Scanning network for Apple TV devices...")
        self.refresh_btn.setEnabled(False)
        
        # Start discovery thread
        self.discovery_thread = DeviceDiscoveryThread()
        self.discovery_thread.devices_found.connect(self._on_devices_found)
        self.discovery_thread.error_occurred.connect(self._on_discovery_error)
        self.discovery_thread.progress_update.connect(self._on_discovery_progress)
        self.discovery_thread.start()
    
    def _on_discovery_progress(self, message: str):
        """Handle discovery progress updates"""
        self.status_label.setText(message)
    
    def _on_devices_found(self, devices: List[Dict[str, Any]]):
        """Handle discovered devices with animation"""
        self.discovered_devices = devices
        self.progress_bar.stop_animation()
        self.refresh_btn.setEnabled(True)
        
        if not devices:
            self.status_label.setText("❌ No Apple TV devices found on network")
            return
        
        self.status_label.setText(f"✅ Found {len(devices)} Apple TV device(s)")
        
        # Populate table with animation
        self.devices_table.setRowCount(len(devices))
        for row, device in enumerate(devices):
            # Add items with slight delay for animation effect
            QTimer.singleShot(row * 100, lambda r=row, d=device: self._add_device_row(r, d))
        
        self.devices_table.resizeColumnsToContents()
    
    def _add_device_row(self, row: int, device: Dict[str, Any]):
        """Add device row with animation"""
        name_item = QTableWidgetItem(device.get('name', 'Unknown Device'))
        model_item = QTableWidgetItem(device.get('model', 'Unknown Model'))
        address_item = QTableWidgetItem(device.get('address', 'Unknown Address'))
        
        # Style items
        for item in [name_item, model_item, address_item]:
            item.setFont(QFont("Arial", 10))
        
        self.devices_table.setItem(row, 0, name_item)
        self.devices_table.setItem(row, 1, model_item)
        self.devices_table.setItem(row, 2, address_item)
    
    def _on_discovery_error(self, error: str):
        """Handle discovery error"""
        self.progress_bar.stop_animation()
        self.refresh_btn.setEnabled(True)
        self.status_label.setText(f"❌ Discovery failed: {error}")
        
        QMessageBox.warning(self, "Discovery Error", 
                           f"Failed to discover devices:\n\n{error}")
    
    def _on_device_selected(self):
        """Handle device selection with animation"""
        selected_rows = self.devices_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_device = self.discovered_devices[row]
            self.pair_btn.setEnabled(True)
            
            # Animate pairing group appearance
            self.pairing_group.setVisible(True)
            self.pairing_status.setText(f"Ready to pair with '{self.selected_device['name']}'")
            
            # Slide in animation
            self._animate_widget_show(self.pairing_group)
        else:
            self.selected_device = None
            self.pair_btn.setEnabled(False)
            self.pairing_group.setVisible(False)
    
    def _animate_widget_show(self, widget):
        """Animate widget appearance"""
        widget.setMaximumHeight(0)
        
        self.show_animation = QPropertyAnimation(widget, b"maximumHeight")
        self.show_animation.setDuration(300)
        self.show_animation.setStartValue(0)
        self.show_animation.setEndValue(200)
        self.show_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.show_animation.start()
    
    def _refresh_discovery(self):
        """Refresh device discovery"""
        self.devices_table.setRowCount(0)
        self.discovered_devices = []
        self.selected_device = None
        self.pair_btn.setEnabled(False)
        self.pairing_group.setVisible(False)
        self.pin_group.setVisible(False)
        self._start_discovery()
    
    def _start_pairing(self):
        """Start device pairing process"""
        if not self.selected_device:
            return
        
        self.pair_btn.setEnabled(False)
        self.pairing_progress.setVisible(True)
        self.pairing_progress.start_animation()
        
        # Start pairing thread
        self.pairing_thread = DevicePairingThread(self.selected_device)
        self.pairing_thread.pairing_started.connect(self._on_pairing_started)
        self.pairing_thread.pin_required.connect(self._on_pin_required)
        self.pairing_thread.pairing_progress.connect(self._on_pairing_progress)
        self.pairing_thread.pairing_completed.connect(self._on_pairing_completed)
        self.pairing_thread.pairing_failed.connect(self._on_pairing_failed)
        self.pairing_thread.start()
    
    def _on_pairing_started(self, device_name: str):
        """Handle pairing start"""
        self.pairing_status.setText(f"🔄 Initiating pairing with '{device_name}'...")
    
    def _on_pin_required(self, service: str, prompt: str):
        """Handle PIN requirement with animation"""
        self.pin_group.setVisible(True)
        self.pin_label.setText(f"🔐 Enter PIN for {service} protocol:\n{prompt}")
        self.pin_input.clear()
        self.pin_input.setFocus()
        self.current_service = service
        
        # Animate PIN group
        self._animate_widget_show(self.pin_group)
    
    def _on_pairing_progress(self, message: str):
        """Handle pairing progress"""
        self.pairing_status.setText(f"🔄 {message}")
    
    def _on_pairing_completed(self, device_info: Dict[str, Any]):
        """Handle successful pairing with celebration animation"""
        self.pairing_progress.stop_animation()
        self.pin_group.setVisible(False)
        self.pairing_status.setText(f"✅ Successfully paired with '{device_info['name']}'!")
        
        # Add timestamp
        device_info['paired_at'] = datetime.now().isoformat()
        
        # Emit signal
        self.device_paired.emit(device_info)
        
        # Show success message
        QMessageBox.information(self, "🎉 Pairing Successful!",
                               f"Successfully paired with '{device_info['name']}'!\n\n"
                               f"The device is now available for control in ApplerGUI.")
        
        # Fade out and close
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.accept)
        self.fade_animation.start()
    
    def _on_pairing_failed(self, error: str):
        """Handle pairing failure"""
        self.pairing_progress.stop_animation()
        self.pin_group.setVisible(False)
        self.pair_btn.setEnabled(True)
        self.pairing_status.setText(f"❌ Pairing failed: {error}")
        
        QMessageBox.warning(self, "Pairing Failed",
                           f"Failed to pair with device:\n\n{error}\n\n"
                           f"Please check that the device is on the same network "
                           f"and try again.")
    
    def _submit_pin(self):
        """Submit PIN for pairing"""
        pin = self.pin_input.text().strip()
        if len(pin) == 4 and pin.isdigit():
            if self.pairing_thread:
                self.pairing_thread.set_pin_response(self.current_service, pin)
            self.pin_group.setVisible(False)
        else:
            QMessageBox.warning(self, "Invalid PIN", 
                               "Please enter a valid 4-digit PIN displayed on your Apple TV.")
            self.pin_input.clear()
            self.pin_input.setFocus()
    
    def _skip_pin(self):
        """Skip PIN entry"""
        self.pin_group.setVisible(False)
        # Continue with pairing process without PIN
    
    def closeEvent(self, event):
        """Handle dialog close"""
        # Stop any running threads
        if hasattr(self, 'discovery_thread') and self.discovery_thread.isRunning():
            self.discovery_thread.terminate()
            self.discovery_thread.wait()
        
        if self.pairing_thread and self.pairing_thread.isRunning():
            self.pairing_thread.terminate()
            self.pairing_thread.wait()
        
        event.accept()