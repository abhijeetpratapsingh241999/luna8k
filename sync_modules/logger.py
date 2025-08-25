"""
Logger Module
Handles application logging and debugging functionality.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json

class SyncLogger:
    """Centralized logging system for the sync emulator"""
    
    def __init__(self, log_file: str = "./logs/sync.log", log_level: str = "INFO"):
        self.log_file = log_file
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Create logs directory
        log_dir = os.path.dirname(log_file)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
        # Setup logging
        self._setup_logging()
        
        # Log startup
        self.info("Sync Logger initialized", extra={'module_name': 'logger'})
        
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module_name)s - %(message)s'
        )
        
        # Setup file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        
        # Setup console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        
        # Setup root logger
        self.logger = logging.getLogger('SyncEmulator')
        self.logger.setLevel(self.log_level)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Prevent duplicate log messages
        self.logger.propagate = False
        
    def _log(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """Internal logging method"""
        if extra is None:
            extra = {}
            
        # Add timestamp if not present
        if 'timestamp' not in extra:
            extra['timestamp'] = datetime.now().isoformat()
            
        # Log with extra context
        log_method = getattr(self.logger, level.lower())
        log_method(message, extra=extra)
        
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self._log('DEBUG', message, extra)
        
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self._log('INFO', message, extra)
        
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self._log('WARNING', message, extra)
        
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message"""
        self._log('ERROR', message, extra)
        
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        self._log('CRITICAL', message, extra)
        
    def log_sync_activity(self, module: str, action: str, details: str = "", status: str = "success"):
        """Log synchronization activity"""
        extra = {
            'module_name': module,
            'action': action,
            'details': details,
            'status': status,
            'log_type': 'sync_activity'
        }
        
        if status == "success":
            self.info(f"Sync activity: {action} - {details}", extra=extra)
        elif status == "warning":
            self.warning(f"Sync activity: {action} - {details}", extra=extra)
        elif status == "error":
            self.error(f"Sync activity: {action} - {details}", extra=extra)
        else:
            self.info(f"Sync activity: {action} - {details}", extra=extra)
            
    def log_file_operation(self, operation: str, file_path: str, status: str = "success", details: str = ""):
        """Log file operations"""
        extra = {
            'operation': operation,
            'file_path': file_path,
            'status': status,
            'details': details,
            'log_type': 'file_operation'
        }
        
        if status == "success":
            self.info(f"File operation: {operation} - {file_path}", extra=extra)
        elif status == "warning":
            self.warning(f"File operation: {operation} - {file_path}", extra=extra)
        elif status == "error":
            self.error(f"File operation: {operation} - {file_path}", extra=extra)
        else:
            self.info(f"File operation: {operation} - {file_path}", extra=extra)
            
    def log_contact_sync(self, action: str, contact_name: str, status: str = "success", details: str = ""):
        """Log contact synchronization activities"""
        extra = {
            'action': action,
            'contact_name': contact_name,
            'status': status,
            'details': details,
            'log_type': 'contact_sync'
        }
        
        if status == "success":
            self.info(f"Contact sync: {action} - {contact_name}", extra=extra)
        elif status == "warning":
            self.warning(f"Contact sync: {action} - {contact_name}", extra=extra)
        elif status == "error":
            self.error(f"Contact sync: {action} - {contact_name}", extra=extra)
        else:
            self.info(f"Contact sync: {action} - {contact_name}", extra=extra)
            
    def log_calendar_sync(self, action: str, event_title: str, status: str = "success", details: str = ""):
        """Log calendar synchronization activities"""
        extra = {
            'action': action,
            'event_title': event_title,
            'status': status,
            'details': details,
            'log_type': 'calendar_sync'
        }
        
        if status == "success":
            self.info(f"Calendar sync: {action} - {event_title}", extra=extra)
        elif status == "warning":
            self.warning(f"Calendar sync: {action} - {event_title}", extra=extra)
        elif status == "error":
            self.error(f"Calendar sync: {action} - {event_title}", extra=extra)
        else:
            self.info(f"Calendar sync: {action} - {event_title}", extra=extra)
            
    def log_media_sync(self, action: str, media_file: str, status: str = "success", details: str = ""):
        """Log media synchronization activities"""
        extra = {
            'action': action,
            'media_file': media_file,
            'status': status,
            'details': details,
            'log_type': 'media_sync'
        }
        
        if status == "success":
            self.info(f"Media sync: {action} - {media_file}", extra=extra)
        elif status == "warning":
            self.warning(f"Media sync: {action} - {media_file}", extra=extra)
        elif status == "error":
            self.error(f"Media sync: {action} - {media_file}", extra=extra)
        else:
            self.info(f"Media sync: {action} - {media_file}", extra=extra)
            
    def log_connection(self, action: str, connection_type: str, status: str = "success", details: str = ""):
        """Log connection activities"""
        extra = {
            'action': action,
            'connection_type': connection_type,
            'status': status,
            'details': details,
            'log_type': 'connection'
        }
        
        if status == "success":
            self.info(f"Connection: {action} - {connection_type}", extra=extra)
        elif status == "warning":
            self.warning(f"Connection: {action} - {connection_type}", extra=extra)
        elif status == "error":
            self.error(f"Connection: {action} - {connection_type}", extra=extra)
        else:
            self.info(f"Connection: {action} - {connection_type}", extra=extra)
            
    def log_settings_change(self, setting_path: str, old_value: Any, new_value: Any):
        """Log settings changes"""
        extra = {
            'setting_path': setting_path,
            'old_value': str(old_value),
            'new_value': str(new_value),
            'log_type': 'settings_change'
        }
        
        self.info(f"Setting changed: {setting_path} = {new_value}", extra=extra)
        
    def log_performance(self, operation: str, duration: float, details: str = ""):
        """Log performance metrics"""
        extra = {
            'operation': operation,
            'duration': duration,
            'details': details,
            'log_type': 'performance'
        }
        
        if duration < 1.0:
            self.debug(f"Performance: {operation} completed in {duration:.3f}s", extra=extra)
        elif duration < 5.0:
            self.info(f"Performance: {operation} completed in {duration:.3f}s", extra=extra)
        else:
            self.warning(f"Performance: {operation} took {duration:.3f}s", extra=extra)
            
    def log_error_with_context(self, error: Exception, context: str = "", extra: Optional[Dict[str, Any]] = None):
        """Log error with additional context"""
        if extra is None:
            extra = {}
            
        extra.update({
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'log_type': 'error_with_context'
        })
        
        self.error(f"Error in {context}: {str(error)}", extra=extra)
        
    def get_log_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get a summary of recent log entries"""
        try:
            if not os.path.exists(self.log_file):
                return {"error": "Log file not found"}
                
            # Read log file and analyze recent entries
            summary = {
                'total_entries': 0,
                'by_level': {},
                'by_module': {},
                'by_type': {},
                'recent_errors': [],
                'recent_warnings': []
            }
            
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            
            with open(self.log_file, 'r') as f:
                for line in f:
                    summary['total_entries'] += 1
                    
                    # Parse log line (simplified)
                    if ' - ERROR - ' in line:
                        summary['by_level']['ERROR'] = summary['by_level'].get('ERROR', 0) + 1
                        if 'timestamp' in line:  # Simplified check
                            summary['recent_errors'].append(line.strip())
                    elif ' - WARNING - ' in line:
                        summary['by_level']['WARNING'] = summary['by_level'].get('WARNING', 0) + 1
                        if 'timestamp' in line:  # Simplified check
                            summary['recent_warnings'].append(line.strip())
                    elif ' - INFO - ' in line:
                        summary['by_level']['INFO'] = summary['by_level'].get('INFO', 0) + 1
                    elif ' - DEBUG - ' in line:
                        summary['by_level']['DEBUG'] = summary['by_level'].get('DEBUG', 0) + 1
                        
            return summary
            
        except Exception as e:
            return {"error": f"Failed to analyze logs: {str(e)}"}
            
    def export_logs(self, output_file: str, hours: int = 24, log_levels: Optional[list] = None):
        """Export logs to a file with filtering options"""
        try:
            if not os.path.exists(self.log_file):
                return False
                
            if log_levels is None:
                log_levels = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
                
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            
            exported_lines = []
            
            with open(self.log_file, 'r') as f:
                for line in f:
                    # Check if line contains any of the specified log levels
                    if any(f" - {level} - " in line for level in log_levels):
                        exported_lines.append(line.strip())
                        
            # Write to output file
            with open(output_file, 'w') as f:
                f.write('\n'.join(exported_lines))
                
            self.info(f"Exported {len(exported_lines)} log entries to {output_file}")
            return True
            
        except Exception as e:
            self.error(f"Failed to export logs: {str(e)}")
            return False
            
    def clear_logs(self):
        """Clear all log files"""
        try:
            # Clear the main log file
            with open(self.log_file, 'w') as f:
                f.write('')
                
            self.info("Logs cleared")
            return True
            
        except Exception as e:
            self.error(f"Failed to clear logs: {str(e)}")
            return False
            
    def rotate_logs(self, max_size_mb: int = 10):
        """Rotate logs when they exceed maximum size"""
        try:
            if not os.path.exists(self.log_file):
                return False
                
            file_size = os.path.getsize(self.log_file)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if file_size > max_size_bytes:
                # Create backup file
                backup_file = f"{self.log_file}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.log_file, backup_file)
                
                # Create new log file
                with open(self.log_file, 'w') as f:
                    f.write('')
                    
                self.info(f"Logs rotated. Old log saved as {backup_file}")
                return True
                
            return False
            
        except Exception as e:
            self.error(f"Failed to rotate logs: {str(e)}")
            return False
            
    def set_log_level(self, level: str):
        """Change the logging level"""
        try:
            new_level = getattr(logging, level.upper(), logging.INFO)
            self.log_level = new_level
            
            # Update logger level
            self.logger.setLevel(new_level)
            
            # Update all handlers
            for handler in self.logger.handlers:
                handler.setLevel(new_level)
                
            self.info(f"Log level changed to {level.upper()}")
            
        except Exception as e:
            self.error(f"Failed to change log level: {str(e)}")
            
    def get_log_file_path(self) -> str:
        """Get the current log file path"""
        return self.log_file
        
    def get_log_level(self) -> str:
        """Get the current log level"""
        return logging.getLevelName(self.log_level)