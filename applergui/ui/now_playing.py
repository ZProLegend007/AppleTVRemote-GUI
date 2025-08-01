"""Now playing widget for displaying and controlling media playback."""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QSlider, QGroupBox, QProgressBar,
                            QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QBrush, QColor
import asyncio
import qasync
from typing import Optional
import requests
from io import BytesIO

# Handle PIL import gracefully
try:
    from PIL import Image, ImageQt
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL/Pillow not available, album artwork will be disabled")

from ..backend.device_controller import DeviceController

class ArtworkLabel(QLabel):
    """Custom label for displaying album artwork."""
    
    def __init__(self, size: int = 200):
        super().__init__()
        self.artwork_size = size
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet('''
        ArtworkLabel {
            border: 2px solid #555555;
            border-radius: 8px;
            background-color: #3c3c3c;
        }
        ''')
        self._set_placeholder()
    
    def _set_placeholder(self):
        """Set placeholder artwork."""
        pixmap = QPixmap(self.artwork_size, self.artwork_size)
        pixmap.fill(QColor(60, 60, 60))
        
        # Draw music note icon
        painter = QPainter(pixmap)
        painter.setPen(QColor(136, 136, 136))
        painter.setFont(QFont("Arial", 48))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "♪")
        painter.end()
        
        self.setPixmap(pixmap)
    
    def set_artwork(self, artwork_data: Optional[bytes]):
        """Set artwork from image data."""
        if artwork_data and PIL_AVAILABLE:
            try:
                # Load image with PIL
                image = Image.open(BytesIO(artwork_data))
                image = image.convert('RGB')
                
                # Resize to fit
                image = image.resize((self.artwork_size, self.artwork_size), Image.Resampling.LANCZOS)
                
                # Convert to QPixmap
                qt_image = ImageQt.ImageQt(image)
                pixmap = QPixmap.fromImage(qt_image)
                
                self.setPixmap(pixmap)
                return
                
            except Exception as e:
                print(f"Failed to load artwork: {e}")
        
        # Fallback to placeholder (either no data, no PIL, or error)
        self._set_placeholder()

