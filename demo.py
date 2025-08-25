#!/usr/bin/env python3
"""
Phone-PC Sync Emulator Demo
Demonstrates the core functionality without the full GUI
"""

import sys
import time
from src.core.sync_manager import SyncManager
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logger


def demo_sync_process():
    """Demonstrate the synchronization process"""
    print("🚀 Phone-PC Sync Emulator Demo")
    print("=" * 40)
    
    # Setup logging
    logger = setup_logger()
    logger.info("Starting demo")
    
    # Initialize configuration
    config = ConfigManager()
    print(f"✅ Configuration loaded: {config.get('General', 'app_name')} v{config.get('General', 'version')}")
    
    # Initialize sync manager
    sync_manager = SyncManager(config)
    print("✅ Sync manager initialized")
    
    # Get device information
    phone_info = sync_manager.phone_emulator.get_device_info()
    pc_info = sync_manager.pc_emulator.get_device_info()
    
    print(f"\n📱 Phone Device: {phone_info.name} ({phone_info.model})")
    print(f"   OS: {phone_info.os_version}")
    print(f"   Storage: {phone_info.capacity // (1024**3)} GB")
    print(f"   Battery: {phone_info.battery_level}%")
    
    print(f"\n💻 PC Device: {pc_info.name} ({pc_info.model})")
    print(f"   OS: {pc_info.os_version}")
    print(f"   Storage: {pc_info.capacity // (1024**3)} GB")
    
    # Show available protocols
    print(f"\n🔌 Available Protocols:")
    protocols = sync_manager.protocol_manager.get_protocol_statistics()
    for protocol, info in protocols.items():
        status = "🟢" if info["is_active"] else "⚪"
        print(f"   {status} {protocol.upper()}: {info['speed']} Mbps ({info['reliability']*100:.0f}% reliable)")
    
    # Simulate device connection
    print(f"\n🔗 Connecting devices...")
    time.sleep(1)
    
    # Start a sync session
    print(f"🔄 Starting synchronization...")
    session_id = sync_manager.start_sync("full")
    print(f"   Session ID: {session_id[:8]}...")
    
    # Monitor sync progress
    print(f"\n📊 Sync Progress:")
    for i in range(10):
        time.sleep(0.5)
        session = sync_manager.get_sync_status(session_id)
        if session and hasattr(session, 'progress'):
            progress = session.progress
            percentage = getattr(progress, 'percentage', 0)
            current_file = getattr(progress, 'current_file', 'Unknown')
            print(f"   [{i+1:2d}/10] {percentage:5.1f}% - {current_file}")
        else:
            print(f"   [{i+1:2d}/10] Initializing...")
    
    # Show final status
    print(f"\n✅ Demo completed successfully!")
    print(f"   Session ID: {session_id[:8]}...")
    print(f"   Total sessions: {len(sync_manager.get_all_sessions())}")
    
    # Show some statistics
    phone_storage = sync_manager.phone_emulator.get_storage_info()
    pc_storage = sync_manager.pc_emulator.get_storage_info()
    
    print(f"\n📈 Storage Statistics:")
    print(f"   Phone: {phone_storage['used_storage'] // (1024**3):.1f} GB / {phone_storage['total_capacity'] // (1024**3):.1f} GB ({phone_storage['usage_percentage']:.1f}%)")
    print(f"   PC: {pc_storage['used_storage'] // (1024**3):.1f} GB / {pc_storage['total_capacity'] // (1024**3):.1f} GB ({pc_storage['usage_percentage']:.1f}%)")
    
    # Show performance metrics
    pc_perf = sync_manager.pc_emulator.get_performance_metrics()
    print(f"\n⚡ Performance Metrics:")
    print(f"   CPU Usage: {pc_perf['cpu_usage']}%")
    print(f"   Memory Usage: {pc_perf['memory_usage']}%")
    print(f"   System Health: {pc_perf['system_health']}")
    
    logger.info("Demo completed successfully")
    print(f"\n🎉 Demo finished! The emulator is working correctly.")
    print(f"   Run 'python main.py' to launch the full GUI application.")


def demo_error_handling():
    """Demonstrate error handling capabilities"""
    print(f"\n🛡️ Error Handling Demo:")
    print("   - The emulator includes comprehensive error handling")
    print("   - Simulated device failures and network interruptions")
    print("   - Automatic retry mechanisms")
    print("   - Detailed logging for debugging")


def demo_features():
    """Show available features"""
    print(f"\n✨ Available Features:")
    print("   - Multiple sync protocols (USB, Bluetooth, WiFi, NFC)")
    print("   - Real-time progress tracking")
    print("   - Device emulation with realistic behavior")
    print("   - Comprehensive logging and monitoring")
    print("   - Modern GUI interface")
    print("   - Configuration management")
    print("   - Error handling and recovery")


if __name__ == "__main__":
    try:
        demo_sync_process()
        demo_error_handling()
        demo_features()
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Demo interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print(f"   This might indicate an issue with the installation or dependencies")
        sys.exit(1)