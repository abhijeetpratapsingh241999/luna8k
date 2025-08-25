"""
Progress Panel
Displays real-time synchronization progress
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
import time


class ProgressPanel(ttk.LabelFrame):
    """Panel for displaying synchronization progress"""
    
    def __init__(self, parent, sync_manager):
        super().__init__(parent, text="Synchronization Progress", padding=10)
        self.sync_manager = sync_manager
        self.current_session_id = None
        
        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the panel widgets"""
        # Overall progress
        overall_frame = ttk.Frame(self)
        overall_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        overall_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(overall_frame, text="Overall Progress:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.overall_progress = ttk.Progressbar(overall_frame, length=300, mode='determinate')
        self.overall_progress.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.overall_percentage = ttk.Label(overall_frame, text="0%")
        self.overall_percentage.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        # Current file progress
        file_frame = ttk.Frame(self)
        file_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        file_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Current File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.current_file_progress = ttk.Progressbar(file_frame, length=300, mode='determinate')
        self.current_file_progress.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.current_file_percentage = ttk.Label(file_frame, text="0%")
        self.current_file_percentage.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        # File information
        info_frame = ttk.LabelFrame(self, text="File Information", padding=10)
        info_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Current file name
        ttk.Label(info_frame, text="File:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.current_file_label = ttk.Label(info_frame, text="No file selected")
        self.current_file_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # File size
        ttk.Label(info_frame, text="Size:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.file_size_label = ttk.Label(info_frame, text="0 bytes")
        self.file_size_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Transfer speed
        ttk.Label(info_frame, text="Speed:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.speed_label = ttk.Label(info_frame, text="0 MB/s")
        self.speed_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Estimated time
        ttk.Label(info_frame, text="ETA:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.eta_label = ttk.Label(info_frame, text="Calculating...")
        self.eta_label.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        # Statistics
        stats_frame = ttk.LabelFrame(self, text="Statistics", padding=10)
        stats_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        stats_frame.grid_columnconfigure(1, weight=1)
        
        # Files processed
        ttk.Label(stats_frame, text="Files Processed:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.files_processed_label = ttk.Label(stats_frame, text="0")
        self.files_processed_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Total files
        ttk.Label(stats_frame, text="Total Files:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.total_files_label = ttk.Label(stats_frame, text="0")
        self.total_files_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Data transferred
        ttk.Label(stats_frame, text="Data Transferred:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.data_transferred_label = ttk.Label(stats_frame, text="0 bytes")
        self.data_transferred_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Total data
        ttk.Label(stats_frame, text="Total Data:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.total_data_label = ttk.Label(stats_frame, text="0 bytes")
        self.total_data_label.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        # Elapsed time
        ttk.Label(stats_frame, text="Elapsed Time:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.elapsed_time_label = ttk.Label(stats_frame, text="00:00:00")
        self.elapsed_time_label.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        
        # Status and controls
        control_frame = ttk.Frame(self)
        control_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        
        self.status_label = ttk.Label(control_frame, text="Ready", font=("Arial", 10, "bold"))
        self.status_label.pack(side="left")
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side="right")
        
        self.pause_btn = ttk.Button(button_frame, text="⏸ Pause", command=self._pause_sync)
        self.pause_btn.pack(side="left", padx=2)
        self.pause_btn.config(state="disabled")
        
        self.resume_btn = ttk.Button(button_frame, text="▶ Resume", command=self._resume_sync)
        self.resume_btn.pack(side="left", padx=2)
        self.resume_btn.config(state="disabled")
        
        self.cancel_btn = ttk.Button(button_frame, text="❌ Cancel", command=self._cancel_sync)
        self.cancel_btn.pack(side="left", padx=2)
        self.cancel_btn.config(state="disabled")
        
        # Initialize start time
        self.start_time = None
    
    def set_session_id(self, session_id: str):
        """Set the current session ID"""
        self.current_session_id = session_id
        self.start_time = time.time()
        self._reset_display()
        self._update_controls(True)
    
    def _reset_display(self):
        """Reset the display to initial state"""
        self.overall_progress["value"] = 0
        self.overall_percentage.config(text="0%")
        self.current_file_progress["value"] = 0
        self.current_file_percentage.config(text="0%")
        
        self.current_file_label.config(text="No file selected")
        self.file_size_label.config(text="0 bytes")
        self.speed_label.config(text="0 MB/s")
        self.eta_label.config(text="Calculating...")
        
        self.files_processed_label.config(text="0")
        self.total_files_label.config(text="0")
        self.data_transferred_label.config(text="0 bytes")
        self.total_data_label.config(text="0 bytes")
        self.elapsed_time_label.config(text="00:00:00")
        
        self.status_label.config(text="Ready", foreground="blue")
    
    def _update_controls(self, enabled: bool):
        """Update control button states"""
        if enabled:
            self.pause_btn.config(state="normal")
            self.resume_btn.config(state="disabled")
            self.cancel_btn.config(state="normal")
        else:
            self.pause_btn.config(state="disabled")
            self.resume_btn.config(state="disabled")
            self.cancel_btn.config(state="disabled")
    
    def update_progress(self, progress_data):
        """Update progress display with new data"""
        try:
            if not progress_data:
                return
            
            # Update overall progress
            overall_percent = progress_data.get("percentage", 0)
            self.overall_progress["value"] = overall_percent
            self.overall_percentage.config(text=f"{overall_percent:.1f}%")
            
            # Update current file progress
            current_file = progress_data.get("current_file", "")
            if current_file:
                self.current_file_label.config(text=current_file)
                
                # Calculate file progress
                current_file_size = progress_data.get("current_file_size", 0)
                total_size = progress_data.get("total_size", 1)
                if total_size > 0:
                    file_percent = (current_file_size / total_size) * 100
                    self.current_file_progress["value"] = file_percent
                    self.current_file_percentage.config(text=f"{file_percent:.1f}%")
                
                # Update file size
                self.file_size_label.config(text=self._format_bytes(current_file_size))
            
            # Update speed
            speed = progress_data.get("speed", 0)
            self.speed_label.config(text=f"{self._format_bytes(speed)}/s")
            
            # Update ETA
            eta = progress_data.get("estimated_time", 0)
            if eta > 0:
                eta_text = self._format_time(eta)
                self.eta_label.config(text=eta_text)
            else:
                self.eta_label.config(text="Calculating...")
            
            # Update statistics
            total_files = progress_data.get("total_files", 0)
            self.total_files_label.config(text=str(total_files))
            
            files_processed = progress_data.get("files_processed", 0)
            self.files_processed_label.config(text=str(files_processed))
            
            total_size = progress_data.get("total_size", 0)
            self.total_data_label.config(text=self._format_bytes(total_size))
            
            # Calculate data transferred
            if total_size > 0:
                transferred = (overall_percent / 100) * total_size
                self.data_transferred_label.config(text=self._format_bytes(transferred))
            
            # Update elapsed time
            if self.start_time:
                elapsed = time.time() - self.start_time
                self.elapsed_time_label.config(text=self._format_time(elapsed))
            
            # Update status
            if overall_percent >= 100:
                self.status_label.config(text="Completed", foreground="green")
                self._update_controls(False)
            elif overall_percent > 0:
                self.status_label.config(text="In Progress", foreground="orange")
                self._update_controls(True)
            else:
                self.status_label.config(text="Ready", foreground="blue")
                self._update_controls(False)
                
        except Exception as e:
            print(f"Error updating progress: {e}")
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human-readable format"""
        if bytes_value == 0:
            return "0 bytes"
        
        units = ["bytes", "KB", "MB", "GB", "TB"]
        unit_index = 0
        
        while bytes_value >= 1024 and unit_index < len(units) - 1:
            bytes_value /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{bytes_value:.0f} {units[unit_index]}"
        else:
            return f"{bytes_value:.1f} {units[unit_index]}"
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds into human-readable time"""
        if seconds < 0:
            return "00:00:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _pause_sync(self):
        """Pause synchronization"""
        if self.current_session_id:
            try:
                # This would integrate with the actual sync manager
                self.status_label.config(text="Paused", foreground="orange")
                self.pause_btn.config(state="disabled")
                self.resume_btn.config(state="normal")
                print("Sync paused")
            except Exception as e:
                print(f"Error pausing sync: {e}")
    
    def _resume_sync(self):
        """Resume synchronization"""
        if self.current_session_id:
            try:
                # This would integrate with the actual sync manager
                self.status_label.config(text="In Progress", foreground="orange")
                self.pause_btn.config(state="normal")
                self.resume_btn.config(state="disabled")
                print("Sync resumed")
            except Exception as e:
                print(f"Error resuming sync: {e}")
    
    def _cancel_sync(self):
        """Cancel synchronization"""
        if self.current_session_id:
            try:
                # This would integrate with the actual sync manager
                self.status_label.config(text="Cancelled", foreground="red")
                self._update_controls(False)
                print("Sync cancelled")
            except Exception as e:
                print(f"Error cancelling sync: {e}")
    
    def update_display(self):
        """Update the progress display"""
        try:
            if self.current_session_id:
                # Get current session status
                session = self.sync_manager.get_sync_status(self.current_session_id)
                if session and hasattr(session, 'progress'):
                    self.update_progress(session.progress.__dict__)
                    
        except Exception as e:
            print(f"Error updating progress display: {e}")
    
    def set_status(self, status: str, color: str = "black"):
        """Set the status display"""
        self.status_label.config(text=status, foreground=color)