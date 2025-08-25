"""
Configuration Manager
Handles application configuration and settings
"""

import configparser
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.default_config = self._get_default_config()
        
        # Load configuration
        self.load_config()
    
    def _get_default_config(self) -> Dict[str, Dict[str, Any]]:
        """Get default configuration values"""
        return {
            "General": {
                "app_name": "Phone-PC Sync Emulator",
                "version": "1.0.0",
                "debug_mode": "false",
                "log_level": "INFO",
                "auto_save": "true"
            },
            "Sync": {
                "default_sync_type": "incremental",
                "auto_sync_interval": "30",
                "max_file_size": "100",
                "conflict_resolution": "newer_wins",
                "retry_attempts": "3",
                "retry_delay": "5"
            },
            "Protocols": {
                "preferred_protocol": "USB",
                "usb_speed": "480",
                "bluetooth_speed": "24",
                "wifi_speed": "100",
                "nfc_speed": "0.424"
            },
            "Devices": {
                "phone_name": "SmartPhone Pro",
                "pc_name": "Desktop Computer",
                "phone_storage": "128",
                "pc_storage": "1000"
            },
            "UI": {
                "theme": "default",
                "window_width": "1200",
                "window_height": "800",
                "auto_refresh": "true",
                "refresh_interval": "1000"
            },
            "Logging": {
                "log_to_file": "true",
                "log_file_path": "logs/sync_emulator.log",
                "max_log_size": "10",
                "log_retention": "30",
                "log_format": "%(asctime)s - %(levelname)s - %(message)s"
            }
        }
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                self.config.read(self.config_file)
                self._validate_config()
            else:
                # Create default configuration
                self._create_default_config()
                
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        try:
            # Set default values
            for section, options in self.default_config.items():
                if not self.config.has_section(section):
                    self.config.add_section(section)
                
                for option, value in options.items():
                    self.config.set(section, option, str(value))
            
            # Save default configuration
            self.save_config()
            
        except Exception as e:
            print(f"Error creating default configuration: {e}")
    
    def _validate_config(self):
        """Validate loaded configuration"""
        try:
            # Check if all required sections exist
            for section in self.default_config.keys():
                if not self.config.has_section(section):
                    print(f"Missing configuration section: {section}")
                    self.config.add_section(section)
            
            # Check if all required options exist
            for section, options in self.default_config.items():
                if not self.config.has_section(section):
                    continue
                
                for option, default_value in options.items():
                    if not self.config.has_option(section, option):
                        print(f"Missing configuration option: {section}.{option}")
                        self.config.set(section, option, str(default_value))
            
            # Validate specific values
            self._validate_sync_config()
            self._validate_protocol_config()
            self._validate_ui_config()
            
        except Exception as e:
            print(f"Error validating configuration: {e}")
    
    def _validate_sync_config(self):
        """Validate synchronization configuration"""
        try:
            # Validate sync interval
            interval = self.get_int("Sync", "auto_sync_interval")
            if interval < 15:
                self.config.set("Sync", "auto_sync_interval", "15")
            
            # Validate max file size
            max_size = self.get_int("Sync", "max_file_size")
            if max_size <= 0:
                self.config.set("Sync", "max_file_size", "100")
            
            # Validate retry attempts
            retries = self.get_int("Sync", "retry_attempts")
            if retries < 1:
                self.config.set("Sync", "retry_attempts", "3")
                
        except Exception as e:
            print(f"Error validating sync configuration: {e}")
    
    def _validate_protocol_config(self):
        """Validate protocol configuration"""
        try:
            # Validate protocol speeds
            protocols = ["usb_speed", "bluetooth_speed", "wifi_speed", "nfc_speed"]
            for protocol in protocols:
                speed = self.get_float("Protocols", protocol)
                if speed < 0:
                    self.config.set("Protocols", protocol, "0")
                    
        except Exception as e:
            print(f"Error validating protocol configuration: {e}")
    
    def _validate_ui_config(self):
        """Validate UI configuration"""
        try:
            # Validate window dimensions
            width = self.get_int("UI", "window_width")
            height = self.get_int("UI", "window_height")
            
            if width < 800:
                self.config.set("UI", "window_width", "800")
            if height < 600:
                self.config.set("UI", "window_height", "600")
                
        except Exception as e:
            print(f"Error validating UI configuration: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            # Ensure directory exists
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
                
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def get(self, section: str, option: str, fallback: str = None) -> str:
        """Get a configuration value"""
        try:
            return self.config.get(section, option, fallback=fallback)
        except Exception as e:
            print(f"Error getting configuration value {section}.{option}: {e}")
            return fallback or ""
    
    def get_int(self, section: str, option: str, fallback: int = 0) -> int:
        """Get a configuration value as integer"""
        try:
            return self.config.getint(section, option, fallback=fallback)
        except Exception as e:
            print(f"Error getting configuration value {section}.{option}: {e}")
            return fallback
    
    def get_float(self, section: str, option: str, fallback: float = 0.0) -> float:
        """Get a configuration value as float"""
        try:
            return self.config.getfloat(section, option, fallback=fallback)
        except Exception as e:
            print(f"Error getting configuration value {section}.{option}: {e}")
            return fallback
    
    def get_boolean(self, section: str, option: str, fallback: bool = False) -> bool:
        """Get a configuration value as boolean"""
        try:
            return self.config.getboolean(section, option, fallback=fallback)
        except Exception as e:
            print(f"Error getting configuration value {section}.{option}: {e}")
            return fallback
    
    def set(self, section: str, option: str, value: str):
        """Set a configuration value"""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            self.config.set(section, option, str(value))
            
        except Exception as e:
            print(f"Error setting configuration value {section}.{option}: {e}")
    
    def set_int(self, section: str, option: str, value: int):
        """Set a configuration value as integer"""
        self.set(section, option, str(value))
    
    def set_float(self, section: str, option: str, value: float):
        """Set a configuration value as float"""
        self.set(section, option, str(value))
    
    def set_boolean(self, section: str, option: str, value: bool):
        """Set a configuration value as boolean"""
        self.set(section, option, str(value))
    
    def has_option(self, section: str, option: str) -> bool:
        """Check if a configuration option exists"""
        return self.config.has_option(section, option)
    
    def has_section(self, section: str) -> bool:
        """Check if a configuration section exists"""
        return self.config.has_section(section)
    
    def get_section(self, section: str) -> Dict[str, str]:
        """Get all options in a section"""
        try:
            if self.config.has_section(section):
                return dict(self.config.items(section))
            return {}
        except Exception as e:
            print(f"Error getting section {section}: {e}")
            return {}
    
    def get_all(self) -> Dict[str, Dict[str, str]]:
        """Get all configuration values"""
        try:
            result = {}
            for section in self.config.sections():
                result[section] = dict(self.config.items(section))
            return result
        except Exception as e:
            print(f"Error getting all configuration: {e}")
            return {}
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        try:
            self.config.clear()
            self._create_default_config()
            print("Configuration reset to defaults")
            
        except Exception as e:
            print(f"Error resetting configuration: {e}")
    
    def export_config(self, file_path: str):
        """Export configuration to a file"""
        try:
            with open(file_path, 'w') as f:
                self.config.write(f)
            print(f"Configuration exported to {file_path}")
            
        except Exception as e:
            print(f"Error exporting configuration: {e}")
    
    def import_config(self, file_path: str):
        """Import configuration from a file"""
        try:
            if os.path.exists(file_path):
                new_config = configparser.ConfigParser()
                new_config.read(file_path)
                
                # Validate imported configuration
                for section in new_config.sections():
                    if not self.config.has_section(section):
                        self.config.add_section(section)
                    
                    for option, value in new_config.items(section):
                        self.config.set(section, option, value)
                
                self._validate_config()
                self.save_config()
                print(f"Configuration imported from {file_path}")
            else:
                print(f"Configuration file not found: {file_path}")
                
        except Exception as e:
            print(f"Error importing configuration: {e}")
    
    def get_sync_config(self) -> Dict[str, Any]:
        """Get synchronization configuration"""
        return {
            "default_sync_type": self.get("Sync", "default_sync_type"),
            "auto_sync_interval": self.get_int("Sync", "auto_sync_interval"),
            "max_file_size": self.get_int("Sync", "max_file_size"),
            "conflict_resolution": self.get("Sync", "conflict_resolution"),
            "retry_attempts": self.get_int("Sync", "retry_attempts"),
            "retry_delay": self.get_int("Sync", "retry_delay")
        }
    
    def get_protocol_config(self) -> Dict[str, Any]:
        """Get protocol configuration"""
        return {
            "preferred_protocol": self.get("Protocols", "preferred_protocol"),
            "usb_speed": self.get_float("Protocols", "usb_speed"),
            "bluetooth_speed": self.get_float("Protocols", "bluetooth_speed"),
            "wifi_speed": self.get_float("Protocols", "wifi_speed"),
            "nfc_speed": self.get_float("Protocols", "nfc_speed")
        }
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration"""
        return {
            "theme": self.get("UI", "theme"),
            "window_width": self.get_int("UI", "window_width"),
            "window_height": self.get_int("UI", "window_height"),
            "auto_refresh": self.get_boolean("UI", "auto_refresh"),
            "refresh_interval": self.get_int("UI", "refresh_interval")
        }