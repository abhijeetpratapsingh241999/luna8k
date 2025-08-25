"""
Log Panel
Displays synchronization logs and events
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import List, Dict
import time
from datetime import datetime


class LogPanel(ttk.Frame):
    """Panel for displaying logs and events"""
    
    def __init__(self, parent, sync_manager):
        super().__init__(parent)
        self.sync_manager = sync_manager
        
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._create_widgets()
        self._setup_logging()
    
    def _create_widgets(self):
        """Create the panel widgets"""
        # Title and controls
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        title_label = ttk.Label(header_frame, text="Synchronization Logs", font=("Arial", 12, "bold"))
        title_label.pack(side="left")
        
        # Control buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side="right")
        
        self.clear_btn = ttk.Button(button_frame, text="Clear Logs", command=self._clear_logs)
        self.clear_btn.pack(side="left", padx=2)
        
        self.export_btn = ttk.Button(button_frame, text="Export", command=self._export_logs)
        self.export_btn.pack(side="left", padx=2)
        
        self.refresh_btn = ttk.Button(button_frame, text="Refresh", command=self._refresh_logs)
        self.refresh_btn.pack(side="left", padx=2)
        
        # Filter controls
        filter_frame = ttk.LabelFrame(self, text="Log Filters", padding=5)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        filter_frame.grid_columnconfigure(1, weight=1)
        
        # Log level filter
        ttk.Label(filter_frame, text="Level:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.level_filter_var = tk.StringVar(value="all")
        level_combo = ttk.Combobox(filter_frame, textvariable=self.level_filter_var,
                                 values=["all", "INFO", "WARNING", "ERROR"], state="readonly")
        level_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        level_combo.bind("<<ComboboxSelected>>", self._apply_filters)
        
        # Session filter
        ttk.Label(filter_frame, text="Session:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.session_filter_var = tk.StringVar(value="all")
        self.session_combo = ttk.Combobox(filter_frame, textvariable=self.session_filter_var, state="readonly")
        self.session_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.session_combo.bind("<<ComboboxSelected>>", self._apply_filters)
        
        # Search filter
        ttk.Label(filter_frame, text="Search:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        search_entry.bind("<KeyRelease>", self._apply_filters)
        
        # Log display
        log_frame = ttk.LabelFrame(self, text="Log Entries", padding=5)
        log_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        # Create log text widget with scrollbar
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure text widget tags for different log levels
        self.log_text.tag_configure("INFO", foreground="black")
        self.log_text.tag_configure("WARNING", foreground="orange")
        self.log_text.tag_configure("ERROR", foreground="red")
        self.log_text.tag_configure("timestamp", foreground="gray")
        self.log_text.tag_configure("session", foreground="blue")
        
        # Status bar
        status_frame = ttk.Frame(self)
        status_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        
        self.log_count_label = ttk.Label(status_frame, text="0 log entries")
        self.log_count_label.pack(side="left")
        
        self.last_update_label = ttk.Label(status_frame, text="Last update: Never")
        self.last_update_label.pack(side="right")
        
        # Initialize log data
        self.log_entries = []
        self.filtered_entries = []
        self._update_session_filter()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # This would integrate with the actual logging system
        pass
    
    def _update_session_filter(self):
        """Update the session filter dropdown"""
        try:
            sessions = self.sync_manager.get_all_sessions()
            session_ids = ["all"] + [session.id[:8] + "..." for session in sessions]
            self.session_combo["values"] = session_ids
        except Exception as e:
            print(f"Error updating session filter: {e}")
    
    def add_log_entry(self, level: str, message: str, session_id: str = None, details: Dict = None):
        """Add a new log entry"""
        try:
            timestamp = datetime.now().isoformat()
            
            log_entry = {
                "timestamp": timestamp,
                "level": level,
                "message": message,
                "session_id": session_id,
                "details": details or {}
            }
            
            self.log_entries.append(log_entry)
            self._apply_filters()
            self._update_display()
            
        except Exception as e:
            print(f"Error adding log entry: {e}")
    
    def _apply_filters(self, event=None):
        """Apply current filters to log entries"""
        try:
            level_filter = self.level_filter_var.get()
            session_filter = self.session_filter_var.get()
            search_term = self.search_var.get().lower()
            
            self.filtered_entries = []
            
            for entry in self.log_entries:
                # Apply level filter
                if level_filter != "all" and entry["level"] != level_filter:
                    continue
                
                # Apply session filter
                if session_filter != "all":
                    if not entry["session_id"] or not entry["session_id"].startswith(session_filter.replace("...", "")):
                        continue
                
                # Apply search filter
                if search_term:
                    if (search_term not in entry["message"].lower() and 
                        search_term not in entry["level"].lower()):
                        continue
                
                self.filtered_entries.append(entry)
            
            self._update_display()
            
        except Exception as e:
            print(f"Error applying filters: {e}")
    
    def _update_display(self):
        """Update the log display"""
        try:
            # Clear current display
            self.log_text.delete(1.0, tk.END)
            
            # Add filtered entries
            for entry in self.filtered_entries:
                self._add_entry_to_display(entry)
            
            # Update status
            self.log_count_label.config(text=f"{len(self.filtered_entries)} log entries")
            self.last_update_label.config(text=f"Last update: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"Error updating log display: {e}")
    
    def _add_entry_to_display(self, entry: Dict):
        """Add a single log entry to the display"""
        try:
            # Format timestamp
            timestamp = entry["timestamp"]
            if "T" in timestamp:
                timestamp = timestamp.split("T")[1][:8]  # Extract time part
            
            # Format session ID
            session_id = entry["session_id"][:8] + "..." if entry["session_id"] else "N/A"
            
            # Create formatted line
            line = f"[{timestamp}] [{entry['level']:7}] [{session_id:11}] {entry['message']}\n"
            
            # Insert with appropriate tags
            start = self.log_text.index(tk.END)
            self.log_text.insert(tk.END, line)
            end = self.log_text.index(tk.END)
            
            # Apply tags
            self.log_text.tag_add("timestamp", start, f"{start}+{len(timestamp)+2}c")
            self.log_text.tag_add(entry["level"], f"{start}+{len(timestamp)+3}c", f"{start}+{len(timestamp)+10}c")
            self.log_text.tag_add("session", f"{start}+{len(timestamp)+12}c", f"{start}+{len(timestamp)+23}c")
            
        except Exception as e:
            print(f"Error adding entry to display: {e}")
    
    def _clear_logs(self):
        """Clear all log entries"""
        try:
            self.log_entries.clear()
            self.filtered_entries.clear()
            self._update_display()
            
        except Exception as e:
            print(f"Error clearing logs: {e}")
    
    def _export_logs(self):
        """Export logs to file"""
        try:
            # This would implement actual file export functionality
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Logs"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write("Phone-PC Sync Emulator - Log Export\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for entry in self.log_entries:
                        timestamp = entry["timestamp"]
                        level = entry["level"]
                        session_id = entry["session_id"] or "N/A"
                        message = entry["message"]
                        
                        f.write(f"[{timestamp}] [{level:7}] [{session_id:11}] {message}\n")
                
                # Show success message
                from tkinter import messagebox
                messagebox.showinfo("Export", f"Logs exported to {filename}")
                
        except Exception as e:
            print(f"Error exporting logs: {e}")
            from tkinter import messagebox
            messagebox.showerror("Export Error", f"Failed to export logs: {str(e)}")
    
    def _refresh_logs(self):
        """Refresh the log display"""
        try:
            self._update_session_filter()
            self._apply_filters()
            
        except Exception as e:
            print(f"Error refreshing logs: {e}")
    
    def update_display(self):
        """Update the log display (called from main window)"""
        try:
            # Update session filter
            self._update_session_filter()
            
            # Check for new log entries from sync sessions
            sessions = self.sync_manager.get_all_sessions()
            for session in sessions:
                if hasattr(session, 'log_entries'):
                    for log_entry in session.log_entries:
                        # Check if this entry is already in our logs
                        if not any(existing["timestamp"] == log_entry["timestamp"] and 
                                 existing["message"] == log_entry["message"] 
                                 for existing in self.log_entries):
                            
                            # Add new entry
                            self.add_log_entry(
                                level=log_entry["level"],
                                message=log_entry["message"],
                                session_id=session.id,
                                details=log_entry.get("details")
                            )
            
        except Exception as e:
            print(f"Error updating log display: {e}")
    
    def add_system_log(self, level: str, message: str):
        """Add a system log entry"""
        self.add_log_entry(level, message, session_id=None, details={"type": "system"})
    
    def add_sync_log(self, level: str, message: str, session_id: str):
        """Add a synchronization log entry"""
        self.add_log_entry(level, message, session_id=session_id, details={"type": "sync"})
    
    def add_error_log(self, error_message: str, session_id: str = None, details: Dict = None):
        """Add an error log entry"""
        self.add_log_entry("ERROR", error_message, session_id=session_id, details=details)
    
    def get_log_summary(self) -> Dict:
        """Get a summary of the logs"""
        try:
            total_entries = len(self.log_entries)
            info_count = len([e for e in self.log_entries if e["level"] == "INFO"])
            warning_count = len([e for e in self.log_entries if e["level"] == "WARNING"])
            error_count = len([e for e in self.log_entries if e["level"] == "ERROR"])
            
            return {
                "total_entries": total_entries,
                "info_count": info_count,
                "warning_count": warning_count,
                "error_count": error_count,
                "last_entry": self.log_entries[-1]["timestamp"] if self.log_entries else None
            }
            
        except Exception as e:
            print(f"Error getting log summary: {e}")
            return {}