import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    print("Warning: keyring not available, using file-based storage for credentials")

class ConfigManager:
    """Manages application configuration and secure credential storage"""
    
    def __init__(self):
        self.app_name = "ApplerGUI"
        self.config_dir = Path.home() / ".config" / "applergui"
        self.config_file = self.config_dir / "config.json"
        self.credentials_file = self.config_dir / "credentials.json"
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        logging.info(f"ConfigManager initialized with config dir: {self.config_dir}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logging.error(f"Failed to load config: {e}")
        
        # Return default configuration
        return {
            "discovery": {
                "timeout": 10,
                "auto_refresh": False,
                "refresh_interval": 30
            },
            "ui": {
                "theme": "system",
                "window_geometry": None,
                "splitter_state": None
            },
            "devices": {
                "auto_connect": False,
                "remember_devices": True
            }
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logging.info("Configuration saved successfully")
        except IOError as e:
            logging.error(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        self.save_config()
    
    def store_credential(self, service: str, username: str, password: str):
        """Store credential securely"""
        if KEYRING_AVAILABLE:
            try:
                keyring.set_password(f"{self.app_name}_{service}", username, password)
                logging.info(f"Credential stored in keyring for {service}")
                return
            except Exception as e:
                logging.warning(f"Failed to store in keyring: {e}, falling back to file storage")
        
        # Fallback to file storage (less secure but functional)
        self._store_credential_file(service, username, password)
    
    def get_credential(self, service: str, username: str) -> Optional[str]:
        """Retrieve credential securely"""
        if KEYRING_AVAILABLE:
            try:
                password = keyring.get_password(f"{self.app_name}_{service}", username)
                if password:
                    return password
            except Exception as e:
                logging.warning(f"Failed to retrieve from keyring: {e}, trying file storage")
        
        # Fallback to file storage
        return self._get_credential_file(service, username)
    
    def _store_credential_file(self, service: str, username: str, password: str):
        """Store credential in file (fallback method)"""
        credentials = {}
        credentials_file = Path(self.credentials_file)
        if credentials_file.exists():
            try:
                with open(credentials_file, 'r') as f:
                    credentials = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        if service not in credentials:
            credentials[service] = {}
        
        # Basic encoding (not secure, but functional)
        import base64
        encoded_password = base64.b64encode(password.encode()).decode()
        credentials[service][username] = encoded_password
        
        try:
            with open(credentials_file, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            # Restrict file permissions
            os.chmod(credentials_file, 0o600)
            logging.info(f"Credential stored in file for {service}")
        except IOError as e:
            logging.error(f"Failed to store credential in file: {e}")
    
    def _get_credential_file(self, service: str, username: str) -> Optional[str]:
        """Retrieve credential from file (fallback method)"""
        credentials_file = Path(self.credentials_file)
        if not credentials_file.exists():
            return None
        
        try:
            with open(credentials_file, 'r') as f:
                credentials = json.load(f)
            
            if service in credentials and username in credentials[service]:
                # Basic decoding
                import base64
                encoded_password = credentials[service][username]
                return base64.b64decode(encoded_password.encode()).decode()
        except (json.JSONDecodeError, IOError, Exception) as e:
            logging.error(f"Failed to retrieve credential from file: {e}")
        
        return None
    
    def delete_credential(self, service: str, username: str):
        """Delete stored credential"""
        if KEYRING_AVAILABLE:
            try:
                keyring.delete_password(f"{self.app_name}_{service}", username)
                logging.info(f"Credential deleted from keyring for {service}")
                return
            except Exception as e:
                logging.warning(f"Failed to delete from keyring: {e}")
        
        # Delete from file storage
        self._delete_credential_file(service, username)
    
    def _delete_credential_file(self, service: str, username: str):
        """Delete credential from file"""
        credentials_file = Path(self.credentials_file)
        if not credentials_file.exists():
            return
        
        try:
            with open(credentials_file, 'r') as f:
                credentials = json.load(f)
            
            if service in credentials and username in credentials[service]:
                del credentials[service][username]
                
                # Remove empty service sections
                if not credentials[service]:
                    del credentials[service]
                
                with open(credentials_file, 'w') as f:
                    json.dump(credentials, f, indent=2)
                
                logging.info(f"Credential deleted from file for {service}")
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Failed to delete credential from file: {e}")