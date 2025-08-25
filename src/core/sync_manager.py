"""
Core Sync Manager
Handles all synchronization operations between phone and PC
"""

import threading
import time
import queue
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from ..models.device import Device, DeviceType
from ..models.sync_session import SyncSession, SyncStatus
from ..sync_protocols.protocol_manager import ProtocolManager
from ..emulators.phone_emulator import PhoneEmulator
from ..emulators.pc_emulator import PCEmulator


class SyncEvent(Enum):
    """Synchronization events"""
    STARTED = "started"
    PROGRESS = "progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DEVICE_CONNECTED = "device_connected"
    DEVICE_DISCONNECTED = "device_disconnected"


@dataclass
class SyncProgress:
    """Synchronization progress information"""
    current_file: str
    total_files: int
    current_file_size: int
    total_size: int
    percentage: float
    speed: float  # bytes per second
    estimated_time: float  # seconds


class SyncManager:
    """Main synchronization manager"""
    
    def __init__(self, config):
        self.config = config
        self.phone_emulator = PhoneEmulator(config)
        self.pc_emulator = PCEmulator(config)
        self.protocol_manager = ProtocolManager(config)
        
        self.sync_queue = queue.Queue()
        self.active_sessions: Dict[str, SyncSession] = {}
        self.event_callbacks: List[Callable] = []
        
        self._running = False
        self._worker_thread = None
        
        # Start the worker thread
        self._start_worker()
    
    def _start_worker(self):
        """Start the background worker thread"""
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
    
    def _worker_loop(self):
        """Main worker loop for processing sync requests"""
        while self._running:
            try:
                # Process sync requests
                if not self.sync_queue.empty():
                    session = self.sync_queue.get_nowait()
                    self._process_sync_session(session)
                
                # Check for device connections
                self._check_device_connections()
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                print(f"Error in sync worker: {e}")
                time.sleep(1)
    
    def _process_sync_session(self, session: SyncSession):
        """Process a synchronization session"""
        try:
            session.status = SyncStatus.IN_PROGRESS
            self._notify_event(SyncEvent.STARTED, session)
            
            # Determine sync type and execute
            if session.sync_type == "full":
                self._execute_full_sync(session)
            elif session.sync_type == "incremental":
                self._execute_incremental_sync(session)
            elif session.sync_type == "selective":
                self._execute_selective_sync(session)
            
            session.status = SyncStatus.COMPLETED
            self._notify_event(SyncEvent.COMPLETED, session)
            
        except Exception as e:
            session.status = SyncStatus.FAILED
            session.error_message = str(e)
            self._notify_event(SyncEvent.FAILED, session)
    
    def _execute_full_sync(self, session: SyncSession):
        """Execute a full synchronization"""
        # Simulate full sync process
        total_files = 1000
        total_size = 1024 * 1024 * 100  # 100 MB
        
        for i in range(total_files):
            if session.cancelled:
                raise Exception("Sync cancelled by user")
            
            # Simulate file processing
            current_file = f"file_{i:04d}.dat"
            current_size = total_size // total_files
            
            progress = SyncProgress(
                current_file=current_file,
                total_files=total_files,
                current_file_size=current_size,
                total_size=total_size,
                percentage=(i + 1) / total_files * 100,
                speed=1024 * 1024,  # 1 MB/s
                estimated_time=(total_size - (i * current_size)) / (1024 * 1024)
            )
            
            session.progress = progress
            self._notify_event(SyncEvent.PROGRESS, session)
            
            # Simulate processing time
            time.sleep(0.01)
    
    def _execute_incremental_sync(self, session: SyncSession):
        """Execute an incremental synchronization"""
        # Simulate incremental sync (only changed files)
        changed_files = 50
        total_size = 1024 * 1024 * 10  # 10 MB
        
        for i in range(changed_files):
            if session.cancelled:
                raise Exception("Sync cancelled by user")
            
            current_file = f"changed_file_{i:03d}.dat"
            current_size = total_size // changed_files
            
            progress = SyncProgress(
                current_file=current_file,
                total_files=changed_files,
                current_file_size=current_size,
                total_size=total_size,
                percentage=(i + 1) / changed_files * 100,
                speed=1024 * 1024 * 2,  # 2 MB/s
                estimated_time=(total_size - (i * current_size)) / (1024 * 1024 * 2)
            )
            
            session.progress = progress
            self._notify_event(SyncEvent.PROGRESS, session)
            
            time.sleep(0.02)
    
    def _execute_selective_sync(self, session: SyncSession):
        """Execute a selective synchronization"""
        # Simulate selective sync (user-selected files)
        selected_files = session.selected_files or []
        total_files = len(selected_files)
        total_size = sum(file.size for file in selected_files) if selected_files else 1024 * 1024
        
        for i, file_info in enumerate(selected_files):
            if session.cancelled:
                raise Exception("Sync cancelled by user")
            
            progress = SyncProgress(
                current_file=file_info.name,
                total_files=total_files,
                current_file_size=file_info.size,
                total_size=total_size,
                percentage=(i + 1) / total_files * 100,
                speed=1024 * 1024 * 1.5,  # 1.5 MB/s
                estimated_time=(total_size - sum(f.size for f in selected_files[:i+1])) / (1024 * 1024 * 1.5)
            )
            
            session.progress = progress
            self._notify_event(SyncEvent.PROGRESS, session)
            
            time.sleep(0.015)
    
    def _check_device_connections(self):
        """Check for device connections/disconnections"""
        # Simulate device detection
        if self.phone_emulator.is_connected() and not hasattr(self, '_phone_connected'):
            self._phone_connected = True
            self._notify_event(SyncEvent.DEVICE_CONNECTED, {"device": "phone"})
        
        elif not self.phone_emulator.is_connected() and hasattr(self, '_phone_connected'):
            self._phone_connected = False
            self._notify_event(SyncEvent.DEVICE_DISCONNECTED, {"device": "phone"})
    
    def start_sync(self, sync_type: str, selected_files: List = None) -> str:
        """Start a new synchronization session"""
        session = SyncSession(
            sync_type=sync_type,
            selected_files=selected_files,
            phone_device=self.phone_emulator.get_device_info(),
            pc_device=self.pc_emulator.get_device_info()
        )
        
        self.active_sessions[session.id] = session
        self.sync_queue.put(session)
        
        return session.id
    
    def cancel_sync(self, session_id: str):
        """Cancel an active synchronization session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].cancelled = True
    
    def get_sync_status(self, session_id: str) -> Optional[SyncSession]:
        """Get the status of a synchronization session"""
        return self.active_sessions.get(session_id)
    
    def get_all_sessions(self) -> List[SyncSession]:
        """Get all synchronization sessions"""
        return list(self.active_sessions.values())
    
    def add_event_callback(self, callback: Callable):
        """Add an event callback function"""
        self.event_callbacks.append(callback)
    
    def _notify_event(self, event: SyncEvent, data):
        """Notify all event callbacks"""
        for callback in self.event_callbacks:
            try:
                callback(event, data)
            except Exception as e:
                print(f"Error in event callback: {e}")
    
    def shutdown(self):
        """Shutdown the sync manager"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)