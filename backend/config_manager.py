"""Configuration manager for storing and retrieving application settings."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import keyring

class ConfigManager:
    """Manages application configuration and credentials."""
    
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'appletv-remote-gui'
        self.config_file = self.config_dir / 'config.json'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        default_config = {
            'theme': 'dark',
            'auto_discover': True,
            'discovery_timeout': 10,
            'connection_timeout': 15,
            'debug_logging': False,
            'known_devices': {},
            'window_geometry': None,
            'last_device': None
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                default_config.update(config)
                return default_config
            except (json.JSONDecodeError, IOError):
                pass
        
        return default_config
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except IOError as e:
            print(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self._config[key] = value
        self.save_config()
    
    def add_known_device(self, device_id: str, device_info: Dict[str, Any]):
        """Add a known device to the configuration."""
        known_devices = self._config.get('known_devices', {})
        known_devices[device_id] = device_info
        self.set('known_devices', known_devices)
    
    def get_known_devices(self) -> Dict[str, Dict[str, Any]]:
        """Get all known devices."""
        return self._config.get('known_devices', {})
    
    def remove_known_device(self, device_id: str):
        """Remove a known device."""
        known_devices = self._config.get('known_devices', {})
        if device_id in known_devices:
            del known_devices[device_id]
            self.set('known_devices', known_devices)
    
    def store_credentials(self, device_id: str, credentials: Dict[str, str]):
        """Store device credentials securely using keyring."""
        try:
            cred_json = json.dumps(credentials)
            keyring.set_password('appletv-remote-gui', device_id, cred_json)
            return True
        except Exception as e:
            print(f"Failed to store credentials for {device_id}: {e}")
            return False
    
    def get_credentials(self, device_id: str) -> Optional[Dict[str, str]]:
        """Retrieve device credentials from keyring."""
        try:
            cred_json = keyring.get_password('appletv-remote-gui', device_id)
            if cred_json:
                return json.loads(cred_json)
        except Exception as e:
            print(f"Failed to retrieve credentials for {device_id}: {e}")
        return None
    
    def delete_credentials(self, device_id: str):
        """Delete device credentials from keyring."""
        try:
            keyring.delete_password('appletv-remote-gui', device_id)
        except Exception as e:
            print(f"Failed to delete credentials for {device_id}: {e}")