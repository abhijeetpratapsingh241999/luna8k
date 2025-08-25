#!/usr/bin/env python3
"""
Launcher - Main entry point for Phone-PC Sync Emulator
Provides a unified interface to start all components
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import subprocess
import threading
import time
import sys
import os
from pathlib import Path
import psutil
import signal

# Set the appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SyncEmulatorLauncher:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Phone-PC Sync Emulator - Launcher")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Process tracking
        self.processes = {}
        self.status = {
            "server": "stopped",
            "devices": "stopped",
            "gui": "stopped"
        }
        
        self.setup_ui()
        self.check_dependencies()
        
    def setup_ui(self):
        """Setup the launcher UI"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Phone-PC Sync Emulator", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        subtitle_label = ctk.CTkLabel(
            self.main_frame, 
            text="Advanced Phone-PC Synchronization Software", 
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Components frame
        components_frame = ctk.CTkFrame(self.main_frame)
        components_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(components_frame, text="System Components", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Server component
        self.create_component_section(
            components_frame, 
            "Sync Server", 
            "Backend server handling device communication and data sync",
            "server"
        )
        
        # Device emulator component
        self.create_component_section(
            components_frame, 
            "Device Emulator", 
            "Virtual phone devices for testing and demonstration",
            "devices"
        )
        
        # GUI component
        self.create_component_section(
            components_frame, 
            "Main Application", 
            "Primary user interface for phone-PC synchronization",
            "gui"
        )
        
        # Control buttons
        self.create_control_buttons(components_frame)
        
        # Status and logs
        self.create_status_section()
        
    def create_component_section(self, parent, title, description, component_key):
        """Create a section for each component"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=20, pady=10)
        
        # Title and description
        header_frame = ctk.CTkFrame(section_frame)
        header_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(header_frame, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(header_frame, text=description, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(5, 0))
        
        # Controls
        controls_frame = ctk.CTkFrame(section_frame)
        controls_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Status label
        status_label = ctk.CTkLabel(controls_frame, text="Stopped", text_color="red")
        status_label.pack(side="left", padx=10, pady=10)
        
        # Buttons
        start_button = ctk.CTkButton(
            controls_frame, 
            text="Start", 
            command=lambda: self.start_component(component_key),
            width=80
        )
        start_button.pack(side="right", padx=5, pady=10)
        
        stop_button = ctk.CTkButton(
            controls_frame, 
            text="Stop", 
            command=lambda: self.stop_component(component_key),
            width=80,
            state="disabled"
        )
        stop_button.pack(side="right", padx=5, pady=10)
        
        # Store references
        setattr(self, f"{component_key}_status_label", status_label)
        setattr(self, f"{component_key}_start_button", start_button)
        setattr(self, f"{component_key}_stop_button", stop_button)
        
    def create_control_buttons(self, parent):
        """Create global control buttons"""
        control_frame = ctk.CTkFrame(parent)
        control_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(control_frame, text="Global Controls", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        buttons_frame = ctk.CTkFrame(control_frame)
        buttons_frame.pack(pady=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="Start All", 
            command=self.start_all,
            width=120,
            height=40
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="Stop All", 
            command=self.stop_all,
            width=120,
            height=40
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="Restart All", 
            command=self.restart_all,
            width=120,
            height=40
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="Open Data Folder", 
            command=self.open_data_folder,
            width=120,
            height=40
        ).pack(side="left", padx=10)
        
    def create_status_section(self):
        """Create status and log section"""
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(status_frame, text="System Status & Logs", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Log display
        self.log_text = ctk.CTkTextbox(status_frame, height=150)
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # System info
        info_frame = ctk.CTkFrame(status_frame)
        info_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.system_info_label = ctk.CTkLabel(info_frame, text="System: Ready")
        self.system_info_label.pack(side="left", padx=10, pady=5)
        
        self.memory_info_label = ctk.CTkLabel(info_frame, text="Memory: --")
        self.memory_info_label.pack(side="right", padx=10, pady=5)
        
    def log_message(self, message):
        """Add a message to the log"""
        timestamp = time.strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        self.log_text.insert("end", log_line)
        self.log_text.see("end")
        
    def update_component_status(self, component, status):
        """Update the status of a component"""
        self.status[component] = status
        
        status_label = getattr(self, f"{component}_status_label")
        start_button = getattr(self, f"{component}_start_button")
        stop_button = getattr(self, f"{component}_stop_button")
        
        if status == "running":
            status_label.configure(text="Running", text_color="green")
            start_button.configure(state="disabled")
            stop_button.configure(state="normal")
        elif status == "starting":
            status_label.configure(text="Starting...", text_color="orange")
            start_button.configure(state="disabled")
            stop_button.configure(state="disabled")
        elif status == "stopping":
            status_label.configure(text="Stopping...", text_color="orange")
            start_button.configure(state="disabled")
            stop_button.configure(state="disabled")
        else:  # stopped
            status_label.configure(text="Stopped", text_color="red")
            start_button.configure(state="normal")
            stop_button.configure(state="disabled")
            
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        self.log_message("Checking dependencies...")
        
        required_modules = [
            "flask", "flask_cors", "flask_socketio", "customtkinter", 
            "requests", "psutil", "cryptography", "pillow"
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module.replace('_', '-'))
            except ImportError:
                missing_modules.append(module)
                
        if missing_modules:
            self.log_message(f"Missing modules: {', '.join(missing_modules)}")
            self.log_message("Please install requirements: pip install -r requirements.txt")
        else:
            self.log_message("All dependencies satisfied")
            
    def start_component(self, component):
        """Start a specific component"""
        if self.status[component] == "running":
            return
            
        self.update_component_status(component, "starting")
        self.log_message(f"Starting {component}...")
        
        try:
            if component == "server":
                process = subprocess.Popen([
                    sys.executable, "sync_server.py"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
            elif component == "devices":
                process = subprocess.Popen([
                    sys.executable, "device_emulator.py"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
            elif component == "gui":
                process = subprocess.Popen([
                    sys.executable, "main.py"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
            self.processes[component] = process
            
            # Monitor process in background
            threading.Thread(
                target=self.monitor_process, 
                args=(component, process), 
                daemon=True
            ).start()
            
            # Give process time to start
            time.sleep(2)
            
            if process.poll() is None:  # Process is running
                self.update_component_status(component, "running")
                self.log_message(f"{component} started successfully")
            else:
                self.update_component_status(component, "stopped")
                self.log_message(f"Failed to start {component}")
                
        except Exception as e:
            self.update_component_status(component, "stopped")
            self.log_message(f"Error starting {component}: {str(e)}")
            
    def stop_component(self, component):
        """Stop a specific component"""
        if self.status[component] != "running":
            return
            
        self.update_component_status(component, "stopping")
        self.log_message(f"Stopping {component}...")
        
        try:
            if component in self.processes:
                process = self.processes[component]
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    
                del self.processes[component]
                
            self.update_component_status(component, "stopped")
            self.log_message(f"{component} stopped")
            
        except Exception as e:
            self.log_message(f"Error stopping {component}: {str(e)}")
            
    def monitor_process(self, component, process):
        """Monitor a process and update status when it exits"""
        process.wait()
        if component in self.processes:
            del self.processes[component]
            self.update_component_status(component, "stopped")
            self.log_message(f"{component} process ended")
            
    def start_all(self):
        """Start all components in order"""
        self.log_message("Starting all components...")
        
        # Start server first
        self.start_component("server")
        time.sleep(3)
        
        # Start device emulator
        self.start_component("devices")
        time.sleep(2)
        
        # Start GUI
        self.start_component("gui")
        
    def stop_all(self):
        """Stop all components"""
        self.log_message("Stopping all components...")
        
        for component in ["gui", "devices", "server"]:
            self.stop_component(component)
            time.sleep(1)
            
    def restart_all(self):
        """Restart all components"""
        self.log_message("Restarting all components...")
        self.stop_all()
        time.sleep(3)
        self.start_all()
        
    def open_data_folder(self):
        """Open the data folder in file explorer"""
        data_path = Path("data").absolute()
        data_path.mkdir(exist_ok=True)
        
        try:
            if sys.platform == "win32":
                subprocess.run(["explorer", str(data_path)])
            elif sys.platform == "darwin":
                subprocess.run(["open", str(data_path)])
            else:
                subprocess.run(["xdg-open", str(data_path)])
        except Exception as e:
            self.log_message(f"Could not open data folder: {str(e)}")
            
    def update_system_info(self):
        """Update system information display"""
        try:
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_text = f"Memory: {memory.percent:.1f}% used"
            self.memory_info_label.configure(text=memory_text)
            
            # Update system status
            running_components = [k for k, v in self.status.items() if v == "running"]
            if running_components:
                system_text = f"System: {len(running_components)}/3 components running"
            else:
                system_text = "System: All components stopped"
            self.system_info_label.configure(text=system_text)
            
        except Exception as e:
            self.log_message(f"Error updating system info: {str(e)}")
            
        # Schedule next update
        self.root.after(5000, self.update_system_info)
        
    def on_closing(self):
        """Handle application closing"""
        if any(status == "running" for status in self.status.values()):
            if messagebox.askyesno("Confirm Exit", "Stop all running components and exit?"):
                self.stop_all()
                time.sleep(2)
                self.root.destroy()
        else:
            self.root.destroy()
            
    def run(self):
        """Start the launcher application"""
        self.log_message("Phone-PC Sync Emulator Launcher started")
        self.log_message("Ready to launch components")
        
        # Start system info updates
        self.update_system_info()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start the main loop
        self.root.mainloop()

if __name__ == "__main__":
    launcher = SyncEmulatorLauncher()
    launcher.run()