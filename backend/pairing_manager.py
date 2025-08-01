#!/usr/bin/env python3
import subprocess

class PairingManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def pair_device(self, device_id):
        """Pair with Apple TV device"""
        try:
            cmd = ['atvremote', '--id', device_id, 'pair']
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Pairing error: {e}")
            return False
    
    def get_paired_devices(self):
        """Get list of paired devices"""
        return self.config_manager.get('devices', [])