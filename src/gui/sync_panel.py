"""
Sync Panel
Provides synchronization controls and options
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List


class SyncPanel(ttk.LabelFrame):
    """Panel for synchronization controls"""
    
    def __init__(self, parent, sync_manager):
        super().__init__(parent, text="Synchronization Controls", padding=10)
        self.sync_manager = sync_manager
        
        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the panel widgets"""
        # Sync type selection
        ttk.Label(self, text="Sync Type:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.sync_type_var = tk.StringVar(value="full")
        sync_type_combo = ttk.Combobox(self, textvariable=self.sync_type_var, 
                                      values=["full", "incremental", "selective"], state="readonly")
        sync_type_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Sync options
        options_frame = ttk.LabelFrame(self, text="Sync Options", padding=10)
        options_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        options_frame.grid_columnconfigure(1, weight=1)
        
        # Data types to sync
        ttk.Label(options_frame, text="Data Types:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.sync_files_var = tk.BooleanVar(value=True)
        self.sync_contacts_var = tk.BooleanVar(value=True)
        self.sync_calendar_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Files", variable=self.sync_files_var).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(options_frame, text="Contacts", variable=self.sync_contacts_var).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(options_frame, text="Calendar", variable=self.sync_calendar_var).grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Sync direction
        ttk.Label(options_frame, text="Direction:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.sync_direction_var = tk.StringVar(value="bidirectional")
        direction_combo = ttk.Combobox(options_frame, textvariable=self.sync_direction_var,
                                     values=["phone_to_pc", "pc_to_phone", "bidirectional"], state="readonly")
        direction_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        
        # Advanced options
        advanced_frame = ttk.LabelFrame(self, text="Advanced Options", padding=10)
        advanced_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        advanced_frame.grid_columnconfigure(1, weight=1)
        
        # Conflict resolution
        ttk.Label(advanced_frame, text="Conflict Resolution:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.conflict_resolution_var = tk.StringVar(value="newer_wins")
        conflict_combo = ttk.Combobox(advanced_frame, textvariable=self.conflict_resolution_var,
                                    values=["newer_wins", "phone_wins", "pc_wins", "ask_user"], state="readonly")
        conflict_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        # Auto-sync
        self.auto_sync_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(advanced_frame, text="Enable Auto-sync", variable=self.auto_sync_var).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        # Auto-sync interval
        ttk.Label(advanced_frame, text="Auto-sync Interval:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.auto_sync_interval_var = tk.StringVar(value="30")
        interval_combo = ttk.Combobox(advanced_frame, textvariable=self.auto_sync_interval_var,
                                    values=["15", "30", "60", "120"], state="readonly")
        interval_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(advanced_frame, text="minutes").grid(row=2, column=2, sticky="w", padx=5, pady=2)
        
        # File filters
        filter_frame = ttk.LabelFrame(self, text="File Filters", padding=10)
        filter_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        filter_frame.grid_columnconfigure(1, weight=1)
        
        # File size limit
        ttk.Label(filter_frame, text="Max File Size:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.max_file_size_var = tk.StringVar(value="100")
        size_combo = ttk.Combobox(filter_frame, textvariable=self.max_file_size_var,
                                values=["10", "50", "100", "500", "1000"], state="readonly")
        size_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(filter_frame, text="MB").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        
        # File types to exclude
        ttk.Label(filter_frame, text="Exclude Types:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.exclude_types_var = tk.StringVar(value="tmp,log,cache")
        exclude_entry = ttk.Entry(filter_frame, textvariable=self.exclude_types_var)
        exclude_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        # Sync buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        
        self.sync_now_btn = ttk.Button(button_frame, text="Sync Now", command=self._sync_now)
        self.sync_now_btn.pack(side="left", padx=5)
        
        self.schedule_btn = ttk.Button(button_frame, text="Schedule Sync", command=self._schedule_sync)
        self.schedule_btn.pack(side="left", padx=5)
        
        self.reset_btn = ttk.Button(button_frame, text="Reset Options", command=self._reset_options)
        self.reset_btn.pack(side="right", padx=5)
        
        # Status display
        status_frame = ttk.Frame(self)
        status_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready to sync", foreground="blue")
        self.status_label.pack(side="left")
        
        # Progress indicator
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(status_frame, textvariable=self.progress_var)
        self.progress_label.pack(side="right")
    
    def get_selected_sync_type(self) -> str:
        """Get the selected synchronization type"""
        return self.sync_type_var.get()
    
    def get_sync_options(self) -> dict:
        """Get all synchronization options"""
        return {
            "sync_type": self.sync_type_var.get(),
            "sync_files": self.sync_files_var.get(),
            "sync_contacts": self.sync_contacts_var.get(),
            "sync_calendar": self.sync_calendar_var.get(),
            "sync_direction": self.sync_direction_var.get(),
            "conflict_resolution": self.conflict_resolution_var.get(),
            "auto_sync": self.auto_sync_var.get(),
            "auto_sync_interval": int(self.auto_sync_interval_var.get()),
            "max_file_size": int(self.max_file_size_var.get()),
            "exclude_types": self.exclude_types_var.get().split(",")
        }
    
    def _sync_now(self):
        """Start synchronization immediately"""
        try:
            # Validate options
            if not self._validate_options():
                return
            
            # Get sync options
            options = self.get_sync_options()
            
            # Update status
            self.status_label.config(text="Starting synchronization...", foreground="orange")
            self.progress_var.set("Initializing...")
            
            # Start sync (this would be handled by the main window)
            self.event_generate("<<StartSync>>")
            
        except Exception as e:
            messagebox.showerror("Sync Error", f"Failed to start sync: {str(e)}")
            self.status_label.config(text="Sync failed", foreground="red")
    
    def _schedule_sync(self):
        """Schedule synchronization for later"""
        try:
            # Validate options
            if not self._validate_options():
                return
            
            # Get sync options
            options = self.get_sync_options()
            
            # Show scheduling dialog
            self._show_schedule_dialog(options)
            
        except Exception as e:
            messagebox.showerror("Schedule Error", f"Failed to schedule sync: {str(e)}")
    
    def _reset_options(self):
        """Reset all options to defaults"""
        try:
            # Reset to default values
            self.sync_type_var.set("full")
            self.sync_files_var.set(True)
            self.sync_contacts_var.set(True)
            self.sync_calendar_var.set(True)
            self.sync_direction_var.set("bidirectional")
            self.conflict_resolution_var.set("newer_wins")
            self.auto_sync_var.set(False)
            self.auto_sync_interval_var.set("30")
            self.max_file_size_var.set("100")
            self.exclude_types_var.set("tmp,log,cache")
            
            # Update status
            self.status_label.config(text="Options reset to defaults", foreground="blue")
            self.progress_var.set("")
            
        except Exception as e:
            messagebox.showerror("Reset Error", f"Failed to reset options: {str(e)}")
    
    def _validate_options(self) -> bool:
        """Validate synchronization options"""
        try:
            # Check if at least one data type is selected
            if not (self.sync_files_var.get() or self.sync_contacts_var.get() or self.sync_calendar_var.get()):
                messagebox.showwarning("Validation Warning", "Please select at least one data type to sync.")
                return False
            
            # Check auto-sync interval
            if self.auto_sync_var.get():
                interval = int(self.auto_sync_interval_var.get())
                if interval < 15:
                    messagebox.showwarning("Validation Warning", "Auto-sync interval must be at least 15 minutes.")
                    return False
            
            # Check max file size
            max_size = int(self.max_file_size_var.get())
            if max_size <= 0:
                messagebox.showwarning("Validation Warning", "Maximum file size must be greater than 0.")
                return False
            
            return True
            
        except ValueError:
            messagebox.showerror("Validation Error", "Please check that all numeric values are valid.")
            return False
        except Exception as e:
            messagebox.showerror("Validation Error", f"Validation failed: {str(e)}")
            return False
    
    def _show_schedule_dialog(self, options):
        """Show dialog for scheduling synchronization"""
        # Create a simple scheduling dialog
        dialog = tk.Toplevel(self)
        dialog.title("Schedule Synchronization")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        ttk.Label(dialog, text="Schedule Synchronization", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Date and time selection
        time_frame = ttk.Frame(dialog)
        time_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(time_frame, text="Date:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        date_entry = ttk.Entry(time_frame, width=15)
        date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        date_entry.insert(0, "2024-01-01")
        
        ttk.Label(time_frame, text="Time:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        time_entry = ttk.Entry(time_frame, width=15)
        time_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        time_entry.insert(0, "09:00")
        
        # Repeat options
        repeat_frame = ttk.LabelFrame(dialog, text="Repeat Options", padding=10)
        repeat_frame.pack(fill="x", padx=20, pady=10)
        
        repeat_var = tk.StringVar(value="once")
        ttk.Radiobutton(repeat_frame, text="Once", variable=repeat_var, value="once").pack(anchor="w")
        ttk.Radiobutton(repeat_frame, text="Daily", variable=repeat_var, value="daily").pack(anchor="w")
        ttk.Radiobutton(repeat_frame, text="Weekly", variable=repeat_var, value="weekly").pack(anchor="w")
        ttk.Radiobutton(repeat_frame, text="Monthly", variable=repeat_var, value="monthly").pack(anchor="w")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def schedule():
            # Here you would implement the actual scheduling logic
            messagebox.showinfo("Scheduled", f"Sync scheduled for {date_entry.get()} at {time_entry.get()}")
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="Schedule", command=schedule).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side="right", padx=5)
    
    def update_display(self):
        """Update the panel display"""
        try:
            # Check if sync is in progress
            active_sessions = self.sync_manager.get_all_sessions()
            active_sync = any(session.is_active() for session in active_sessions)
            
            if active_sync:
                self.status_label.config(text="Synchronization in progress...", foreground="green")
                self.sync_now_btn.config(state="disabled")
            else:
                self.status_label.config(text="Ready to sync", foreground="blue")
                self.sync_now_btn.config(state="normal")
                
        except Exception as e:
            print(f"Error updating sync panel: {e}")
    
    def set_status(self, status: str, color: str = "black"):
        """Set the status display"""
        self.status_label.config(text=status, foreground=color)
    
    def set_progress(self, progress: str):
        """Set the progress display"""
        self.progress_var.set(progress)