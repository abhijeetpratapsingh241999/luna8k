#!/usr/bin/env python3
"""
Phone-PC Sync Emulator Launcher
Simple launcher script for the application
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are available"""
    required_modules = ['tkinter', 'psutil']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("Missing required modules:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install missing dependencies:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("Phone-PC Sync Emulator")
    print("=" * 30)
    
    # Check dependencies
    if not check_dependencies():
        print("\nDependency check failed. Exiting.")
        sys.exit(1)
    
    print("Dependencies OK!")
    print("Starting application...")
    
    try:
        # Import and run the main application
        from main import main as app_main
        app_main()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all files are in the correct locations.")
        sys.exit(1)
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()