#!/usr/bin/env python3
"""
Phone-PC Sync Emulator Demo
Demonstrates the sync emulator functionality without requiring PyQt6.
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Add the sync_modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sync_modules'))

def demo_file_sync():
    """Demonstrate file synchronization functionality"""
    print("\n📁 File Sync Module Demo")
    print("=" * 40)
    
    try:
        # Import using absolute path
        import file_sync
        
        # Create file sync module
        file_sync_module = file_sync.FileSyncModule()
        print("✅ File sync module created successfully")
        
        # Show file stats
        stats = file_sync_module.get_file_stats()
        print(f"📊 File Statistics:")
        print(f"   Total files: {stats['total_files']}")
        print(f"   Phone files: {stats['phone_files']}")
        print(f"   PC files: {stats['pc_files']}")
        print(f"   Sync files: {stats['sync_files']}")
        
        # Show file tree
        file_tree = file_sync_module.get_file_tree()
        print(f"\n🌳 File Tree Structure:")
        for source, files in file_tree.items():
            print(f"   {source.upper()}: {len(files)} files")
            
        return True
        
    except Exception as e:
        print(f"❌ Error in file sync demo: {e}")
        return False

def demo_contact_sync():
    """Demonstrate contact synchronization functionality"""
    print("\n👥 Contact Sync Module Demo")
    print("=" * 40)
    
    try:
        # Import using absolute path
        import contact_sync
        
        # Create contact sync module
        contact_sync_module = contact_sync.ContactSyncModule()
        print("✅ Contact sync module created successfully")
        
        # Show contact stats
        stats = contact_sync_module.get_contact_stats()
        print(f"📊 Contact Statistics:")
        print(f"   Total contacts: {stats['total_contacts']}")
        print(f"   Phone contacts: {stats['phone_contacts']}")
        print(f"   PC contacts: {stats['pc_contacts']}")
        print(f"   Merged contacts: {stats['merged_contacts']}")
        
        # Search for contacts
        results = contact_sync_module.search_contacts("john")
        print(f"\n🔍 Search Results for 'john': {len(results)} contacts found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in contact sync demo: {e}")
        return False

def demo_calendar_sync():
    """Demonstrate calendar synchronization functionality"""
    print("\n📅 Calendar Sync Module Demo")
    print("=" * 40)
    
    try:
        # Import using absolute path
        import calendar_sync
        
        # Create calendar sync module
        calendar_sync_module = calendar_sync.CalendarSyncModule()
        print("✅ Calendar sync module created successfully")
        
        # Show calendar stats
        stats = calendar_sync_module.get_event_stats()
        print(f"📊 Calendar Statistics:")
        print(f"   Total events: {stats['total_events']}")
        print(f"   Phone events: {stats['phone_events']}")
        print(f"   PC events: {stats['pc_events']}")
        print(f"   Merged events: {stats['merged_events']}")
        print(f"   Upcoming events: {stats['upcoming_events']}")
        
        # Get upcoming events
        upcoming = calendar_sync_module.get_upcoming_events(7)
        print(f"\n📅 Upcoming Events (next 7 days): {len(upcoming)} events")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in calendar sync demo: {e}")
        return False

def demo_media_sync():
    """Demonstrate media synchronization functionality"""
    print("\n🎵 Media Sync Module Demo")
    print("=" * 40)
    
    try:
        # Import using absolute path
        import media_sync
        
        # Create media sync module
        media_sync_module = media_sync.MediaSyncModule()
        print("✅ Media sync module created successfully")
        
        # Show media stats
        stats = media_sync_module.get_media_stats()
        print(f"📊 Media Statistics:")
        print(f"   Total files: {stats['total_files']}")
        print(f"   Total size: {stats['total_size']:,} bytes")
        print(f"   Phone media: {stats['phone_media']}")
        print(f"   PC media: {stats['pc_media']}")
        print(f"   Merged media: {stats['merged_media']}")
        
        # Show media by type
        for media_type in ['music', 'photo', 'video']:
            type_media = media_sync_module.get_media_by_type(media_type)
            print(f"   {media_type.title()}: {len(type_media)} files")
            
        return True
        
    except Exception as e:
        print(f"❌ Error in media sync demo: {e}")
        return False

def demo_settings_manager():
    """Demonstrate settings management functionality"""
    print("\n⚙️ Settings Manager Demo")
    print("=" * 40)
    
    try:
        import settings_manager
        
        # Create settings manager
        settings = settings_manager.SettingsManager()
        print("✅ Settings manager created successfully")
        
        # Show settings summary
        summary = settings.get_settings_summary()
        print(f"📊 Settings Summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
            
        # Validate settings
        validation = settings.validate_settings()
        print(f"\n✅ Settings Validation:")
        print(f"   Valid: {validation['valid']}")
        if validation['errors']:
            print(f"   Errors: {validation['errors']}")
        if validation['warnings']:
            print(f"   Warnings: {validation['warnings']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error in settings manager demo: {e}")
        return False

def demo_logger():
    """Demonstrate logging functionality"""
    print("\n📝 Logger Demo")
    print("=" * 40)
    
    try:
        import logger
        
        # Create logger
        sync_logger = logger.SyncLogger("./logs/demo.log")
        print("✅ Logger created successfully")
        
        # Test different log levels
        sync_logger.info("This is an info message")
        sync_logger.warning("This is a warning message")
        sync_logger.error("This is an error message")
        
        # Test specialized logging
        sync_logger.log_sync_activity("demo", "test_sync", "Testing sync functionality")
        sync_logger.log_file_operation("read", "/test/file.txt", "success", "File read successfully")
        
        print("✅ Logging test completed")
        print(f"📁 Log file created at: {sync_logger.get_log_file_path()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in logger demo: {e}")
        return False

def create_sample_data():
    """Create sample data files for demonstration"""
    print("\n📊 Creating Sample Data")
    print("=" * 40)
    
    try:
        # Create sample text file
        sample_file = "./phone_files/sample_document.txt"
        os.makedirs(os.path.dirname(sample_file), exist_ok=True)
        
        with open(sample_file, 'w') as f:
            f.write("This is a sample document for demonstration purposes.\n")
            f.write("It shows how the file sync module would handle text files.\n")
            f.write(f"Created on: {datetime.now()}\n")
            
        print(f"✅ Created sample file: {sample_file}")
        
        # Create sample log entry
        log_file = "./logs/sample.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'w') as f:
            f.write(f"{datetime.now()} - INFO - Sample log entry created\n")
            f.write(f"{datetime.now()} - WARNING - This is a sample warning\n")
            
        print(f"✅ Created sample log: {log_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def main():
    """Main demo function"""
    print("🚀 Phone-PC Sync Emulator Demo")
    print("=" * 50)
    print("This demo showcases the sync emulator functionality")
    print("without requiring the PyQt6 GUI framework.")
    print()
    
    # Create necessary directories
    directories = [
        './logs',
        './sync_folder',
        './phone_files',
        './pc_files',
        './phone_media',
        './pc_media',
        './sync_media'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Create sample data
    create_sample_data()
    
    # Run demos
    demos = [
        ("File Sync", demo_file_sync),
        ("Contact Sync", demo_contact_sync),
        ("Calendar Sync", demo_calendar_sync),
        ("Media Sync", demo_media_sync),
        ("Settings Manager", demo_settings_manager),
        ("Logger", demo_logger)
    ]
    
    successful_demos = 0
    total_demos = len(demos)
    
    for demo_name, demo_func in demos:
        try:
            if demo_func():
                successful_demos += 1
        except Exception as e:
            print(f"❌ {demo_name} demo failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Demo Summary")
    print("=" * 50)
    print(f"✅ Successful demos: {successful_demos}/{total_demos}")
    print(f"❌ Failed demos: {total_demos - successful_demos}")
    
    if successful_demos == total_demos:
        print("\n🎉 All demos completed successfully!")
        print("The Phone-PC Sync Emulator is ready to use.")
        print("\nTo run the full GUI application, install PyQt6:")
        print("pip install PyQt6")
        print("\nThen run: python main.py")
    else:
        print(f"\n⚠️  {total_demos - successful_demos} demo(s) failed.")
        print("Check the error messages above for details.")
    
    print("\n📁 Project structure created:")
    for directory in directories:
        print(f"   {directory}/")

if __name__ == "__main__":
    main()