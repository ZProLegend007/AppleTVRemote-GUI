"""Device controller for managing Apple TV/HomePod connections and operations."""

import asyncio
from typing import Optional, Dict, Any, List
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import qasync
import pyatv
from pyatv.interface import AppleTV, Playing
from backend.config_manager import ConfigManager

class DeviceController(QObject):
    """Controls Apple TV/HomePod device connections and operations."""
    
    # Signals for UI updates
    devices_discovered = pyqtSignal(list)  # List of discovered devices
    device_connected = pyqtSignal(str, dict)  # device_id, device_info
    device_disconnected = pyqtSignal(str)  # device_id
    connection_failed = pyqtSignal(str, str)  # device_id, error
    now_playing_updated = pyqtSignal(dict)  # now_playing_info
    device_state_changed = pyqtSignal(str, dict)  # device_id, state
    discovery_started = pyqtSignal()
    discovery_finished = pyqtSignal()
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self._connected_devices: Dict[str, AppleTV] = {}
        self._device_info: Dict[str, Dict[str, Any]] = {}
        self._current_device_id: Optional[str] = None
        self._discovery_task: Optional[asyncio.Task] = None
        
        # Timer for periodic now playing updates
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_now_playing)
        self._update_timer.setInterval(1000)  # Update every second
    
    async def discover_devices(self, timeout: int = 10) -> List[Dict[str, Any]]:
        """Discover Apple TV and HomePod devices on the network."""
        try:
            self.discovery_started.emit()
            
            # Scan for devices
            atvs = await pyatv.scan(timeout=timeout, loop=asyncio.get_event_loop())
            
            devices = []
            for conf in atvs:
                device_info = {
                    'id': conf.identifier or conf.address,
                    'name': conf.name,
                    'address': conf.address,  
                    'identifier': conf.identifier,
                    'model': getattr(conf, 'model', 'Unknown'),
                    'services': []
                }
                
                # Extract service information
                for service in conf.services:
                    service_info = {
                        'protocol': service.protocol.value,
                        'port': service.port,
                        'identifier': service.identifier,
                        'properties': dict(service.properties) if service.properties else {}
                    }
                    device_info['services'].append(service_info)
                
                devices.append(device_info)
                
                # Store in known devices
                self.config_manager.add_known_device(device_info['id'], device_info)
            
            self.devices_discovered.emit(devices)
            return devices
            
        except Exception as e:
            print(f"Device discovery failed: {e}")
            return []
        finally:
            self.discovery_finished.emit()
    
    async def connect_device(self, device_id: str) -> bool:
        """Connect to a specific device."""
        try:
            # Get device info
            known_devices = self.config_manager.get_known_devices()
            if device_id not in known_devices:
                self.connection_failed.emit(device_id, "Device not found in known devices")
                return False
            
            device_info = known_devices[device_id]
            
            # Create AppleTV configuration
            config = pyatv.conf.AppleTVConf(
                identifier=device_info.get('identifier', device_id),
                name=device_info.get('name', 'Apple TV'),
                address=device_info['address'],
                services=[]
            )
            
            # Add services
            for service_info in device_info.get('services', []):
                service = pyatv.conf.ManualService(
                    identifier=service_info.get('identifier'),
                    protocol=pyatv.const.Protocol(service_info['protocol']),
                    port=service_info['port'],
                    properties=service_info.get('properties', {})
                )
                config.add_service(service)
            
            # Get stored credentials
            credentials = self.config_manager.get_credentials(device_id)
            if credentials:
                for service in config.services:
                    service_name = service.protocol.name
                    if service_name in credentials:
                        service.credentials = credentials[service_name]
            
            # Connect to device
            atv = await pyatv.connect(config, loop=asyncio.get_event_loop())
            
            # Store connection
            self._connected_devices[device_id] = atv
            self._device_info[device_id] = device_info
            self._current_device_id = device_id
            
            # Start periodic updates
            if not self._update_timer.isActive():
                self._update_timer.start()
            
            self.device_connected.emit(device_id, device_info)
            self.config_manager.set('last_device', device_id)
            
            return True
            
        except Exception as e:
            self.connection_failed.emit(device_id, str(e))
            return False
    
    async def disconnect_device(self, device_id: str):
        """Disconnect from a specific device."""
        if device_id in self._connected_devices:
            try:
                atv = self._connected_devices[device_id]
                atv.close()
                
                del self._connected_devices[device_id]
                if device_id in self._device_info:
                    del self._device_info[device_id]
                
                if self._current_device_id == device_id:
                    self._current_device_id = None
                    
                # Stop updates if no devices connected
                if not self._connected_devices and self._update_timer.isActive():
                    self._update_timer.stop()
                
                self.device_disconnected.emit(device_id)
                
            except Exception as e:
                print(f"Error disconnecting from {device_id}: {e}")
    
    def get_current_device(self) -> Optional[AppleTV]:
        """Get the currently selected device."""
        if self._current_device_id and self._current_device_id in self._connected_devices:
            return self._connected_devices[self._current_device_id]
        return None
    
    def set_current_device(self, device_id: str):
        """Set the current active device."""
        if device_id in self._connected_devices:
            self._current_device_id = device_id
            self.config_manager.set('last_device', device_id)
    
    def get_connected_devices(self) -> Dict[str, Dict[str, Any]]:
        """Get all connected devices with their info."""
        return {device_id: self._device_info[device_id] 
                for device_id in self._connected_devices.keys() 
                if device_id in self._device_info}
    
    # Remote control methods
    async def remote_up(self):
        """Send up button press."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.up()
    
    async def remote_down(self):
        """Send down button press."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.down()
    
    async def remote_left(self):
        """Send left button press."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.left()
    
    async def remote_right(self):
        """Send right button press."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.right()
    
    async def remote_select(self):
        """Send select button press."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.select()
    
    async def remote_menu(self):
        """Send menu button press."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.menu()
    
    async def remote_home(self):
        """Send home button press."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.home()
    
    async def remote_play_pause(self):
        """Send play/pause button press."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.play_pause()
    
    async def remote_volume_up(self):
        """Send volume up."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.volume_up()
    
    async def remote_volume_down(self):
        """Send volume down."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.volume_down()
    
    # Playback control methods
    async def play(self):
        """Start playback."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.play()
    
    async def pause(self):
        """Pause playback."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.pause()
    
    async def next_track(self):
        """Skip to next track."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.next()
    
    async def previous_track(self):
        """Skip to previous track."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.previous()
    
    async def set_position(self, position: float):
        """Set playback position in seconds."""
        atv = self.get_current_device()
        if atv:
            await atv.remote_control.set_position(position)
    
    async def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)."""
        atv = self.get_current_device()
        if atv:
            # Convert to percentage for pyatv
            await atv.remote_control.set_volume(volume * 100)
    
    @qasync.asyncSlot()
    async def _update_now_playing(self):
        """Update now playing information."""
        if self._current_device_id:
            await self._async_update_now_playing()
    
    async def _async_update_now_playing(self):
        """Async method to update now playing info."""
        try:
            atv = self.get_current_device()
            if not atv:
                return
            
            # Get now playing info
            playing = await atv.metadata.playing()
            
            now_playing_info = {
                'device_id': self._current_device_id,
                'title': playing.title or 'Unknown',
                'artist': playing.artist or 'Unknown Artist',
                'album': playing.album or 'Unknown Album',
                'artwork_url': str(playing.artwork_url) if playing.artwork_url else None,
                'position': playing.position or 0,
                'total_time': playing.total_time or 0,
                'device_state': playing.device_state.value if playing.device_state else 'unknown',
                'media_type': playing.media_type.value if playing.media_type else 'unknown',
                'play_state': playing.play_state.value if playing.play_state else 'unknown',
                'repeat': playing.repeat.value if playing.repeat else 'off',
                'shuffle': playing.shuffle.value if playing.shuffle else 'off'
            }
            
            self.now_playing_updated.emit(now_playing_info)
            
        except Exception as e:
            print(f"Failed to update now playing: {e}")
    
    async def get_artwork(self) -> Optional[bytes]:
        """Get current artwork as bytes."""
        try:
            atv = self.get_current_device()
            if atv:
                playing = await atv.metadata.playing()
                if playing.artwork:
                    return await playing.artwork()
        except Exception as e:
            print(f"Failed to get artwork: {e}")
        return None