"""
Base Sync Module
Provides common functionality for all synchronization modules.
"""

import os
import json
import time
import threading
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional

# Mock PyQt6 classes for demo purposes
class MockQObject:
    """Mock QObject class for demo purposes"""
    def __init__(self):
        pass

class MockQTimer:
    """Mock QTimer class for demo purposes"""
    def __init__(self):
        self.is_active = False
    
    def start(self, ms):
        self.is_active = True
    
    def stop(self):
        self.is_active = False
    
    def isActive(self):
        return self.is_active

class MockSignal:
    """Mock signal class for demo purposes"""
    def __init__(self, *args):
        self.connected_functions = []
    
    def connect(self, func):
        self.connected_functions.append(func)
    
    def emit(self, *args):
        for func in self.connected_functions:
            try:
                func(*args)
            except:
                pass

class BaseSyncModule(MockQObject, ABC):
    """Base class for all synchronization modules"""
    
    # Signals (mocked for demo)
    sync_progress = MockSignal()
    sync_status = MockSignal()
    sync_activity = MockSignal()
    sync_error = MockSignal()
    
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.is_running_flag = False
        self.sync_thread = None
        self.progress = 0
        self.status = "⏸️ Paused"
        self.sync_data = {}
        self.last_sync_time = None
        self.sync_interval = 30  # seconds
        self.error_count = 0
        self.success_count = 0
        
        # Setup timer for periodic sync
        self.sync_timer = MockQTimer()
        
    @abstractmethod
    def sync_data_type(self) -> str:
        """Return the type of data this module syncs"""
        pass
        
    @abstractmethod
    def get_sync_items(self) -> List[Dict[str, Any]]:
        """Get list of items to sync"""
        pass
        
    @abstractmethod
    def perform_sync(self, items: List[Dict[str, Any]]) -> bool:
        """Perform the actual synchronization"""
        pass
        
    def start_sync(self):
        """Start the synchronization process"""
        if not self.is_running_flag:
            self.is_running_flag = True
            self.status = "🔄 Syncing"
            self.sync_status.emit(self.name, self.status)
            self.sync_activity.emit(self.name, "Sync started")
            
            # Start sync thread
            self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
            self.sync_thread.start()
            
            # Start periodic sync timer
            self.sync_timer.start(self.sync_interval * 1000)
            
    def stop_sync(self):
        """Stop the synchronization process"""
        if self.is_running_flag:
            self.is_running_flag = False
            self.status = "⏸️ Paused"
            self.sync_status.emit(self.name, self.status)
            self.sync_activity.emit(self.name, "Sync stopped")
            
            # Stop periodic sync timer
            self.sync_timer.stop()
            
    def is_running(self) -> bool:
        """Check if sync is currently running"""
        return self.is_running_flag
        
    def get_progress(self) -> int:
        """Get current sync progress (0-100)"""
        return self.progress
        
    def get_status(self) -> str:
        """Get current sync status"""
        return self.status
        
    def get_stats(self) -> Dict[str, Any]:
        """Get synchronization statistics"""
        return {
            'name': self.name,
            'status': self.status,
            'progress': self.progress,
            'is_running': self.is_running_flag,
            'last_sync': self.last_sync_time,
            'error_count': self.error_count,
            'success_count': self.success_count,
            'sync_interval': self.sync_interval
        }
        
    def _sync_worker(self):
        """Worker thread for synchronization"""
        try:
            while self.is_running_flag:
                # Get items to sync
                items = self.get_sync_items()
                
                if items:
                    # Perform sync
                    success = self.perform_sync(items)
                    
                    if success:
                        self.success_count += 1
                        self.sync_activity.emit(self.name, f"Successfully synced {len(items)} items")
                    else:
                        self.error_count += 1
                        self.sync_activity.emit(self.name, f"Failed to sync {len(items)} items")
                        
                    # Update last sync time
                    self.last_sync_time = datetime.now()
                    
                # Wait before next sync cycle
                time.sleep(5)
                
        except Exception as e:
            self.sync_error.emit(self.name, str(e))
            self.error_count += 1
            self.status = "❌ Error"
            self.sync_status.emit(self.name, self.status)
            
    def periodic_sync(self):
        """Triggered by timer for periodic synchronization"""
        if self.is_running_flag:
            self.sync_activity.emit(self.name, "Periodic sync triggered")
            
    def update_progress(self, progress: int):
        """Update sync progress"""
        self.progress = max(0, min(100, progress))
        self.sync_progress.emit(self.name, self.progress)
        
    def simulate_sync_progress(self):
        """Simulate sync progress for demonstration"""
        if self.is_running_flag:
            # Simulate progress from 0 to 100
            for i in range(0, 101, 10):
                if not self.is_running_flag:
                    break
                self.update_progress(i)
                time.sleep(0.5)
                
            if self.is_running_flag:
                self.update_progress(100)
                self.sync_activity.emit(self.name, "Sync simulation completed")
                
    def reset_stats(self):
        """Reset synchronization statistics"""
        self.error_count = 0
        self.success_count = 0
        self.progress = 0
        self.last_sync_time = None
        
    def set_sync_interval(self, interval: int):
        """Set synchronization interval in seconds"""
        self.sync_interval = max(1, interval)
        if self.sync_timer.isActive():
            self.sync_timer.stop()
            self.sync_timer.start(self.sync_interval * 1000)
            
    def export_sync_data(self, file_path: str) -> bool:
        """Export sync data to file"""
        try:
            data = {
                'module_name': self.name,
                'sync_data': self.sync_data,
                'stats': self.get_stats(),
                'export_time': datetime.now().isoformat()
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to export data: {str(e)}")
            return False
            
    def import_sync_data(self, file_path: str) -> bool:
        """Import sync data from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            if data.get('module_name') == self.name:
                self.sync_data = data.get('sync_data', {})
                return True
            else:
                self.sync_error.emit(self.name, "Invalid sync data file")
                return False
                
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to import data: {str(e)}")
            return False