#!/usr/bin/env python3
import subprocess
import json

class DeviceController:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.current_device = None
    
    def send_command(self, command, device_id=None):
        """Send command to Apple TV device"""
        try:
            if device_id:
                cmd = ['atvremote', '--id', device_id, command]
            else:
                cmd = ['atvremote', command]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Command error: {e}")
            return False
    
    def navigate_up(self):
        return self.send_command('up')
    
    def navigate_down(self):
        return self.send_command('down')
    
    def navigate_left(self):
        return self.send_command('left')
    
    def navigate_right(self):
        return self.send_command('right')
    
    def select(self):
        return self.send_command('select')
    
    def menu(self):
        return self.send_command('menu')
    
    def home(self):
        return self.send_command('home')
    
    def play_pause(self):
        return self.send_command('play_pause')
    
    def volume_up(self):
        return self.send_command('volume_up')
    
    def volume_down(self):
        return self.send_command('volume_down')