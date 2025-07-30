"""Settings dialog for application configuration."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QComboBox, QSpinBox, QCheckBox,
                            QGroupBox, QTabWidget, QWidget, QTextEdit,
                            QDialogButtonBox, QSlider, QFrame, QListWidget,
                            QListWidgetItem, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont
import json
from pathlib import Path

from backend.config_manager import ConfigManager

class GeneralSettingsWidget(QWidget):
    """Widget for general application settings."""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Set up the general settings UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Theme settings
        theme_group = QGroupBox("Appearance")
        theme_layout = QVBoxLayout(theme_group)
        
        theme_selection_layout = QHBoxLayout()
        theme_selection_layout.addWidget(QLabel("Theme:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        theme_selection_layout.addWidget(self.theme_combo)
        theme_selection_layout.addStretch()
        
        theme_layout.addLayout(theme_selection_layout)
        layout.addWidget(theme_group)
        
        # Device settings
        device_group = QGroupBox("Device Discovery")
        device_layout = QVBoxLayout(device_group)
        
        # Auto-discover checkbox
        self.auto_discover_checkbox = QCheckBox("Auto-discover devices on startup")
        device_layout.addWidget(self.auto_discover_checkbox)
        
        # Discovery timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Discovery timeout:"))
        
        self.discovery_timeout_spinbox = QSpinBox()
        self.discovery_timeout_spinbox.setRange(5, 60)
        self.discovery_timeout_spinbox.setSuffix(" seconds")
        timeout_layout.addWidget(self.discovery_timeout_spinbox)
        timeout_layout.addStretch()
        
        device_layout.addLayout(timeout_layout)
        
        # Connection timeout
        conn_timeout_layout = QHBoxLayout()
        conn_timeout_layout.addWidget(QLabel("Connection timeout:"))
        
        self.connection_timeout_spinbox = QSpinBox()
        self.connection_timeout_spinbox.setRange(5, 30)
        self.connection_timeout_spinbox.setSuffix(" seconds")
        conn_timeout_layout.addWidget(self.connection_timeout_spinbox)
        conn_timeout_layout.addStretch()
        
        device_layout.addLayout(conn_timeout_layout)
        layout.addWidget(device_group)
        
        # Debug settings
        debug_group = QGroupBox("Debug")
        debug_layout = QVBoxLayout(debug_group)
        
        self.debug_logging_checkbox = QCheckBox("Enable debug logging")
        debug_layout.addWidget(self.debug_logging_checkbox)
        
        layout.addWidget(debug_group)
        
        layout.addStretch()
    
    def _load_settings(self):
        """Load settings from configuration."""
        # Theme
        theme = self.config_manager.get('theme', 'dark')
        self.theme_combo.setCurrentText(theme.title())
        
        # Device settings
        self.auto_discover_checkbox.setChecked(
            self.config_manager.get('auto_discover', True)
        )
        self.discovery_timeout_spinbox.setValue(
            self.config_manager.get('discovery_timeout', 10)
        )
        self.connection_timeout_spinbox.setValue(
            self.config_manager.get('connection_timeout', 15)
        )
        
        # Debug
        self.debug_logging_checkbox.setChecked(
            self.config_manager.get('debug_logging', False)
        )
    
    def save_settings(self):
        """Save settings to configuration."""
        # Theme
        theme = self.theme_combo.currentText().lower()
        self.config_manager.set('theme', theme)
        
        # Device settings
        self.config_manager.set('auto_discover', self.auto_discover_checkbox.isChecked())
        self.config_manager.set('discovery_timeout', self.discovery_timeout_spinbox.value())
        self.config_manager.set('connection_timeout', self.connection_timeout_spinbox.value())
        
        # Debug
        self.config_manager.set('debug_logging', self.debug_logging_checkbox.isChecked())

class DeviceManagementWidget(QWidget):
    """Widget for managing known devices and credentials."""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self._setup_ui()
        self._load_devices()
    
    def _setup_ui(self):
        """Set up the device management UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Known devices
        devices_group = QGroupBox("Known Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        self.devices_list = QListWidget()
        self.devices_list.setAlternatingRowColors(True)
        devices_layout.addWidget(self.devices_list)
        
        # Device management buttons
        device_buttons_layout = QHBoxLayout()
        
        self.refresh_devices_button = QPushButton("Refresh")
        self.refresh_devices_button.clicked.connect(self._load_devices)
        device_buttons_layout.addWidget(self.refresh_devices_button)
        
        self.remove_device_button = QPushButton("Remove Selected")
        self.remove_device_button.clicked.connect(self._remove_selected_device)
        self.remove_device_button.setEnabled(False)
        device_buttons_layout.addWidget(self.remove_device_button)
        
        self.clear_credentials_button = QPushButton("Clear Credentials")
        self.clear_credentials_button.clicked.connect(self._clear_credentials)
        self.clear_credentials_button.setEnabled(False)
        device_buttons_layout.addWidget(self.clear_credentials_button)
        
        device_buttons_layout.addStretch()
        
        devices_layout.addLayout(device_buttons_layout)
        layout.addWidget(devices_group)
        
        # Device list selection
        self.devices_list.itemSelectionChanged.connect(self._on_device_selection_changed)
        
        # Device details
        details_group = QGroupBox("Device Details")
        details_layout = QVBoxLayout(details_group)
        
        self.device_details_text = QTextEdit()
        self.device_details_text.setReadOnly(True)
        self.device_details_text.setMaximumHeight(150)
        self.device_details_text.setStyleSheet('''
        QTextEdit {
            background-color: #2a2a2a;
            color: #cccccc;
            border: 1px solid #555555;
            font-family: monospace;
            font-size: 10px;
        }
        ''')
        details_layout.addWidget(self.device_details_text)
        
        layout.addWidget(details_group)
        
        layout.addStretch()
    
    def _load_devices(self):
        """Load known devices from configuration."""
        self.devices_list.clear()
        known_devices = self.config_manager.get_known_devices()
        
        for device_id, device_info in known_devices.items():
            device_name = device_info.get('name', 'Unknown Device')
            device_address = device_info.get('address', 'Unknown')
            
            item_text = f"{device_name} ({device_address})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, device_id)
            
            self.devices_list.addItem(item)
    
    def _on_device_selection_changed(self):
        """Handle device selection change."""
        selected_items = self.devices_list.selectedItems()
        has_selection = len(selected_items) > 0
        
        self.remove_device_button.setEnabled(has_selection)
        self.clear_credentials_button.setEnabled(has_selection)
        
        if has_selection:
            device_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self._show_device_details(device_id)
        else:
            self.device_details_text.clear()
    
    def _show_device_details(self, device_id: str):
        """Show details for selected device."""
        known_devices = self.config_manager.get_known_devices()
        device_info = known_devices.get(device_id, {})
        
        details = f"Device ID: {device_id}\n"
        details += f"Name: {device_info.get('name', 'Unknown')}\n"
        details += f"Address: {device_info.get('address', 'Unknown')}\n"
        details += f"Model: {device_info.get('model', 'Unknown')}\n"
        details += f"Identifier: {device_info.get('identifier', 'Unknown')}\n\n"
        
        services = device_info.get('services', [])
        details += f"Services ({len(services)}):\n"
        for service in services:
            details += f"  - {service.get('protocol', 'Unknown')} "
            details += f"(Port: {service.get('port', 'Unknown')})\n"
        
        # Check for stored credentials
        credentials = self.config_manager.get_credentials(device_id)
        if credentials:
            details += f"\nStored Credentials: {len(credentials)} service(s)"
        else:
            details += "\nNo stored credentials"
        
        self.device_details_text.setPlainText(details)
    
    def _remove_selected_device(self):
        """Remove the selected device."""
        selected_items = self.devices_list.selectedItems()
        if not selected_items:
            return
        
        device_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        device_name = selected_items[0].text().split(' (')[0]
        
        reply = QMessageBox.question(
            self, 
            "Remove Device",
            f"Are you sure you want to remove '{device_name}' from known devices?\n\n"
            "This will also delete any stored credentials for this device.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.remove_known_device(device_id)
            self.config_manager.delete_credentials(device_id)
            self._load_devices()
            QMessageBox.information(self, "Device Removed", f"'{device_name}' has been removed.")
    
    def _clear_credentials(self):
        """Clear credentials for the selected device."""
        selected_items = self.devices_list.selectedItems()
        if not selected_items:
            return
        
        device_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        device_name = selected_items[0].text().split(' (')[0]
        
        reply = QMessageBox.question(
            self,
            "Clear Credentials",
            f"Are you sure you want to clear stored credentials for '{device_name}'?\n\n"
            "You will need to pair with this device again.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.delete_credentials(device_id)
            self._show_device_details(device_id)  # Refresh details
            QMessageBox.information(self, "Credentials Cleared", 
                                  f"Credentials for '{device_name}' have been cleared.")

class AboutWidget(QWidget):
    """Widget for application information."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the about widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # App icon/logo placeholder
        icon_label = QLabel("🍎📱")
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # App name
        name_label = QLabel("AppleTVRemote-GUI")
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(24)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # Version
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #888888; font-size: 14px;")
        layout.addWidget(version_label)
        
        # Description
        description_label = QLabel(
            "A modern Linux GUI application for controlling Apple TV and HomePod devices."
        )
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setStyleSheet("color: #bbbbbb; font-size: 12px; margin: 20px 0;")
        layout.addWidget(description_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Technology info
        tech_group = QGroupBox("Built With")
        tech_layout = QVBoxLayout(tech_group)
        
        tech_info = """
        • PyQt6 - Modern GUI framework
        • pyatv - Apple TV communication library
        • qasync - Async/await support for Qt
        • Python 3.8+ - Programming language
        """
        
        tech_label = QLabel(tech_info)
        tech_label.setStyleSheet("color: #cccccc; font-size: 11px;")
        tech_layout.addWidget(tech_label)
        
        layout.addWidget(tech_group)
        
        # Author and license
        author_group = QGroupBox("Information")
        author_layout = QVBoxLayout(author_group)
        
        author_info = """
        Author: Zac
        License: MIT License
        Repository: github.com/ZProLegend007/AppleTVRemote-GUI
        """
        
        author_label = QLabel(author_info)
        author_label.setStyleSheet("color: #cccccc; font-size: 11px;")
        author_layout.addWidget(author_label)
        
        layout.addWidget(author_group)
        
        layout.addStretch()

class SettingsDialog(QDialog):
    """Main settings dialog."""
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        
        self._setup_ui()
        self.setModal(True)
        self.setWindowTitle("Settings")
        self.resize(600, 500)
    
    def _setup_ui(self):
        """Set up the settings dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # General settings tab
        self.general_widget = GeneralSettingsWidget(self.config_manager)
        self.tab_widget.addTab(self.general_widget, "General")
        
        # Device management tab
        self.device_widget = DeviceManagementWidget(self.config_manager)
        self.tab_widget.addTab(self.device_widget, "Devices")
        
        # About tab
        self.about_widget = AboutWidget()
        self.tab_widget.addTab(self.about_widget, "About")
        
        layout.addWidget(self.tab_widget)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        
        button_box.accepted.connect(self._accept_settings)
        button_box.rejected.connect(self.reject)
        
        apply_button = button_box.button(QDialogButtonBox.StandardButton.Apply)
        apply_button.clicked.connect(self._apply_settings)
        
        layout.addWidget(button_box)
    
    def _apply_settings(self):
        """Apply settings without closing dialog."""
        self.general_widget.save_settings()
        QMessageBox.information(self, "Settings Applied", "Settings have been applied successfully.")
    
    def _accept_settings(self):
        """Accept and save settings."""
        self.general_widget.save_settings()
        self.accept()