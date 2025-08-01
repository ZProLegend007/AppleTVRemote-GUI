"""Pairing manager for handling Apple TV/HomePod device pairing."""

import asyncio
from typing import Optional, Callable, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal
import pyatv
from pyatv.interface import PairingHandler
from .config_manager import ConfigManager

class PairingManager(QObject):
    """Manages device pairing operations."""
    
    # Signals
    pairing_started = pyqtSignal(str)  # device_id
    pairing_pin_required = pyqtSignal(str, str)  # device_id, service_type
    pairing_device_code_required = pyqtSignal(str, str)  # device_id, code
    pairing_progress = pyqtSignal(str, str)  # device_id, message
    pairing_completed = pyqtSignal(str, dict)  # device_id, credentials
    pairing_failed = pyqtSignal(str, str)  # device_id, error
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self._pairing_handlers: Dict[str, PairingHandler] = {}
        self._pending_pins: Dict[str, str] = {}
    
    async def start_pairing(self, device_id: str, device_config: Dict[str, Any]):
        """Start pairing process for a device."""
        try:
            self.pairing_started.emit(device_id)
            
            # Create config from device info
            config = pyatv.conf.AppleTVConf(
                identifier=device_config.get('identifier', device_id),
                name=device_config.get('name', 'Apple TV'),
                address=device_config['address'],
                services=[]
            )
            
            # Add services
            for service_info in device_config.get('services', []):
                service = pyatv.conf.ManualService(
                    identifier=service_info.get('identifier'),
                    protocol=pyatv.const.Protocol(service_info['protocol']),
                    port=service_info['port'],
                    properties=service_info.get('properties', {})
                )
                config.add_service(service)
            
            # Start pairing for each service that requires it
            credentials = {}
            
            for service in config.services:
                if service.protocol in [pyatv.const.Protocol.MRP, pyatv.const.Protocol.Companion]:
                    try:
                        self.pairing_progress.emit(device_id, f"Pairing {service.protocol.name} service...")
                        
                        handler = await pyatv.pair(config, service.protocol, loop=asyncio.get_event_loop())
                        self._pairing_handlers[f"{device_id}_{service.protocol.name}"] = handler
                        
                        # Begin pairing
                        handler.device_provides_pin = True
                        await handler.begin()
                        
                        if handler.has_paired:
                            # Already paired
                            credentials[service.protocol.name] = handler.service.credentials
                        else:
                            # Need user interaction
                            if service.protocol == pyatv.const.Protocol.Companion:
                                # Device code pairing
                                device_code = await self._get_device_code(handler)
                                if device_code:
                                    self.pairing_device_code_required.emit(device_id, device_code)
                                    
                                    # Wait for user to confirm on device
                                    await self._wait_for_device_confirmation(handler)
                                    
                                    if handler.has_paired:
                                        credentials[service.protocol.name] = handler.service.credentials
                                    else:
                                        raise Exception("Device code pairing failed")
                            else:
                                # PIN pairing
                                self.pairing_pin_required.emit(device_id, service.protocol.name)
                                
                                # Wait for PIN input
                                pin = await self._wait_for_pin(device_id, service.protocol.name)
                                if pin:
                                    handler.pin(pin)
                                    await handler.finish()
                                    
                                    if handler.has_paired:
                                        credentials[service.protocol.name] = handler.service.credentials
                                    else:
                                        raise Exception("PIN pairing failed")
                                else:
                                    raise Exception("PIN not provided")
                    
                    except Exception as e:
                        print(f"Failed to pair {service.protocol.name}: {e}")
                        continue
            
            if credentials:
                # Store credentials
                self.config_manager.store_credentials(device_id, credentials)
                self.pairing_completed.emit(device_id, credentials)
            else:
                self.pairing_failed.emit(device_id, "No services could be paired")
        
        except Exception as e:
            self.pairing_failed.emit(device_id, str(e))
        finally:
            # Clean up handlers
            keys_to_remove = [k for k in self._pairing_handlers.keys() if k.startswith(device_id)]
            for key in keys_to_remove:
                handler = self._pairing_handlers.pop(key)
                try:
                    await handler.close()
                except:
                    pass
    
    async def _get_device_code(self, handler: PairingHandler) -> Optional[str]:
        """Get device code for Companion protocol pairing."""
        try:
            # This would typically display a code on the Apple TV
            # For now, we'll simulate getting the code
            await asyncio.sleep(1)  # Simulate API call
            return "1234"  # Placeholder - real implementation would get this from the device
        except Exception:
            return None
    
    async def _wait_for_device_confirmation(self, handler: PairingHandler):
        """Wait for user to confirm pairing on the device."""
        # Poll for pairing completion
        for _ in range(60):  # Wait up to 60 seconds
            if handler.has_paired:
                break
            await asyncio.sleep(1)
    
    async def _wait_for_pin(self, device_id: str, service_type: str) -> Optional[str]:
        """Wait for PIN input from user."""
        key = f"{device_id}_{service_type}"
        
        # Wait for PIN to be provided
        for _ in range(60):  # Wait up to 60 seconds
            if key in self._pending_pins:
                return self._pending_pins.pop(key)
            await asyncio.sleep(1)
        
        return None
    
    def provide_pin(self, device_id: str, service_type: str, pin: str):
        """Provide PIN for pairing."""
        key = f"{device_id}_{service_type}"
        self._pending_pins[key] = pin
    
    def cancel_pairing(self, device_id: str):
        """Cancel ongoing pairing for a device."""
        keys_to_remove = [k for k in self._pairing_handlers.keys() if k.startswith(device_id)]
        for key in keys_to_remove:
            handler = self._pairing_handlers.pop(key)
            asyncio.create_task(self._close_handler(handler))
        
        # Remove any pending PINs
        pin_keys_to_remove = [k for k in self._pending_pins.keys() if k.startswith(device_id)]
        for key in pin_keys_to_remove:
            del self._pending_pins[key]
    
    async def _close_handler(self, handler: PairingHandler):
        """Safely close a pairing handler."""
        try:
            await handler.close()
        except Exception as e:
            print(f"Error closing pairing handler: {e}")