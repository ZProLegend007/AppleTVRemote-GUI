"""PIN entry overlay that darkens the main window background."""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFrame, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPalette

class PinOverlay(QWidget):
    """PIN entry overlay that darkens the main window background."""
    
    pin_entered = pyqtSignal(dict, str)  # device_info, pin
    overlay_closed = pyqtSignal()
    
    def __init__(self, device_info, parent=None):
        super().__init__(parent)
        self.device_info = device_info
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup PIN overlay UI."""
        # Semi-transparent background
        self.setStyleSheet("""
            QWidget {
                background: rgba(0, 0, 0, 0.7);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.addStretch()
        
        # PIN dialog frame
        pin_frame = QFrame()
        pin_frame.setFixedSize(400, 300)
        pin_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 15px;
                border: 2px solid #3498db;
            }
        """)
        
        frame_layout = QVBoxLayout(pin_frame)
        frame_layout.setContentsMargins(30, 30, 30, 30)
        frame_layout.setSpacing(20)
        
        # Header
        header_label = QLabel(f"📱 Pair with {self.device_info.get('name', 'Device')}")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(header_label)
        
        # Instructions
        instruction_label = QLabel("Enter the 4-digit PIN displayed on your Apple TV:")
        instruction_label.setFont(QFont("Arial", 11))
        instruction_label.setStyleSheet("color: #34495e; margin-bottom: 10px;")
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setWordWrap(True)
        frame_layout.addWidget(instruction_label)
        
        # PIN input
        self.pin_input = QLineEdit()
        self.pin_input.setMaxLength(4)
        self.pin_input.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.pin_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pin_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 15px;
                background: #ecf0f1;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background: white;
            }
        """)
        self.pin_input.setPlaceholderText("0000")
        self.pin_input.textChanged.connect(self._on_pin_changed)
        self.pin_input.returnPressed.connect(self._on_connect_clicked)
        frame_layout.addWidget(self.pin_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFont(QFont("Arial", 11))
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                border: none;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
            QPushButton:pressed {
                background: #6c7b7d;
            }
        """)
        self.cancel_btn.clicked.connect(self._on_cancel_clicked)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setFont(QFont("Arial", 11))
        self.connect_btn.setEnabled(False)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                border: none;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:pressed {
                background: #21618c;
            }
            QPushButton:disabled {
                background: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        button_layout.addWidget(self.connect_btn)
        
        frame_layout.addLayout(button_layout)
        
        # Center the frame
        layout.addWidget(pin_frame, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
    
    def _on_pin_changed(self, text):
        """Handle PIN input changes."""
        # Enable connect button only when PIN is 4 digits
        self.connect_btn.setEnabled(len(text) == 4 and text.isdigit())
    
    def _on_connect_clicked(self):
        """Handle connect button click."""
        pin = self.pin_input.text().strip()
        if len(pin) == 4 and pin.isdigit():
            self.pin_entered.emit(self.device_info, pin)
            self.hide()
    
    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        self.overlay_closed.emit()
        self.hide()
    
    def show_overlay(self):
        """Show the overlay and focus on PIN input."""
        if self.parent():
            # Resize to parent size
            self.resize(self.parent().size())
            
        self.show()
        self.raise_()
        self.pin_input.setFocus()
        self.pin_input.clear()
    
    def resizeEvent(self, event):
        """Handle window resize."""
        super().resizeEvent(event)
        if self.parent():
            self.resize(self.parent().size())