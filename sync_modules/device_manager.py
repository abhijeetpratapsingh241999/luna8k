"""
Device Manager Module
Handles device detection, connection, and status monitoring.
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
import random

class DeviceInfo:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name', 'Unknown Device')
        self.model = kwargs.get('model', 'Unknown Model')
        self.manufacturer = kwargs.get('manufacturer', 'Unknown')
        self.os_type = kwargs.get('os_type', 'Unknown')  # 'iOS', 'Android', 'Windows', 'macOS'
        self.os_version = kwargs.get('os_version', 'Unknown')
        self.serial_number = kwargs.get('serial_number', '')
        self.imei = kwargs.get('imei', '')  # For mobile devices
        self.mac_address = kwargs.get('mac_address', '')
        self.connection_type = kwargs.get('connection_type', 'Unknown')  # 'USB', 'WiFi', 'Bluetooth'
        self.connection_status = kwargs.get('connection_status', 'disconnected')
        self.battery_level = kwargs.get('battery_level', 0)
        self.battery_charging = kwargs.get('battery_charging', False)
        self.storage_total = kwargs.get('storage_total', 0)  # in bytes
        self.storage_available = kwargs.get('storage_available', 0)  # in bytes
        self.last_seen = kwargs.get('last_seen', datetime.now())
        self.is_trusted = kwargs.get('is_trusted', False)
        self.sync_enabled = kwargs.get('sync_enabled', True)
        
    def to_dict(self) -> Dict:
        """Convert device info to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'model': self.model,
            'manufacturer': self.manufacturer,
            'os_type': self.os_type,
            'os_version': self.os_version,
            'serial_number': self.serial_number,
            'imei': self.imei,
            'mac_address': self.mac_address,
            'connection_type': self.connection_type,
            'connection_status': self.connection_status,
            'battery_level': self.battery_level,
            'battery_charging': self.battery_charging,
            'storage_total': self.storage_total,
            'storage_available': self.storage_available,
            'last_seen': self.last_seen.isoformat(),
            'is_trusted': self.is_trusted,
            'sync_enabled': self.sync_enabled
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'DeviceInfo':
        """Create device info from dictionary"""
        if 'last_seen' in data and data['last_seen']:
            try:
                data['last_seen'] = datetime.fromisoformat(data['last_seen'])
            except ValueError:
                data['last_seen'] = datetime.now()
        return cls(**data)
        
    def get_storage_usage_percent(self) -> float:
        """Get storage usage percentage"""
        if self.storage_total == 0:
            return 0.0
        return ((self.storage_total - self.storage_available) / self.storage_total) * 100
        
    def get_storage_available_gb(self) -> float:
        """Get available storage in GB"""
        return self.storage_available / (1024**3)
        
    def get_storage_total_gb(self) -> float:
        """Get total storage in GB"""
        return self.storage_total / (1024**3)
        
    def is_connected(self) -> bool:
        """Check if device is connected"""
        return self.connection_status == 'connected'
        
    def is_low_battery(self) -> bool:
        """Check if device has low battery"""
        return self.battery_level < 20
        
    def is_low_storage(self) -> bool:
        """Check if device has low storage"""
        return self.get_storage_usage_percent() > 90

class DeviceConnection:
    def __init__(self, device: DeviceInfo):
        self.device = device
        self.connection_time = datetime.now()
        self.last_activity = datetime.now()
        self.transfer_speed = 0  # bytes per second
        self.is_secure = False
        self.encryption_type = 'none'
        self.sync_progress = 0
        self.sync_status = 'idle'  # 'idle', 'syncing', 'completed', 'failed'
        
    def update_activity(self):
        """Update last activity time"""
        self.last_activity = datetime.now()
        
    def get_connection_duration(self) -> timedelta:
        """Get duration of current connection"""
        return datetime.now() - self.connection_time
        
    def is_active(self, timeout_minutes: int = 5) -> bool:
        """Check if connection is still active"""
        return (datetime.now() - self.last_activity).total_seconds() < (timeout_minutes * 60)

