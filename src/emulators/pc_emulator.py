"""
PC Emulator
Simulates a computer system with realistic behavior
"""

import random
import time
import threading
import psutil
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from ..models.device import Device, DeviceType, ConnectionType, FileInfo, Contact, CalendarEvent
from ..models.device import DeviceInfo


class PCEmulator(Device):
    """PC device emulator"""
    
    def __init__(self, config):
        super().__init__(DeviceType.PC, "Desktop Computer", "DC-2024")
        self.config = config
        
        # PC-specific properties
        self.cpu_usage = 0
        self.memory_usage = 0
        self.disk_usage = 0
        self.network_activity = 0
        self.antivirus_status = "active"
        self.firewall_status = "enabled"
        
        # Storage information
        self.storage_capacity = 1000 * 1024 * 1024 * 1024  # 1 TB
        self.used_storage = 400 * 1024 * 1024 * 1024  # 400 GB used
        
        # Simulate realistic PC data
        self._populate_sample_data()
        
        # Background processes
        self._system_monitor_thread = None
        self._start_background_processes()
    
    def _populate_sample_data(self):
        """Populate the PC with sample data"""
        # Sample files in different directories
        directories = [
            "/Users/Desktop",
            "/Users/Documents",
            "/Users/Pictures",
            "/Users/Music",
            "/Users/Videos",
            "/Users/Downloads"
        ]
        
        file_types = ["jpg", "png", "mp4", "avi", "mp3", "wav", "pdf", "doc", "docx", "xls", "xlsx", "txt"]
        file_sizes = [1024 * 1024, 5 * 1024 * 1024, 10 * 1024 * 1024, 50 * 1024 * 1024, 100 * 1024 * 1024]
        
        for i in range(1000):
            directory = random.choice(directories)
            file_type = random.choice(file_types)
            file_size = random.choice(file_sizes)
            
            file_info = FileInfo(
                name=f"pc_file_{i:04d}.{file_type}",
                path=f"{directory}/pc_file_{i:04d}.{file_type}",
                size=file_size,
                modified_date=(datetime.now() - timedelta(days=random.randint(0, 60))).isoformat(),
                created_date=(datetime.now() - timedelta(days=random.randint(60, 730))).isoformat(),
                file_type=file_type,
                checksum=f"pc_hash_{i:08x}",
                is_synced=random.choice([True, False]),
                sync_priority=random.randint(1, 10)
            )
            self.add_file(file_info)
        
        # Sample contacts (PC contacts are usually business-focused)
        first_names = ["Robert", "Jennifer", "Michael", "Amanda", "Christopher", "Jessica", "Daniel", "Ashley"]
        last_names = ["Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia"]
        companies = ["Enterprise Solutions", "Global Tech", "Innovation Labs", "Digital Dynamics", "Future Systems"]
        
        for i in range(150):
            contact = Contact(
                id=f"pc_contact_{i:04d}",
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                phone_numbers=[f"+1-555-{random.randint(100, 999):03d}-{random.randint(1000, 9999):04d}"],
                email_addresses=[f"{random.choice(first_names).lower()}.{random.choice(last_names).lower()}@company.com"],
                company=random.choice(companies),
                job_title=random.choice(["CEO", "CTO", "Manager", "Developer", "Designer", "Analyst", "Engineer", "Director"]),
                notes=f"Business contact {i}",
                is_synced=random.choice([True, False]),
                last_modified=(datetime.now() - timedelta(days=random.randint(0, 14))).isoformat()
            )
            self.add_contact(contact)
        
        # Sample calendar events (PC events are usually work-related)
        event_titles = ["Team Meeting", "Client Call", "Project Review", "Strategy Session", "Training", "Conference Call"]
        locations = ["Conference Room A", "Meeting Room B", "Office", "Client Office", "Training Center", "Virtual"]
        
        for i in range(80):
            start_date = datetime.now() + timedelta(days=random.randint(-60, 60))
            end_date = start_date + timedelta(hours=random.randint(1, 3))
            
            event = CalendarEvent(
                id=f"pc_event_{i:04d}",
                title=f"{random.choice(event_titles)} {i}",
                description=f"Work event description for event {i}",
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                location=random.choice(locations),
                attendees=[f"colleague_{j}@company.com" for j in range(random.randint(2, 8))],
                reminder_time=(start_date - timedelta(minutes=15)).isoformat(),
                is_synced=random.choice([True, False]),
                last_modified=(datetime.now() - timedelta(days=random.randint(0, 7))).isoformat()
            )
            self.add_calendar_event(event)
    
    def _start_background_processes(self):
        """Start background processes that simulate real PC behavior"""
        self._system_monitor_thread = threading.Thread(target=self._system_monitoring, daemon=True)
        self._system_monitor_thread.start()
    
    def _system_monitoring(self):
        """Monitor system resources and simulate realistic behavior"""
        while True:
            try:
                time.sleep(10)  # Update every 10 seconds
                
                # Simulate realistic CPU usage
                if random.random() < 0.3:  # 30% chance of high usage
                    self.cpu_usage = random.randint(60, 95)
                else:
                    self.cpu_usage = random.randint(5, 40)
                
                # Simulate memory usage
                if random.random() < 0.2:  # 20% chance of high memory usage
                    self.memory_usage = random.randint(70, 90)
                else:
                    self.memory_usage = random.randint(30, 60)
                
                # Simulate disk usage
                self.disk_usage = (self.used_storage / self.storage_capacity) * 100
                
                # Simulate network activity
                if random.random() < 0.4:  # 40% chance of network activity
                    self.network_activity = random.randint(10, 80)
                else:
                    self.network_activity = random.randint(0, 20)
                
                # Simulate occasional system events
                if random.random() < 0.01:  # 1% chance
                    self._simulate_system_event()
                    
            except Exception as e:
                print(f"Error in system monitoring: {e}")
                time.sleep(30)
    
    def _simulate_system_event(self):
        """Simulate occasional system events"""
        events = [
            "antivirus_scan",
            "system_update",
            "backup_process",
            "disk_cleanup",
            "software_installation"
        ]
        
        event = random.choice(events)
        
        if event == "antivirus_scan":
            self.antivirus_status = "scanning"
            # Reset after some time
            threading.Timer(60, lambda: setattr(self, 'antivirus_status', 'active')).start()
        
        elif event == "system_update":
            # Simulate system update process
            pass
        
        elif event == "backup_process":
            # Simulate backup process
            pass
    
    def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        return {
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "network_activity": self.network_activity,
            "antivirus_status": self.antivirus_status,
            "firewall_status": self.firewall_status,
            "uptime": self._get_uptime(),
            "last_boot": self._get_last_boot()
        }
    
    def get_storage_info(self) -> Dict:
        """Get detailed storage information"""
        return {
            "total_capacity": self.storage_capacity,
            "used_storage": self.used_storage,
            "free_storage": self.storage_capacity - self.used_storage,
            "usage_percentage": (self.used_storage / self.storage_capacity) * 100,
            "documents_size": sum(f.size for f in self.get_files() if f.file_type in ["pdf", "doc", "docx", "txt"]),
            "media_size": sum(f.size for f in self.get_files() if f.file_type in ["jpg", "png", "mp4", "avi", "mp3", "wav"]),
            "applications_size": sum(f.size for f in self.get_files() if f.file_type in ["exe", "dmg", "pkg", "deb"])
        }
    
    def get_network_info(self) -> Dict:
        """Get network information"""
        return {
            "connection_type": self.connection_type.value if self.connection_type else None,
            "connection_speed": self.connection_speed,
            "is_connected": self.is_connected,
            "network_activity": self.network_activity,
            "firewall_status": self.firewall_status
        }
    
    def simulate_file_changes(self):
        """Simulate file changes (new files, modifications)"""
        # Add new files occasionally
        if random.random() < 0.05:  # 5% chance
            directories = ["/Users/Downloads", "/Users/Documents", "/Users/Pictures"]
            directory = random.choice(directories)
            file_types = ["pdf", "doc", "jpg", "mp4", "mp3"]
            file_type = random.choice(file_types)
            file_size = random.randint(1024 * 1024, 50 * 1024 * 1024)
            
            new_file = FileInfo(
                name=f"new_pc_file_{int(time.time())}.{file_type}",
                path=f"{directory}/new_pc_file_{int(time.time())}.{file_type}",
                size=file_size,
                modified_date=datetime.now().isoformat(),
                created_date=datetime.now().isoformat(),
                file_type=file_type,
                checksum=f"new_pc_hash_{int(time.time()):08x}",
                is_synced=False,
                sync_priority=random.randint(1, 10)
            )
            self.add_file(new_file)
            
            # Update storage
            self.used_storage += file_size
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        return {
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "network_activity": self.network_activity,
            "system_health": self._calculate_system_health()
        }
    
    def _calculate_system_health(self) -> str:
        """Calculate overall system health"""
        health_score = 100
        
        if self.cpu_usage > 80:
            health_score -= 20
        elif self.cpu_usage > 60:
            health_score -= 10
        
        if self.memory_usage > 85:
            health_score -= 20
        elif self.memory_usage > 70:
            health_score -= 10
        
        if self.disk_usage > 90:
            health_score -= 15
        elif self.disk_usage > 80:
            health_score -= 5
        
        if self.antivirus_status != "active":
            health_score -= 10
        
        if self.firewall_status != "enabled":
            health_score -= 10
        
        if health_score >= 80:
            return "Excellent"
        elif health_score >= 60:
            return "Good"
        elif health_score >= 40:
            return "Fair"
        else:
            return "Poor"
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        # Simulate uptime
        uptime_hours = random.randint(24, 168)  # 1 day to 1 week
        days = uptime_hours // 24
        hours = uptime_hours % 24
        return f"{days} days, {hours} hours"
    
    def _get_last_boot(self) -> str:
        """Get last boot time"""
        # Simulate last boot time
        boot_time = datetime.now() - timedelta(hours=random.randint(24, 168))
        return boot_time.isoformat()
    
    def _get_manufacturer(self) -> str:
        return "TechCorp"
    
    def _get_os_version(self) -> str:
        return "Windows 11 Pro"
    
    def _get_firmware_version(self) -> str:
        return "v3.2.1"
    
    def _get_serial_number(self) -> str:
        return f"DC{random.randint(100000, 999999)}"
    
    def _get_capacity(self) -> int:
        return self.storage_capacity
    
    def _get_free_space(self) -> int:
        return self.storage_capacity - self.used_storage
    
    def _get_battery_level(self) -> int:
        return 100  # PCs are usually plugged in
    
    def _get_charging_status(self) -> bool:
        return True  # PCs are usually plugged in
    
    def _get_last_seen(self) -> str:
        return datetime.now().isoformat()