from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class PinDialog(QDialog):
    """Clean PIN entry dialog without colors"""
    
    def __init__(self, device_info, parent=None):
        super().__init__(parent)
        self.device_info = device_info
        self.pin = ""
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup PIN dialog with clean neutral styling"""
        self.setWindowTitle("Device Pairing")
        self.setModal(True)
        self.setFixedSize(400, 250)
        
        # Clean neutral dialog styling
        self.setStyleSheet("""
            QDialog {
                background: #f8f8f8;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header
        header = QLabel(f"Pair with {self.device_info['name']}")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel("Enter the 4-digit PIN displayed on your Apple TV:")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # PIN input with clean styling
        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("Enter 4-digit PIN")
        self.pin_input.setMaxLength(4)
        self.pin_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pin_input.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.pin_input.setStyleSheet("""
            QLineEdit {
                background-color: #fff;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QLineEdit:focus {
                border-color: #999;
            }
        """)
        layout.addWidget(self.pin_input)
        
        # Buttons with clean neutral styling
        button_layout = QHBoxLayout()
        
        cancel_btn = self._create_clean_button("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        ok_btn = self._create_clean_button("Pair Device")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self._accept_pin)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        # Focus on input
        self.pin_input.setFocus()
        self.pin_input.returnPressed.connect(self._accept_pin)
    
    def _create_clean_button(self, text):
        """Create clean neutral button"""
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #f8f8f8;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: normal;
                min-height: 28px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #aaa;
            }
            QPushButton:pressed {
                background-color: #e8e8e8;
            }
            QPushButton:default {
                font-weight: bold;
            }
        """)
        return button
    
    def _accept_pin(self):
        """Accept PIN if valid"""
        pin = self.pin_input.text().strip()
        if len(pin) == 4 and pin.isdigit():
            self.pin = pin
            self.accept()
        else:
            # Clean validation feedback - neutral styling
            self.pin_input.setStyleSheet("""
                QLineEdit {
                    background-color: #fff;
                    border: 2px solid #999;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QLineEdit:focus {
                    border-color: #777;
                }
            """)
            self.pin_input.clear()
            self.pin_input.setFocus()
    
    def get_pin(self):
        """Get entered PIN"""
        return self.pin