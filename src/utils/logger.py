"""
Logging Utility
Handles application logging
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict


def setup_logger(name: str = "PhonePCSyncEmulator", 
                log_file: str = "logs/sync_emulator.log",
                level: str = "INFO") -> logging.Logger:
    """Setup and configure the application logger"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create file handler: {e}")
    
    # Add custom log levels if needed
    _add_custom_levels(logger)
    
    return logger


def _add_custom_levels(logger: logging.Logger):
    """Add custom log levels"""
    # You can add custom log levels here if needed
    pass


class LoggerMixin:
    """Mixin class to add logging capabilities to other classes"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def log_info(self, message: str):
        """Log an info message"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log a warning message"""
        self.logger.warning(message)
    
    def log_error(self, message: str):
        """Log an error message"""
        self.logger.error(message)
    
    def log_debug(self, message: str):
        """Log a debug message"""
        self.logger.debug(message)
    
    def log_critical(self, message: str):
        """Log a critical message"""
        self.logger.critical(message)


class LogManager:
    """Manages application logging"""
    
    def __init__(self, config):
        self.config = config
        self.logger = None
        self.log_file = config.get("Logging", "log_file_path", fallback="logs/sync_emulator.log")
        self.log_level = config.get("Logging", "log_level", fallback="INFO")
        self.max_log_size = config.get_int("Logging", "max_log_size", fallback=10)
        self.log_retention = config.get_int("Logging", "log_retention", fallback=30)
        
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging system"""
        try:
            self.logger = setup_logger(
                name="PhonePCSyncEmulator",
                log_file=self.log_file,
                level=self.log_level
            )
            
            self.logger.info("Logging system initialized")
            
        except Exception as e:
            print(f"Error setting up logging: {e}")
            # Fallback to basic logging
            self.logger = logging.getLogger("PhonePCSyncEmulator")
            self.logger.setLevel(logging.INFO)
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """Get a logger instance"""
        if name:
            return logging.getLogger(name)
        return self.logger
    
    def log_sync_event(self, event_type: str, message: str, session_id: str = None, details: Dict = None):
        """Log a synchronization event"""
        try:
            if self.logger:
                log_message = f"[SYNC] {event_type}: {message}"
                if session_id:
                    log_message += f" (Session: {session_id[:8]}...)"
                
                self.logger.info(log_message)
                
                if details:
                    self.logger.debug(f"Event details: {details}")
                    
        except Exception as e:
            print(f"Error logging sync event: {e}")
    
    def log_device_event(self, event_type: str, device_name: str, message: str, details: Dict = None):
        """Log a device event"""
        try:
            if self.logger:
                log_message = f"[DEVICE] {event_type} - {device_name}: {message}"
                self.logger.info(log_message)
                
                if details:
                    self.logger.debug(f"Device event details: {details}")
                    
        except Exception as e:
            print(f"Error logging device event: {e}")
    
    def log_protocol_event(self, protocol: str, event_type: str, message: str, details: Dict = None):
        """Log a protocol event"""
        try:
            if self.logger:
                log_message = f"[PROTOCOL] {protocol} - {event_type}: {message}"
                self.logger.info(log_message)
                
                if details:
                    self.logger.debug(f"Protocol event details: {details}")
                    
        except Exception as e:
            print(f"Error logging protocol event: {e}")
    
    def log_error(self, error_message: str, error_details: Dict = None, session_id: str = None):
        """Log an error"""
        try:
            if self.logger:
                log_message = f"[ERROR] {error_message}"
                if session_id:
                    log_message += f" (Session: {session_id[:8]}...)"
                
                self.logger.error(log_message)
                
                if error_details:
                    self.logger.error(f"Error details: {error_details}")
                    
        except Exception as e:
            print(f"Error logging error: {e}")
    
    def log_performance(self, operation: str, duration: float, details: Dict = None):
        """Log performance metrics"""
        try:
            if self.logger:
                log_message = f"[PERFORMANCE] {operation}: {duration:.3f}s"
                self.logger.info(log_message)
                
                if details:
                    self.logger.debug(f"Performance details: {details}")
                    
        except Exception as e:
            print(f"Error logging performance: {e}")
    
    def rotate_logs(self):
        """Rotate log files"""
        try:
            if not os.path.exists(self.log_file):
                return
            
            # Check if log file size exceeds limit
            file_size = os.path.getsize(self.log_file)
            max_size_bytes = self.max_log_size * 1024 * 1024  # Convert MB to bytes
            
            if file_size > max_size_bytes:
                # Create backup filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{self.log_file}.{timestamp}"
                
                # Rename current log file
                os.rename(self.log_file, backup_file)
                
                # Create new log file
                open(self.log_file, 'a').close()
                
                # Log the rotation
                if self.logger:
                    self.logger.info(f"Log file rotated to {backup_file}")
                
                # Clean up old log files
                self._cleanup_old_logs()
                
        except Exception as e:
            print(f"Error rotating logs: {e}")
    
    def _cleanup_old_logs(self):
        """Clean up old log files based on retention policy"""
        try:
            log_dir = os.path.dirname(self.log_file)
            if not log_dir:
                return
            
            current_time = datetime.now()
            
            for filename in os.listdir(log_dir):
                if filename.startswith(os.path.basename(self.log_file)) and filename != os.path.basename(self.log_file):
                    file_path = os.path.join(log_dir, filename)
                    
                    # Check file age
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    age_days = (current_time - file_time).days
                    
                    if age_days > self.log_retention:
                        try:
                            os.remove(file_path)
                            if self.logger:
                                self.logger.info(f"Removed old log file: {filename}")
                        except Exception as e:
                            print(f"Error removing old log file {filename}: {e}")
                            
        except Exception as e:
            print(f"Error cleaning up old logs: {e}")
    
    def export_logs(self, output_file: str, start_date: str = None, end_date: str = None, level: str = "INFO"):
        """Export logs to a file with optional filtering"""
        try:
            if not os.path.exists(self.log_file):
                print("No log file found to export")
                return False
            
            with open(self.log_file, 'r') as source, open(output_file, 'w') as target:
                for line in source:
                    # Apply filters if specified
                    if self._should_include_line(line, start_date, end_date, level):
                        target.write(line)
            
            print(f"Logs exported to {output_file}")
            return True
            
        except Exception as e:
            print(f"Error exporting logs: {e}")
            return False
    
    def _should_include_line(self, line: str, start_date: str, end_date: str, level: str) -> bool:
        """Check if a log line should be included based on filters"""
        try:
            # Check log level
            if level != "ALL" and level not in line:
                return False
            
            # Check date range if specified
            if start_date or end_date:
                # Extract date from log line (assuming format: YYYY-MM-DD HH:MM:SS)
                if " - " in line:
                    date_part = line.split(" - ")[0]
                    try:
                        log_date = datetime.strptime(date_part, "%Y-%m-%d %H:%M:%S")
                        
                        if start_date:
                            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                            if log_date.date() < start_dt.date():
                                return False
                        
                        if end_date:
                            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                            if log_date.date() > end_dt.date():
                                return False
                                
                    except ValueError:
                        # If date parsing fails, include the line
                        pass
            
            return True
            
        except Exception:
            # If any error occurs, include the line
            return True
    
    def get_log_statistics(self) -> Dict:
        """Get statistics about the logs"""
        try:
            if not os.path.exists(self.log_file):
                return {"error": "Log file not found"}
            
            stats = {
                "file_size": os.path.getsize(self.log_file),
                "file_size_mb": round(os.path.getsize(self.log_file) / (1024 * 1024), 2),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(self.log_file)).isoformat(),
                "line_count": 0,
                "level_counts": {"INFO": 0, "WARNING": 0, "ERROR": 0, "DEBUG": 0, "CRITICAL": 0}
            }
            
            with open(self.log_file, 'r') as f:
                for line in f:
                    stats["line_count"] += 1
                    
                    # Count log levels
                    for level in stats["level_counts"]:
                        if level in line:
                            stats["level_counts"][level] += 1
            
            return stats
            
        except Exception as e:
            return {"error": str(e)}
    
    def clear_logs(self):
        """Clear all log files"""
        try:
            if os.path.exists(self.log_file):
                # Clear the main log file
                open(self.log_file, 'w').close()
            
            # Clear backup log files
            log_dir = os.path.dirname(self.log_file)
            if log_dir:
                for filename in os.listdir(log_dir):
                    if filename.startswith(os.path.basename(self.log_file)) and filename != os.path.basename(self.log_file):
                        try:
                            os.remove(os.path.join(log_dir, filename))
                        except Exception as e:
                            print(f"Error removing backup log file {filename}: {e}")
            
            if self.logger:
                self.logger.info("All log files cleared")
                
        except Exception as e:
            print(f"Error clearing logs: {e}")


# Global logger instance
_global_logger = None


def get_logger(name: str = None) -> logging.Logger:
    """Get the global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = setup_logger()
    
    if name:
        return logging.getLogger(name)
    return _global_logger


def log_info(message: str):
    """Log an info message using the global logger"""
    get_logger().info(message)


def log_warning(message: str):
    """Log a warning message using the global logger"""
    get_logger().warning(message)


def log_error(message: str):
    """Log an error message using the global logger"""
    get_logger().error(message)


def log_debug(message: str):
    """Log a debug message using the global logger"""
    get_logger().debug(message)


def log_critical(message: str):
    """Log a critical message using the global logger"""
    get_logger().critical(message)