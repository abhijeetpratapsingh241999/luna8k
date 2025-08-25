"""
Sync Engine Module
Coordinates all synchronization operations between different modules.
"""

import json
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from enum import Enum
import queue

class SyncStatus(Enum):
    IDLE = "idle"
    SCANNING = "scanning"
    SYNCHRONIZING = "synchronizing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class SyncPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class SyncOperation:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.operation_type = kwargs.get('operation_type', 'unknown')  # 'file', 'contact', 'calendar', 'full'
        self.priority = kwargs.get('priority', SyncPriority.NORMAL)
        self.status = kwargs.get('status', SyncStatus.IDLE)
        self.progress = kwargs.get('progress', 0)  # 0-100
        self.start_time = kwargs.get('start_time')
        self.end_time = kwargs.get('end_time')
        self.device_id = kwargs.get('device_id')
        self.source_path = kwargs.get('source_path', '')
        self.destination_path = kwargs.get('destination_path', '')
        self.total_items = kwargs.get('total_items', 0)
        self.processed_items = kwargs.get('processed_items', 0)
        self.errors = kwargs.get('errors', [])
        self.warnings = kwargs.get('warnings', [])
        self.metadata = kwargs.get('metadata', {})
        
    def to_dict(self) -> Dict:
        """Convert operation to dictionary"""
        return {
            'id': self.id,
            'operation_type': self.operation_type,
            'priority': self.priority.value if isinstance(self.priority, SyncPriority) else str(self.priority),
            'status': self.status.value if isinstance(self.status, SyncStatus) else str(self.status),
            'progress': self.progress,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'device_id': self.device_id,
            'source_path': self.source_path,
            'destination_path': self.destination_path,
            'total_items': self.total_items,
            'processed_items': self.processed_items,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'SyncOperation':
        """Create operation from dictionary"""
        # Parse datetime fields
        for field in ['start_time', 'end_time']:
            if field in data and data[field]:
                try:
                    data[field] = datetime.fromisoformat(data[field])
                except ValueError:
                    data[field] = None
                    
        # Parse enums
        if 'priority' in data:
            try:
                data['priority'] = SyncPriority(data['priority'])
            except ValueError:
                data['priority'] = SyncPriority.NORMAL
                
        if 'status' in data:
            try:
                data['status'] = SyncStatus(data['status'])
            except ValueError:
                data['status'] = SyncStatus.IDLE
                
        return cls(**data)
        
    def update_progress(self, processed: int, total: int = None):
        """Update operation progress"""
        if total:
            self.total_items = total
        self.processed_items = processed
        
        if self.total_items > 0:
            self.progress = min(100, int((processed / self.total_items) * 100))
            
    def add_error(self, error: str):
        """Add error to operation"""
        self.errors.append({
            'message': error,
            'timestamp': datetime.now().isoformat()
        })
        
    def add_warning(self, warning: str):
        """Add warning to operation"""
        self.warnings.append({
            'message': warning,
            'timestamp': datetime.now().isoformat()
        })
        
    def is_completed(self) -> bool:
        """Check if operation is completed"""
        return self.status in [SyncStatus.COMPLETED, SyncStatus.FAILED, SyncStatus.CANCELLED]
        
    def get_duration(self) -> Optional[timedelta]:
        """Get duration of operation"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return datetime.now() - self.start_time
        return None

class SyncEngine:
    def __init__(self):
        self.sync_queue = queue.PriorityQueue()
        self.active_operations: List[SyncOperation] = []
        self.completed_operations: List[SyncOperation] = []
        self.sync_callbacks: List[Callable] = []
        self.is_running = False
        self.sync_thread = None
        self.sync_config = {
            'max_concurrent_syncs': 3,
            'auto_retry_failed': True,
            'max_retry_attempts': 3,
            'sync_timeout_minutes': 30,
            'enable_background_sync': True,
            'sync_interval_minutes': 15
        }
        
        # Statistics
        self.sync_stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'total_items_synced': 0,
            'total_sync_time': timedelta(0),
            'last_sync': None
        }
        
    def start_sync_engine(self):
        """Start the sync engine"""
        if not self.is_running:
            self.is_running = True
            self.sync_thread = threading.Thread(target=self._sync_worker_loop, daemon=True)
            self.sync_thread.start()
            
    def stop_sync_engine(self):
        """Stop the sync engine"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join()
            
    def _sync_worker_loop(self):
        """Main sync worker loop"""
        while self.is_running:
            try:
                # Process sync queue
                if not self.sync_queue.empty() and len(self.active_operations) < self.sync_config['max_concurrent_syncs']:
                    priority, operation = self.sync_queue.get()
                    self._execute_sync_operation(operation)
                    
                # Check for completed operations
                self._cleanup_completed_operations()
                
                # Check for timed out operations
                self._check_timeouts()
                
                time.sleep(1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                print(f"Error in sync worker loop: {e}")
                time.sleep(5)  # Wait before retrying
                
    def _execute_sync_operation(self, operation: SyncOperation):
        """Execute a sync operation"""
        try:
            operation.status = SyncStatus.SYNCHRONIZING
            operation.start_time = datetime.now()
            self.active_operations.append(operation)
            
            # Notify callbacks
            self._notify_sync_started(operation)
            
            # Simulate sync process based on operation type
            if operation.operation_type == 'file':
                self._simulate_file_sync(operation)
            elif operation.operation_type == 'contact':
                self._simulate_contact_sync(operation)
            elif operation.operation_type == 'calendar':
                self._simulate_calendar_sync(operation)
            elif operation.operation_type == 'full':
                self._simulate_full_sync(operation)
            else:
                self._simulate_generic_sync(operation)
                
            # Mark as completed
            operation.status = SyncStatus.COMPLETED
            operation.end_time = datetime.now()
            operation.progress = 100
            
            # Update statistics
            self._update_sync_stats(operation, success=True)
            
            # Notify callbacks
            self._notify_sync_completed(operation)
            
        except Exception as e:
            operation.status = SyncStatus.FAILED
            operation.end_time = datetime.now()
            operation.add_error(str(e))
            
            # Update statistics
            self._update_sync_stats(operation, success=False)
            
            # Notify callbacks
            self._notify_sync_failed(operation)
            
            # Handle retry logic
            if self.sync_config['auto_retry_failed']:
                self._handle_retry(operation)
                
    def _simulate_file_sync(self, operation: SyncOperation):
        """Simulate file synchronization"""
        total_files = operation.total_items or 100
        operation.total_items = total_files
        
        for i in range(total_files):
            if operation.status == SyncStatus.CANCELLED:
                break
                
            # Simulate file processing
            time.sleep(0.1)
            
            # Update progress
            operation.update_progress(i + 1, total_files)
            
            # Simulate occasional errors
            if i == total_files // 4:  # 25% through
                operation.add_warning(f"Slow file transfer for file {i}")
                
            # Notify progress
            self._notify_sync_progress(operation)
            
    def _simulate_contact_sync(self, operation: SyncOperation):
        """Simulate contact synchronization"""
        total_contacts = operation.total_items or 50
        operation.total_items = total_contacts
        
        for i in range(total_contacts):
            if operation.status == SyncStatus.CANCELLED:
                break
                
            # Simulate contact processing
            time.sleep(0.05)
            
            # Update progress
            operation.update_progress(i + 1, total_contacts)
            
            # Notify progress
            self._notify_sync_progress(operation)
            
    def _simulate_calendar_sync(self, operation: SyncOperation):
        """Simulate calendar synchronization"""
        total_events = operation.total_items or 30
        operation.total_items = total_events
        
        for i in range(total_events):
            if operation.status == SyncStatus.CANCELLED:
                break
                
            # Simulate event processing
            time.sleep(0.08)
            
            # Update progress
            operation.update_progress(i + 1, total_events)
            
            # Notify progress
            self._notify_sync_progress(operation)
            
    def _simulate_full_sync(self, operation: SyncOperation):
        """Simulate full synchronization"""
        # Simulate scanning phase
        operation.status = SyncStatus.SCANNING
        operation.progress = 0
        self._notify_sync_progress(operation)
        
        time.sleep(2)  # Simulate scanning time
        
        # Simulate sync phase
        operation.status = SyncStatus.SYNCHRONIZING
        total_steps = 100
        operation.total_items = total_steps
        
        for i in range(total_steps):
            if operation.status == SyncStatus.CANCELLED:
                break
                
            # Simulate sync step
            time.sleep(0.1)
            
            # Update progress
            operation.update_progress(i + 1, total_steps)
            
            # Notify progress
            self._notify_sync_progress(operation)
            
    def _simulate_generic_sync(self, operation: SyncOperation):
        """Simulate generic synchronization"""
        total_steps = operation.total_items or 50
        operation.total_items = total_steps
        
        for i in range(total_steps):
            if operation.status == SyncStatus.CANCELLED:
                break
                
            # Simulate sync step
            time.sleep(0.1)
            
            # Update progress
            operation.update_progress(i + 1, total_steps)
            
            # Notify progress
            self._notify_sync_progress(operation)
            
    def _handle_retry(self, operation: SyncOperation):
        """Handle retry logic for failed operations"""
        retry_count = operation.metadata.get('retry_count', 0)
        
        if retry_count < self.sync_config['max_retry_attempts']:
            # Increment retry count
            operation.metadata['retry_count'] = retry_count + 1
            
            # Reset operation for retry
            operation.status = SyncStatus.IDLE
            operation.progress = 0
            operation.start_time = None
            operation.end_time = None
            operation.errors = []
            operation.warnings = []
            
            # Re-queue with lower priority
            priority = self._calculate_priority(operation.priority, retry_count)
            self.sync_queue.put((priority, operation))
            
    def _calculate_priority(self, base_priority: SyncPriority, retry_count: int) -> int:
        """Calculate priority value for queue ordering"""
        priority_values = {
            SyncPriority.LOW: 4,
            SyncPriority.NORMAL: 3,
            SyncPriority.HIGH: 2,
            SyncPriority.CRITICAL: 1
        }
        
        base_value = priority_values.get(base_priority, 3)
        return base_value + retry_count  # Lower number = higher priority
        
    def _cleanup_completed_operations(self):
        """Clean up completed operations"""
        completed = [op for op in self.active_operations if op.is_completed()]
        
        for operation in completed:
            self.active_operations.remove(operation)
            self.completed_operations.append(operation)
            
            # Keep only last 100 completed operations
            if len(self.completed_operations) > 100:
                self.completed_operations.pop(0)
                
    def _check_timeouts(self):
        """Check for timed out operations"""
        timeout_minutes = self.sync_config['sync_timeout_minutes']
        timeout_threshold = datetime.now() - timedelta(minutes=timeout_minutes)
        
        for operation in self.active_operations:
            if operation.start_time and operation.start_time < timeout_threshold:
                operation.status = SyncStatus.FAILED
                operation.add_error(f"Operation timed out after {timeout_minutes} minutes")
                operation.end_time = datetime.now()
                
    def _update_sync_stats(self, operation: SyncOperation, success: bool):
        """Update sync statistics"""
        self.sync_stats['total_syncs'] += 1
        
        if success:
            self.sync_stats['successful_syncs'] += 1
        else:
            self.sync_stats['failed_syncs'] += 1
            
        if operation.total_items:
            self.sync_stats['total_items_synced'] += operation.total_items
            
        if operation.get_duration():
            self.sync_stats['total_sync_time'] += operation.get_duration()
            
        self.sync_stats['last_sync'] = datetime.now()
        
    def add_sync_callback(self, callback: Callable):
        """Add callback for sync events"""
        self.sync_callbacks.append(callback)
        
    def remove_sync_callback(self, callback: Callable):
        """Remove sync callback"""
        if callback in self.sync_callbacks:
            self.sync_callbacks.remove(callback)
            
    def _notify_sync_started(self, operation: SyncOperation):
        """Notify callbacks of sync start"""
        for callback in self.sync_callbacks:
            try:
                callback('started', operation)
            except Exception as e:
                print(f"Error in sync callback: {e}")
                
    def _notify_sync_progress(self, operation: SyncOperation):
        """Notify callbacks of sync progress"""
        for callback in self.sync_callbacks:
            try:
                callback('progress', operation)
            except Exception as e:
                print(f"Error in sync callback: {e}")
                
    def _notify_sync_completed(self, operation: SyncOperation):
        """Notify callbacks of sync completion"""
        for callback in self.sync_callbacks:
            try:
                callback('completed', operation)
            except Exception as e:
                print(f"Error in sync callback: {e}")
                
    def _notify_sync_failed(self, operation: SyncOperation):
        """Notify callbacks of sync failure"""
        for callback in self.sync_callbacks:
            try:
                callback('failed', operation)
            except Exception as e:
                print(f"Error in sync callback: {e}")
                
    def queue_sync_operation(self, operation: SyncOperation) -> bool:
        """Queue a sync operation for execution"""
        try:
            if not operation.id:
                operation.id = self._generate_operation_id()
                
            # Calculate priority value
            priority = self._calculate_priority(operation.priority, 0)
            
            # Add to queue
            self.sync_queue.put((priority, operation))
            return True
            
        except Exception as e:
            print(f"Error queuing sync operation: {e}")
            return False
            
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        import uuid
        return str(uuid.uuid4())
        
    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel a sync operation"""
        # Check active operations
        for operation in self.active_operations:
            if operation.id == operation_id:
                operation.status = SyncStatus.CANCELLED
                operation.end_time = datetime.now()
                return True
                
        # Check queued operations
        # Note: This is a simplified approach. In a real implementation,
        # you'd need to handle the queue more carefully
        return False
        
    def pause_operation(self, operation_id: str) -> bool:
        """Pause a sync operation"""
        for operation in self.active_operations:
            if operation.id == operation_id:
                operation.status = SyncStatus.PAUSED
                return True
        return False
        
    def resume_operation(self, operation_id: str) -> bool:
        """Resume a paused sync operation"""
        for operation in self.active_operations:
            if operation.id == operation_id and operation.status == SyncStatus.PAUSED:
                operation.status = SyncStatus.SYNCHRONIZING
                return True
        return False
        
    def get_operation_status(self, operation_id: str) -> Optional[SyncOperation]:
        """Get status of a sync operation"""
        # Check active operations
        for operation in self.active_operations:
            if operation.id == operation_id:
                return operation
                
        # Check completed operations
        for operation in self.completed_operations:
            if operation.id == operation_id:
                return operation
                
        return None
        
    def get_all_operations(self) -> List[SyncOperation]:
        """Get all operations (active and completed)"""
        return self.active_operations + self.completed_operations
        
    def get_sync_summary(self) -> Dict:
        """Get summary of sync operations"""
        active_count = len(self.active_operations)
        completed_count = len(self.completed_operations)
        
        return {
            'active_operations': active_count,
            'completed_operations': completed_count,
            'queued_operations': self.sync_queue.qsize(),
            'total_operations': active_count + completed_count,
            'statistics': self.sync_stats.copy()
        }
        
    def clear_completed_operations(self):
        """Clear completed operations history"""
        self.completed_operations.clear()
        
    def update_config(self, new_config: Dict):
        """Update sync engine configuration"""
        self.sync_config.update(new_config)
        
    def get_config(self) -> Dict:
        """Get current sync engine configuration"""
        return self.sync_config.copy()