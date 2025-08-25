"""
Logger Utility
Handles comprehensive logging of sync operations and system events.
"""

import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
from pathlib import Path

class SyncLogger:
    def __init__(self, log_dir: str = "logs", max_log_size: int = 10 * 1024 * 1024, backup_count: int = 5):
        self.log_dir = Path(log_dir)
        self.max_log_size = max_log_size
        self.backup_count = backup_count
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize loggers
        self._setup_loggers()
        
        # Log rotation
        self._setup_log_rotation()
        
    def _setup_loggers(self):
        """Setup different loggers for different purposes"""
        # Main sync logger
        self.sync_logger = self._create_logger(
            'sync',
            self.log_dir / 'sync.log',
            logging.INFO
        )
        
        # Error logger
        self.error_logger = self._create_logger(
            'error',
            self.log_dir / 'errors.log',
            logging.ERROR
        )
        
        # Device logger
        self.device_logger = self._create_logger(
            'device',
            self.log_dir / 'device.log',
            logging.INFO
        )
        
        # Performance logger
        self.performance_logger = self._create_logger(
            'performance',
            self.log_dir / 'performance.log',
            logging.INFO
        )
        
        # Debug logger
        self.debug_logger = self._create_logger(
            'debug',
            self.log_dir / 'debug.log',
            logging.DEBUG
        )
        
    def _create_logger(self, name: str, log_file: Path, level: int) -> logging.Logger:
        """Create a logger with file and console handlers"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_log_size,
            backupCount=self.backup_count
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        return logger
        
    def _setup_log_rotation(self):
        """Setup automatic log rotation"""
        # This will be handled by RotatingFileHandler
        pass
        
    def log_sync_start(self, operation_type: str, device_id: str = None, metadata: Dict = None):
        """Log the start of a synchronization operation"""
        message = f"Sync started - Type: {operation_type}"
        if device_id:
            message += f", Device: {device_id}"
        if metadata:
            message += f", Metadata: {json.dumps(metadata)}"
            
        self.sync_logger.info(message)
        
    def log_sync_progress(self, operation_type: str, progress: int, current_item: str = None, device_id: str = None):
        """Log synchronization progress"""
        message = f"Sync progress - Type: {operation_type}, Progress: {progress}%"
        if device_id:
            message += f", Device: {device_id}"
        if current_item:
            message += f", Current: {current_item}"
            
        self.sync_logger.info(message)
        
    def log_sync_complete(self, operation_type: str, success: bool, duration: float, 
                         items_processed: int = 0, device_id: str = None, errors: List[str] = None):
        """Log synchronization completion"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Sync {status} - Type: {operation_type}, Duration: {duration:.2f}s, Items: {items_processed}"
        if device_id:
            message += f", Device: {device_id}"
        if errors:
            message += f", Errors: {errors}"
            
        if success:
            self.sync_logger.info(message)
        else:
            self.sync_logger.error(message)
            # Also log to error logger
            self.error_logger.error(message)
            
    def log_device_connected(self, device_id: str, device_name: str, connection_type: str):
        """Log device connection"""
        message = f"Device connected - ID: {device_id}, Name: {device_name}, Type: {connection_type}"
        self.device_logger.info(message)
        
    def log_device_disconnected(self, device_id: str, device_name: str, duration: float):
        """Log device disconnection"""
        message = f"Device disconnected - ID: {device_id}, Name: {device_name}, Duration: {duration:.2f}s"
        self.device_logger.info(message)
        
    def log_device_error(self, device_id: str, error: str, context: str = None):
        """Log device-related errors"""
        message = f"Device error - ID: {device_id}, Error: {error}"
        if context:
            message += f", Context: {context}"
            
        self.device_logger.error(message)
        self.error_logger.error(message)
        
    def log_performance(self, operation: str, duration: float, items_processed: int = 0, 
                       throughput: float = 0.0, metadata: Dict = None):
        """Log performance metrics"""
        message = f"Performance - Operation: {operation}, Duration: {duration:.2f}s, Items: {items_processed}"
        if throughput > 0:
            message += f", Throughput: {throughput:.2f} items/s"
        if metadata:
            message += f", Metadata: {json.dumps(metadata)}"
            
        self.performance_logger.info(message)
        
    def log_error(self, error: str, context: str = None, stack_trace: str = None):
        """Log general errors"""
        message = f"Error: {error}"
        if context:
            message += f", Context: {context}"
        if stack_trace:
            message += f", Stack: {stack_trace}"
            
        self.error_logger.error(message)
        
    def log_warning(self, warning: str, context: str = None):
        """Log warnings"""
        message = f"Warning: {warning}"
        if context:
            message += f", Context: {context}"
            
        self.sync_logger.warning(message)
        
    def log_info(self, message: str, context: str = None):
        """Log general information"""
        if context:
            message = f"{context}: {message}"
        self.sync_logger.info(message)
        
    def log_debug(self, message: str, context: str = None):
        """Log debug information"""
        if context:
            message = f"{context}: {message}"
        self.debug_logger.debug(message)
        
    def log_file_operation(self, operation: str, file_path: str, size: int = 0, 
                          status: str = "unknown", device_id: str = None):
        """Log file operations"""
        message = f"File {operation} - Path: {file_path}, Size: {size} bytes, Status: {status}"
        if device_id:
            message += f", Device: {device_id}"
            
        self.sync_logger.info(message)
        
    def log_contact_operation(self, operation: str, contact_id: str, contact_name: str, 
                             status: str = "unknown", device_id: str = None):
        """Log contact operations"""
        message = f"Contact {operation} - ID: {contact_id}, Name: {contact_name}, Status: {status}"
        if device_id:
            message += f", Device: {device_id}"
            
        self.sync_logger.info(message)
        
    def log_calendar_operation(self, operation: str, event_id: str, event_title: str, 
                              status: str = "unknown", device_id: str = None):
        """Log calendar operations"""
        message = f"Calendar {operation} - ID: {event_id}, Title: {event_title}, Status: {status}"
        if device_id:
            message += f", Device: {device_id}"
            
        self.sync_logger.info(message)
        
    def log_config_change(self, key: str, old_value: str, new_value: str, user: str = None):
        """Log configuration changes"""
        message = f"Config changed - Key: {key}, Old: {old_value}, New: {new_value}"
        if user:
            message += f", User: {user}"
            
        self.sync_logger.info(message)
        
    def log_security_event(self, event_type: str, details: str, user: str = None, ip_address: str = None):
        """Log security-related events"""
        message = f"Security event - Type: {event_type}, Details: {details}"
        if user:
            message += f", User: {user}"
        if ip_address:
            message += f", IP: {ip_address}"
            
        self.sync_logger.warning(message)
        self.error_logger.warning(message)
        
    def log_system_event(self, event_type: str, details: str, severity: str = "info"):
        """Log system events"""
        message = f"System event - Type: {event_type}, Details: {details}"
        
        if severity.lower() == "error":
            self.error_logger.error(message)
        elif severity.lower() == "warning":
            self.sync_logger.warning(message)
        else:
            self.sync_logger.info(message)
            
    def get_log_summary(self, hours: int = 24) -> Dict:
        """Get summary of recent log entries"""
        try:
            summary = {
                'total_entries': 0,
                'errors': 0,
                'warnings': 0,
                'info': 0,
                'debug': 0,
                'sync_operations': 0,
                'device_events': 0,
                'file_operations': 0,
                'contact_operations': 0,
                'calendar_operations': 0
            }
            
            # Count entries in log files
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            for log_file in self.log_dir.glob("*.log"):
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            # Parse timestamp from log line
                            try:
                                timestamp_str = line.split(' - ')[0]
                                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                
                                if timestamp >= cutoff_time:
                                    summary['total_entries'] += 1
                                    
                                    # Count by level
                                    if 'ERROR' in line:
                                        summary['errors'] += 1
                                    elif 'WARNING' in line:
                                        summary['warnings'] += 1
                                    elif 'INFO' in line:
                                        summary['info'] += 1
                                    elif 'DEBUG' in line:
                                        summary['debug'] += 1
                                        
                                    # Count by operation type
                                    if 'Sync' in line:
                                        summary['sync_operations'] += 1
                                    if 'Device' in line:
                                        summary['device_events'] += 1
                                    if 'File' in line:
                                        summary['file_operations'] += 1
                                    if 'Contact' in line:
                                        summary['contact_operations'] += 1
                                    if 'Calendar' in line:
                                        summary['calendar_operations'] += 1
                                        
                            except (ValueError, IndexError):
                                continue
                                
                except Exception as e:
                    print(f"Error reading log file {log_file}: {e}")
                    
            return summary
            
        except Exception as e:
            print(f"Error getting log summary: {e}")
            return {}
            
    def search_logs(self, query: str, log_files: List[str] = None, hours: int = 24) -> List[str]:
        """Search logs for specific text"""
        try:
            results = []
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Default to all log files if none specified
            if not log_files:
                log_files = [f.name for f in self.log_dir.glob("*.log")]
                
            for log_file_name in log_files:
                log_file = self.log_dir / log_file_name
                if not log_file.exists():
                    continue
                    
                try:
                    with open(log_file, 'r') as f:
                        for line_num, line in enumerate(f, 1):
                            if query.lower() in line.lower():
                                # Parse timestamp
                                try:
                                    timestamp_str = line.split(' - ')[0]
                                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                    
                                    if timestamp >= cutoff_time:
                                        results.append(f"{log_file_name}:{line_num}: {line.strip()}")
                                        
                                except (ValueError, IndexError):
                                    # If timestamp parsing fails, include the line anyway
                                    results.append(f"{log_file_name}:{line_num}: {line.strip()}")
                                    
                except Exception as e:
                    print(f"Error searching log file {log_file}: {e}")
                    
            return results
            
        except Exception as e:
            print(f"Error searching logs: {e}")
            return []
            
    def export_logs(self, output_file: str, log_files: List[str] = None, hours: int = 24, 
                   include_metadata: bool = True) -> bool:
        """Export logs to a file"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Default to all log files if none specified
            if not log_files:
                log_files = [f.name for f in self.log_dir.glob("*.log")]
                
            with open(output_file, 'w') as output:
                if include_metadata:
                    output.write(f"Log Export - Generated: {datetime.now().isoformat()}\n")
                    output.write(f"Time Range: Last {hours} hours\n")
                    output.write(f"Log Files: {', '.join(log_files)}\n")
                    output.write("-" * 80 + "\n\n")
                    
                for log_file_name in log_files:
                    log_file = self.log_dir / log_file_name
                    if not log_file.exists():
                        continue
                        
                    output.write(f"=== {log_file_name} ===\n")
                    
                    try:
                        with open(log_file, 'r') as f:
                            for line in f:
                                try:
                                    timestamp_str = line.split(' - ')[0]
                                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                    
                                    if timestamp >= cutoff_time:
                                        output.write(line)
                                        
                                except (ValueError, IndexError):
                                    # If timestamp parsing fails, include the line anyway
                                    output.write(line)
                                    
                    except Exception as e:
                        output.write(f"Error reading log file: {e}\n")
                        
                    output.write("\n")
                    
            return True
            
        except Exception as e:
            print(f"Error exporting logs: {e}")
            return False
            
    def clear_old_logs(self, days_to_keep: int = 30) -> bool:
        """Clear old log files"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)
            files_removed = 0
            
            for log_file in self.log_dir.glob("*.log.*"):  # Backup files
                try:
                    if log_file.stat().st_mtime < cutoff_time.timestamp():
                        log_file.unlink()
                        files_removed += 1
                except Exception as e:
                    print(f"Error removing old log file {log_file}: {e}")
                    
            self.log_info(f"Cleared {files_removed} old log files")
            return True
            
        except Exception as e:
            print(f"Error clearing old logs: {e}")
            return False
            
    def get_log_file_info(self) -> Dict:
        """Get information about log files"""
        try:
            info = {
                'total_files': 0,
                'total_size': 0,
                'files': []
            }
            
            for log_file in self.log_dir.glob("*.log*"):
                try:
                    stat = log_file.stat()
                    file_info = {
                        'name': log_file.name,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'is_backup': log_file.suffix != '.log'
                    }
                    
                    info['files'].append(file_info)
                    info['total_files'] += 1
                    info['total_size'] += stat.st_size
                    
                except Exception as e:
                    print(f"Error getting info for log file {log_file}: {e}")
                    
            return info
            
        except Exception as e:
            print(f"Error getting log file info: {e}")
            return {}

# Create a global logger instance
logger = SyncLogger()

# Convenience functions for easy access
def log_sync_start(operation_type: str, device_id: str = None, metadata: Dict = None):
    logger.log_sync_start(operation_type, device_id, metadata)
    
def log_sync_progress(operation_type: str, progress: int, current_item: str = None, device_id: str = None):
    logger.log_sync_progress(operation_type, progress, current_item, device_id)
    
def log_sync_complete(operation_type: str, success: bool, duration: float, 
                     items_processed: int = 0, device_id: str = None, errors: List[str] = None):
    logger.log_sync_complete(operation_type, success, duration, items_processed, device_id, errors)
    
def log_error(error: str, context: str = None, stack_trace: str = None):
    logger.log_error(error, context, stack_trace)
    
def log_warning(warning: str, context: str = None):
    logger.log_warning(warning, context)
    
def log_info(message: str, context: str = None):
    logger.log_info(message, context)
    
def log_debug(message: str, context: str = None):
    logger.log_debug(message, context)