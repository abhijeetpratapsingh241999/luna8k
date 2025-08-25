#!/usr/bin/env python3
"""
Phone-PC Sync Emulator Demo
Demonstrates core functionality without the GUI.
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_file_sync():
    """Demonstrate file synchronization"""
    print("🔍 File Synchronization Demo")
    print("=" * 40)
    
    try:
        from sync_modules.file_sync import FileSyncModule
        
        # Create file sync module
        fs = FileSyncModule()
        
        # Simulate scanning a directory
        print("📁 Scanning directory...")
        files = fs.scan_directory(".", "/device/path")
        print(f"Found {len(files)} files")
        
        # Show some file info
        for i, (path, info) in enumerate(list(files.items())[:5]):
            print(f"  {i+1}. {path} ({info['size']} bytes)")
            
        print("✅ File sync demo completed\n")
        
    except Exception as e:
        print(f"❌ File sync demo failed: {e}\n")

def demo_contact_sync():
    """Demonstrate contact synchronization"""
    print("👥 Contact Synchronization Demo")
    print("=" * 40)
    
    try:
        from sync_modules.contact_sync import ContactSyncModule, Contact
        
        # Create contact sync module
        cs = ContactSyncModule()
        
        # Add some sample contacts
        contacts = [
            Contact(first_name="John", last_name="Doe", 
                   emails=["john.doe@email.com"], 
                   phones=["+1-555-123-4567"]),
            Contact(first_name="Jane", last_name="Smith", 
                   emails=["jane.smith@email.com"], 
                   phones=["+1-555-987-6543"]),
            Contact(first_name="Bob", last_name="Johnson", 
                   company="Tech Corp", 
                   phones=["+1-555-456-7890"])
        ]
        
        print("➕ Adding contacts...")
        for contact in contacts:
            if cs.add_contact(contact):
                print(f"  Added: {contact.get_full_name()}")
            else:
                print(f"  Failed to add: {contact.get_full_name()}")
                
        # Show summary
        summary = cs.get_contacts_summary()
        print(f"📊 Total contacts: {summary['total_contacts']}")
        print(f"📧 With emails: {summary['with_emails']}")
        print(f"📱 With phones: {summary['with_phones']}")
        
        print("✅ Contact sync demo completed\n")
        
    except Exception as e:
        print(f"❌ Contact sync demo failed: {e}\n")

def demo_calendar_sync():
    """Demonstrate calendar synchronization"""
    print("📅 Calendar Synchronization Demo")
    print("=" * 40)
    
    try:
        from sync_modules.calendar_sync import CalendarSyncModule, CalendarEvent
        
        # Create calendar sync module
        cal = CalendarSyncModule()
        
        # Add some sample events
        today = datetime.now()
        events = [
            CalendarEvent(title="Team Meeting", 
                         start_time=today + timedelta(days=1, hours=9),
                         end_time=today + timedelta(days=1, hours=10),
                         location="Conference Room A"),
            CalendarEvent(title="Doctor Appointment", 
                         start_time=today + timedelta(days=2, hours=14, minutes=30),
                         end_time=today + timedelta(days=2, hours=15, minutes=30),
                         location="Medical Center"),
            CalendarEvent(title="Project Deadline", 
                         start_time=today + timedelta(days=3, hours=17),
                         end_time=today + timedelta(days=3, hours=18),
                         all_day=False)
        ]
        
        print("➕ Adding calendar events...")
        for event in events:
            if cal.add_event(event):
                print(f"  Added: {event.title}")
            else:
                print(f"  Failed to add: {event.title}")
                
        # Show summary
        summary = cal.get_calendar_summary()
        print(f"📊 Total events: {summary['total_events']}")
        print(f"📅 Events today: {summary['events_today']}")
        print(f"📅 Events this week: {summary['events_this_week']}")
        
        print("✅ Calendar sync demo completed\n")
        
    except Exception as e:
        print(f"❌ Calendar sync demo failed: {e}\n")

def demo_device_manager():
    """Demonstrate device management"""
    print("📱 Device Management Demo")
    print("=" * 40)
    
    try:
        from sync_modules.device_manager import DeviceManager
        
        # Create device manager
        dm = DeviceManager()
        
        # Wait a moment for devices to be discovered
        print("🔍 Discovering devices...")
        time.sleep(2)
        
        # Show device summary
        summary = dm.get_devices_summary()
        print(f"📊 Total devices: {summary['total_devices']}")
        print(f"🔗 Connected devices: {summary['connected_devices']}")
        print(f"🔒 Trusted devices: {summary['trusted_devices']}")
        
        # Show connected devices
        connected = dm.get_connected_devices()
        if connected:
            print("📱 Connected devices:")
            for device in connected:
                print(f"  • {device.name} ({device.os_type} {device.os_version})")
                print(f"    Battery: {device.battery_level}%")
                print(f"    Storage: {device.get_storage_available_gb():.1f}GB free")
        else:
            print("📱 No devices currently connected")
            
        print("✅ Device management demo completed\n")
        
    except Exception as e:
        print(f"❌ Device management demo failed: {e}\n")

def demo_sync_engine():
    """Demonstrate sync engine"""
    print("🔄 Sync Engine Demo")
    print("=" * 40)
    
    try:
        from sync_modules.sync_engine import SyncEngine, SyncOperation, SyncPriority
        
        # Create sync engine
        se = SyncEngine()
        
        # Start the engine
        se.start_sync_engine()
        
        # Create some sync operations
        operations = [
            SyncOperation(operation_type='file', priority=SyncPriority.HIGH, total_items=100),
            SyncOperation(operation_type='contact', priority=SyncPriority.NORMAL, total_items=50),
            SyncOperation(operation_type='calendar', priority=SyncPriority.LOW, total_items=30)
        ]
        
        print("📋 Queuing sync operations...")
        for op in operations:
            if se.queue_sync_operation(op):
                print(f"  Queued: {op.operation_type} sync (Priority: {op.priority.value})")
            else:
                print(f"  Failed to queue: {op.operation_type} sync")
                
        # Wait for operations to complete
        print("⏳ Waiting for operations to complete...")
        time.sleep(5)
        
        # Show summary
        summary = se.get_sync_summary()
        print(f"📊 Active operations: {summary['active_operations']}")
        print(f"✅ Completed operations: {summary['completed_operations']}")
        print(f"📋 Queued operations: {summary['queued_operations']}")
        
        # Stop the engine
        se.stop_sync_engine()
        
        print("✅ Sync engine demo completed\n")
        
    except Exception as e:
        print(f"❌ Sync engine demo failed: {e}\n")

def main():
    """Run all demos"""
    print("🚀 Phone-PC Sync Emulator Demo")
    print("=" * 50)
    print("This demo showcases the core functionality of the sync emulator.\n")
    
    # Run all demos
    demo_file_sync()
    demo_contact_sync()
    demo_calendar_sync()
    demo_device_manager()
    demo_sync_engine()
    
    print("🎉 All demos completed!")
    print("\nTo run the full GUI application, use:")
    print("  python main.py")
    print("  or")
    print("  python run.py")

if __name__ == "__main__":
    main()