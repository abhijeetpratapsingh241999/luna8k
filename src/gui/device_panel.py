"""
Device Panel
Displays device information for phone and PC
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List


class DevicePanel(ttk.Frame):
    """Panel for displaying device information"""
    
    def __init__(self, parent, sync_manager):
        super().__init__(parent)
        self.sync_manager = sync_manager
        
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._create_widgets()
        self._update_display()
    
    def _create_widgets(self):
        """Create the panel widgets"""
        # Title
        title_label = ttk.Label(self, text="Device Information", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Create notebook for device tabs
        self.device_notebook = ttk.Notebook(self)
        self.device_notebook.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Phone tab
        self.phone_frame = ttk.Frame(self.device_notebook)
        self.device_notebook.add(self.phone_frame, text="📱 Phone")
        self._create_phone_widgets()
        
        # PC tab
        self.pc_frame = ttk.Frame(self.device_notebook)
        self.device_notebook.add(self.pc_frame, text="💻 PC")
        self._create_pc_widgets()
        
        # Connection tab
        self.connection_frame = ttk.Frame(self.device_notebook)
        self.device_notebook.add(self.connection_frame, text="🔌 Connection")
        self._create_connection_widgets()
    
    def _create_phone_widgets(self):
        """Create phone device widgets"""
        # Device info section
        phone_info_frame = ttk.LabelFrame(self.phone_frame, text="Device Info", padding=10)
        phone_info_frame.pack(fill="x", padx=5, pady=5)
        
        # Device name and model
        ttk.Label(phone_info_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.phone_name_label = ttk.Label(phone_info_frame, text="SmartPhone Pro")
        self.phone_name_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(phone_info_frame, text="Model:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.phone_model_label = ttk.Label(phone_info_frame, text="SP-2024")
        self.phone_model_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(phone_info_frame, text="OS:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.phone_os_label = ttk.Label(phone_info_frame, text="Android 14.0")
        self.phone_os_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Battery section
        battery_frame = ttk.LabelFrame(self.phone_frame, text="Battery", padding=10)
        battery_frame.pack(fill="x", padx=5, pady=5)
        
        self.battery_progress = ttk.Progressbar(battery_frame, length=200, mode='determinate')
        self.battery_progress.pack(fill="x", padx=5, pady=5)
        
        self.battery_label = ttk.Label(battery_frame, text="85% - Not charging")
        self.battery_label.pack(pady=5)
        
        # Storage section
        storage_frame = ttk.LabelFrame(self.phone_frame, text="Storage", padding=10)
        storage_frame.pack(fill="x", padx=5, pady=5)
        
        self.storage_progress = ttk.Progressbar(storage_frame, length=200, mode='determinate')
        self.storage_progress.pack(fill="x", padx=5, pady=5)
        
        self.storage_label = ttk.Label(storage_frame, text="64 GB / 128 GB (50%)")
        self.storage_label.pack(pady=5)
        
        # Network section
        network_frame = ttk.LabelFrame(self.phone_frame, text="Network", padding=10)
        network_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(network_frame, text="Signal:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.signal_label = ttk.Label(network_frame, text="●●●●● (5G)")
        self.signal_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(network_frame, text="Status:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.network_status_label = ttk.Label(network_frame, text="Disconnected", foreground="red")
        self.network_status_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
    
    def _create_pc_widgets(self):
        """Create PC device widgets"""
        # Device info section
        pc_info_frame = ttk.LabelFrame(self.pc_frame, text="Device Info", padding=10)
        pc_info_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(pc_info_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.pc_name_label = ttk.Label(pc_info_frame, text="Desktop Computer")
        self.pc_name_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(pc_info_frame, text="Model:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.pc_model_label = ttk.Label(pc_info_frame, text="DC-2024")
        self.pc_model_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(pc_info_frame, text="OS:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.pc_os_label = ttk.Label(pc_info_frame, text="Windows 11 Pro")
        self.pc_os_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # System performance section
        perf_frame = ttk.LabelFrame(self.pc_frame, text="System Performance", padding=10)
        perf_frame.pack(fill="x", padx=5, pady=5)
        
        # CPU usage
        ttk.Label(perf_frame, text="CPU:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.cpu_progress = ttk.Progressbar(perf_frame, length=150, mode='determinate')
        self.cpu_progress.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.cpu_label = ttk.Label(perf_frame, text="0%")
        self.cpu_label.grid(row=0, column=2, sticky="w", padx=5, pady=2)
        
        # Memory usage
        ttk.Label(perf_frame, text="Memory:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.memory_progress = ttk.Progressbar(perf_frame, length=150, mode='determinate')
        self.memory_progress.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.memory_label = ttk.Label(perf_frame, text="0%")
        self.memory_label.grid(row=1, column=2, sticky="w", padx=5, pady=2)
        
        # Storage section
        storage_frame = ttk.LabelFrame(self.pc_frame, text="Storage", padding=10)
        storage_frame.pack(fill="x", padx=5, pady=5)
        
        self.pc_storage_progress = ttk.Progressbar(storage_frame, length=200, mode='determinate')
        self.pc_storage_progress.pack(fill="x", padx=5, pady=5)
        
        self.pc_storage_label = ttk.Label(storage_frame, text="400 GB / 1 TB (40%)")
        self.pc_storage_label.pack(pady=5)
        
        # System health
        health_frame = ttk.LabelFrame(self.pc_frame, text="System Health", padding=10)
        health_frame.pack(fill="x", padx=5, pady=5)
        
        self.health_label = ttk.Label(health_frame, text="Excellent", font=("Arial", 10, "bold"))
        self.health_label.pack(pady=5)
    
    def _create_connection_widgets(self):
        """Create connection widgets"""
        # Connection status
        status_frame = ttk.LabelFrame(self.connection_frame, text="Connection Status", padding=10)
        status_frame.pack(fill="x", padx=5, pady=5)
        
        self.connection_status_label = ttk.Label(status_frame, text="Disconnected", font=("Arial", 12, "bold"), foreground="red")
        self.connection_status_label.pack(pady=10)
        
        # Protocol information
        protocol_frame = ttk.LabelFrame(self.connection_frame, text="Protocol Information", padding=10)
        protocol_frame.pack(fill="x", padx=5, pady=5)
        
        # Protocol selection
        ttk.Label(protocol_frame, text="Protocol:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.protocol_var = tk.StringVar(value="USB")
        protocol_combo = ttk.Combobox(protocol_frame, textvariable=self.protocol_var, 
                                     values=["USB", "Bluetooth", "WiFi", "NFC"], state="readonly")
        protocol_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Connection speed
        ttk.Label(protocol_frame, text="Speed:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.speed_label = ttk.Label(protocol_frame, text="480 Mbps")
        self.speed_label.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Reliability
        ttk.Label(protocol_frame, text="Reliability:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.reliability_label = ttk.Label(protocol_frame, text="99%")
        self.reliability_label.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Connection button
        self.connect_btn = ttk.Button(protocol_frame, text="Connect", command=self._connect_protocol)
        self.connect_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        protocol_frame.grid_columnconfigure(1, weight=1)
    
    def _connect_protocol(self):
        """Connect using selected protocol"""
        protocol = self.protocol_var.get()
        # This would integrate with the actual protocol manager
        print(f"Connecting via {protocol}")
    
    def update_display(self):
        """Update the device display"""
        try:
            # Update phone information
            phone_info = self.sync_manager.phone_emulator.get_device_info()
            phone_storage = self.sync_manager.phone_emulator.get_storage_info()
            phone_battery = self.sync_manager.phone_emulator.get_battery_info()
            phone_network = self.sync_manager.phone_emulator.get_network_info()
            
            # Update phone labels
            self.phone_name_label.config(text=phone_info.name)
            self.phone_model_label.config(text=phone_info.model)
            self.phone_os_label.config(text=phone_info.os_version)
            
            # Update battery
            battery_level = phone_battery["level"]
            self.battery_progress["value"] = battery_level
            charging_text = "Charging" if phone_battery["is_charging"] else "Not charging"
            self.battery_label.config(text=f"{battery_level}% - {charging_text}")
            
            # Update storage
            storage_percent = phone_storage["usage_percentage"]
            self.storage_progress["value"] = storage_percent
            used_gb = phone_storage["used_storage"] / (1024**3)
            total_gb = phone_storage["total_capacity"] / (1024**3)
            self.storage_label.config(text=f"{used_gb:.1f} GB / {total_gb:.1f} GB ({storage_percent:.1f}%)")
            
            # Update network
            signal_bars = "●" * phone_network["signal_strength"] + "○" * (5 - phone_network["signal_strength"])
            self.signal_label.config(text=f"{signal_bars} ({phone_network['network_type']})")
            
            network_status = "Connected" if phone_network["is_connected"] else "Disconnected"
            network_color = "green" if phone_network["is_connected"] else "red"
            self.network_status_label.config(text=network_status, foreground=network_color)
            
            # Update PC information
            pc_info = self.sync_manager.pc_emulator.get_device_info()
            pc_storage = self.sync_manager.pc_emulator.get_storage_info()
            pc_system = self.sync_manager.pc_emulator.get_system_info()
            pc_perf = self.sync_manager.pc_emulator.get_performance_metrics()
            
            # Update PC labels
            self.pc_name_label.config(text=pc_info.name)
            self.pc_model_label.config(text=pc_info.model)
            self.pc_os_label.config(text=pc_info.os_version)
            
            # Update performance
            cpu_usage = pc_system["cpu_usage"]
            self.cpu_progress["value"] = cpu_usage
            self.cpu_label.config(text=f"{cpu_usage}%")
            
            memory_usage = pc_system["memory_usage"]
            self.memory_progress["value"] = memory_usage
            self.memory_label.config(text=f"{memory_usage}%")
            
            # Update PC storage
            pc_storage_percent = pc_storage["usage_percentage"]
            self.pc_storage_progress["value"] = pc_storage_percent
            pc_used_gb = pc_storage["used_storage"] / (1024**3)
            pc_total_gb = pc_storage["total_capacity"] / (1024**3)
            self.pc_storage_label.config(text=f"{pc_used_gb:.1f} GB / {pc_total_gb:.1f} GB ({pc_storage_percent:.1f}%)")
            
            # Update system health
            health = pc_perf["system_health"]
            health_color = "green" if health == "Excellent" else "orange" if health == "Good" else "red"
            self.health_label.config(text=health, foreground=health_color)
            
            # Update connection status
            if phone_network["is_connected"]:
                self.connection_status_label.config(text="Connected", foreground="green")
                self.connect_btn.config(state="disabled")
            else:
                self.connection_status_label.config(text="Disconnected", foreground="red")
                self.connect_btn.config(state="normal")
            
            # Update protocol information based on selected protocol
            protocol = self.protocol_var.get()
            if protocol == "USB":
                self.speed_label.config(text="480 Mbps")
                self.reliability_label.config(text="99%")
            elif protocol == "Bluetooth":
                self.speed_label.config(text="24 Mbps")
                self.reliability_label.config(text="85%")
            elif protocol == "WiFi":
                self.speed_label.config(text="100 Mbps")
                self.reliability_label.config(text="90%")
            elif protocol == "NFC":
                self.speed_label.config(text="0.424 Mbps")
                self.reliability_label.config(text="95%")
                
        except Exception as e:
            print(f"Error updating device display: {e}")
    
    def on_device_connected(self):
        """Handle device connection event"""
        self.network_status_label.config(text="Connected", foreground="green")
        self.connection_status_label.config(text="Connected", foreground="green")
        self.connect_btn.config(state="disabled")
    
    def on_device_disconnected(self):
        """Handle device disconnection event"""
        self.network_status_label.config(text="Disconnected", foreground="red")
        self.connection_status_label.config(text="Disconnected", foreground="red")
        self.connect_btn.config(state="normal")