class DeviceManager:
    def __init__(self):
        self.devices: List[DeviceInfo] = []
        self.active_connections: List[DeviceConnection] = []
        self.device_callbacks: List[Callable] = []
        self.scan_interval = 30  # seconds
        self.is_scanning = False
        self.scan_thread = None
        
        # Load known devices
        self._load_known_devices()
        
        # Start device scanning
        self.start_device_scanning()
        
    def _load_known_devices(self):
        """Load known devices from storage"""
        try:
            # For demo purposes, create some sample devices
            sample_devices = [
                DeviceInfo(
                    id='iphone_15_pro',
                    name='iPhone 15 Pro',
                    model='A3102',
                    manufacturer='Apple',
                    os_type='iOS',
                    os_version='17.2',
                    serial_number='FVFQ123456789',
                    imei='123456789012345',
                    mac_address='00:11:22:33:44:55',
                    connection_type='USB',
                    connection_status='disconnected',
                    battery_level=87,
                    battery_charging=False,
                    storage_total=128 * (1024**3),  # 128GB
                    storage_available=45 * (1024**3),  # 45GB
                    is_trusted=True
                ),
                DeviceInfo(
                    id='samsung_galaxy_s24',
                    name='Samsung Galaxy S24',
                    model='SM-S921B',
                    manufacturer='Samsung',
                    os_type='Android',
                    os_version='14.0',
                    serial_number='RF8Q123456789',
                    imei='987654321098765',
                    mac_address='AA:BB:CC:DD:EE:FF',
                    connection_type='WiFi',
                    connection_status='disconnected',
                    battery_level=65,
                    battery_charging=True,
                    storage_total=256 * (1024**3),  # 256GB
                    storage_available=120 * (1024**3),  # 120GB
                    is_trusted=True
                )
            ]
            
            self.devices.extend(sample_devices)
            
        except Exception as e:
            print(f"Error loading known devices: {e}")
            
    def start_device_scanning(self):
        """Start background device scanning"""
        if not self.is_scanning:
            self.is_scanning = True
            self.scan_thread = threading.Thread(target=self._scan_devices_loop, daemon=True)
            self.scan_thread.start()
            
    def stop_device_scanning(self):
        """Stop background device scanning"""
        self.is_scanning = False
        if self.scan_thread:
            self.scan_thread.join()
            
    def _scan_devices_loop(self):
        """Main device scanning loop"""
        while self.is_scanning:
            try:
                self._scan_for_devices()
                time.sleep(self.scan_interval)
            except Exception as e:
                print(f"Error in device scanning loop: {e}")
                time.sleep(5)  # Wait before retrying
                
    def _scan_for_devices(self):
        """Scan for available devices"""
        # Simulate device discovery
        for device in self.devices:
            # Simulate connection status changes
            if random.random() > 0.7:  # 30% chance of status change
                old_status = device.connection_status
                
                if device.connection_status == 'disconnected':
                    # Simulate device connection
                    if random.random() > 0.3:  # 70% chance of connecting
                        device.connection_status = 'connected'
                        device.connection_type = random.choice(['USB', 'WiFi', 'Bluetooth'])
                        device.last_seen = datetime.now()
                        
                        # Create connection object
                        connection = DeviceConnection(device)
                        self.active_connections.append(connection)
                        
                        # Notify callbacks
                        self._notify_device_connected(device)
                        
                elif device.connection_status == 'connected':
                    # Simulate device disconnection
                    if random.random() > 0.8:  # 20% chance of disconnecting
                        device.connection_status = 'disconnected'
                        device.last_seen = datetime.now()
                        
                        # Remove connection object
                        self.active_connections = [c for c in self.active_connections if c.device.id != device.id]
                        
                        # Notify callbacks
                        self._notify_device_disconnected(device)
                        
                # Update battery level
                if device.connection_status == 'connected':
                    battery_change = random.randint(-2, 1)
                    device.battery_level = max(0, min(100, device.battery_level + battery_change))
                    
                    # Simulate charging
                    if device.battery_level < 30:
                        device.battery_charging = random.choice([True, False])
                    elif device.battery_level > 90:
                        device.battery_charging = False
                        
                # Update storage (simulate file changes)
                if device.connection_status == 'connected' and random.random() > 0.9:
                    storage_change = random.randint(-100, 50) * (1024**2)  # MB
                    device.storage_available = max(0, device.storage_available + storage_change)
                    
    def add_device_callback(self, callback: Callable):
        """Add callback for device events"""
        self.device_callbacks.append(callback)
        
    def remove_device_callback(self, callback: Callable):
        """Remove device callback"""
        if callback in self.device_callbacks:
            self.device_callbacks.remove(callback)
            
    def _notify_device_connected(self, device: DeviceInfo):
        """Notify callbacks of device connection"""
        for callback in self.device_callbacks:
            try:
                callback('connected', device)
            except Exception as e:
                print(f"Error in device callback: {e}")
                
    def _notify_device_disconnected(self, device: DeviceInfo):
        """Notify callbacks of device disconnection"""
        for callback in self.device_callbacks:
            try:
                callback('disconnected', device)
            except Exception as e:
                print(f"Error in device callback: {e}")
                
    def get_connected_devices(self) -> List[DeviceInfo]:
        """Get list of currently connected devices"""
        return [device for device in self.devices if device.is_connected()]
        
    def get_device_by_id(self, device_id: str) -> Optional[DeviceInfo]:
        """Get device by ID"""
        for device in self.devices:
            if device.id == device_id:
                return device
        return None
        
    def get_device_by_name(self, name: str) -> Optional[DeviceInfo]:
        """Get device by name"""
        for device in self.devices:
            if device.name.lower() == name.lower():
                return device
        return None
        
    def add_device(self, device: DeviceInfo) -> bool:
        """Add a new device"""
        try:
            # Check if device already exists
            if self.get_device_by_id(device.id):
                return False
                
            self.devices.append(device)
            return True
            
        except Exception as e:
            print(f"Error adding device: {e}")
            return False
            
    def remove_device(self, device_id: str) -> bool:
        """Remove a device"""
        try:
            device = self.get_device_by_id(device_id)
            if device:
                # Disconnect if connected
                if device.is_connected():
                    device.connection_status = 'disconnected'
                    self.active_connections = [c for c in self.active_connections if c.device.id != device_id]
                    
                self.devices.remove(device)
                return True
            return False
            
        except Exception as e:
            print(f"Error removing device: {e}")
            return False
            
    def trust_device(self, device_id: str) -> bool:
        """Mark device as trusted"""
        try:
            device = self.get_device_by_id(device_id)
            if device:
                device.is_trusted = True
                return True
            return False
            
        except Exception as e:
            print(f"Error trusting device: {e}")
            return False
            
    def untrust_device(self, device_id: str) -> bool:
        """Mark device as untrusted"""
        try:
            device = self.get_device_by_id(device_id)
            if device:
                device.is_trusted = False
                return True
            return False
            
        except Exception as e:
            print(f"Error untrusting device: {e}")
            return False
            
    def get_device_connection(self, device_id: str) -> Optional[DeviceConnection]:
        """Get connection object for device"""
        for connection in self.active_connections:
            if connection.device.id == device_id:
                return connection
        return None
        
    def update_device_status(self, device_id: str, status_updates: Dict) -> bool:
        """Update device status"""
        try:
            device = self.get_device_by_id(device_id)
            if not device:
                return False
                
            # Update fields
            for key, value in status_updates.items():
                if hasattr(device, key):
                    setattr(device, key, value)
                    
            device.last_seen = datetime.now()
            return True
            
        except Exception as e:
            print(f"Error updating device status: {e}")
            return False
            
    def get_devices_summary(self) -> Dict:
        """Get summary of all devices"""
        total_devices = len(self.devices)
        connected_devices = len(self.get_connected_devices())
        trusted_devices = len([d for d in self.devices if d.is_trusted])
        
        return {
            'total_devices': total_devices,
            'connected_devices': connected_devices,
            'disconnected_devices': total_devices - connected_devices,
            'trusted_devices': trusted_devices,
            'untrusted_devices': total_devices - trusted_devices,
            'last_scan': datetime.now()
        }
        
    def export_devices_list(self, file_path: str) -> bool:
        """Export devices list to JSON file"""
        try:
            devices_data = [device.to_dict() for device in self.devices]
            
            export_data = {
                'export_time': datetime.now().isoformat(),
                'total_devices': len(devices_data),
                'devices': devices_data
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error exporting devices list: {e}")
            return False
            
    def import_devices_list(self, file_path: str) -> Dict:
        """Import devices list from JSON file"""
        import_results = {
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'errors_list': []
        }
        
        try:
            with open(file_path, 'r') as f:
                import_data = json.load(f)
                
            if 'devices' in import_data:
                for device_data in import_data['devices']:
                    try:
                        device = DeviceInfo.from_dict(device_data)
                        
                        # Check if device already exists
                        if not self.get_device_by_id(device.id):
                            if self.add_device(device):
                                import_results['imported'] += 1
                            else:
                                import_results['skipped'] += 1
                        else:
                            import_results['skipped'] += 1
                            
                    except Exception as e:
                        import_results['errors'] += 1
                        import_results['errors_list'].append(f"Device {device_data.get('name', 'Unknown')}: {str(e)}")
                        
        except Exception as e:
            import_results['errors'] += 1
            import_results['errors_list'].append(f"File error: {str(e)}")
            
        return import_results