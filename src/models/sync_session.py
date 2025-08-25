"""
Synchronization session model
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict
from datetime import datetime
import uuid

from .device import DeviceInfo, FileInfo


class SyncStatus(Enum):
    """Synchronization status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class SyncType(Enum):
    """Synchronization types"""
    FULL = "full"
    INCREMENTAL = "incremental"
    SELECTIVE = "selective"
    CONTACTS_ONLY = "contacts_only"
    CALENDAR_ONLY = "calendar_only"
    FILES_ONLY = "files_only"


@dataclass
class SyncProgress:
    """Synchronization progress information"""
    current_file: str = ""
    total_files: int = 0
    current_file_size: int = 0
    total_size: int = 0
    percentage: float = 0.0
    speed: float = 0.0  # bytes per second
    estimated_time: float = 0.0  # seconds
    files_processed: int = 0
    files_failed: int = 0
    start_time: Optional[datetime] = None
    last_update: Optional[datetime] = None


@dataclass
class SyncStatistics:
    """Synchronization statistics"""
    total_files_synced: int = 0
    total_data_transferred: int = 0  # in bytes
    sync_duration: float = 0.0  # in seconds
    average_speed: float = 0.0  # bytes per second
    peak_speed: float = 0.0  # bytes per second
    errors_encountered: int = 0
    retry_attempts: int = 0


class SyncSession:
    """Synchronization session"""
    
    def __init__(self, sync_type: str, selected_files: List[FileInfo] = None,
                 phone_device: DeviceInfo = None, pc_device: DeviceInfo = None):
        self.id = str(uuid.uuid4())
        self.sync_type = sync_type
        self.selected_files = selected_files or []
        self.phone_device = phone_device
        self.pc_device = pc_device
        
        # Session state
        self.status = SyncStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        
        # Progress tracking
        self.progress = SyncProgress()
        self.statistics = SyncStatistics()
        
        # Control flags
        self.cancelled = False
        self.paused = False
        
        # Error handling
        self.error_message: Optional[str] = None
        self.error_details: Optional[Dict] = None
        
        # Configuration
        self.auto_retry = True
        self.max_retries = 3
        self.retry_count = 0
        
        # Logging
        self.log_entries: List[Dict] = []
    
    def start(self):
        """Start the synchronization session"""
        if self.status != SyncStatus.PENDING:
            raise ValueError("Session cannot be started in current status")
        
        self.status = SyncStatus.IN_PROGRESS
        self.started_at = datetime.now()
        self.progress.start_time = datetime.now()
        self.progress.last_update = datetime.now()
        
        self._log_event("Session started", "INFO")
    
    def complete(self):
        """Mark the session as completed"""
        self.status = SyncStatus.COMPLETED
        self.completed_at = datetime.now()
        
        if self.started_at:
            self.statistics.sync_duration = (self.completed_at - self.started_at).total_seconds()
        
        self._log_event("Session completed successfully", "INFO")
    
    def fail(self, error_message: str, error_details: Dict = None):
        """Mark the session as failed"""
        self.status = SyncStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message
        self.error_details = error_details
        
        if self.started_at:
            self.statistics.sync_duration = (self.completed_at - self.started_at).total_seconds()
        
        self._log_event(f"Session failed: {error_message}", "ERROR")
    
    def cancel(self):
        """Cancel the session"""
        self.cancelled = True
        self.status = SyncStatus.CANCELLED
        self.completed_at = datetime.now()
        
        if self.started_at:
            self.statistics.sync_duration = (self.completed_at - self.started_at).total_seconds()
        
        self._log_event("Session cancelled by user", "WARNING")
    
    def pause(self):
        """Pause the session"""
        if self.status == SyncStatus.IN_PROGRESS:
            self.status = SyncStatus.PAUSED
            self.paused = True
            self._log_event("Session paused", "INFO")
    
    def resume(self):
        """Resume the session"""
        if self.status == SyncStatus.PAUSED:
            self.status = SyncStatus.IN_PROGRESS
            self.paused = False
            self._log_event("Session resumed", "INFO")
    
    def update_progress(self, **kwargs):
        """Update progress information"""
        for key, value in kwargs.items():
            if hasattr(self.progress, key):
                setattr(self.progress, key, value)
        
        self.progress.last_update = datetime.now()
        
        # Update statistics
        if self.progress.files_processed > 0:
            self.statistics.total_files_synced = self.progress.files_processed
        
        if self.progress.total_size > 0:
            self.statistics.total_data_transferred = self.progress.total_size
        
        if self.progress.speed > 0:
            if self.progress.speed > self.statistics.peak_speed:
                self.statistics.peak_speed = self.progress.speed
            
            # Calculate average speed
            if self.statistics.sync_duration > 0:
                self.statistics.average_speed = self.statistics.total_data_transferred / self.statistics.sync_duration
    
    def add_error(self, error_message: str, error_details: Dict = None):
        """Add an error to the session"""
        self.statistics.errors_encountered += 1
        self._log_event(error_message, "ERROR", error_details)
    
    def retry(self):
        """Retry the session"""
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            self.status = SyncStatus.PENDING
            self.error_message = None
            self.error_details = None
            self.statistics.retry_attempts += 1
            
            self._log_event(f"Retry attempt {self.retry_count}/{self.max_retries}", "INFO")
            return True
        else:
            self._log_event("Max retry attempts reached", "ERROR")
            return False
    
    def _log_event(self, message: str, level: str, details: Dict = None):
        """Log an event in the session"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "details": details
        }
        self.log_entries.append(log_entry)
    
    def get_log_summary(self) -> Dict:
        """Get a summary of the session logs"""
        return {
            "total_entries": len(self.log_entries),
            "error_count": len([e for e in self.log_entries if e["level"] == "ERROR"]),
            "warning_count": len([e for e in self.log_entries if e["level"] == "WARNING"]),
            "info_count": len([e for e in self.log_entries if e["level"] == "INFO"]),
            "recent_errors": [e for e in self.log_entries[-5:] if e["level"] == "ERROR"]
        }
    
    def is_active(self) -> bool:
        """Check if the session is currently active"""
        return self.status in [SyncStatus.PENDING, SyncStatus.IN_PROGRESS, SyncStatus.PAUSED]
    
    def get_elapsed_time(self) -> float:
        """Get the elapsed time since the session started"""
        if not self.started_at:
            return 0.0
        
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()
    
    def get_remaining_time(self) -> float:
        """Get estimated remaining time"""
        if self.progress.percentage <= 0 or self.progress.percentage >= 100:
            return 0.0
        
        elapsed = self.get_elapsed_time()
        if elapsed <= 0:
            return 0.0
        
        # Estimate based on current progress
        estimated_total = elapsed / (self.progress.percentage / 100)
        return estimated_total - elapsed