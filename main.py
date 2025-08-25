#!/usr/bin/env python3
"""
Phone-PC Sync Emulator
A comprehensive emulation of phone-to-computer synchronization processes
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import MainWindow
from src.core.sync_manager import SyncManager
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logger

def main():
    """Main entry point for the application"""
    try:
        # Setup logging
        logger = setup_logger()
        logger.info("Starting Phone-PC Sync Emulator")
        
        # Initialize configuration
        config = ConfigManager()
        config.load_config()
        
        # Initialize sync manager
        sync_manager = SyncManager(config)
        
        # Create and run the main application
        root = tk.Tk()
        app = MainWindow(root, sync_manager, config)
        
        # Set window properties
        root.title("Phone-PC Sync Emulator v1.0")
        root.geometry("1200x800")
        root.minsize(1000, 700)
        
        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_width() // 2)
        root.geometry(f"+{x}+{y}")
        
        logger.info("Application initialized successfully")
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()