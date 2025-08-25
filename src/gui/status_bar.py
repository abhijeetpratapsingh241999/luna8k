"""
Status Bar
Displays application status and information
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import time


class StatusBar(ttk.Frame):
    """Status bar for the application"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        
        self._create_widgets()
        self._start_update_timer()
    
    def _create_widgets(self):
        """Create the status bar widgets"""
        # Left side - Application status
        self.status_label = ttk.Label(self, text="Ready", relief="sunken", padding=(5, 2))
        self.status_label.grid(row=0, column=0, sticky="w")
        
        # Center - Tab information
        self.tab_info_label = ttk.Label(self, text="", relief="sunken", padding=(5, 2))
        self.tab_info_label.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Right side - Time and additional info
        self.time_label = ttk.Label(self, text="", relief="sunken", padding=(5, 2))
        self.time_label.grid(row=0, column=2, sticky="e")
        
        # Initialize time display
        self._update_time()
    
    def _start_update_timer(self):
        """Start the timer for updating the status bar"""
        def update_loop():
            while True:
                try:
                    self._update_time()
                    time.sleep(1)  # Update every second
                except Exception as e:
                    print(f"Error in status bar update loop: {e}")
                    time.sleep(5)
        
        import threading
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    def _update_time(self):
        """Update the time display"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=current_time)
        except Exception as e:
            print(f"Error updating time: {e}")
    
    def set_status(self, status: str, color: str = "black"):
        """Set the status message"""
        try:
            self.status_label.config(text=status, foreground=color)
        except Exception as e:
            print(f"Error setting status: {e}")
    
    def set_tab_info(self, tab_info: str):
        """Set the tab information"""
        try:
            self.tab_info_label.config(text=tab_info)
        except Exception as e:
            print(f"Error setting tab info: {e}")
    
    def update_status(self):
        """Update the status bar (called from main window)"""
        try:
            # This method can be overridden or extended as needed
            pass
        except Exception as e:
            print(f"Error updating status bar: {e}")
    
    def show_message(self, message: str, duration: int = 3000):
        """Show a temporary message in the status bar"""
        try:
            # Store original status
            original_status = self.status_label.cget("text")
            original_color = self.status_label.cget("foreground")
            
            # Show new message
            self.set_status(message, "blue")
            
            # Schedule restoration
            def restore_status():
                self.set_status(original_status, original_color)
            
            self.after(duration, restore_status)
            
        except Exception as e:
            print(f"Error showing message: {e}")
    
    def show_error(self, error_message: str, duration: int = 5000):
        """Show an error message in the status bar"""
        try:
            # Store original status
            original_status = self.status_label.cget("text")
            original_color = self.status_label.cget("foreground")
            
            # Show error message
            self.set_status(error_message, "red")
            
            # Schedule restoration
            def restore_status():
                self.set_status(original_status, original_color)
            
            self.after(duration, restore_status)
            
        except Exception as e:
            print(f"Error showing error message: {e}")
    
    def show_success(self, success_message: str, duration: int = 3000):
        """Show a success message in the status bar"""
        try:
            # Store original status
            original_status = self.status_label.cget("text")
            original_color = self.status_label.cget("foreground")
            
            # Show success message
            self.set_status(success_message, "green")
            
            # Schedule restoration
            def restore_status():
                self.set_status(original_status, original_color)
            
            self.after(duration, restore_status)
            
        except Exception as e:
            print(f"Error showing success message: {e}")
    
    def show_warning(self, warning_message: str, duration: int = 4000):
        """Show a warning message in the status bar"""
        try:
            # Store original status
            original_status = self.status_label.cget("text")
            original_color = self.status_label.cget("foreground")
            
            # Show warning message
            self.set_status(warning_message, "orange")
            
            # Schedule restoration
            def restore_status():
                self.set_status(original_status, original_color)
            
            self.after(duration, restore_status)
            
        except Exception as e:
            print(f"Error showing warning message: {e}")
    
    def set_busy(self, busy: bool = True):
        """Set the status bar to busy state"""
        try:
            if busy:
                self.status_label.config(text="Processing...", foreground="blue")
                # You could also add a spinner or other visual indicator here
            else:
                self.status_label.config(text="Ready", foreground="black")
        except Exception as e:
            print(f"Error setting busy state: {e}")
    
    def clear_tab_info(self):
        """Clear the tab information"""
        try:
            self.tab_info_label.config(text="")
        except Exception as e:
            print(f"Error clearing tab info: {e}")
    
    def get_status(self) -> str:
        """Get the current status message"""
        try:
            return self.status_label.cget("text")
        except Exception as e:
            print(f"Error getting status: {e}")
            return ""
    
    def get_tab_info(self) -> str:
        """Get the current tab information"""
        try:
            return self.tab_info_label.cget("text")
        except Exception as e:
            print(f"Error getting tab info: {e}")
            return ""