#!/usr/bin/env python3
"""
Phone-PC Sync Emulator
A complex synchronization software that emulates phone-PC connectivity
with features like file transfer, contacts sync, messages, and device management.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import threading
import json
import os
import sys
from datetime import datetime
import socket
import subprocess
from pathlib import Path

# Set the appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PhonePCSyncEmulator:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Phone-PC Sync Emulator Pro")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize data directories
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / "phones").mkdir(exist_ok=True)
        (self.data_dir / "transfers").mkdir(exist_ok=True)
        (self.data_dir / "backups").mkdir(exist_ok=True)
        
        # Application state
        self.connected_devices = {}
        self.sync_status = "Disconnected"
        self.transfer_progress = 0
        
        self.setup_ui()
        self.load_sample_data()
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Phone-PC Sync Emulator Pro", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create tabs
        self.create_connection_tab()
        self.create_file_transfer_tab()
        self.create_contacts_tab()
        self.create_messages_tab()
        self.create_device_info_tab()
        self.create_settings_tab()
        
        # Status bar
        self.create_status_bar()
        
    def create_connection_tab(self):
        """Create the device connection and management tab"""
        tab = self.notebook.add("Connection")
        
        # Connection frame
        conn_frame = ctk.CTkFrame(tab)
        conn_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(conn_frame, text="Device Connection", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Connection controls
        controls_frame = ctk.CTkFrame(conn_frame)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        self.scan_button = ctk.CTkButton(
            controls_frame, 
            text="Scan for Devices", 
            command=self.scan_devices,
            width=150
        )
        self.scan_button.pack(side="left", padx=10, pady=10)
        
        self.connect_button = ctk.CTkButton(
            controls_frame, 
            text="Connect", 
            command=self.connect_device,
            width=150
        )
        self.connect_button.pack(side="left", padx=10, pady=10)
        
        self.disconnect_button = ctk.CTkButton(
            controls_frame, 
            text="Disconnect", 
            command=self.disconnect_device,
            width=150,
            state="disabled"
        )
        self.disconnect_button.pack(side="left", padx=10, pady=10)
        
        # Device list
        devices_frame = ctk.CTkFrame(conn_frame)
        devices_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(devices_frame, text="Available Devices:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        # Create treeview for devices
        self.device_tree = ttk.Treeview(devices_frame, columns=("Name", "Type", "Status", "Battery"), show="headings", height=8)
        self.device_tree.heading("Name", text="Device Name")
        self.device_tree.heading("Type", text="Type")
        self.device_tree.heading("Status", text="Status")
        self.device_tree.heading("Battery", text="Battery")
        
        self.device_tree.column("Name", width=200)
        self.device_tree.column("Type", width=100)
        self.device_tree.column("Status", width=100)
        self.device_tree.column("Battery", width=100)
        
        scrollbar = ttk.Scrollbar(devices_frame, orient="vertical", command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=scrollbar.set)
        
        self.device_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
    def create_file_transfer_tab(self):
        """Create the file transfer tab"""
        tab = self.notebook.add("File Transfer")
        
        # Transfer controls
        controls_frame = ctk.CTkFrame(tab)
        controls_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(controls_frame, text="File Transfer", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(controls_frame)
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="Send to Phone", 
            command=self.send_to_phone,
            width=150
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="Receive from Phone", 
            command=self.receive_from_phone,
            width=150
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="Sync Folders", 
            command=self.sync_folders,
            width=150
        ).pack(side="left", padx=10, pady=10)
        
        # Progress frame
        progress_frame = ctk.CTkFrame(controls_frame)
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(progress_frame, text="Transfer Progress:").pack(anchor="w", padx=10, pady=5)
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="Ready")
        self.progress_label.pack(anchor="w", padx=10, pady=5)
        
        # File lists
        lists_frame = ctk.CTkFrame(tab)
        lists_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # PC files
        pc_frame = ctk.CTkFrame(lists_frame)
        pc_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(pc_frame, text="PC Files", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.pc_files_tree = ttk.Treeview(pc_frame, columns=("Size", "Modified"), show="tree headings", height=15)
        self.pc_files_tree.heading("#0", text="Name")
        self.pc_files_tree.heading("Size", text="Size")
        self.pc_files_tree.heading("Modified", text="Modified")
        
        pc_scrollbar = ttk.Scrollbar(pc_frame, orient="vertical", command=self.pc_files_tree.yview)
        self.pc_files_tree.configure(yscrollcommand=pc_scrollbar.set)
        
        self.pc_files_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        pc_scrollbar.pack(side="right", fill="y", pady=5)
        
        # Phone files
        phone_frame = ctk.CTkFrame(lists_frame)
        phone_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(phone_frame, text="Phone Files", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.phone_files_tree = ttk.Treeview(phone_frame, columns=("Size", "Modified"), show="tree headings", height=15)
        self.phone_files_tree.heading("#0", text="Name")
        self.phone_files_tree.heading("Size", text="Size")
        self.phone_files_tree.heading("Modified", text="Modified")
        
        phone_scrollbar = ttk.Scrollbar(phone_frame, orient="vertical", command=self.phone_files_tree.yview)
        self.phone_files_tree.configure(yscrollcommand=phone_scrollbar.set)
        
        self.phone_files_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        phone_scrollbar.pack(side="right", fill="y", pady=5)
        
    def create_contacts_tab(self):
        """Create the contacts synchronization tab"""
        tab = self.notebook.add("Contacts")
        
        # Controls
        controls_frame = ctk.CTkFrame(tab)
        controls_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(controls_frame, text="Contacts Synchronization", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        buttons_frame = ctk.CTkFrame(controls_frame)
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="Sync to Phone", 
            command=self.sync_contacts_to_phone,
            width=150
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="Sync from Phone", 
            command=self.sync_contacts_from_phone,
            width=150
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="Merge Contacts", 
            command=self.merge_contacts,
            width=150
        ).pack(side="left", padx=10, pady=10)
        
        # Contacts display
        contacts_frame = ctk.CTkFrame(tab)
        contacts_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # PC contacts
        pc_contacts_frame = ctk.CTkFrame(contacts_frame)
        pc_contacts_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(pc_contacts_frame, text="PC Contacts", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.pc_contacts_tree = ttk.Treeview(pc_contacts_frame, columns=("Phone", "Email"), show="tree headings", height=15)
        self.pc_contacts_tree.heading("#0", text="Name")
        self.pc_contacts_tree.heading("Phone", text="Phone")
        self.pc_contacts_tree.heading("Email", text="Email")
        
        self.pc_contacts_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Phone contacts
        phone_contacts_frame = ctk.CTkFrame(contacts_frame)
        phone_contacts_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(phone_contacts_frame, text="Phone Contacts", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.phone_contacts_tree = ttk.Treeview(phone_contacts_frame, columns=("Phone", "Email"), show="tree headings", height=15)
        self.phone_contacts_tree.heading("#0", text="Name")
        self.phone_contacts_tree.heading("Phone", text="Phone")
        self.phone_contacts_tree.heading("Email", text="Email")
        
        self.phone_contacts_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
    def create_messages_tab(self):
        """Create the messages/SMS synchronization tab"""
        tab = self.notebook.add("Messages")
        
        # Controls
        controls_frame = ctk.CTkFrame(tab)
        controls_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(controls_frame, text="Messages Synchronization", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        buttons_frame = ctk.CTkFrame(controls_frame)
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="Sync Messages", 
            command=self.sync_messages,
            width=150
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="Export Messages", 
            command=self.export_messages,
            width=150
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="Send Test SMS", 
            command=self.send_test_sms,
            width=150
        ).pack(side="left", padx=10, pady=10)
        
        # Messages display
        messages_frame = ctk.CTkFrame(tab)
        messages_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.messages_tree = ttk.Treeview(
            messages_frame, 
            columns=("Contact", "Message", "Time", "Type"), 
            show="headings", 
            height=20
        )
        self.messages_tree.heading("Contact", text="Contact")
        self.messages_tree.heading("Message", text="Message")
        self.messages_tree.heading("Time", text="Time")
        self.messages_tree.heading("Type", text="Type")
        
        self.messages_tree.column("Contact", width=150)
        self.messages_tree.column("Message", width=400)
        self.messages_tree.column("Time", width=150)
        self.messages_tree.column("Type", width=100)
        
        messages_scrollbar = ttk.Scrollbar(messages_frame, orient="vertical", command=self.messages_tree.yview)
        self.messages_tree.configure(yscrollcommand=messages_scrollbar.set)
        
        self.messages_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        messages_scrollbar.pack(side="right", fill="y", pady=5)
        
    def create_device_info_tab(self):
        """Create the device information and monitoring tab"""
        tab = self.notebook.add("Device Info")
        
        # Device status
        status_frame = ctk.CTkFrame(tab)
        status_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(status_frame, text="Device Information", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Info grid
        info_frame = ctk.CTkFrame(status_frame)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        # Device details
        self.device_info_labels = {}
        info_items = [
            ("Device Name:", "Not Connected"),
            ("Model:", "Unknown"),
            ("OS Version:", "Unknown"),
            ("Battery Level:", "Unknown"),
            ("Storage Used:", "Unknown"),
            ("Signal Strength:", "Unknown"),
            ("Last Sync:", "Never")
        ]
        
        for i, (label, value) in enumerate(info_items):
            ctk.CTkLabel(info_frame, text=label, font=ctk.CTkFont(weight="bold")).grid(
                row=i, column=0, sticky="w", padx=10, pady=5
            )
            self.device_info_labels[label] = ctk.CTkLabel(info_frame, text=value)
            self.device_info_labels[label].grid(row=i, column=1, sticky="w", padx=10, pady=5)
        
        # System monitoring
        monitoring_frame = ctk.CTkFrame(tab)
        monitoring_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(monitoring_frame, text="System Monitoring", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Activity log
        log_frame = ctk.CTkFrame(monitoring_frame)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(log_frame, text="Activity Log:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        self.activity_log = ctk.CTkTextbox(log_frame, height=300)
        self.activity_log.pack(fill="both", expand=True, padx=10, pady=10)
        
    def create_settings_tab(self):
        """Create the settings and configuration tab"""
        tab = self.notebook.add("Settings")
        
        # Settings frame
        settings_frame = ctk.CTkFrame(tab)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(settings_frame, text="Settings & Configuration", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Sync settings
        sync_frame = ctk.CTkFrame(settings_frame)
        sync_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(sync_frame, text="Sync Options", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        self.auto_sync_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(sync_frame, text="Enable Auto-Sync", variable=self.auto_sync_var).pack(anchor="w", padx=20, pady=5)
        
        self.backup_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(sync_frame, text="Create Backups", variable=self.backup_var).pack(anchor="w", padx=20, pady=5)
        
        self.notifications_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(sync_frame, text="Show Notifications", variable=self.notifications_var).pack(anchor="w", padx=20, pady=5)
        
        # Connection settings
        conn_settings_frame = ctk.CTkFrame(settings_frame)
        conn_settings_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(conn_settings_frame, text="Connection Settings", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        ctk.CTkLabel(conn_settings_frame, text="Connection Type:").pack(anchor="w", padx=20, pady=2)
        self.connection_type = ctk.CTkOptionMenu(
            conn_settings_frame, 
            values=["USB", "WiFi", "Bluetooth", "Cloud"]
        )
        self.connection_type.pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkLabel(conn_settings_frame, text="Sync Frequency:").pack(anchor="w", padx=20, pady=2)
        self.sync_frequency = ctk.CTkOptionMenu(
            conn_settings_frame, 
            values=["Manual", "Every 5 minutes", "Every 15 minutes", "Every hour", "Daily"]
        )
        self.sync_frequency.pack(anchor="w", padx=20, pady=5)
        
        # Save settings button
        ctk.CTkButton(
            settings_frame, 
            text="Save Settings", 
            command=self.save_settings,
            width=150
        ).pack(pady=20)
        
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        self.status_frame = ctk.CTkFrame(self.root, height=40)
        self.status_frame.pack(fill="x", side="bottom")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="Status: Ready", 
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=10)
        
        self.connection_status = ctk.CTkLabel(
            self.status_frame, 
            text="Disconnected", 
            font=ctk.CTkFont(size=12),
            text_color="red"
        )
        self.connection_status.pack(side="right", padx=10, pady=10)
        
    def log_activity(self, message):
        """Add a message to the activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.activity_log.insert("end", log_message)
        self.activity_log.see("end")
        
    def update_status(self, message, connection_status=None):
        """Update the status bar"""
        self.status_label.configure(text=f"Status: {message}")
        if connection_status:
            color = "green" if connection_status == "Connected" else "red"
            self.connection_status.configure(text=connection_status, text_color=color)
        
    # Device connection methods
    def scan_devices(self):
        """Simulate scanning for devices"""
        self.log_activity("Scanning for devices...")
        self.update_status("Scanning...")
        
        # Simulate scan delay
        self.root.after(2000, self._populate_devices)
        
    def _populate_devices(self):
        """Populate the device list with simulated devices"""
        # Clear existing items
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)
            
        # Add simulated devices
        devices = [
            ("Samsung Galaxy S21", "Android", "Available", "85%"),
            ("iPhone 13 Pro", "iOS", "Available", "92%"),
            ("OnePlus 9", "Android", "Available", "67%"),
            ("Google Pixel 6", "Android", "Available", "78%"),
        ]
        
        for device in devices:
            self.device_tree.insert("", "end", values=device)
            
        self.log_activity(f"Found {len(devices)} devices")
        self.update_status("Scan complete")
        
    def connect_device(self):
        """Connect to selected device"""
        selected = self.device_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a device to connect")
            return
            
        device = self.device_tree.item(selected[0])['values']
        device_name = device[0]
        
        self.log_activity(f"Connecting to {device_name}...")
        self.update_status("Connecting...", "Connecting")
        
        # Simulate connection delay
        self.root.after(3000, lambda: self._complete_connection(device_name))
        
    def _complete_connection(self, device_name):
        """Complete the device connection"""
        self.connected_devices[device_name] = {
            "name": device_name,
            "connected_at": datetime.now(),
            "status": "Connected"
        }
        
        # Update UI
        self.connect_button.configure(state="disabled")
        self.disconnect_button.configure(state="normal")
        
        # Update device info
        self.device_info_labels["Device Name:"].configure(text=device_name)
        self.device_info_labels["Model:"].configure(text="SM-G991B" if "Samsung" in device_name else "A2633")
        self.device_info_labels["OS Version:"].configure(text="Android 12" if "Samsung" in device_name else "iOS 15.6")
        self.device_info_labels["Battery Level:"].configure(text="85%")
        self.device_info_labels["Storage Used:"].configure(text="45.2 GB / 128 GB")
        self.device_info_labels["Signal Strength:"].configure(text="4 bars")
        self.device_info_labels["Last Sync:"].configure(text="Just now")
        
        self.log_activity(f"Successfully connected to {device_name}")
        self.update_status("Ready", "Connected")
        
        # Load phone data
        self.load_phone_data()
        
    def disconnect_device(self):
        """Disconnect from device"""
        self.connected_devices.clear()
        
        # Update UI
        self.connect_button.configure(state="normal")
        self.disconnect_button.configure(state="disabled")
        
        # Reset device info
        for label in self.device_info_labels.values():
            label.configure(text="Not Connected")
            
        self.log_activity("Device disconnected")
        self.update_status("Ready", "Disconnected")
        
        # Clear phone data
        for item in self.phone_files_tree.get_children():
            self.phone_files_tree.delete(item)
        for item in self.phone_contacts_tree.get_children():
            self.phone_contacts_tree.delete(item)
            
    # File transfer methods
    def send_to_phone(self):
        """Send files to phone"""
        if not self.connected_devices:
            messagebox.showwarning("Warning", "No device connected")
            return
            
        files = filedialog.askopenfilenames(title="Select files to send to phone")
        if files:
            self.log_activity(f"Sending {len(files)} files to phone...")
            self._simulate_transfer("send", files)
            
    def receive_from_phone(self):
        """Receive files from phone"""
        if not self.connected_devices:
            messagebox.showwarning("Warning", "No device connected")
            return
            
        # Simulate file selection from phone
        files = ["photo_001.jpg", "video_001.mp4", "document.pdf"]
        self.log_activity(f"Receiving {len(files)} files from phone...")
        self._simulate_transfer("receive", files)
        
    def sync_folders(self):
        """Synchronize folders between PC and phone"""
        if not self.connected_devices:
            messagebox.showwarning("Warning", "No device connected")
            return
            
        self.log_activity("Starting folder synchronization...")
        self._simulate_transfer("sync", ["Documents", "Pictures", "Music"])
        
    def _simulate_transfer(self, operation, files):
        """Simulate file transfer with progress"""
        self.progress_bar.set(0)
        self.progress_label.configure(text=f"{operation.capitalize()}ing files...")
        
        def update_progress():
            current = self.progress_bar.get()
            if current < 1.0:
                current += 0.1
                self.progress_bar.set(current)
                self.progress_label.configure(text=f"{operation.capitalize()}ing... {int(current*100)}%")
                self.root.after(500, update_progress)
            else:
                self.progress_label.configure(text=f"{operation.capitalize()} complete!")
                self.log_activity(f"Transfer complete: {len(files)} items")
                
        update_progress()
        
    # Contacts methods
    def sync_contacts_to_phone(self):
        """Sync contacts from PC to phone"""
        if not self.connected_devices:
            messagebox.showwarning("Warning", "No device connected")
            return
            
        self.log_activity("Syncing contacts to phone...")
        self.update_status("Syncing contacts...")
        
        # Simulate sync
        self.root.after(2000, lambda: self._complete_sync("contacts", "to phone"))
        
    def sync_contacts_from_phone(self):
        """Sync contacts from phone to PC"""
        if not self.connected_devices:
            messagebox.showwarning("Warning", "No device connected")
            return
            
        self.log_activity("Syncing contacts from phone...")
        self.update_status("Syncing contacts...")
        
        # Simulate sync
        self.root.after(2000, lambda: self._complete_sync("contacts", "from phone"))
        
    def merge_contacts(self):
        """Merge contacts between PC and phone"""
        if not self.connected_devices:
            messagebox.showwarning("Warning", "No device connected")
            return
            
        self.log_activity("Merging contacts...")
        self.update_status("Merging contacts...")
        
        # Simulate merge
        self.root.after(3000, lambda: self._complete_sync("contacts", "merge"))
        
    def _complete_sync(self, sync_type, direction):
        """Complete synchronization operation"""
        self.log_activity(f"Contact {direction} completed successfully")
        self.update_status("Ready", "Connected")
        
    # Messages methods
    def sync_messages(self):
        """Sync messages"""
        if not self.connected_devices:
            messagebox.showwarning("Warning", "No device connected")
            return
            
        self.log_activity("Syncing messages...")
        self.update_status("Syncing messages...")
        
        # Simulate message sync
        self.root.after(2000, self._load_messages)
        
    def export_messages(self):
        """Export messages to file"""
        filename = filedialog.asksaveasfilename(
            title="Export messages",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.log_activity(f"Exporting messages to {filename}")
            
    def send_test_sms(self):
        """Send a test SMS"""
        if not self.connected_devices:
            messagebox.showwarning("Warning", "No device connected")
            return
            
        self.log_activity("Sending test SMS...")
        # Add test message to the tree
        current_time = datetime.now().strftime("%H:%M:%S")
        self.messages_tree.insert("", "end", values=("Test Contact", "This is a test message", current_time, "Sent"))
        
    def _load_messages(self):
        """Load sample messages"""
        messages = [
            ("Alice Smith", "Hey, how are you doing?", "10:30 AM", "Received"),
            ("Bob Johnson", "Meeting at 3 PM today", "11:15 AM", "Received"),
            ("Charlie Brown", "Thanks for the help!", "2:45 PM", "Sent"),
            ("Diana Wilson", "Call me when you're free", "4:20 PM", "Received"),
        ]
        
        for item in self.messages_tree.get_children():
            self.messages_tree.delete(item)
            
        for message in messages:
            self.messages_tree.insert("", "end", values=message)
            
        self.log_activity("Messages synchronized successfully")
        self.update_status("Ready", "Connected")
        
    def save_settings(self):
        """Save application settings"""
        settings = {
            "auto_sync": self.auto_sync_var.get(),
            "backup": self.backup_var.get(),
            "notifications": self.notifications_var.get(),
            "connection_type": self.connection_type.get(),
            "sync_frequency": self.sync_frequency.get()
        }
        
        with open(self.data_dir / "settings.json", "w") as f:
            json.dump(settings, f, indent=2)
            
        self.log_activity("Settings saved successfully")
        messagebox.showinfo("Success", "Settings saved successfully!")
        
    def load_sample_data(self):
        """Load sample data for demonstration"""
        # Load PC files
        pc_files = [
            ("Documents", "Folder", "2024-01-15 10:30"),
            ("  report.docx", "2.5 MB", "2024-01-15 09:45"),
            ("  presentation.pptx", "5.1 MB", "2024-01-14 16:20"),
            ("Pictures", "Folder", "2024-01-15 11:00"),
            ("  vacation.jpg", "3.2 MB", "2024-01-10 14:30"),
            ("  family.png", "1.8 MB", "2024-01-12 19:15"),
            ("Music", "Folder", "2024-01-15 12:00"),
            ("  song1.mp3", "4.5 MB", "2024-01-08 20:00"),
            ("  song2.mp3", "3.9 MB", "2024-01-09 21:30"),
        ]
        
        for file_info in pc_files:
            if file_info[1] == "Folder":
                parent = self.pc_files_tree.insert("", "end", text=file_info[0], values=("", file_info[2]))
            else:
                self.pc_files_tree.insert(parent, "end", text=file_info[0], values=(file_info[1], file_info[2]))
                
        # Load PC contacts
        pc_contacts = [
            ("John Doe", "+1-555-0123", "john@email.com"),
            ("Jane Smith", "+1-555-0456", "jane@email.com"),
            ("Mike Wilson", "+1-555-0789", "mike@email.com"),
            ("Sarah Davis", "+1-555-0321", "sarah@email.com"),
        ]
        
        for contact in pc_contacts:
            self.pc_contacts_tree.insert("", "end", text=contact[0], values=(contact[1], contact[2]))
            
    def load_phone_data(self):
        """Load simulated phone data"""
        # Load phone files
        phone_files = [
            ("DCIM", "Folder", "2024-01-15 14:30"),
            ("  IMG_001.jpg", "2.1 MB", "2024-01-15 14:25"),
            ("  IMG_002.jpg", "1.9 MB", "2024-01-15 14:26"),
            ("Downloads", "Folder", "2024-01-15 15:00"),
            ("  app.apk", "25.3 MB", "2024-01-14 10:15"),
            ("  document.pdf", "1.2 MB", "2024-01-13 16:45"),
            ("Music", "Folder", "2024-01-15 16:00"),
            ("  ringtone.mp3", "0.8 MB", "2024-01-10 12:00"),
        ]
        
        for file_info in phone_files:
            if file_info[1] == "Folder":
                parent = self.phone_files_tree.insert("", "end", text=file_info[0], values=("", file_info[2]))
            else:
                self.phone_files_tree.insert(parent, "end", text=file_info[0], values=(file_info[1], file_info[2]))
                
        # Load phone contacts
        phone_contacts = [
            ("Alice Brown", "+1-555-1111", "alice@phone.com"),
            ("Bob Green", "+1-555-2222", "bob@phone.com"),
            ("Carol White", "+1-555-3333", "carol@phone.com"),
            ("David Black", "+1-555-4444", "david@phone.com"),
        ]
        
        for contact in phone_contacts:
            self.phone_contacts_tree.insert("", "end", text=contact[0], values=(contact[1], contact[2]))
            
    def run(self):
        """Start the application"""
        self.log_activity("Phone-PC Sync Emulator started")
        self.update_status("Ready")
        self.root.mainloop()

if __name__ == "__main__":
    app = PhonePCSyncEmulator()
    app.run()