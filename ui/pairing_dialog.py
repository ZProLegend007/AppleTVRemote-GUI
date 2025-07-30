"""Pairing dialog manager for handling device pairing workflows."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QProgressBar, QTextEdit,
                            QDialogButtonBox, QGroupBox, QSpinBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QPixmap
from typing import Optional

from backend.pairing_manager import PairingManager

class PinEntryDialog(QDialog):
    """Dialog for entering pairing PIN."""
    
    def __init__(self, device_name: str, service_type: str, parent=None):
        super().__init__(parent)
        self.device_name = device_name
        self.service_type = service_type
        self.pin = ""
        
        self._setup_ui()
        self.setModal(True)
        self.setWindowTitle(f"Pair with {device_name}")
    
    def _setup_ui(self):
        """Set up the PIN entry dialog UI."""
        self.setFixedSize(400, 300)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Device Pairing Required")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Instructions
        instructions = QLabel(
            f"To pair with '{self.device_name}', please enter the PIN that appears on your Apple TV screen."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #bbbbbb; margin: 10px 0;")
        layout.addWidget(instructions)
        
        # Service type info
        service_label = QLabel(f"Service: {self.service_type}")
        service_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(service_label)
        
        # PIN entry group
        pin_group = QGroupBox("Enter PIN")
        pin_layout = QVBoxLayout(pin_group)
        
        # PIN input with large font
        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("Enter 4-digit PIN...")
        self.pin_input.setMaxLength(4)
        pin_font = QFont()
        pin_font.setPointSize(18)
        pin_font.setBold(True)
        self.pin_input.setFont(pin_font)
        self.pin_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pin_input.setStyleSheet('''
        QLineEdit {
            padding: 10px;
            border: 2px solid #555555;
            border-radius: 8px;
            background-color: #404040;
            color: #ffffff;
        }
        QLineEdit:focus {
            border-color: #0078d4;
        }
        ''')
        self.pin_input.textChanged.connect(self._validate_pin)
        pin_layout.addWidget(self.pin_input)
        
        # PIN validation message
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: #ff6666; font-size: 11px;")
        self.validation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pin_layout.addWidget(self.validation_label)
        
        layout.addWidget(pin_group)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        
        self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("Pair")
        self.ok_button.setEnabled(False)
        
        button_box.accepted.connect(self._accept_pin)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        # Focus on PIN input
        self.pin_input.setFocus()
    
    def _validate_pin(self, text: str):
        """Validate PIN input."""
        # Only allow digits
        filtered_text = ''.join(filter(str.isdigit, text))
        if filtered_text != text:
            self.pin_input.setText(filtered_text)
            return
        
        # Check length
        if len(filtered_text) == 4:
            self.validation_label.setText("✓ PIN ready")
            self.validation_label.setStyleSheet("color: #00ff00; font-size: 11px;")
            self.ok_button.setEnabled(True)
        elif len(filtered_text) > 0:
            self.validation_label.setText("PIN must be 4 digits")
            self.validation_label.setStyleSheet("color: #ffaa00; font-size: 11px;")
            self.ok_button.setEnabled(False)
        else:
            self.validation_label.setText("")
            self.ok_button.setEnabled(False)
    
    def _accept_pin(self):
        """Accept the entered PIN."""
        self.pin = self.pin_input.text()
        if len(self.pin) == 4:
            self.accept()
    
    def get_pin(self) -> str:
        """Get the entered PIN."""
        return self.pin

class DeviceCodeDialog(QDialog):
    """Dialog for displaying device code pairing."""
    
    def __init__(self, device_name: str, device_code: str, parent=None):
        super().__init__(parent)
        self.device_name = device_name
        self.device_code = device_code
        
        self._setup_ui()
        self.setModal(True)
        self.setWindowTitle(f"Pair with {device_name}")
        
        # Auto-close timer (60 seconds)
        self.timeout_timer = QTimer()
        self.timeout_timer.timeout.connect(self._timeout)
        self.timeout_timer.start(60000)
        
        # Countdown timer
        self.countdown_value = 60
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self._update_countdown)
        self.countdown_timer.start(1000)
    
    def _setup_ui(self):
        """Set up the device code dialog UI."""
        self.setFixedSize(450, 350)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Device Code Pairing")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Instructions
        instructions = QLabel(
            f"A pairing request has been sent to '{self.device_name}'. "
            "Please check your Apple TV screen and confirm the following code matches:"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #bbbbbb; margin: 10px 0;")
        layout.addWidget(instructions)
        
        # Device code display
        code_group = QGroupBox("Verification Code")
        code_layout = QVBoxLayout(code_group)
        
        self.code_label = QLabel(self.device_code)
        code_font = QFont()
        code_font.setPointSize(36)
        code_font.setBold(True)
        code_font.setFamily("monospace")
        self.code_label.setFont(code_font)
        self.code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.code_label.setStyleSheet('''
        QLabel {
            padding: 20px;
            border: 3px solid #0078d4;
            border-radius: 12px;
            background-color: #404040;
            color: #ffffff;
        }
        ''')
        code_layout.addWidget(self.code_label)
        
        layout.addWidget(code_group)
        
        # Progress and status
        status_group = QGroupBox("Pairing Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Waiting for confirmation on Apple TV...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #00aaff; font-size: 12px;")
        status_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        status_layout.addWidget(self.progress_bar)
        
        # Countdown
        self.countdown_label = QLabel("Timeout in 60 seconds")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        self.countdown_label.setStyleSheet("color: #888888; font-size: 10px;")
        status_layout.addWidget(self.countdown_label)
        
        layout.addWidget(status_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _update_countdown(self):
        """Update countdown display."""
        self.countdown_value -= 1
        self.countdown_label.setText(f"Timeout in {self.countdown_value} seconds")
        
        if self.countdown_value <= 0:
            self.countdown_timer.stop()
    
    def _timeout(self):
        """Handle timeout."""
        self.status_label.setText("Pairing timed out")
        self.status_label.setStyleSheet("color: #ff6666; font-size: 12px;")
        self.progress_bar.setVisible(False)
        self.reject()
    
    def set_success(self):
        """Set pairing success state."""
        self.timeout_timer.stop()
        self.countdown_timer.stop()
        self.status_label.setText("✓ Pairing successful!")
        self.status_label.setStyleSheet("color: #00ff00; font-size: 12px; font-weight: bold;")
        self.progress_bar.setVisible(False)
        QTimer.singleShot(2000, self.accept)  # Auto-close after 2 seconds
    
    def set_failed(self, error: str):
        """Set pairing failed state."""
        self.timeout_timer.stop()
        self.countdown_timer.stop()
        self.status_label.setText(f"✗ Pairing failed: {error}")
        self.status_label.setStyleSheet("color: #ff6666; font-size: 12px;")
        self.progress_bar.setVisible(False)

class PairingProgressDialog(QDialog):
    """Dialog for showing pairing progress."""
    
    def __init__(self, device_name: str, parent=None):
        super().__init__(parent)
        self.device_name = device_name
        
        self._setup_ui()
        self.setModal(True)
        self.setWindowTitle(f"Pairing with {device_name}")
    
    def _setup_ui(self):
        """Set up the pairing progress dialog UI."""
        self.setFixedSize(400, 250)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Pairing in Progress")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Device info
        device_label = QLabel(f"Device: {self.device_name}")
        device_label.setStyleSheet("color: #bbbbbb; margin: 10px 0;")
        layout.addWidget(device_label)
        
        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Initializing pairing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #00aaff; font-size: 11px;")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # Log area
        log_group = QGroupBox("Details")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(80)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet('''
        QTextEdit {
            background-color: #2a2a2a;
            color: #cccccc;
            border: 1px solid #555555;
            font-family: monospace;
            font-size: 9px;
        }
        ''')
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Cancel button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def set_status(self, message: str):
        """Set the status message."""
        self.status_label.setText(message)
        self.log_text.append(f"[INFO] {message}")
    
    def set_error(self, error: str):
        """Set error status."""
        self.status_label.setText(f"Error: {error}")
        self.status_label.setStyleSheet("color: #ff6666; font-size: 11px;")
        self.log_text.append(f"[ERROR] {error}")
        self.progress_bar.setVisible(False)
    
    def set_success(self):
        """Set success status."""
        self.status_label.setText("✓ Pairing completed successfully!")
        self.status_label.setStyleSheet("color: #00ff00; font-size: 11px; font-weight: bold;")
        self.log_text.append("[SUCCESS] Pairing completed successfully!")
        self.progress_bar.setVisible(False)
        QTimer.singleShot(2000, self.accept)  # Auto-close after 2 seconds

class PairingDialogManager:
    """Manages pairing dialogs and workflows."""
    
    def __init__(self, pairing_manager: PairingManager, parent_window):
        self.pairing_manager = pairing_manager
        self.parent_window = parent_window
        
        # Active dialogs
        self._progress_dialog: Optional[PairingProgressDialog] = None
        self._pin_dialog: Optional[PinEntryDialog] = None
        self._device_code_dialog: Optional[DeviceCodeDialog] = None
        
        self._setup_connections()
    
    def _setup_connections(self):
        """Set up signal connections with pairing manager."""
        self.pairing_manager.pairing_started.connect(self._on_pairing_started)
        self.pairing_manager.pairing_pin_required.connect(self._on_pin_required)
        self.pairing_manager.pairing_device_code_required.connect(self._on_device_code_required)
        self.pairing_manager.pairing_progress.connect(self._on_pairing_progress)
        self.pairing_manager.pairing_completed.connect(self._on_pairing_completed)
        self.pairing_manager.pairing_failed.connect(self._on_pairing_failed)
    
    @pyqtSlot(str)
    def _on_pairing_started(self, device_id: str):
        """Handle pairing start."""
        # Get device name from known devices
        config_manager = self.pairing_manager.config_manager
        known_devices = config_manager.get_known_devices()
        device_name = known_devices.get(device_id, {}).get('name', device_id)
        
        # Show progress dialog
        self._progress_dialog = PairingProgressDialog(device_name, self.parent_window)
        self._progress_dialog.show()
    
    @pyqtSlot(str, str)
    def _on_pin_required(self, device_id: str, service_type: str):
        """Handle PIN requirement."""
        # Get device name
        config_manager = self.pairing_manager.config_manager
        known_devices = config_manager.get_known_devices()
        device_name = known_devices.get(device_id, {}).get('name', device_id)
        
        # Close progress dialog
        if self._progress_dialog:
            self._progress_dialog.close()
            self._progress_dialog = None
        
        # Show PIN dialog
        self._pin_dialog = PinEntryDialog(device_name, service_type, self.parent_window)
        
        if self._pin_dialog.exec() == QDialog.DialogCode.Accepted:
            pin = self._pin_dialog.get_pin()
            self.pairing_manager.provide_pin(device_id, service_type, pin)
            
            # Show progress dialog again
            self._progress_dialog = PairingProgressDialog(device_name, self.parent_window)
            self._progress_dialog.set_status("Verifying PIN...")
            self._progress_dialog.show()
        else:
            # User cancelled PIN entry
            self.pairing_manager.cancel_pairing(device_id)
        
        self._pin_dialog = None
    
    @pyqtSlot(str, str)
    def _on_device_code_required(self, device_id: str, device_code: str):
        """Handle device code requirement."""
        # Get device name
        config_manager = self.pairing_manager.config_manager
        known_devices = config_manager.get_known_devices()
        device_name = known_devices.get(device_id, {}).get('name', device_id)
        
        # Close progress dialog
        if self._progress_dialog:
            self._progress_dialog.close()
            self._progress_dialog = None
        
        # Show device code dialog
        self._device_code_dialog = DeviceCodeDialog(device_name, device_code, self.parent_window)
        self._device_code_dialog.show()
        
        # Note: This dialog will be updated by pairing progress/completion signals
    
    @pyqtSlot(str, str)
    def _on_pairing_progress(self, device_id: str, message: str):
        """Handle pairing progress update."""
        if self._progress_dialog:
            self._progress_dialog.set_status(message)
    
    @pyqtSlot(str, dict)
    def _on_pairing_completed(self, device_id: str, credentials: dict):
        """Handle pairing completion."""
        # Update progress dialog
        if self._progress_dialog:
            self._progress_dialog.set_success()
        
        # Update device code dialog
        if self._device_code_dialog:
            self._device_code_dialog.set_success()
        
        # Clean up dialogs after a delay
        QTimer.singleShot(3000, self._cleanup_dialogs)
    
    @pyqtSlot(str, str)
    def _on_pairing_failed(self, device_id: str, error: str):
        """Handle pairing failure."""
        # Update progress dialog
        if self._progress_dialog:
            self._progress_dialog.set_error(error)
        
        # Update device code dialog
        if self._device_code_dialog:
            self._device_code_dialog.set_failed(error)
        
        # Clean up dialogs after a delay
        QTimer.singleShot(5000, self._cleanup_dialogs)
    
    def _cleanup_dialogs(self):
        """Clean up active dialogs."""
        if self._progress_dialog:
            self._progress_dialog.close()
            self._progress_dialog = None
        
        if self._device_code_dialog:
            self._device_code_dialog.close()
            self._device_code_dialog = None
        
        if self._pin_dialog:
            self._pin_dialog.close()
            self._pin_dialog = None