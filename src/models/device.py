"""
Device models for phone and PC
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import uuid


class DeviceType(Enum):
    """Device types"""
    PHONE = "phone"
    PC = "pc"
    TABLET = "tablet"
    SMARTWATCH = "smartwatch"


class ConnectionType(Enum):
    """Connection types"""
    USB = "usb"
    BLUETOOTH = "bluetooth"
    WIFI = "wifi"
    NFC = "nfc"


@dataclass
class DeviceInfo:
    """Device information"""
    id: str
    name: str
    model: str
    manufacturer: str
    device_type: DeviceType
    os_version: str
    firmware_version: str
    serial_number: str
    capacity: int  # in bytes
    free_space: int  # in bytes
    battery_level: int  # percentage
    is_charging: bool
    connection_type: ConnectionType
    connection_speed: float  # in Mbps
    last_seen: str
    is_connected: bool


@dataclass
class FileInfo:
    """File information"""
    name: str
    path: str
    size: int  # in bytes
    modified_date: str
    created_date: str
    file_type: str
    checksum: str
    is_synced: bool
    sync_priority: int  # 1-10, higher is more important


@dataclass
class Contact:
    """Contact information"""
    id: str
    first_name: str
    last_name: str
    phone_numbers: List[str]
    email_addresses: List[str]
    company: str
    job_title: str
    notes: str
    is_synced: bool
    last_modified: str


@dataclass
class CalendarEvent:
    """Calendar event information"""
    id: str
    title: str
    description: str
    start_date: str
    end_date: str
    location: str
    attendees: List[str]
    reminder_time: str
    is_synced: bool
    last_modified: str


class Device:
    """Base device class"""
    
    def __init__(self, device_type: DeviceType, name: str, model: str):
        self.device_type = device_type
        self.name = name
        self.model = model
        self.id = str(uuid.uuid4())
        self.is_connected = False
        self.connection_type = None
        self.connection_speed = 0.0
        
        # Device state
        self._files: Dict[str, FileInfo] = {}
        self._contacts: Dict[str, Contact] = {}
        self._calendar_events: Dict[str, CalendarEvent] = {}
        
        # Performance metrics
        self._sync_history: List[Dict] = []
        self._error_log: List[str] = []
    
    def connect(self, connection_type: ConnectionType, speed: float = 100.0):
        """Connect the device"""
        self.is_connected = True
        self.connection_type = connection_type
        self.connection_speed = speed
    
    def disconnect(self):
        """Disconnect the device"""
        self.is_connected = False
        self.connection_type = None
        self.connection_speed = 0.0
    
    def get_device_info(self) -> DeviceInfo:
        """Get comprehensive device information"""
        return DeviceInfo(
            id=self.id,
            name=self.name,
            model=self.model,
            manufacturer=self._get_manufacturer(),
            device_type=self.device_type,
            os_version=self._get_os_version(),
            firmware_version=self._get_firmware_version(),
            serial_number=self._get_serial_number(),
            capacity=self._get_capacity(),
            free_space=self._get_free_space(),
            battery_level=self._get_battery_level(),
            is_charging=self._get_charging_status(),
            connection_type=self.connection_type,
            connection_speed=self.connection_speed,
            last_seen=self._get_last_seen(),
            is_connected=self.is_connected
        )
    
    def add_file(self, file_info: FileInfo):
        """Add a file to the device"""
        self._files[file_info.path] = file_info
    
    def remove_file(self, file_path: str):
        """Remove a file from the device"""
        if file_path in self._files:
            del self._files[file_path]
    
    def get_files(self, path: str = "/") -> List[FileInfo]:
        """Get files from a specific path"""
        if path == "/":
            return list(self._files.values())
        
        return [f for f in self._files.values() if f.path.startswith(path)]
    
    def add_contact(self, contact: Contact):
        """Add a contact to the device"""
        self._contacts[contact.id] = contact
    
    def get_contacts(self) -> List[Contact]:
        """Get all contacts"""
        return list(self._contacts.values())
    
    def add_calendar_event(self, event: CalendarEvent):
        """Add a calendar event to the device"""
        self._calendar_events[event.id] = event
    
    def get_calendar_events(self) -> List[CalendarEvent]:
        """Get all calendar events"""
        return list(self._calendar_events.values())
    
    def get_sync_history(self) -> List[Dict]:
        """Get synchronization history"""
        return self._sync_history.copy()
    
    def add_sync_record(self, sync_data: Dict):
        """Add a synchronization record"""
        self._sync_history.append(sync_data)
    
    def get_error_log(self) -> List[str]:
        """Get error log"""
        return self._error_log.copy()
    
    def add_error(self, error_message: str):
        """Add an error to the log"""
        self._error_log.append(error_message)
    
    # Abstract methods to be implemented by subclasses
    def _get_manufacturer(self) -> str:
        raise NotImplementedError
    
    def _get_os_version(self) -> str:
        raise NotImplementedError
    
    def _get_firmware_version(self) -> str:
        raise NotImplementedError
    
    def _get_serial_number(self) -> str:
        raise NotImplementedError
    
    def _get_capacity(self) -> int:
        raise NotImplementedError
    
    def _get_free_space(self) -> int:
        raise NotImplementedError
    
    def _get_battery_level(self) -> int:
        raise NotImplementedError
    
    def _get_charging_status(self) -> bool:
        raise NotImplementedError
    
    def _get_last_seen(self) -> str:
        raise NotImplementedError