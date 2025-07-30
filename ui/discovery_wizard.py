import asyncio
import logging
import subprocess
import re
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QProgressBar, QTextEdit, QGroupBox, QLineEdit,
                             QMessageBox, QDialogButtonBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont
from datetime import datetime

class DeviceDiscoveryThread(QThread):
    """Thread for running atvremote scan command"""
    
    devices_found = pyqtSignal(list)  # List of discovered devices
    error_occurred = pyqtSignal(str)  # Error message
    output_received = pyqtSignal(str)  # Raw command output
    
    def run(self):
        """Run device discovery"""
        try:
            # Run atvremote scan for device discovery (non-interactive)
            process = subprocess.Popen(
                ['atvremote', 'scan'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            output, error = process.communicate(timeout=30)
            
            if process.returncode != 0:
                self.error_occurred.emit(f"Command failed: {error}")
                return
            
            # Parse the output to extract device information
            devices = self._parse_scan_output(output)
            self.devices_found.emit(devices)
            
        except subprocess.TimeoutExpired:
            self.error_occurred.emit("Device discovery timed out")
        except FileNotFoundError:
            self.error_occurred.emit("atvremote command not found. Please install pyatv.")
        except Exception as e:
            self.error_occurred.emit(f"Discovery failed: {str(e)}")
    
    def _parse_scan_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse atvremote scan output to extract device information"""
        devices = []
        
        # Look for device entries in the format:
        # Name: Device Name
        # Model: Device Model  
        # Address: IP Address
        # Services: [list of services]
        
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
    
    def set_pin_response(self, service: str, pin: str):
        """Set PIN response for a service"""
        self.pin_responses[service] = pin
    
    def run(self):
        """Run device pairing process"""
        try:
            device_name = self.device_info['name']
            device_address = self.device_info['address']
            
            self.pairing_started.emit(device_name)
            
            # Use atvremote pair command for each service
            services = self.device_info.get('services', [])
            
            for service in services:
                if service.lower() in ['companion', 'airplay', 'raop']:
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
            self.pairing_progress.emit(f"Pairing {service}...")
            
            # Run pairing command
            process = subprocess.Popen(
                ['atvremote', '--address', address, 'pair', '--protocol', service.lower()],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # If PIN is required, provide it
            if service in self.pin_responses:
                pin = self.pin_responses[service]
                process.stdin.write(f"{pin}\n")
                process.stdin.flush()
            
            output, error = process.communicate(timeout=60)
            
            if process.returncode != 0:
                if "already paired" not in error.lower():
                    raise Exception(f"{service} pairing failed: {error}")
            
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
    """Apple TV Discovery and Pairing Wizard"""
    
    device_paired = pyqtSignal(dict)  # Device info
    discovery_finished = pyqtSignal()  # Discovery completed
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.discovered_devices = []
        self.selected_device = None
        
        self._setup_ui()
        self._start_discovery()
    
    def _setup_ui(self):
        """Setup the wizard UI"""
        self.setWindowTitle("Apple TV Discovery & Pairing Wizard")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("🍎 Apple TV Discovery & Pairing")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Discovery section
        discovery_group = QGroupBox("Device Discovery")
        discovery_layout = QVBoxLayout(discovery_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        discovery_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Scanning for Apple TV devices...")
        discovery_layout.addWidget(self.status_label)
        
        layout.addWidget(discovery_group)
        
        # Device list section
        devices_group = QGroupBox("Discovered Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(3)
        self.devices_table.setHorizontalHeaderLabels(["Name", "Model", "Address"])
        self.devices_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.devices_table.itemSelectionChanged.connect(self._on_device_selected)
        devices_layout.addWidget(self.devices_table)
        
        layout.addWidget(devices_group)
        
        # Pairing section
        self.pairing_group = QGroupBox("Device Pairing")
        self.pairing_group.setVisible(False)
        pairing_layout = QVBoxLayout(self.pairing_group)
        
        self.pairing_status = QLabel("Select a device to pair")
        pairing_layout.addWidget(self.pairing_status)
        
        self.pairing_progress = QProgressBar()
        self.pairing_progress.setVisible(False)
        pairing_layout.addWidget(self.pairing_progress)
        
        # PIN entry section
        self.pin_group = QGroupBox("PIN Entry")
        self.pin_group.setVisible(False)
        pin_layout = QVBoxLayout(self.pin_group)
        
        self.pin_label = QLabel("Enter PIN shown on device:")
        pin_layout.addWidget(self.pin_label)
        
        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("Enter 4-digit PIN")
        self.pin_input.returnPressed.connect(self._submit_pin)
        pin_layout.addWidget(self.pin_input)
        
        pin_button_layout = QHBoxLayout()
        self.submit_pin_btn = QPushButton("Submit PIN")
        self.submit_pin_btn.clicked.connect(self._submit_pin)
        self.skip_pin_btn = QPushButton("Skip")
        self.skip_pin_btn.clicked.connect(self._skip_pin)
        
        pin_button_layout.addWidget(self.submit_pin_btn)
        pin_button_layout.addWidget(self.skip_pin_btn)
        pin_layout.addLayout(pin_button_layout)
        
        self.pairing_group.addWidget(self.pin_group)
        layout.addWidget(self.pairing_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self._refresh_discovery)
        button_layout.addWidget(self.refresh_btn)
        
        self.pair_btn = QPushButton("📱 Pair Device")
        self.pair_btn.setEnabled(False)
        self.pair_btn.clicked.connect(self._start_pairing)
        button_layout.addWidget(self.pair_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def _start_discovery(self):
        """Start device discovery"""
        self.progress_bar.setVisible(True)
        self.status_label.setText("Scanning for Apple TV devices...")
        self.refresh_btn.setEnabled(False)
        
        # Start discovery thread
        self.discovery_thread = DeviceDiscoveryThread()
        self.discovery_thread.devices_found.connect(self._on_devices_found)
        self.discovery_thread.error_occurred.connect(self._on_discovery_error)
        self.discovery_thread.start()
    
    def _on_devices_found(self, devices: List[Dict[str, Any]]):
        """Handle discovered devices"""
        self.discovered_devices = devices
        self.progress_bar.setVisible(False)
        self.refresh_btn.setEnabled(True)
        
        if not devices:
            self.status_label.setText("No Apple TV devices found")
            return
        
        self.status_label.setText(f"Found {len(devices)} device(s)")
        
        # Populate table
        self.devices_table.setRowCount(len(devices))
        for row, device in enumerate(devices):
            self.devices_table.setItem(row, 0, QTableWidgetItem(device.get('name', 'Unknown')))
            self.devices_table.setItem(row, 1, QTableWidgetItem(device.get('model', 'Unknown')))
            self.devices_table.setItem(row, 2, QTableWidgetItem(device.get('address', 'Unknown')))
        
        self.devices_table.resizeColumnsToContents()
    
    def _on_discovery_error(self, error: str):
        """Handle discovery error"""
        self.progress_bar.setVisible(False)
        self.refresh_btn.setEnabled(True)
        self.status_label.setText(f"Discovery failed: {error}")
        
        QMessageBox.warning(self, "Discovery Error", 
                           f"Failed to discover devices:\n{error}")
    
    def _on_device_selected(self):
        """Handle device selection"""
        selected_rows = self.devices_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_device = self.discovered_devices[row]
            self.pair_btn.setEnabled(True)
            self.pairing_group.setVisible(True)
            self.pairing_status.setText(f"Ready to pair with {self.selected_device['name']}")
        else:
            self.selected_device = None
            self.pair_btn.setEnabled(False)
            self.pairing_group.setVisible(False)
    
    def _refresh_discovery(self):
        """Refresh device discovery"""
        self.devices_table.setRowCount(0)
        self.discovered_devices = []
        self.selected_device = None
        self.pair_btn.setEnabled(False)
        self.pairing_group.setVisible(False)
        self._start_discovery()
    
    def _start_pairing(self):
        """Start device pairing process"""
        if not self.selected_device:
            return
        
        self.pair_btn.setEnabled(False)
        self.pairing_progress.setVisible(True)
        self.pairing_progress.setRange(0, 0)  # Indeterminate
        
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
        self.pairing_status.setText(f"Starting pairing with {device_name}...")
    
    def _on_pin_required(self, service: str, prompt: str):
        """Handle PIN requirement"""
        self.pin_group.setVisible(True)
        self.pin_label.setText(f"Enter PIN for {service}:\n{prompt}")
        self.pin_input.clear()
        self.pin_input.setFocus()
        self.current_service = service
    
    def _on_pairing_progress(self, message: str):
        """Handle pairing progress"""
        self.pairing_status.setText(message)
    
    def _on_pairing_completed(self, device_info: Dict[str, Any]):
        """Handle successful pairing"""
        self.pairing_progress.setVisible(False)
        self.pin_group.setVisible(False)
        self.pairing_status.setText(f"✅ Successfully paired with {device_info['name']}!")
        
        # Add timestamp
        device_info['paired_at'] = datetime.now().isoformat()
        
        # Emit signal
        self.device_paired.emit(device_info)
        
        # Show success message
        QMessageBox.information(self, "Pairing Successful",
                               f"Successfully paired with {device_info['name']}!\n"
                               f"The device is now available for control.")
        
        self.accept()
    
    def _on_pairing_failed(self, error: str):
        """Handle pairing failure"""
        self.pairing_progress.setVisible(False)
        self.pin_group.setVisible(False)
        self.pair_btn.setEnabled(True)
        self.pairing_status.setText(f"❌ Pairing failed: {error}")
        
        QMessageBox.warning(self, "Pairing Failed",
                           f"Failed to pair with device:\n{error}")
    
    def _submit_pin(self):
        """Submit PIN for pairing"""
        pin = self.pin_input.text().strip()
        if len(pin) == 4 and pin.isdigit():
            self.pairing_thread.set_pin_response(self.current_service, pin)
            self.pin_group.setVisible(False)
        else:
            QMessageBox.warning(self, "Invalid PIN", "Please enter a 4-digit PIN.")
    
    def _skip_pin(self):
        """Skip PIN entry"""
        self.pin_group.setVisible(False)
        # Continue with pairing process