"""
Phone Emulator
Simulates a mobile device with realistic behavior
"""

import random
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from ..models.device import Device, DeviceType, ConnectionType, FileInfo, Contact, CalendarEvent
from ..models.device import DeviceInfo


class PhoneEmulator(Device):
    """Phone device emulator"""
    
    def __init__(self, config):
        super().__init__(DeviceType.PHONE, "SmartPhone Pro", "SP-2024")
        self.config = config
        
        # Phone-specific properties
        self.battery_level = 85
        self.is_charging = False
        self.signal_strength = 4  # 1-5 bars
        self.network_type = "5G"
        self.storage_capacity = 128 * 1024 * 1024 * 1024  # 128 GB
        self.used_storage = 64 * 1024 * 1024 * 1024  # 64 GB used
        
        # Simulate realistic phone data
        self._populate_sample_data()
        
        # Background processes
        self._battery_thread = None
        self._signal_thread = None
        self._start_background_processes()
    
    def _populate_sample_data(self):
        """Populate the phone with sample data"""
        # Sample files
        file_types = ["jpg", "mp4", "mp3", "pdf", "doc", "txt"]
        file_sizes = [1024 * 1024, 5 * 1024 * 1024, 10 * 1024 * 1024, 50 * 1024 * 1024]
        
        for i in range(500):
            file_type = random.choice(file_types)
            file_size = random.choice(file_sizes)
            
            file_info = FileInfo(
                name=f"file_{i:04d}.{file_type}",
                path=f"/storage/emulated/0/DCIM/file_{i:04d}.{file_type}",
                size=file_size,
                modified_date=(datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                created_date=(datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
                file_type=file_type,
                checksum=f"hash_{i:08x}",
                is_synced=random.choice([True, False]),
                sync_priority=random.randint(1, 10)
            )
            self.add_file(file_info)
        
        # Sample contacts
        first_names = ["John", "Jane", "Mike", "Sarah", "David", "Lisa", "Tom", "Emma"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
        companies = ["Tech Corp", "Innovation Inc", "Global Solutions", "Startup Co"]
        
        for i in range(200):
            contact = Contact(
                id=f"contact_{i:04d}",
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                phone_numbers=[f"+1-555-{random.randint(100, 999):03d}-{random.randint(1000, 9999):04d}"],
                email_addresses=[f"{random.choice(first_names).lower()}.{random.choice(last_names).lower()}@email.com"],
                company=random.choice(companies),
                job_title=random.choice(["Manager", "Developer", "Designer", "Analyst", "Engineer"]),
                notes=f"Contact note {i}",
                is_synced=random.choice([True, False]),
                last_modified=(datetime.now() - timedelta(days=random.randint(0, 7))).isoformat()
            )
            self.add_contact(contact)
        
        # Sample calendar events
        event_titles = ["Meeting", "Appointment", "Conference", "Lunch", "Call", "Review"]
        locations = ["Office", "Conference Room", "Restaurant", "Home", "Client Site"]
        
        for i in range(100):
            start_date = datetime.now() + timedelta(days=random.randint(-30, 30))
            end_date = start_date + timedelta(hours=random.randint(1, 4))
            
            event = CalendarEvent(
                id=f"event_{i:04d}",
                title=f"{random.choice(event_titles)} {i}",
                description=f"Event description for event {i}",
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                location=random.choice(locations),
                attendees=[f"attendee_{j}@email.com" for j in range(random.randint(1, 5))],
                reminder_time=(start_date - timedelta(minutes=30)).isoformat(),
                is_synced=random.choice([True, False]),
                last_modified=(datetime.now() - timedelta(days=random.randint(0, 3))).isoformat()
            )
            self.add_calendar_event(event)
    
    def _start_background_processes(self):
        """Start background processes that simulate real phone behavior"""
        self._battery_thread = threading.Thread(target=self._battery_simulation, daemon=True)
        self._signal_thread = threading.Thread(target=self._signal_simulation, daemon=True)
        
        self._battery_thread.start()
        self._signal_thread.start()
    
    def _battery_simulation(self):
        """Simulate battery drain and charging"""
        while True:
            try:
                time.sleep(30)  # Update every 30 seconds
                
                if self.is_charging:
                    # Charging - increase battery
                    if self.battery_level < 100:
                        self.battery_level = min(100, self.battery_level + random.randint(1, 3))
                else:
                    # Not charging - decrease battery
                    if self.battery_level > 0:
                        drain_rate = random.randint(1, 3)
                        if self.is_connected:
                            drain_rate = max(1, drain_rate - 1)  # Less drain when connected
                        self.battery_level = max(0, self.battery_level - drain_rate)
                
                # Random charging state changes
                if random.random() < 0.01:  # 1% chance
                    self.is_charging = not self.is_charging
                    
            except Exception as e:
                print(f"Error in battery simulation: {e}")
                time.sleep(60)
    
    def _signal_simulation(self):
        """Simulate signal strength changes"""
        while True:
            try:
                time.sleep(45)  # Update every 45 seconds
                
                # Random signal changes
                if random.random() < 0.3:  # 30% chance
                    change = random.choice([-1, 0, 1])
                    self.signal_strength = max(1, min(5, self.signal_strength + change))
                
                # Network type changes (rare)
                if random.random() < 0.001:  # 0.1% chance
                    self.network_type = random.choice(["4G", "5G", "WiFi"])
                    
            except Exception as e:
                print(f"Error in signal simulation: {e}")
                time.sleep(60)
    
    def connect(self, connection_type: ConnectionType, speed: float = 100.0):
        """Connect the phone with realistic behavior"""
        super().connect(connection_type, speed)
        
        # Simulate connection delay
        time.sleep(random.uniform(0.5, 2.0))
        
        # Update device state
        self.signal_strength = 5  # Full signal when connected
        self.network_type = "USB" if connection_type == ConnectionType.USB else "WiFi"
        
        # Add connection record
        self.add_sync_record({
            "timestamp": datetime.now().isoformat(),
            "event": "device_connected",
            "connection_type": connection_type.value,
            "speed": speed
        })
    
    def disconnect(self):
        """Disconnect the phone"""
        super().disconnect()
        
        # Simulate disconnection delay
        time.sleep(random.uniform(0.2, 1.0))
        
        # Add disconnection record
        self.add_sync_record({
            "timestamp": datetime.now().isoformat(),
            "event": "device_disconnected"
        })
    
    def get_storage_info(self) -> Dict:
        """Get detailed storage information"""
        return {
            "total_capacity": self.storage_capacity,
            "used_storage": self.used_storage,
            "free_storage": self.storage_capacity - self.used_storage,
            "usage_percentage": (self.used_storage / self.storage_capacity) * 100,
            "photos_size": sum(f.size for f in self.get_files() if f.file_type in ["jpg", "png", "mp4"]),
            "documents_size": sum(f.size for f in self.get_files() if f.file_type in ["pdf", "doc", "txt"]),
            "music_size": sum(f.size for f in self.get_files() if f.file_type in ["mp3", "wav", "flac"])
        }
    
    def get_network_info(self) -> Dict:
        """Get network information"""
        return {
            "signal_strength": self.signal_strength,
            "network_type": self.network_type,
            "connection_type": self.connection_type.value if self.connection_type else None,
            "connection_speed": self.connection_speed,
            "is_connected": self.is_connected
        }
    
    def get_battery_info(self) -> Dict:
        """Get battery information"""
        return {
            "level": self.battery_level,
            "is_charging": self.is_charging,
            "estimated_time": self._estimate_battery_time()
        }
    
    def _estimate_battery_time(self) -> str:
        """Estimate remaining battery time"""
        if self.is_charging:
            if self.battery_level >= 100:
                return "Fully charged"
            else:
                remaining = 100 - self.battery_level
                minutes = remaining * 2  # Rough estimate
                return f"Charging: {minutes} minutes remaining"
        else:
            if self.battery_level <= 0:
                return "Battery dead"
            else:
                # Rough estimate based on usage
                hours = self.battery_level // 10
                return f"{hours} hours remaining"
    
    def simulate_file_changes(self):
        """Simulate file changes (new files, modifications)"""
        # Add new files occasionally
        if random.random() < 0.1:  # 10% chance
            file_types = ["jpg", "mp4", "mp3", "pdf"]
            file_type = random.choice(file_types)
            file_size = random.randint(1024 * 1024, 10 * 1024 * 1024)
            
            new_file = FileInfo(
                name=f"new_file_{int(time.time())}.{file_type}",
                path=f"/storage/emulated/0/DCIM/new_file_{int(time.time())}.{file_type}",
                size=file_size,
                modified_date=datetime.now().isoformat(),
                created_date=datetime.now().isoformat(),
                file_type=file_type,
                checksum=f"new_hash_{int(time.time()):08x}",
                is_synced=False,
                sync_priority=random.randint(1, 10)
            )
            self.add_file(new_file)
            
            # Update storage
            self.used_storage += file_size
    
    def _get_manufacturer(self) -> str:
        return "TechCorp"
    
    def _get_os_version(self) -> str:
        return "Android 14.0"
    
    def _get_firmware_version(self) -> str:
        return "v2.1.4"
    
    def _get_serial_number(self) -> str:
        return f"SP{random.randint(100000, 999999)}"
    
    def _get_capacity(self) -> int:
        return self.storage_capacity
    
    def _get_free_space(self) -> int:
        return self.storage_capacity - self.used_storage
    
    def _get_battery_level(self) -> int:
        return self.battery_level
    
    def _get_charging_status(self) -> bool:
        return self.is_charging
    
    def _get_last_seen(self) -> str:
        return datetime.now().isoformat()