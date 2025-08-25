"""
Main Window GUI
Main application window for the phone-PC sync emulator
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Dict, List

from .device_panel import DevicePanel
from .sync_panel import SyncPanel
from .progress_panel import ProgressPanel
from .log_panel import LogPanel
from .status_bar import StatusBar


class MainWindow:
    """Main application window"""
    
    def __init__(self, root, sync_manager, config):
        self.root = root
        self.sync_manager = sync_manager
        self.config = config
        
        # GUI state
        self.current_session_id = None
        self.is_connected = False
        
        # Setup the main window
        self._setup_window()
        self._create_menu()
        self._create_toolbar()
        self._create_main_content()
        self._create_status_bar()
        
        # Bind events
        self._bind_events()
        
        # Start update timer
        self._start_update_timer()
        
        # Register for sync events
        self.sync_manager.add_event_callback(self._on_sync_event)
    
    def _setup_window(self):
        """Setup the main window properties"""
        self.root.title("Phone-PC Sync Emulator v1.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Configure grid weights
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Set window icon (if available)
        try:
            # self.root.iconbitmap("icon.ico")  # Windows
            pass
        except:
            pass
    
    def _create_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Sync Session", command=self._new_sync_session)
        file_menu.add_command(label="Open Session...", command=self._open_session)
        file_menu.add_separator()
        file_menu.add_command(label="Export Logs...", command=self._export_logs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._exit_application)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Device Manager", command=self._show_device_manager)
        tools_menu.add_command(label="Protocol Settings", command=self._show_protocol_settings)
        tools_menu.add_command(label="Sync History", command=self._show_sync_history)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show Device Panel", command=self._toggle_device_panel)
        view_menu.add_command(label="Show Progress Panel", command=self._toggle_progress_panel)
        view_menu.add_command(label="Show Log Panel", command=self._toggle_log_panel)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Manual", command=self._show_manual)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_toolbar(self):
        """Create the toolbar"""
        toolbar = ttk.Frame(self.root)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        
        # Connection controls
        ttk.Label(toolbar, text="Connection:").pack(side="left", padx=(0, 5))
        
        self.connect_btn = ttk.Button(toolbar, text="Connect", command=self._connect_devices)
        self.connect_btn.pack(side="left", padx=2)
        
        self.disconnect_btn = ttk.Button(toolbar, text="Disconnect", command=self._disconnect_devices)
        self.disconnect_btn.pack(side="left", padx=2)
        self.disconnect_btn.config(state="disabled")
        
        # Sync controls
        ttk.Separator(toolbar, orient="vertical").pack(side="left", padx=10, fill="y")
        ttk.Label(toolbar, text="Sync:").pack(side="left", padx=(0, 5))
        
        self.sync_btn = ttk.Button(toolbar, text="Start Sync", command=self._start_sync)
        self.sync_btn.pack(side="left", padx=2)
        self.sync_btn.config(state="disabled")
        
        self.stop_btn = ttk.Button(toolbar, text="Stop Sync", command=self._stop_sync)
        self.stop_btn.pack(side="left", padx=2)
        self.stop_btn.config(state="disabled")
        
        # Status indicator
        ttk.Separator(toolbar, orient="vertical").pack(side="left", padx=10, fill="y")
        self.status_label = ttk.Label(toolbar, text="Status: Disconnected", foreground="red")
        self.status_label.pack(side="left", padx=5)
        
        # Right-aligned controls
        ttk.Separator(toolbar, orient="vertical").pack(side="right", padx=10, fill="y")
        
        self.settings_btn = ttk.Button(toolbar, text="⚙", width=3, command=self._show_settings)
        self.settings_btn.pack(side="right", padx=2)
    
    def _create_main_content(self):
        """Create the main content area"""
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        # Main sync tab
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="Sync")
        
        # Configure grid weights for main frame
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Left panel - Device information
        self.device_panel = DevicePanel(main_frame, self.sync_manager)
        self.device_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Right panel - Sync controls and progress
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        self.sync_panel = SyncPanel(right_frame, self.sync_manager)
        self.sync_panel.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        
        self.progress_panel = ProgressPanel(right_frame, self.sync_manager)
        self.progress_panel.grid(row=1, column=0, sticky="nsew")
        
        # Log tab
        self.log_panel = LogPanel(self.notebook, self.sync_manager)
        self.notebook.add(self.log_panel, text="Logs")
        
        # Statistics tab
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
        self._create_statistics_tab(stats_frame)
    
    def _create_statistics_tab(self, parent):
        """Create the statistics tab"""
        # Statistics content will be implemented here
        ttk.Label(parent, text="Sync Statistics", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Label(parent, text="Detailed statistics and analytics will be displayed here.").pack()
    
    def _create_status_bar(self):
        """Create the status bar"""
        self.status_bar = StatusBar(self.root)
        self.status_bar.grid(row=3, column=0, sticky="ew", padx=5, pady=2)
    
    def _bind_events(self):
        """Bind window events"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Bind notebook tab changes
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _start_update_timer(self):
        """Start the update timer for real-time updates"""
        def update_loop():
            while True:
                try:
                    self._update_ui()
                    time.sleep(1)  # Update every second
                except Exception as e:
                    print(f"Error in update loop: {e}")
                    time.sleep(5)
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    def _update_ui(self):
        """Update the UI with current data"""
        try:
            # Update device panel
            if hasattr(self, 'device_panel'):
                self.device_panel.update_display()
            
            # Update sync panel
            if hasattr(self, 'sync_panel'):
                self.sync_panel.update_display()
            
            # Update progress panel
            if hasattr(self, 'progress_panel'):
                self.progress_panel.update_display()
            
            # Update status bar
            if hasattr(self, 'status_bar'):
                self.status_bar.update_status()
                
        except Exception as e:
            print(f"Error updating UI: {e}")
    
    def _connect_devices(self):
        """Connect the devices"""
        try:
            # Simulate device connection
            self.is_connected = True
            
            # Update UI state
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            self.sync_btn.config(state="normal")
            self.status_label.config(text="Status: Connected", foreground="green")
            
            # Update device panel
            self.device_panel.on_device_connected()
            
            messagebox.showinfo("Connection", "Devices connected successfully!")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect devices: {str(e)}")
    
    def _disconnect_devices(self):
        """Disconnect the devices"""
        try:
            # Simulate device disconnection
            self.is_connected = False
            
            # Update UI state
            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")
            self.sync_btn.config(state="disabled")
            self.stop_btn.config(state="disabled")
            self.status_label.config(text="Status: Disconnected", foreground="red")
            
            # Update device panel
            self.device_panel.on_device_disconnected()
            
            messagebox.showinfo("Disconnection", "Devices disconnected successfully!")
            
        except Exception as e:
            messagebox.showerror("Disconnection Error", f"Failed to disconnect devices: {str(e)}")
    
    def _start_sync(self):
        """Start synchronization"""
        try:
            # Get sync type from sync panel
            sync_type = self.sync_panel.get_selected_sync_type()
            
            # Start sync session
            session_id = self.sync_manager.start_sync(sync_type)
            self.current_session_id = session_id
            
            # Update UI state
            self.sync_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            
            # Update progress panel
            self.progress_panel.set_session_id(session_id)
            
            messagebox.showinfo("Sync Started", f"Synchronization started with session ID: {session_id}")
            
        except Exception as e:
            messagebox.showerror("Sync Error", f"Failed to start sync: {str(e)}")
    
    def _stop_sync(self):
        """Stop synchronization"""
        try:
            if self.current_session_id:
                self.sync_manager.cancel_sync(self.current_session_id)
                
                # Update UI state
                self.sync_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                
                messagebox.showinfo("Sync Stopped", "Synchronization stopped successfully!")
                
        except Exception as e:
            messagebox.showerror("Stop Error", f"Failed to stop sync: {str(e)}")
    
    def _on_sync_event(self, event, data):
        """Handle sync events"""
        try:
            if event.value == "completed":
                self.sync_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                messagebox.showinfo("Sync Complete", "Synchronization completed successfully!")
                
            elif event.value == "failed":
                self.sync_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                messagebox.showerror("Sync Failed", f"Synchronization failed: {data.error_message}")
                
            elif event.value == "device_connected":
                self.device_panel.on_device_connected()
                
            elif event.value == "device_disconnected":
                self.device_panel.on_device_disconnected()
                
        except Exception as e:
            print(f"Error handling sync event: {e}")
    
    def _on_tab_changed(self, event):
        """Handle notebook tab changes"""
        current_tab = self.notebook.select()
        tab_name = self.notebook.tab(current_tab, "text")
        
        # Update status bar
        self.status_bar.set_tab_info(f"Current tab: {tab_name}")
    
    def _on_closing(self):
        """Handle window closing"""
        try:
            # Shutdown sync manager
            self.sync_manager.shutdown()
            
            # Close the window
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
            self.root.destroy()
    
    # Menu command methods
    def _new_sync_session(self):
        messagebox.showinfo("New Session", "New sync session functionality will be implemented here.")
    
    def _open_session(self):
        messagebox.showinfo("Open Session", "Open session functionality will be implemented here.")
    
    def _export_logs(self):
        messagebox.showinfo("Export Logs", "Export logs functionality will be implemented here.")
    
    def _exit_application(self):
        self._on_closing()
    
    def _show_device_manager(self):
        messagebox.showinfo("Device Manager", "Device manager functionality will be implemented here.")
    
    def _show_protocol_settings(self):
        messagebox.showinfo("Protocol Settings", "Protocol settings functionality will be implemented here.")
    
    def _show_sync_history(self):
        messagebox.showinfo("Sync History", "Sync history functionality will be implemented here.")
    
    def _toggle_device_panel(self):
        messagebox.showinfo("Toggle Panel", "Toggle device panel functionality will be implemented here.")
    
    def _toggle_progress_panel(self):
        messagebox.showinfo("Toggle Panel", "Toggle progress panel functionality will be implemented here.")
    
    def _toggle_log_panel(self):
        messagebox.showinfo("Toggle Panel", "Toggle log panel functionality will be implemented here.")
    
    def _show_manual(self):
        messagebox.showinfo("User Manual", "User manual functionality will be implemented here.")
    
    def _show_about(self):
        messagebox.showinfo("About", 
                          "Phone-PC Sync Emulator v1.0\n\n"
                          "A comprehensive emulation of phone-to-computer synchronization processes.\n\n"
                          "Features:\n"
                          "• Multiple sync protocols (USB, Bluetooth, WiFi, NFC)\n"
                          "• Real-time progress tracking\n"
                          "• Device emulation\n"
                          "• Comprehensive logging\n"
                          "• Modern GUI interface")
    
    def _show_settings(self):
        messagebox.showinfo("Settings", "Settings functionality will be implemented here.")