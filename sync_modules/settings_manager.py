"""
Settings Manager Module
Handles application configuration and settings management.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class SettingsManager:
    """Manages application settings and configuration"""
    
    def __init__(self, config_file: str = "sync_config.json"):
        self.config_file = config_file
        self.settings = self._load_default_settings()
        self.load_settings()
        
    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default application settings"""
        return {
            'sync': {
                'auto_sync_interval': 30,  # minutes
                'conflict_resolution': 'newest_wins',
                'enable_notifications': True,
                'sync_on_startup': False,
                'max_sync_retries': 3,
                'sync_timeout': 300  # seconds
            },
            'connection': {
                'connection_type': 'USB',
                'device_name': 'MyPhone',
                'sync_folder': './sync_folder',
                'auto_connect': True,
                'connection_timeout': 60
            },
            'file_sync': {
                'include_hidden_files': False,
                'max_file_size': 1073741824,  # 1GB
                'supported_extensions': ['.txt', '.doc', '.docx', '.pdf', '.jpg', '.png', '.mp3', '.mp4'],
                'exclude_patterns': ['*.tmp', '*.log', 'Thumbs.db'],
                'preserve_timestamps': True
            },
            'contact_sync': {
                'merge_duplicates': True,
                'sync_frequency': 'realtime',
                'include_photos': True,
                'max_contacts': 10000
            },
            'calendar_sync': {
                'sync_frequency': 'hourly',
                'include_recurring_events': True,
                'sync_reminders': True,
                'max_events': 5000
            },
            'media_sync': {
                'sync_photos': True,
                'sync_music': True,
                'sync_videos': True,
                'compress_photos': False,
                'max_media_size': 5368709120,  # 5GB
                'preserve_quality': True
            },
            'ui': {
                'theme': 'dark',
                'language': 'en',
                'show_system_tray': True,
                'minimize_to_tray': True,
                'start_minimized': False
            },
            'logging': {
                'log_level': 'INFO',
                'log_to_file': True,
                'log_file_path': './logs/sync.log',
                'max_log_size': 10485760,  # 10MB
                'log_retention_days': 30
            },
            'security': {
                'encrypt_sync_data': False,
                'require_authentication': False,
                'session_timeout': 3600,  # 1 hour
                'allowed_ips': []
            }
        }
        
    def load_settings(self):
        """Load settings from configuration file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    self._merge_settings(loaded_settings)
                    print(f"Settings loaded from {self.config_file}")
            else:
                print(f"Configuration file not found. Using default settings.")
                
        except Exception as e:
            print(f"Error loading settings: {e}. Using default settings.")
            
    def save_settings(self):
        """Save current settings to configuration file"""
        try:
            # Create directory if it doesn't exist
            config_dir = os.path.dirname(self.config_file)
            if config_dir:
                Path(config_dir).mkdir(parents=True, exist_ok=True)
                
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2, default=str)
                
            print(f"Settings saved to {self.config_file}")
            return True
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
            
    def _merge_settings(self, new_settings: Dict[str, Any]):
        """Merge new settings with existing settings"""
        def merge_dict(target: Dict[str, Any], source: Dict[str, Any]):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    merge_dict(target[key], value)
                else:
                    target[key] = value
                    
        merge_dict(self.settings, new_settings)
        
    def get_setting(self, key_path: str, default: Any = None) -> Any:
        """Get a setting value by key path (e.g., 'sync.auto_sync_interval')"""
        try:
            keys = key_path.split('.')
            value = self.settings
            
            for key in keys:
                value = value[key]
                
            return value
            
        except (KeyError, TypeError):
            return default
            
    def set_setting(self, key_path: str, value: Any):
        """Set a setting value by key path"""
        try:
            keys = key_path.split('.')
            target = self.settings
            
            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in target:
                    target[key] = {}
                target = target[key]
                
            # Set the value
            target[keys[-1]] = value
            
        except Exception as e:
            print(f"Error setting setting {key_path}: {e}")
            
    def get_sync_settings(self) -> Dict[str, Any]:
        """Get all sync-related settings"""
        return self.settings.get('sync', {})
        
    def get_connection_settings(self) -> Dict[str, Any]:
        """Get all connection-related settings"""
        return self.settings.get('connection', {})
        
    def get_file_sync_settings(self) -> Dict[str, Any]:
        """Get all file sync-related settings"""
        return self.settings.get('file_sync', {})
        
    def get_contact_sync_settings(self) -> Dict[str, Any]:
        """Get all contact sync-related settings"""
        return self.settings.get('contact_sync', {})
        
    def get_calendar_sync_settings(self) -> Dict[str, Any]:
        """Get all calendar sync-related settings"""
        return self.settings.get('calendar_sync', {})
        
    def get_media_sync_settings(self) -> Dict[str, Any]:
        """Get all media sync-related settings"""
        return self.settings.get('media_sync', {})
        
    def get_ui_settings(self) -> Dict[str, Any]:
        """Get all UI-related settings"""
        return self.settings.get('ui', {})
        
    def get_logging_settings(self) -> Dict[str, Any]:
        """Get all logging-related settings"""
        return self.settings.get('logging', {})
        
    def get_security_settings(self) -> Dict[str, Any]:
        """Get all security-related settings"""
        return self.settings.get('security', {})
        
    def update_sync_settings(self, new_settings: Dict[str, Any]):
        """Update sync settings"""
        self.settings['sync'].update(new_settings)
        
    def update_connection_settings(self, new_settings: Dict[str, Any]):
        """Update connection settings"""
        self.settings['connection'].update(new_settings)
        
    def update_file_sync_settings(self, new_settings: Dict[str, Any]):
        """Update file sync settings"""
        self.settings['file_sync'].update(new_settings)
        
    def update_contact_sync_settings(self, new_settings: Dict[str, Any]):
        """Update contact sync settings"""
        self.settings['contact_sync'].update(new_settings)
        
    def update_calendar_sync_settings(self, new_settings: Dict[str, Any]):
        """Update calendar sync settings"""
        self.settings['calendar_sync'].update(new_settings)
        
    def update_media_sync_settings(self, new_settings: Dict[str, Any]):
        """Update media sync settings"""
        self.settings['media_sync'].update(new_settings)
        
    def update_ui_settings(self, new_settings: Dict[str, Any]):
        """Update UI settings"""
        self.settings['ui'].update(new_settings)
        
    def update_logging_settings(self, new_settings: Dict[str, Any]):
        """Update logging settings"""
        self.settings['logging'].update(new_settings)
        
    def update_security_settings(self, new_settings: Dict[str, Any]):
        """Update security settings"""
        self.settings['security'].update(new_settings)
        
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        self.settings = self._load_default_settings()
        print("Settings reset to defaults")
        
    def export_settings(self, file_path: str) -> bool:
        """Export settings to a file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.settings, f, indent=2, default=str)
                
            print(f"Settings exported to {file_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
            
    def import_settings(self, file_path: str) -> bool:
        """Import settings from a file"""
        try:
            with open(file_path, 'r') as f:
                imported_settings = json.load(f)
                
            self._merge_settings(imported_settings)
            print(f"Settings imported from {file_path}")
            return True
            
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False
            
    def validate_settings(self) -> Dict[str, Any]:
        """Validate current settings and return validation results"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validate sync settings
        sync_interval = self.get_setting('sync.auto_sync_interval')
        if sync_interval < 1 or sync_interval > 1440:
            validation_results['errors'].append("Auto-sync interval must be between 1 and 1440 minutes")
            validation_results['valid'] = False
            
        # Validate file sync settings
        max_file_size = self.get_setting('file_sync.max_file_size')
        if max_file_size <= 0:
            validation_results['errors'].append("Max file size must be positive")
            validation_results['valid'] = False
            
        # Validate connection settings
        sync_folder = self.get_setting('connection.sync_folder')
        if not sync_folder:
            validation_results['errors'].append("Sync folder path cannot be empty")
            validation_results['valid'] = False
            
        # Validate logging settings
        log_retention = self.get_setting('logging.log_retention_days')
        if log_retention < 1:
            validation_results['warnings'].append("Log retention days should be at least 1")
            
        return validation_results
        
    def get_settings_summary(self) -> Dict[str, Any]:
        """Get a summary of current settings"""
        return {
            'auto_sync_interval': self.get_setting('sync.auto_sync_interval'),
            'connection_type': self.get_setting('connection.connection_type'),
            'device_name': self.get_setting('connection.device_name'),
            'sync_folder': self.get_setting('connection.sync_folder'),
            'theme': self.get_setting('ui.theme'),
            'log_level': self.get_setting('logging.log_level'),
            'encrypt_data': self.get_setting('security.encrypt_sync_data')
        }