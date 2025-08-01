"""Device manager widget for discovering and managing Apple TV/HomePod devices."""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                            QListWidgetItem, QPushButton, QLabel, QGroupBox,
                            QProgressBar, QMessageBox, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QFont
import asyncio
import qasync
import logging

from ..backend.config_manager import ConfigManager
from ..backend.device_controller import DeviceController
from ..backend.pairing_manager import PairingManager

class DeviceListItem(QWidget):
    """Custom widget for device list items."""
    
    def __init__(self, device_info: dict, device_controller: DeviceController, 
                 pairing_manager: PairingManager):
        super().__init__()
        self.device_info = device_info
        self.device_controller = device_controller
        self.pairing_manager = pairing_manager
        
        # Safely get device ID with fallbacks
        self.device_id = device_info.get('id') or device_info.get('name') or 'unknown_device'
        
        self._setup_ui()
        self._update_connection_status()
        
        # Timer to update connection status
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_connection_status)
        self.status_timer.start(2000)  # Update every 2 seconds
    
    def _setup_ui(self):
        """Set up the device item UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)
        
        # Device name and model
        name_layout = QHBoxLayout()
        
        self.name_label = QLabel(self.device_info.get('name', 'Unknown Device'))
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(12)
        self.name_label.setFont(name_font)
        name_layout.addWidget(self.name_label)
        
        name_layout.addStretch()
        
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #666666; font-size: 10px;")
        name_layout.addWidget(self.status_label)
        
        layout.addLayout(name_layout)
        
        # Device details
        details_layout = QVBoxLayout()
        
        model_label = QLabel(f"Model: {self.device_info.get('model', 'Unknown')}")
        model_label.setStyleSheet("color: #888888; font-size: 10px;")
        details_layout.addWidget(model_label)
        
        address_label = QLabel(f"Address: {self.device_info.get('address', 'Unknown')}")
        address_label.setStyleSheet("color: #888888; font-size: 10px;")
        details_layout.addWidget(address_label)
        
        # Services
        services = self.device_info.get('services', [])
        services_text = ", ".join([s.get('protocol', 'Unknown') for s in services])
        services_label = QLabel(f"Services: {services_text}")
        services_label.setStyleSheet("color: #888888; font-size: 10px;")
        details_layout.addWidget(services_label)
        
        layout.addLayout(details_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self._connect_device)
        button_layout.addWidget(self.connect_button)
        
        self.pair_button = QPushButton("Pair")
        self.pair_button.clicked.connect(self._pair_device)
        button_layout.addWidget(self.pair_button)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Style the widget
        self.setStyleSheet('''
        DeviceListItem {
            border: 1px solid #555555;
            border-radius: 8px;
            background-color: #3c3c3c;
            margin: 2px;
        }
        DeviceListItem:hover {
            background-color: #404040;
        }
        ''')
    
    def _update_connection_status(self):
        """Update the connection status display."""
        connected_devices = self.device_controller.get_connected_devices()
        is_connected = self.device_id in connected_devices
        
        if is_connected:
            self.status_label.setText("● Connected")
            self.status_label.setStyleSheet("color: #00ff00; font-size: 10px;")
            self.connect_button.setText("Disconnect")
            self.connect_button.setEnabled(True)
            self.pair_button.setEnabled(False)
        else:
            self.status_label.setText("○ Not Connected")
            self.status_label.setStyleSheet("color: #666666; font-size: 10px;")
            self.connect_button.setText("Connect")
            self.connect_button.setEnabled(True)
            self.pair_button.setEnabled(True)
    
    @qasync.asyncSlot()
    async def _connect_device(self):
        """Connect or disconnect the device."""
        connected_devices = self.device_controller.get_connected_devices()
        is_connected = self.device_id in connected_devices
        
        if is_connected:
            await self.device_controller.disconnect_device(self.device_id)
        else:
            await self.device_controller.connect_device(self.device_id)
    
    @qasync.asyncSlot()
    async def _pair_device(self):
        """Start pairing process for the device."""
        await self.pairing_manager.start_pairing(self.device_id, self.device_info)

class DeviceManagerWidget(QWidget):
    """Widget for managing device discovery and connections."""
    
    def __init__(self, config_manager: ConfigManager, 
                 device_controller: DeviceController,
                 pairing_manager: PairingManager):
        super().__init__()
        
        self.config_manager = config_manager
        self.device_controller = device_controller
        self.pairing_manager = pairing_manager
        
        self._setup_ui()
        self._setup_connections()
        
        # Load known devices
        self._load_known_devices()
    
    def _setup_ui(self):
        """Set up the device manager UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("Device Manager")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Discovery controls
        discovery_group = QGroupBox("Device Discovery")
        discovery_layout = QVBoxLayout(discovery_group)
        
        # Discovery buttons
        button_layout = QHBoxLayout()
        
        self.discover_button = QPushButton("Discover Devices")
        self.discover_button.clicked.connect(self._discover_devices)
        button_layout.addWidget(self.discover_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._refresh_devices)
        button_layout.addWidget(self.refresh_button)
        
        # Timeout control
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Timeout:"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 60)
        self.timeout_spin.setValue(10)
        self.timeout_spin.setSuffix(" seconds")
        timeout_layout.addWidget(self.timeout_spin)
        button_layout.addLayout(timeout_layout)
        
        discovery_layout.addLayout(button_layout)
        
        # Discovery progress
        self.discovery_progress = QProgressBar()
        self.discovery_progress.setVisible(False)
        discovery_layout.addWidget(self.discovery_progress)
        
        # Discovery status
        self.discovery_status = QLabel("Ready to discover devices")
        self.discovery_status.setStyleSheet("color: #888888; font-size: 10px;")
        discovery_layout.addWidget(self.discovery_status)
        
        layout.addWidget(discovery_group)
        
        # Device list
        devices_group = QGroupBox("Discovered Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        self.device_list = QListWidget()
        self.device_list.setAlternatingRowColors(True)
        self.device_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        devices_layout.addWidget(self.device_list)
        
        # Device count label
        self.device_count_label = QLabel("0 devices found")
        self.device_count_label.setStyleSheet("color: #888888; font-size: 10px;")
        devices_layout.addWidget(self.device_count_label)
        
        layout.addWidget(devices_group)
        
        # Connection status
        status_group = QGroupBox("Connection Status")
        status_layout = QVBoxLayout(status_group)
        
        self.connection_status_label = QLabel("No device connected")
        status_layout.addWidget(self.connection_status_label)
        
        # Current device info
        self.current_device_info = QLabel("")
        self.current_device_info.setStyleSheet("color: #888888; font-size: 10px;")
        self.current_device_info.setWordWrap(True)
        status_layout.addWidget(self.current_device_info)
        
        layout.addWidget(status_group)
        
        layout.addStretch()
    
    def _setup_connections(self):
        """Set up signal connections."""
        self.device_controller.discovery_started.connect(self._on_discovery_started)
        self.device_controller.discovery_finished.connect(self._on_discovery_finished)
        self.device_controller.discovery_progress.connect(self._on_discovery_progress)
        self.device_controller.discovery_error.connect(self._on_discovery_error)
        self.device_controller.devices_discovered.connect(self._on_devices_discovered)
        self.device_controller.device_connected.connect(self._on_device_connected)
        self.device_controller.device_disconnected.connect(self._on_device_disconnected)
        self.device_controller.connection_failed.connect(self._on_connection_failed)
    
    def _load_known_devices(self):
        """Load known devices from configuration."""
        known_devices = self.config_manager.get_known_devices()
        devices_list = list(known_devices.values())
        self._populate_device_list(devices_list)
    
    def _discover_devices(self):
        """Launch Apple TV discovery and pairing wizard"""
        try:
            from .discovery_wizard import DiscoveryWizard
            
            # Create and show discovery wizard
            wizard = DiscoveryWizard(self.config_manager, parent=self)
            
            # Connect signals
            wizard.device_paired.connect(self._on_device_paired)
            wizard.discovery_finished.connect(self._on_discovery_finished)
            
            # Show wizard with exec() for modal behavior
            wizard.exec()
            
        except Exception as e:
            logging.error(f"Failed to launch discovery wizard: {e}")
            # Show error with more details
            error_msg = f"Failed to launch device discovery wizard:\n\n{str(e)}\n\nPlease ensure pyatv is installed:\npip install pyatv"
            if hasattr(self, '_show_error'):
                self._show_error("Discovery Error", error_msg)
            else:
                # Fallback error display
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Discovery Error", error_msg)

    def _on_device_paired(self, device_info):
        """Handle successful device pairing"""
        try:
            device_name = device_info.get('name', 'Unknown Device')
            logging.info(f"Device paired successfully: {device_name}")
            
            # Add to known devices
            device_id = f"{device_name}_{device_info.get('address', 'unknown')}"
            self.config_manager.save_known_device(device_id, device_info)
            
            # Refresh the device list
            self._load_known_devices()
            
            # Show success message
            success_msg = f"Successfully paired with '{device_name}'!\n\nThe device is now available in your device list."
            if hasattr(self, '_show_info'):
                self._show_info("Device Paired", success_msg)
            else:
                # Fallback success display
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Device Paired", success_msg)
                
        except Exception as e:
            logging.error(f"Error handling device pairing: {e}")

    def _on_discovery_finished(self):
        """Handle discovery wizard completion"""
        logging.info("Device discovery wizard completed")
        # Refresh device list in case new devices were added
        self._load_known_devices()
    
    def _refresh_devices(self):
        """Refresh the device list."""
        self._discover_devices()
    
    def _populate_device_list(self, devices: list):
        """Populate the device list with discovered devices."""
        self.device_list.clear()
        
        try:
            for device_info in devices:
                # Validate device_info has required structure
                if not isinstance(device_info, dict):
                    continue
                    
                # Ensure minimum required fields exist (at least name or id)
                if not device_info.get('name') and not device_info.get('id'):
                    continue
                
                # Create custom widget for device
                device_widget = DeviceListItem(
                    device_info, 
                    self.device_controller, 
                    self.pairing_manager
                )
                
                # Create list item
                item = QListWidgetItem()
                item.setSizeHint(device_widget.sizeHint())
                
                # Add to list
                self.device_list.addItem(item)
                self.device_list.setItemWidget(item, device_widget)
            
        except Exception as e:
            print(f"Error populating device list: {e}")
            # Continue to show device count even if some devices failed to load
        
        # Update device count
        count = self.device_list.count()
        self.device_count_label.setText(f"{count} device{'s' if count != 1 else ''} found")
    
    def _set_discovery_state(self, discovering: bool):
        """Set the discovery UI state."""
        if discovering:
            self.discovery_progress.setVisible(True)
            self.discovery_progress.setRange(0, 0)  # Indeterminate progress
            self.discover_button.setEnabled(False)
            self.refresh_button.setEnabled(False)
            self.discovery_status.setText("Discovering devices...")
            self.discovery_status.setStyleSheet("color: #00aaff; font-size: 10px;")
        else:
            self.discovery_progress.setVisible(False)
            self.discover_button.setEnabled(True)
            self.refresh_button.setEnabled(True)
            self.discovery_status.setText("Ready to discover devices")
            self.discovery_status.setStyleSheet("color: #888888; font-size: 10px;")
    
    @pyqtSlot()
    def _on_discovery_started(self):
        """Handle discovery start."""
        self.discovery_progress.setVisible(True)
        self.discovery_progress.setRange(0, 0)  # Indeterminate progress
        self.discover_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        self.discovery_status.setText("Discovering devices...")
        self.discovery_status.setStyleSheet("color: #00aaff; font-size: 10px;")
    
    @pyqtSlot()
    def _on_discovery_finished(self):
        """Handle discovery completion."""
        self.discovery_progress.setVisible(False)
        self.discover_button.setEnabled(True)
        self.refresh_button.setEnabled(True)
        self.discovery_status.setText("Discovery completed")
        self.discovery_status.setStyleSheet("color: #00ff00; font-size: 10px;")
        
        # Reset status after 3 seconds
        QTimer.singleShot(3000, lambda: self.discovery_status.setText("Ready to discover devices"))
        QTimer.singleShot(3000, lambda: self.discovery_status.setStyleSheet("color: #888888; font-size: 10px;"))
    
    @pyqtSlot(list)
    def _on_devices_discovered(self, devices: list):
        """Handle device discovery completion."""
        self._populate_device_list(devices)
    
    @pyqtSlot(str, dict)
    def _on_device_connected(self, device_id: str, device_info: dict):
        """Handle device connection."""
        device_name = device_info.get('name', 'Unknown Device')
        self.connection_status_label.setText(f"Connected to: {device_name}")
        self.connection_status_label.setStyleSheet("color: #00ff00; font-size: 12px; font-weight: bold;")
        
        # Show device details
        info_text = f"Address: {device_info.get('address', 'Unknown')}\n"
        info_text += f"Model: {device_info.get('model', 'Unknown')}\n"
        services = device_info.get('services', [])
        if services:
            protocols = [s.get('protocol', 'Unknown') for s in services]
            info_text += f"Services: {', '.join(protocols)}"
        
        self.current_device_info.setText(info_text)
    
    @pyqtSlot(str)
    def _on_device_disconnected(self, device_id: str):
        """Handle device disconnection."""
        self.connection_status_label.setText("No device connected")
        self.connection_status_label.setStyleSheet("color: #888888; font-size: 12px;")
        self.current_device_info.setText("")
    
    @pyqtSlot(str, str)
    def _on_connection_failed(self, device_id: str, error: str):
        """Handle connection failure."""
        QMessageBox.warning(self, "Connection Failed", 
                          f"Failed to connect to device:\n{error}")
    
    @pyqtSlot(str)
    def _on_discovery_progress(self, message: str):
        """Handle discovery progress updates."""
        self.discovery_status.setText(message)
        self.discovery_status.setStyleSheet("color: #00aaff; font-size: 10px;")
    
    @pyqtSlot(str)
    def _on_discovery_error(self, error: str):
        """Handle discovery errors."""
        self.discovery_status.setText(f"Error: {error}")
        self.discovery_status.setStyleSheet("color: #ff0000; font-size: 10px;")
        QMessageBox.warning(self, "Discovery Error", f"Discovery failed:\n{error}")
    
    def _on_device_paired(self, device_info):
        """Handle successful device pairing"""
        try:
            device_name = device_info.get('name', 'Unknown Device')
            logging.info(f"Device paired successfully: {device_name}")
            
            # Add to known devices
            device_id = f"{device_name}_{device_info.get('address', 'unknown')}"
            self.config_manager.save_known_device(device_id, device_info)
            
            # Refresh the device list
            self._load_known_devices()
            
            # Show success message
            success_msg = f"Successfully paired with '{device_name}'!\n\nThe device is now available in your device list."
            if hasattr(self, '_show_info'):
                self._show_info("Device Paired", success_msg)
            else:
                # Fallback success display
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Device Paired", success_msg)
                
        except Exception as e:
            logging.error(f"Error handling device pairing: {e}")

    def _on_discovery_finished(self):
        """Handle discovery wizard completion"""
        logging.info("Device discovery wizard completed")
        # Refresh device list in case new devices were added
        self._load_known_devices()
    
    def _show_error(self, title: str, message: str):
        """Show error message dialog"""
        QMessageBox.warning(self, title, message)
    
    def _show_info(self, title: str, message: str):
        """Show info message dialog"""
        QMessageBox.information(self, title, message)
    
    def get_selected_device(self) -> dict:
        """Get the currently selected device info."""
        current_item = self.device_list.currentItem()
        if current_item:
            widget = self.device_list.itemWidget(current_item)
            if isinstance(widget, DeviceListItem):
                return widget.device_info
        return None