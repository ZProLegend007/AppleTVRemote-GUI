"""Simple PIN entry dialog that matches current main window aesthetic."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class PinDialog(QDialog):
    """Simple PIN entry dialog that matches current main window aesthetic"""
    
    def __init__(self, device_info, parent=None):
        super().__init__(parent)
        self.device_info = device_info
        self.pin = ""
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup PIN dialog with consistent styling"""
        self.setWindowTitle("Device Pairing")
        self.setModal(True)
        self.setFixedSize(350, 200)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel(f"Pair with {self.device_info['name']}")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel("Enter the 4-digit PIN displayed on your Apple TV:")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # PIN input
        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("Enter 4-digit PIN")
        self.pin_input.setMaxLength(4)
        self.pin_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.pin_input.font()
        font.setPointSize(14)
        self.pin_input.setFont(font)
        layout.addWidget(self.pin_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Pair")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self._accept_pin)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        # Focus on input
        self.pin_input.setFocus()
        self.pin_input.returnPressed.connect(self._accept_pin)
    
    def _accept_pin(self):
        """Accept PIN if valid"""
        pin = self.pin_input.text().strip()
        if len(pin) == 4 and pin.isdigit():
            self.pin = pin
            self.accept()
        else:
            # Simple validation feedback
            self.pin_input.setStyleSheet("QLineEdit { border: 2px solid red; }")
            self.pin_input.clear()
            self.pin_input.setFocus()
    
    def get_pin(self):
        """Get entered PIN"""
        return self.pin