class PlaybackControlsWidget(QWidget):
    """Widget for playback controls."""
    
    # Signals
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    previous_clicked = pyqtSignal()
    position_changed = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._is_playing = False
        self._duration = 0
        self._position = 0
    
    def _setup_ui(self):
        """Set up the playback controls UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Transport controls
        transport_layout = QHBoxLayout()
        transport_layout.setSpacing(15)
        
        # Previous button
        self.previous_button = QPushButton("⏮")
        self.previous_button.setFixedSize(50, 40)
        self.previous_button.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.previous_button.clicked.connect(self.previous_clicked.emit)
        transport_layout.addWidget(self.previous_button)
        
        # Play/Pause button
        self.play_pause_button = QPushButton("▶")
        self.play_pause_button.setFixedSize(60, 50)
        self.play_pause_button.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.play_pause_button.clicked.connect(self._toggle_play_pause)
        transport_layout.addWidget(self.play_pause_button)
        
        # Next button
        self.next_button = QPushButton("⏭")
        self.next_button.setFixedSize(50, 40)
        self.next_button.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.next_button.clicked.connect(self.next_clicked.emit)
        transport_layout.addWidget(self.next_button)
        
        layout.addLayout(transport_layout)
        
        # Progress bar and time info
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(5)
        
        # Time labels
        time_layout = QHBoxLayout()
        
        self.current_time_label = QLabel("0:00")
        self.current_time_label.setStyleSheet("color: #888888; font-size: 11px;")
        time_layout.addWidget(self.current_time_label)
        
        time_layout.addStretch()
        
        self.total_time_label = QLabel("0:00")
        self.total_time_label.setStyleSheet("color: #888888; font-size: 11px;")
        time_layout.addWidget(self.total_time_label)
        
        progress_layout.addLayout(time_layout)
        
        # Progress slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setValue(0)
        self.progress_slider.sliderReleased.connect(self._on_position_changed)
        progress_layout.addWidget(self.progress_slider)
        
        layout.addLayout(progress_layout)
    
    def _toggle_play_pause(self):
        """Toggle between play and pause."""
        if self._is_playing:
            self.pause_clicked.emit()
        else:
            self.play_clicked.emit()
    
    def _on_position_changed(self):
        """Handle position change from user interaction."""
        if self._duration > 0:
            position = (self.progress_slider.value() / 100.0) * self._duration
            self.position_changed.emit(position)
    
    def set_playing_state(self, is_playing: bool):
        """Set the playing state."""
        self._is_playing = is_playing
        if is_playing:
            self.play_pause_button.setText("⏸")
        else:
            self.play_pause_button.setText("▶")
    
    def set_progress(self, position: float, duration: float):
        """Set the playback progress."""
        self._position = position
        self._duration = duration
        
        # Update time labels
        self.current_time_label.setText(self._format_time(position))
        self.total_time_label.setText(self._format_time(duration))
        
        # Update progress slider
        if duration > 0:
            progress = int((position / duration) * 100)
            self.progress_slider.setValue(progress)
        else:
            self.progress_slider.setValue(0)
    
    def _format_time(self, seconds: float) -> str:
        """Format time in MM:SS format."""
        if seconds < 0:
            return "0:00"
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"
    
    def set_enabled_state(self, enabled: bool):
        """Enable or disable all controls."""
        self.previous_button.setEnabled(enabled)
        self.play_pause_button.setEnabled(enabled)
        self.next_button.setEnabled(enabled)
        self.progress_slider.setEnabled(enabled)

class NowPlayingWidget(QWidget):
    """Widget for displaying and controlling now playing media."""
    
    def __init__(self, device_controller: DeviceController):
        super().__init__()
        self.device_controller = device_controller
        
        self._setup_ui()
        self._setup_connections()
        
        # Update timer for artwork and state
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_artwork)
        self.update_timer.start(10000)  # Update artwork every 10 seconds
        
        # UI state update timer
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self._update_ui_state)
        self.ui_timer.start(2000)  # Update UI state every 2 seconds
        
        # Initial state
        self._current_now_playing = None
        self._update_ui_state()
    
    def _setup_ui(self):
        """Set up the now playing UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Now Playing")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Connection status
        self.connection_label = QLabel("No device connected")
        self.connection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connection_label.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(self.connection_label)
        
        # Main content layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # Left side - Artwork
        artwork_layout = QVBoxLayout()
        
        self.artwork_label = ArtworkLabel(200)
        artwork_layout.addWidget(self.artwork_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addLayout(artwork_layout)
        
        # Right side - Media info and controls
        info_controls_layout = QVBoxLayout()
        info_controls_layout.setSpacing(20)
        
        # Media information
        media_info_group = QGroupBox("Media Information")
        media_info_layout = QVBoxLayout(media_info_group)
        
        # Title
        self.title_label = QLabel("No media playing")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        self.title_label.setFont(title_font)
        self.title_label.setWordWrap(True)
        media_info_layout.addWidget(self.title_label)
        
        # Artist
        self.artist_label = QLabel("Unknown Artist")
        artist_font = QFont()
        artist_font.setPointSize(12)
        self.artist_label.setFont(artist_font)
        self.artist_label.setStyleSheet("color: #bbbbbb;")
        self.artist_label.setWordWrap(True)
        media_info_layout.addWidget(self.artist_label)
        
        # Album
        self.album_label = QLabel("Unknown Album")
        self.album_label.setStyleSheet("color: #888888; font-size: 11px;")
        self.album_label.setWordWrap(True)
        media_info_layout.addWidget(self.album_label)
        
        # Media type and state
        state_layout = QHBoxLayout()
        
        self.media_type_label = QLabel("Type: Unknown")
        self.media_type_label.setStyleSheet("color: #888888; font-size: 10px;")
        state_layout.addWidget(self.media_type_label)
        
        state_layout.addStretch()
        
        self.play_state_label = QLabel("State: Unknown")
        self.play_state_label.setStyleSheet("color: #888888; font-size: 10px;")
        state_layout.addWidget(self.play_state_label)
        
        media_info_layout.addLayout(state_layout)
        
        info_controls_layout.addWidget(media_info_group)
        
        # Playback controls
        controls_group = QGroupBox("Playback Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        self.playback_controls = PlaybackControlsWidget()
        controls_layout.addWidget(self.playback_controls)
        
        info_controls_layout.addWidget(controls_group)
        
        # Volume control
        volume_group = QGroupBox("Volume")
        volume_layout = QHBoxLayout(volume_group)
        
        volume_down_btn = QPushButton("🔉")
        volume_down_btn.setFixedSize(40, 30)
        volume_down_btn.clicked.connect(self._on_volume_down_clicked)
        volume_layout.addWidget(volume_down_btn)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_layout.addWidget(self.volume_slider)
        
        volume_up_btn = QPushButton("🔊")
        volume_up_btn.setFixedSize(40, 30)
        volume_up_btn.clicked.connect(self._on_volume_up_clicked)
        volume_layout.addWidget(volume_up_btn)
        
        info_controls_layout.addWidget(volume_group)
        
        # Repeat and shuffle controls
        modes_group = QGroupBox("Playback Modes")
        modes_layout = QHBoxLayout(modes_group)
        
        self.repeat_button = QPushButton("🔁 Repeat: Off")
        self.repeat_button.setCheckable(True)
        self.repeat_button.setEnabled(False)  # Not implemented yet
        modes_layout.addWidget(self.repeat_button)
        
        self.shuffle_button = QPushButton("🔀 Shuffle: Off")
        self.shuffle_button.setCheckable(True)
        self.shuffle_button.setEnabled(False)  # Not implemented yet
        modes_layout.addWidget(self.shuffle_button)
        
        info_controls_layout.addWidget(modes_group)
        
        info_controls_layout.addStretch()
        
        content_layout.addLayout(info_controls_layout)
        
        layout.addLayout(content_layout)
        
        layout.addStretch()
    
    def _setup_connections(self):
        """Set up signal connections."""
        # Device controller signals
        self.device_controller.device_connected.connect(self._on_device_connected)
        self.device_controller.device_disconnected.connect(self._on_device_disconnected)
        self.device_controller.now_playing_updated.connect(self._on_now_playing_updated)
        
        # Playback control signals
        self.playback_controls.play_clicked.connect(self._on_play_clicked)
        self.playback_controls.pause_clicked.connect(self._on_pause_clicked)
        self.playback_controls.next_clicked.connect(self._on_next_clicked)
        self.playback_controls.previous_clicked.connect(self._on_previous_clicked)
        self.playback_controls.position_changed.connect(self._on_position_changed)
    
    def _update_ui_state(self):
        """Update UI state based on device connection."""
        connected_devices = self.device_controller.get_connected_devices()
        has_connection = len(connected_devices) > 0
        
        # Enable/disable controls
        self.playback_controls.set_enabled_state(has_connection)
        self.volume_slider.setEnabled(has_connection)
        
        # Update connection status
        if has_connection:
            device_info = next(iter(connected_devices.values()))
            device_name = device_info.get('name', 'Unknown Device')
            self.connection_label.setText(f"Connected to: {device_name}")
            self.connection_label.setStyleSheet("color: #00ff00; font-size: 12px; font-weight: bold;")
        else:
            self.connection_label.setText("No device connected")
            self.connection_label.setStyleSheet("color: #888888; font-size: 12px;")
            
            # Reset display when disconnected
            self._reset_display()
    
    def _reset_display(self):
        """Reset the display to default state."""
        self.title_label.setText("No media playing")
        self.artist_label.setText("Unknown Artist")
        self.album_label.setText("Unknown Album")
        self.media_type_label.setText("Type: Unknown")
        self.play_state_label.setText("State: Unknown")
        self.artwork_label._set_placeholder()
        self.playback_controls.set_progress(0, 0)
        self.playback_controls.set_playing_state(False)
    
    @qasync.asyncSlot()
    async def _update_artwork(self):
        """Update artwork from current device."""
        if self.device_controller.get_current_device():
            await self._load_artwork()
    
    async def _load_artwork(self):
        """Load artwork asynchronously."""
        try:
            artwork_data = await self.device_controller.get_artwork()
            self.artwork_label.set_artwork(artwork_data)
        except Exception as e:
            print(f"Failed to load artwork: {e}")
    
    @pyqtSlot(str, dict)
    def _on_device_connected(self, device_id: str, device_info: dict):
        """Handle device connection."""
        self._update_ui_state()
    
    @pyqtSlot(str)
    def _on_device_disconnected(self, device_id: str):
        """Handle device disconnection."""
        self._update_ui_state()
    
    @pyqtSlot(dict)
    def _on_now_playing_updated(self, now_playing_info: dict):
        """Handle now playing information update."""
        self._current_now_playing = now_playing_info
        
        # Update media information
        self.title_label.setText(now_playing_info.get('title', 'Unknown Title'))
        self.artist_label.setText(now_playing_info.get('artist', 'Unknown Artist'))
        self.album_label.setText(now_playing_info.get('album', 'Unknown Album'))
        
        # Update state information
        media_type = now_playing_info.get('media_type', 'unknown').replace('_', ' ').title()
        self.media_type_label.setText(f"Type: {media_type}")
        
        play_state = now_playing_info.get('play_state', 'unknown').replace('_', ' ').title()
        self.play_state_label.setText(f"State: {play_state}")
        
        # Update playback controls
        position = now_playing_info.get('position', 0)
        duration = now_playing_info.get('total_time', 0)
        self.playback_controls.set_progress(position, duration)
        
        is_playing = now_playing_info.get('play_state') == 'playing'
        self.playback_controls.set_playing_state(is_playing)
        
        # Update repeat and shuffle (placeholder)
        repeat_mode = now_playing_info.get('repeat', 'off').title()
        self.repeat_button.setText(f"🔁 Repeat: {repeat_mode}")
        
        shuffle_mode = now_playing_info.get('shuffle', 'off').title()
        self.shuffle_button.setText(f"🔀 Shuffle: {shuffle_mode}")
    
    @qasync.asyncSlot()
    async def _on_play_clicked(self):
        """Handle play button click."""
        await self.device_controller.play()
    
    @qasync.asyncSlot()
    async def _on_pause_clicked(self):
        """Handle pause button click."""
        await self.device_controller.pause()
    
    @qasync.asyncSlot()
    async def _on_next_clicked(self):
        """Handle next button click."""
        await self.device_controller.next_track()
    
    @qasync.asyncSlot()
    async def _on_previous_clicked(self):
        """Handle previous button click."""
        await self.device_controller.previous_track()
    
    @qasync.asyncSlot(float)
    async def _on_position_changed(self, position: float):
        """Handle position change."""
        await self.device_controller.set_position(position)
    
    @qasync.asyncSlot()
    async def _on_volume_up_clicked(self):
        """Handle volume up button click."""
        await self.device_controller.remote_volume_up()
    
    @qasync.asyncSlot()
    async def _on_volume_down_clicked(self):
        """Handle volume down button click."""
        await self.device_controller.remote_volume_down()
    
    @qasync.asyncSlot(int)
    async def _on_volume_changed(self, value: int):
        """Handle volume slider change."""
        # Convert to 0-1 range and set volume
        volume = value / 100.0
        await self.device_controller.set_volume(volume)