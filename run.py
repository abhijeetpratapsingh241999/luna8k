#!/usr/bin/env python3
"""
Phone-PC Sync Emulator Launcher
Simple launcher script for the sync emulator application.
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['PyQt6']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install dependencies with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def create_directories():
    """Create necessary directories if they don't exist"""
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
        print(f"📁 Created directory: {directory}")

def main():
    """Main launcher function"""
    print("🚀 Phone-PC Sync Emulator Launcher")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    print("\n📁 Setting up directories...")
    create_directories()
    
    # Launch application
    print("\n🎯 Launching Phone-PC Sync Emulator...")
    try:
        from main import main as app_main
        app_main()
    except ImportError as e:
        print(f"❌ Error importing main application: {e}")
        print("Make sure you're running this from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()