#!/usr/bin/env python3
"""
Complete demonstration of the new ApplerGUI responsive three-section layout.
This script showcases all the major features implemented.
"""

import sys
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PyQt6.QtCore import QCoreApplication, QTimer
from PyQt6.QtGui import QFont

class DemoController(QWidget):
    """Demo controller to showcase all features."""
    
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.demo_step = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Setup demo controller UI."""
        self.setWindowTitle("ApplerGUI New UI Demonstration")
        self.setGeometry(100, 100, 500, 400)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🎯 ApplerGUI Modern UI Overhaul Demo")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Description
        desc = QTextEdit()
        desc.setMaximumHeight(150)
        desc.setHtml("""
        <h3>🚀 MAJOR IMPROVEMENTS IMPLEMENTED:</h3>
        <ul>
        <li><b>✅ Fixed Window Opacity Error</b> - No more modal discovery wizards</li>
        <li><b>✅ Three-Section Responsive Layout</b> - Discovery | Remote | Now Playing</li>
        <li><b>✅ Automatic Mobile/Desktop Switching</b> - Tabs vs. side-by-side</li>
        <li><b>✅ Modern PIN Overlay</b> - Clean device pairing experience</li>
        <li><b>✅ Apple TV-Style Remote</b> - Authentic look with keyboard shortcuts</li>
        <li><b>✅ Rich Now Playing Panel</b> - Beautiful music display</li>
        </ul>
        """)
        layout.addWidget(desc)
        
        # Demo buttons
        button_layout = QVBoxLayout()
        
        self.wide_btn = QPushButton("🖥️  Demo Wide Layout (Three Sections)")
        self.wide_btn.clicked.connect(self.demo_wide_layout)
        button_layout.addWidget(self.wide_btn)
        
        self.narrow_btn = QPushButton("📱 Demo Narrow Layout (Tabs)")
        self.narrow_btn.clicked.connect(self.demo_narrow_layout)
        button_layout.addWidget(self.narrow_btn)
        
        self.pin_btn = QPushButton("🔐 Demo PIN Overlay")
        self.pin_btn.clicked.connect(self.demo_pin_overlay)
        button_layout.addWidget(self.pin_btn)
        
        self.responsive_btn = QPushButton("🔄 Demo Responsive Behavior")
        self.responsive_btn.clicked.connect(self.demo_responsive)
        button_layout.addWidget(self.responsive_btn)
        
        self.features_btn = QPushButton("⭐ Demo All Features")
        self.features_btn.clicked.connect(self.demo_all_features)
        button_layout.addWidget(self.features_btn)
        
        layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("Ready to demonstrate new UI features!")
        layout.addWidget(self.status_label)
    
    def demo_wide_layout(self):
        """Demonstrate wide three-section layout."""
        self.status_label.setText("Showing wide layout with three sections...")
        self.show_layout(1400, 800, "Wide layout: Discovery | Remote | Now Playing sections side-by-side")
    
    def demo_narrow_layout(self):
        """Demonstrate narrow tabbed layout."""
        self.status_label.setText("Showing narrow layout with tabs...")
        self.show_layout(800, 600, "Narrow layout: Tabbed interface for mobile/small screens")
    
    def demo_pin_overlay(self):
        """Demonstrate PIN overlay functionality."""
        self.status_label.setText("Showing PIN overlay for device pairing...")
        if not self.main_window:
            self.show_layout(1200, 700, "")
        
        # Trigger PIN overlay after short delay
        QTimer.singleShot(1000, self.trigger_pin_overlay)
    
    def demo_responsive(self):
        """Demonstrate responsive behavior."""
        self.status_label.setText("Demonstrating responsive layout switching...")
        
        # Show wide first
        self.show_layout(1400, 800, "Starting wide...")
        
        # Then switch to narrow
        QTimer.singleShot(2000, lambda: self.resize_layout(800, 600, "Switching to narrow..."))
        
        # Then back to wide
        QTimer.singleShot(4000, lambda: self.resize_layout(1400, 800, "Back to wide layout!"))
    
    def demo_all_features(self):
        """Demonstrate all features in sequence."""
        self.status_label.setText("Full feature demonstration starting...")
        self.demo_step = 0
        self.run_full_demo()
    
    def run_full_demo(self):
        """Run complete feature demonstration."""
        if self.demo_step == 0:
            self.show_layout(1400, 800, "Step 1: Wide three-section layout")
            QTimer.singleShot(3000, self.run_full_demo)
        elif self.demo_step == 1:
            self.resize_layout(800, 600, "Step 2: Responsive switch to tabs")
            QTimer.singleShot(3000, self.run_full_demo)
        elif self.demo_step == 2:
            self.resize_layout(1200, 700, "Step 3: Back to sections for PIN demo")
            QTimer.singleShot(2000, self.run_full_demo)
        elif self.demo_step == 3:
            self.trigger_pin_overlay()
            self.status_label.setText("Step 4: PIN overlay (no modal dialog issues!)")
            QTimer.singleShot(4000, self.run_full_demo)
        elif self.demo_step == 4:
            self.status_label.setText("🎉 Demo complete! All features successfully demonstrated.")
            self.take_final_screenshot()
        
        self.demo_step += 1
    
    def show_layout(self, width, height, message):
        """Show the main window with specified dimensions."""
        from ui.main_window import MainWindow, ConfigManager, DeviceController, PairingManager
        
        if self.main_window:
            self.main_window.close()
        
        # Create dummy backends
        config_manager = ConfigManager()
        device_controller = DeviceController(config_manager)
        pairing_manager = PairingManager(config_manager)
        
        # Create and show main window
        self.main_window = MainWindow(config_manager, device_controller, pairing_manager)
        self.main_window.resize(width, height)
        self.main_window.show()
        
        if message:
            self.status_label.setText(message)
    
    def resize_layout(self, width, height, message):
        """Resize existing window to trigger responsive behavior."""
        if self.main_window:
            self.main_window.resize(width, height)
            if message:
                self.status_label.setText(message)
    
    def trigger_pin_overlay(self):
        """Trigger the PIN overlay demonstration."""
        if self.main_window:
            device_info = {
                "name": "Demo Apple TV 4K",
                "model": "Apple TV 4K (2023)",
                "id": "demo_device"
            }
            self.main_window._handle_pairing_request(device_info)
    
    def take_final_screenshot(self):
        """Take final demonstration screenshot."""
        try:
            subprocess.run([
                "scrot", "-z", "/tmp/appgui_demo_complete.png"
            ], env={"DISPLAY": ":99"}, check=True)
            print("Final demo screenshot saved: /tmp/appgui_demo_complete.png")
        except Exception as e:
            print(f"Failed to take final screenshot: {e}")

def main():
    """Main demo entry point."""
    # Set application properties
    QCoreApplication.setApplicationName("ApplerGUI Demo")
    QCoreApplication.setApplicationVersion("1.0.0")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("ApplerGUI Demo")
    
    # Create and show demo controller
    demo = DemoController()
    demo.show()
    
    # Start with wide layout demo
    QTimer.singleShot(500, demo.demo_wide_layout)
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()