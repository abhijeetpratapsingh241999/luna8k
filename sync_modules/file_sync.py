"""
File Synchronization Module
Handles file operations and synchronization between mobile device and PC.
"""

import os
import shutil
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import mimetypes

class FileSyncModule:
    def __init__(self):
        self.sync_config = {
            'include_hidden': False,
            'exclude_patterns': ['.DS_Store', 'Thumbs.db', '*.tmp'],
            'max_file_size': 1024 * 1024 * 1024,  # 1GB
            'sync_direction': 'bidirectional',  # 'device_to_pc', 'pc_to_device', 'bidirectional'
            'conflict_resolution': 'newer_wins'  # 'newer_wins', 'device_wins', 'pc_wins'
        }
        
        self.sync_history = []
        self.current_sync_session = None
        
    def scan_directory(self, path: str, device_path: str = None) -> Dict[str, Dict]:
        """
        Scan a directory and return file information
        
        Args:
            path: Path to scan
            device_path: Corresponding path on device (if different)
            
        Returns:
            Dictionary with file information
        """
        files_info = {}
        
        if not os.path.exists(path):
            return files_info
            
        for root, dirs, files in os.walk(path):
            # Skip hidden directories if configured
            if not self.sync_config['include_hidden']:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
            for file in files:
                # Skip excluded files
                if self._should_exclude_file(file):
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, path)
                
                try:
                    stat = os.stat(file_path)
                    file_info = {
                        'name': file,
                        'path': file_path,
                        'relative_path': rel_path,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'is_file': True,
                        'mime_type': self._get_mime_type(file_path),
                        'hash': self._calculate_file_hash(file_path),
                        'device_path': device_path + '/' + rel_path if device_path else None
                    }
                    
                    files_info[rel_path] = file_info
                    
                except (OSError, PermissionError) as e:
                    print(f"Error accessing file {file_path}: {e}")
                    
        return files_info
        
    def _should_exclude_file(self, filename: str) -> bool:
        """Check if file should be excluded based on patterns"""
        for pattern in self.sync_config['exclude_patterns']:
            if pattern.startswith('*'):
                if filename.endswith(pattern[1:]):
                    return True
            elif pattern == filename:
                return True
        return False
        
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type of file"""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'
        
    def _calculate_file_hash(self, file_path: str, algorithm: str = 'md5') -> str:
        """Calculate hash of file for change detection"""
        hash_func = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except (OSError, PermissionError):
            return ""
            
    def compare_directories(self, pc_files: Dict, device_files: Dict) -> Dict[str, List]:
        """
        Compare two directories and identify differences
        
        Returns:
            Dictionary with 'new', 'modified', 'deleted', 'conflicts' lists
        """
        differences = {
            'new_on_pc': [],
            'new_on_device': [],
            'modified_on_pc': [],
            'modified_on_device': [],
            'deleted_on_pc': [],
            'deleted_on_device': [],
            'conflicts': []
        }
        
        # Find new and modified files
        for rel_path, pc_info in pc_files.items():
            if rel_path not in device_files:
                differences['new_on_pc'].append(pc_info)
            else:
                device_info = device_files[rel_path]
                if pc_info['hash'] != device_info['hash']:
                    # Check modification times for conflict resolution
                    if pc_info['modified'] > device_info['modified']:
                        differences['modified_on_pc'].append(pc_info)
                    elif device_info['modified'] > pc_info['modified']:
                        differences['modified_on_device'].append(device_info)
                    else:
                        differences['conflicts'].append((pc_info, device_info))
                        
        # Find files deleted from PC
        for rel_path, device_info in device_files.items():
            if rel_path not in pc_files:
                differences['deleted_on_pc'].append(device_info)
                
        return differences
        
    def sync_files(self, differences: Dict, pc_base_path: str, device_base_path: str) -> Dict:
        """
        Synchronize files based on differences
        
        Args:
            differences: Output from compare_directories
            pc_base_path: Base path on PC
            device_base_path: Base path on device
            
        Returns:
            Sync results summary
        """
        sync_results = {
            'files_copied': 0,
            'files_updated': 0,
            'files_deleted': 0,
            'errors': [],
            'start_time': datetime.now(),
            'end_time': None
        }
        
        try:
            # Copy new files from PC to device
            for file_info in differences['new_on_pc']:
                if self._copy_file_to_device(file_info, pc_base_path, device_base_path):
                    sync_results['files_copied'] += 1
                    
            # Copy new files from device to PC
            for file_info in differences['new_on_device']:
                if self._copy_file_to_pc(file_info, device_base_path, pc_base_path):
                    sync_results['files_copied'] += 1
                    
            # Update modified files
            for file_info in differences['modified_on_pc']:
                if self._copy_file_to_device(file_info, pc_base_path, device_base_path):
                    sync_results['files_updated'] += 1
                    
            for file_info in differences['modified_on_device']:
                if self._copy_file_to_pc(file_info, device_base_path, pc_base_path):
                    sync_results['files_updated'] += 1
                    
            # Handle conflicts based on configuration
            for pc_info, device_info in differences['conflicts']:
                if self.sync_config['conflict_resolution'] == 'newer_wins':
                    if pc_info['modified'] > device_info['modified']:
                        if self._copy_file_to_device(pc_info, pc_base_path, device_base_path):
                            sync_results['files_updated'] += 1
                    else:
                        if self._copy_file_to_pc(device_info, device_base_path, pc_base_path):
                            sync_results['files_updated'] += 1
                elif self.sync_config['conflict_resolution'] == 'device_wins':
                    if self._copy_file_to_pc(device_info, device_base_path, pc_base_path):
                        sync_results['files_updated'] += 1
                elif self.sync_config['conflict_resolution'] == 'pc_wins':
                    if self._copy_file_to_device(pc_info, pc_base_path, device_base_path):
                        sync_results['files_updated'] += 1
                        
        except Exception as e:
            sync_results['errors'].append(str(e))
            
        sync_results['end_time'] = datetime.now()
        sync_results['duration'] = sync_results['end_time'] - sync_results['start_time']
        
        # Add to sync history
        self.sync_history.append(sync_results)
        
        return sync_results
        
    def _copy_file_to_device(self, file_info: Dict, pc_base: str, device_base: str) -> bool:
        """Copy file from PC to device"""
        try:
            device_path = os.path.join(device_base, file_info['relative_path'])
            device_dir = os.path.dirname(device_path)
            
            # Create directory if it doesn't exist
            os.makedirs(device_dir, exist_ok=True)
            
            # Copy file
            shutil.copy2(file_info['path'], device_path)
            return True
            
        except Exception as e:
            print(f"Error copying {file_info['path']} to device: {e}")
            return False
            
    def _copy_file_to_pc(self, file_info: Dict, device_base: str, pc_base: str) -> bool:
        """Copy file from device to PC"""
        try:
            pc_path = os.path.join(pc_base, file_info['relative_path'])
            pc_dir = os.path.dirname(pc_path)
            
            # Create directory if it doesn't exist
            os.makedirs(pc_dir, exist_ok=True)
            
            # Copy file
            shutil.copy2(file_info['path'], pc_path)
            return True
            
        except Exception as e:
            print(f"Error copying {file_info['path']} to PC: {e}")
            return False
            
    def get_sync_summary(self) -> Dict:
        """Get summary of all sync operations"""
        if not self.sync_history:
            return {}
            
        total_files = sum(h['files_copied'] + h['files_updated'] + h['files_deleted'] 
                         for h in self.sync_history)
        total_errors = sum(len(h['errors']) for h in self.sync_history)
        
        return {
            'total_syncs': len(self.sync_history),
            'total_files_processed': total_files,
            'total_errors': total_errors,
            'last_sync': self.sync_history[-1]['end_time'] if self.sync_history else None,
            'average_duration': sum((h['end_time'] - h['start_time']).total_seconds() 
                                  for h in self.sync_history) / len(self.sync_history) if self.sync_history else 0
        }
        
    def update_config(self, new_config: Dict):
        """Update synchronization configuration"""
        self.sync_config.update(new_config)
        
    def get_config(self) -> Dict:
        """Get current synchronization configuration"""
        return self.sync_config.copy()
        
    def clear_history(self):
        """Clear sync history"""
        self.sync_history.clear()
        
    def export_sync_report(self, file_path: str):
        """Export sync report to JSON file"""
        try:
            report = {
                'config': self.sync_config,
                'summary': self.get_sync_summary(),
                'history': self.sync_history
            }
            
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error exporting sync report: {e}")