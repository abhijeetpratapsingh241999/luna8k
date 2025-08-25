#!/usr/bin/env python3
"""
Device Emulator - Simulates phone devices for the Phone-PC Sync Emulator
Creates virtual phone instances with realistic data and behavior
"""

import json
import uuid
import threading
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import requests
import socketio
from typing import Dict, List, Any

class PhoneDevice:
    """Represents a virtual phone device"""
    
    def __init__(self, device_type="Android", name=None):
        self.id = str(uuid.uuid4())
        self.device_type = device_type
        self.name = name or f"{device_type} Device {self.id[:8]}"
        
        # Device properties
        self.battery_level = random.randint(20, 100)
        self.storage_total = random.choice([32, 64, 128, 256, 512]) * 1024 * 1024 * 1024  # GB to bytes
        self.storage_used = random.randint(30, 80) * self.storage_total // 100
        self.signal_strength = random.randint(1, 5)
        
        # Device info based on type
        if device_type == "Android":
            self.os_version = random.choice(["Android 11", "Android 12", "Android 13", "Android 14"])
            self.model = random.choice(["SM-G991B", "SM-N981B", "Pixel 6", "OnePlus 9"])
            self.manufacturer = random.choice(["Samsung", "Google", "OnePlus", "Xiaomi"])
        else:  # iOS
            self.os_version = random.choice(["iOS 15.6", "iOS 16.1", "iOS 17.0"])
            self.model = random.choice(["iPhone 13", "iPhone 14", "iPhone 15"])
            self.manufacturer = "Apple"
            
        # State
        self.is_connected = False
        self.last_sync = None
        self.running = False
        
        # Data
        self.files = self.generate_files()
        self.contacts = self.generate_contacts()
        self.messages = self.generate_messages()
        self.apps = self.generate_apps()
        
        # Behavior simulation
        self.battery_drain_rate = random.uniform(0.1, 0.5)  # % per minute
        self.usage_patterns = self.generate_usage_patterns()
        
    def generate_files(self) -> List[Dict]:
        """Generate realistic file structure"""
        files = []
        
        # Photos
        photo_count = random.randint(50, 200)
        for i in range(photo_count):
            files.append({
                "name": f"IMG_{i:04d}.jpg",
                "path": f"/DCIM/Camera/IMG_{i:04d}.jpg",
                "type": "image",
                "size": random.randint(1024*1024, 5*1024*1024),  # 1-5MB
                "created": self.random_date(days_back=365),
                "modified": self.random_date(days_back=30),
                "checksum": hashlib.md5(f"photo_{i}".encode()).hexdigest()
            })
            
        # Videos
        video_count = random.randint(10, 50)
        for i in range(video_count):
            files.append({
                "name": f"VID_{i:04d}.mp4",
                "path": f"/DCIM/Camera/VID_{i:04d}.mp4",
                "type": "video",
                "size": random.randint(10*1024*1024, 100*1024*1024),  # 10-100MB
                "created": self.random_date(days_back=180),
                "modified": self.random_date(days_back=180),
                "checksum": hashlib.md5(f"video_{i}".encode()).hexdigest()
            })
            
        # Documents
        doc_types = [".pdf", ".doc", ".docx", ".txt", ".xlsx"]
        doc_count = random.randint(5, 30)
        for i in range(doc_count):
            ext = random.choice(doc_types)
            files.append({
                "name": f"document_{i}{ext}",
                "path": f"/Documents/document_{i}{ext}",
                "type": "document",
                "size": random.randint(1024*100, 1024*1024*10),  # 100KB-10MB
                "created": self.random_date(days_back=90),
                "modified": self.random_date(days_back=7),
                "checksum": hashlib.md5(f"doc_{i}".encode()).hexdigest()
            })
            
        # Music
        music_count = random.randint(20, 100)
        for i in range(music_count):
            files.append({
                "name": f"Song_{i:03d}.mp3",
                "path": f"/Music/Song_{i:03d}.mp3",
                "type": "audio",
                "size": random.randint(3*1024*1024, 8*1024*1024),  # 3-8MB
                "created": self.random_date(days_back=730),
                "modified": self.random_date(days_back=730),
                "checksum": hashlib.md5(f"song_{i}".encode()).hexdigest()
            })
            
        return files
        
    def generate_contacts(self) -> List[Dict]:
        """Generate realistic contacts"""
        first_names = ["Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry", 
                      "Ivy", "Jack", "Kate", "Liam", "Mia", "Noah", "Olivia", "Paul"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                     "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez"]
                     
        contacts = []
        contact_count = random.randint(50, 200)
        
        for i in range(contact_count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            name = f"{first} {last}"
            
            contacts.append({
                "id": str(uuid.uuid4()),
                "name": name,
                "phone": f"+1-555-{random.randint(1000, 9999)}",
                "email": f"{first.lower()}.{last.lower()}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com'])}",
                "photo": None,
                "created": self.random_date(days_back=1000),
                "modified": self.random_date(days_back=30),
                "favorite": random.choice([True, False, False, False]),  # 25% chance
                "blocked": random.choice([True, False, False, False, False, False, False, False]),  # 12.5% chance
                "groups": random.sample(["Family", "Work", "Friends", "School"], random.randint(0, 2))
            })
            
        return contacts
        
    def generate_messages(self) -> List[Dict]:
        """Generate realistic message history"""
        messages = []
        message_templates = [
            "Hey, how are you?", "What's up?", "Can you call me?", "Running late!",
            "Thanks!", "See you later", "Good morning!", "Have a great day!",
            "Let's meet for lunch", "Check this out", "LOL", "👍", "❤️",
            "Happy birthday!", "Congratulations!", "Good luck!", "Drive safe",
            "Can you pick up milk?", "Meeting at 3 PM", "Traffic is bad"
        ]
        
        # Generate messages for random contacts
        active_contacts = random.sample(self.contacts, min(20, len(self.contacts)))
        
        for contact in active_contacts:
            conversation_length = random.randint(1, 50)
            
            for i in range(conversation_length):
                is_sent = random.choice([True, False])
                
                messages.append({
                    "id": str(uuid.uuid4()),
                    "contact_id": contact["id"],
                    "contact_name": contact["name"],
                    "message": random.choice(message_templates),
                    "timestamp": self.random_date(days_back=30),
                    "type": "sent" if is_sent else "received",
                    "read": True if is_sent else random.choice([True, True, True, False]),  # 75% read
                    "thread_id": contact["id"]  # Group by contact
                })
                
        # Sort messages by timestamp
        messages.sort(key=lambda x: x["timestamp"], reverse=True)
        return messages
        
    def generate_apps(self) -> List[Dict]:
        """Generate installed apps"""
        apps = [
            {"name": "WhatsApp", "package": "com.whatsapp", "size": 150*1024*1024, "version": "2.23.24.75"},
            {"name": "Instagram", "package": "com.instagram.android", "size": 200*1024*1024, "version": "302.0.0.23.63"},
            {"name": "Facebook", "package": "com.facebook.katana", "size": 180*1024*1024, "version": "442.0.0.28.69"},
            {"name": "YouTube", "package": "com.google.android.youtube", "size": 120*1024*1024, "version": "18.43.45"},
            {"name": "Gmail", "package": "com.google.android.gm", "size": 80*1024*1024, "version": "2023.10.29.581172671"},
            {"name": "Chrome", "package": "com.android.chrome", "size": 250*1024*1024, "version": "119.0.6045.163"},
            {"name": "Spotify", "package": "com.spotify.music", "size": 100*1024*1024, "version": "8.8.66.488"},
            {"name": "Netflix", "package": "com.netflix.mediaclient", "size": 90*1024*1024, "version": "8.88.0"},
        ]
        
        # Randomly select which apps are installed
        installed_apps = random.sample(apps, random.randint(5, len(apps)))
        
        for app in installed_apps:
            app["installed_date"] = self.random_date(days_back=365)
            app["last_used"] = self.random_date(days_back=7)
            app["permissions"] = random.sample([
                "CAMERA", "MICROPHONE", "LOCATION", "CONTACTS", "STORAGE", 
                "PHONE", "SMS", "CALENDAR", "NOTIFICATIONS"
            ], random.randint(2, 6))
            
        return installed_apps
        
    def generate_usage_patterns(self) -> Dict:
        """Generate realistic usage patterns"""
        return {
            "daily_screen_time": random.randint(2*3600, 8*3600),  # 2-8 hours in seconds
            "most_used_apps": random.sample([app["name"] for app in self.apps], min(5, len(self.apps))),
            "peak_usage_hours": random.sample(range(7, 23), 3),  # 3 peak hours
            "notification_frequency": random.randint(10, 100),  # notifications per day
            "call_frequency": random.randint(2, 20),  # calls per day
            "sms_frequency": random.randint(5, 50),  # SMS per day
        }
        
    def random_date(self, days_back=30):
        """Generate a random date within the last N days"""
        start_date = datetime.now() - timedelta(days=days_back)
        random_days = random.randint(0, days_back)
        random_seconds = random.randint(0, 24*3600)
        
        date = start_date + timedelta(days=random_days, seconds=random_seconds)
        return date.isoformat()
        
    def simulate_battery_drain(self):
        """Simulate battery drain over time"""
        while self.running:
            if self.battery_level > 0:
                drain = random.uniform(0.1, self.battery_drain_rate)
                self.battery_level = max(0, self.battery_level - drain)
                
                # Simulate charging
                if random.random() < 0.05:  # 5% chance per minute to start charging
                    charge_time = random.randint(30, 120)  # 30-120 minutes
                    for _ in range(charge_time):
                        if not self.running:
                            break
                        if self.battery_level < 100:
                            self.battery_level = min(100, self.battery_level + random.uniform(0.5, 2.0))
                        time.sleep(60)  # 1 minute
                        
            time.sleep(60)  # Check every minute
            
    def simulate_usage(self):
        """Simulate device usage patterns"""
        while self.running:
            # Simulate receiving messages
            if random.random() < 0.1:  # 10% chance per cycle
                self.receive_message()
                
            # Simulate taking photos
            if random.random() < 0.05:  # 5% chance per cycle
                self.take_photo()
                
            # Simulate downloading files
            if random.random() < 0.02:  # 2% chance per cycle
                self.download_file()
                
            # Simulate adding contacts
            if random.random() < 0.01:  # 1% chance per cycle
                self.add_contact()
                
            time.sleep(30)  # Check every 30 seconds
            
    def receive_message(self):
        """Simulate receiving a new message"""
        if not self.contacts:
            return
            
        contact = random.choice(self.contacts)
        message_templates = [
            "Hey!", "What's up?", "Call me", "Thanks!", "See you later",
            "Good morning!", "How's it going?", "Can you help me?",
            "Let's meet up", "Check this out", "👍", "😊"
        ]
        
        new_message = {
            "id": str(uuid.uuid4()),
            "contact_id": contact["id"],
            "contact_name": contact["name"],
            "message": random.choice(message_templates),
            "timestamp": datetime.now().isoformat(),
            "type": "received",
            "read": False,
            "thread_id": contact["id"]
        }
        
        self.messages.insert(0, new_message)  # Add to beginning (most recent)
        print(f"[{self.name}] Received message from {contact['name']}: {new_message['message']}")
        
    def take_photo(self):
        """Simulate taking a photo"""
        photo_count = len([f for f in self.files if f["type"] == "image"])
        
        new_photo = {
            "name": f"IMG_{photo_count + 1:04d}.jpg",
            "path": f"/DCIM/Camera/IMG_{photo_count + 1:04d}.jpg",
            "type": "image",
            "size": random.randint(1024*1024, 5*1024*1024),
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "checksum": hashlib.md5(f"photo_{photo_count + 1}".encode()).hexdigest()
        }
        
        self.files.append(new_photo)
        self.storage_used += new_photo["size"]
        print(f"[{self.name}] Took photo: {new_photo['name']}")
        
    def download_file(self):
        """Simulate downloading a file"""
        file_types = [
            (".pdf", "document", 1024*1024*2),
            (".mp3", "audio", 1024*1024*4),
            (".mp4", "video", 1024*1024*20),
            (".apk", "application", 1024*1024*50)
        ]
        
        ext, file_type, avg_size = random.choice(file_types)
        download_count = len([f for f in self.files if f["path"].startswith("/Downloads")])
        
        new_file = {
            "name": f"download_{download_count + 1}{ext}",
            "path": f"/Downloads/download_{download_count + 1}{ext}",
            "type": file_type,
            "size": random.randint(avg_size//2, avg_size*2),
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "checksum": hashlib.md5(f"download_{download_count + 1}".encode()).hexdigest()
        }
        
        self.files.append(new_file)
        self.storage_used += new_file["size"]
        print(f"[{self.name}] Downloaded: {new_file['name']}")
        
    def add_contact(self):
        """Simulate adding a new contact"""
        first_names = ["Alex", "Sam", "Jordan", "Taylor", "Casey", "Morgan"]
        last_names = ["Wilson", "Anderson", "Taylor", "Thomas", "Jackson", "White"]
        
        first = random.choice(first_names)
        last = random.choice(last_names)
        name = f"{first} {last}"
        
        new_contact = {
            "id": str(uuid.uuid4()),
            "name": name,
            "phone": f"+1-555-{random.randint(1000, 9999)}",
            "email": f"{first.lower()}.{last.lower()}@example.com",
            "photo": None,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "favorite": False,
            "blocked": False,
            "groups": []
        }
        
        self.contacts.append(new_contact)
        print(f"[{self.name}] Added contact: {name}")
        
    def get_device_info(self) -> Dict:
        """Get comprehensive device information"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.device_type,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "os_version": self.os_version,
            "battery_level": round(self.battery_level, 1),
            "storage_total": self.storage_total,
            "storage_used": self.storage_used,
            "storage_free": self.storage_total - self.storage_used,
            "signal_strength": self.signal_strength,
            "is_connected": self.is_connected,
            "last_sync": self.last_sync,
            "file_count": len(self.files),
            "contact_count": len(self.contacts),
            "message_count": len(self.messages),
            "app_count": len(self.apps),
            "usage_patterns": self.usage_patterns
        }
        
    def start_simulation(self):
        """Start device simulation threads"""
        self.running = True
        
        # Start background simulation threads
        threading.Thread(target=self.simulate_battery_drain, daemon=True).start()
        threading.Thread(target=self.simulate_usage, daemon=True).start()
        
        print(f"[{self.name}] Simulation started")
        
    def stop_simulation(self):
        """Stop device simulation"""
        self.running = False
        print(f"[{self.name}] Simulation stopped")
        
    def export_data(self, export_dir: Path):
        """Export device data to files"""
        device_dir = export_dir / self.id
        device_dir.mkdir(exist_ok=True)
        
        # Export device info
        with open(device_dir / "device_info.json", "w") as f:
            json.dump(self.get_device_info(), f, indent=2)
            
        # Export files
        with open(device_dir / "files.json", "w") as f:
            json.dump(self.files, f, indent=2)
            
        # Export contacts
        with open(device_dir / "contacts.json", "w") as f:
            json.dump(self.contacts, f, indent=2)
            
        # Export messages
        with open(device_dir / "messages.json", "w") as f:
            json.dump(self.messages, f, indent=2)
            
        # Export apps
        with open(device_dir / "apps.json", "w") as f:
            json.dump(self.apps, f, indent=2)
            
        print(f"[{self.name}] Data exported to {device_dir}")

class DeviceManager:
    """Manages multiple virtual phone devices"""
    
    def __init__(self, server_url="http://localhost:5000"):
        self.server_url = server_url
        self.devices = {}
        self.data_dir = Path("data/devices")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def create_device(self, device_type="Android", name=None) -> PhoneDevice:
        """Create a new virtual device"""
        device = PhoneDevice(device_type, name)
        self.devices[device.id] = device
        device.start_simulation()
        
        # Export initial data
        device.export_data(self.data_dir)
        
        print(f"Created device: {device.name} ({device.id})")
        return device
        
    def remove_device(self, device_id: str):
        """Remove a virtual device"""
        if device_id in self.devices:
            device = self.devices[device_id]
            device.stop_simulation()
            del self.devices[device_id]
            print(f"Removed device: {device.name}")
            
    def connect_device(self, device_id: str) -> bool:
        """Connect a device to the sync server"""
        if device_id not in self.devices:
            return False
            
        device = self.devices[device_id]
        
        try:
            # Send connection request to server
            response = requests.post(
                f"{self.server_url}/api/devices/{device_id}/connect",
                json={
                    "name": device.name,
                    "type": device.device_type,
                    "battery": device.battery_level,
                    "storage_used": (device.storage_used / device.storage_total) * 100,
                    "capabilities": ["file_transfer", "contacts", "messages", "apps"]
                },
                timeout=5
            )
            
            if response.status_code == 200:
                device.is_connected = True
                device.last_sync = datetime.now().isoformat()
                print(f"Connected device: {device.name}")
                return True
            else:
                print(f"Failed to connect device: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            return False
            
    def disconnect_device(self, device_id: str) -> bool:
        """Disconnect a device from the sync server"""
        if device_id not in self.devices:
            return False
            
        device = self.devices[device_id]
        
        try:
            response = requests.post(
                f"{self.server_url}/api/devices/{device_id}/disconnect",
                timeout=5
            )
            
            device.is_connected = False
            print(f"Disconnected device: {device.name}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Disconnection error: {e}")
            return False
            
    def get_device_list(self) -> List[Dict]:
        """Get list of all devices"""
        return [device.get_device_info() for device in self.devices.values()]
        
    def export_all_data(self):
        """Export data for all devices"""
        for device in self.devices.values():
            device.export_data(self.data_dir)
            
    def create_sample_devices(self):
        """Create a set of sample devices for testing"""
        devices = [
            ("Android", "Samsung Galaxy S21"),
            ("iOS", "iPhone 13 Pro"),
            ("Android", "OnePlus 9"),
            ("Android", "Google Pixel 6"),
            ("iOS", "iPhone 14"),
        ]
        
        for device_type, name in devices:
            self.create_device(device_type, name)
            
        print(f"Created {len(devices)} sample devices")

if __name__ == "__main__":
    manager = DeviceManager()
    
    # Create sample devices
    manager.create_sample_devices()
    
    print(f"Device manager started with {len(manager.devices)} devices")
    print("Available devices:")
    for device_info in manager.get_device_list():
        print(f"  - {device_info['name']} ({device_info['type']}) - Battery: {device_info['battery_level']}%")
        
    # Keep running to simulate devices
    try:
        while True:
            time.sleep(60)  # Update every minute
            manager.export_all_data()
    except KeyboardInterrupt:
        print("\nShutting down device manager...")
        for device in manager.devices.values():
            device.stop_simulation()