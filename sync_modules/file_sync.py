"""
File Synchronization Module
Handles file synchronization between phone and PC.
"""

import os
import shutil
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

from base_sync import BaseSyncModule

class FileSyncModule(BaseSyncModule):
    """File synchronization module"""
    
    def __init__(self):
        super().__init__("file_sync")
        self.phone_folder = "./phone_files"
        self.pc_folder = "./pc_files"
        self.sync_folder = "./sync_folder"
        self.file_index = {}
        self.conflict_resolution = "newest_wins"
        self.supported_extensions = ['.txt', '.doc', '.docx', '.pdf', '.jpg', '.png', '.mp3', '.mp4', '.zip']
        
        # Create necessary directories
        self._create_directories()
        
        # Initialize file index
        self._build_file_index()
        
    def sync_data_type(self) -> str:
        return "files"
        
    def _create_directories(self):
        """Create necessary directories for file sync"""
        for folder in [self.phone_folder, self.pc_folder, self.sync_folder]:
            Path(folder).mkdir(exist_ok=True)
            
    def _build_file_index(self):
        """Build index of existing files"""
        self.file_index = {
            'phone': self._scan_directory(self.phone_folder),
            'pc': self._scan_directory(self.pc_folder),
            'sync': self._scan_directory(self.sync_folder)
        }
        
    def _scan_directory(self, directory: str) -> Dict[str, Dict[str, Any]]:
        """Scan directory and return file information"""
        files = {}
        if os.path.exists(directory):
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, directory)
                    
                    try:
                        stat = os.stat(file_path)
                        files[rel_path] = {
                            'path': file_path,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime),
                            'hash': self._calculate_file_hash(file_path)
                        }
                    except OSError:
                        continue
                        
        return files
        
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
            
    def get_sync_items(self) -> List[Dict[str, Any]]:
        """Get list of files that need synchronization"""
        sync_items = []
        
        # Check for new files in phone folder
        for rel_path, file_info in self.file_index['phone'].items():
            if rel_path not in self.file_index['sync']:
                sync_items.append({
                    'source': 'phone',
                    'path': rel_path,
                    'action': 'copy_to_sync',
                    'file_info': file_info
                })
                
        # Check for new files in PC folder
        for rel_path, file_info in self.file_index['pc'].items():
            if rel_path not in self.file_index['sync']:
                sync_items.append({
                    'source': 'pc',
                    'path': rel_path,
                    'action': 'copy_to_sync',
                    'file_info': file_info
                })
                
        # Check for conflicts and updates
        for rel_path in set(self.file_index['phone'].keys()) & set(self.file_index['pc'].keys()):
            phone_info = self.file_index['phone'][rel_path]
            pc_info = self.file_index['pc'][rel_path]
            
            if phone_info['hash'] != pc_info['hash']:
                # Conflict detected
                sync_items.append({
                    'source': 'conflict',
                    'path': rel_path,
                    'action': 'resolve_conflict',
                    'phone_info': phone_info,
                    'pc_info': pc_info
                })
                
        return sync_items
        
    def perform_sync(self, items: List[Dict[str, Any]]) -> bool:
        """Perform file synchronization"""
        try:
            for item in items:
                if item['action'] == 'copy_to_sync':
                    self._copy_file_to_sync(item)
                elif item['action'] == 'resolve_conflict':
                    self._resolve_file_conflict(item)
                    
            # Update file index after sync
            self._build_file_index()
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"File sync failed: {str(e)}")
            return False
            
    def _copy_file_to_sync(self, item: Dict[str, Any]):
        """Copy file to sync folder"""
        source_path = item['file_info']['path']
        sync_path = os.path.join(self.sync_folder, item['path'])
        
        # Create directory structure if needed
        os.makedirs(os.path.dirname(sync_path), exist_ok=True)
        
        # Copy file
        shutil.copy2(source_path, sync_path)
        
        self.sync_activity.emit(self.name, f"Copied {item['path']} to sync folder")
        
    def _resolve_file_conflict(self, item: Dict[str, Any]):
        """Resolve file conflict based on resolution strategy"""
        phone_info = item['phone_info']
        pc_info = item['pc_info']
        rel_path = item['path']
        
        if self.conflict_resolution == "newest_wins":
            if phone_info['modified'] > pc_info['modified']:
                winner = 'phone'
                winner_info = phone_info
            else:
                winner = 'pc'
                winner_info = pc_info
                
        elif self.conflict_resolution == "phone_wins":
            winner = 'phone'
            winner_info = phone_info
        elif self.conflict_resolution == "pc_wins":
            winner = 'pc'
            winner_info = pc_info
        else:
            # Ask user - for now, use newest
            winner = 'newest'
            winner_info = phone_info if phone_info['modified'] > pc_info['modified'] else pc_info
            
        # Copy winning file to sync folder
        sync_path = os.path.join(self.sync_folder, rel_path)
        os.makedirs(os.path.dirname(sync_path), exist_ok=True)
        shutil.copy2(winner_info['path'], sync_path)
        
        self.sync_activity.emit(self.name, f"Resolved conflict for {rel_path} using {winner} version")
        
    def add_file(self, file_path: str, destination: str = "sync") -> bool:
        """Add a new file to the sync system"""
        try:
            if not os.path.exists(file_path):
                return False
                
            filename = os.path.basename(file_path)
            dest_folder = getattr(self, f"{destination}_folder")
            dest_path = os.path.join(dest_folder, filename)
            
            # Copy file to destination
            shutil.copy2(file_path, dest_path)
            
            # Update file index
            self._build_file_index()
            
            self.sync_activity.emit(self.name, f"Added {filename} to {destination} folder")
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to add file: {str(e)}")
            return False
            
    def remove_file(self, file_path: str, source: str = "sync") -> bool:
        """Remove a file from the sync system"""
        try:
            source_folder = getattr(self, f"{source}_folder")
            full_path = os.path.join(source_folder, file_path)
            
            if os.path.exists(full_path):
                os.remove(full_path)
                
                # Update file index
                self._build_file_index()
                
                self.sync_activity.emit(self.name, f"Removed {file_path} from {source} folder")
                return True
                
            return False
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to remove file: {str(e)}")
            return False
            
    def get_file_stats(self) -> Dict[str, Any]:
        """Get file synchronization statistics"""
        total_files = sum(len(files) for files in self.file_index.values())
        total_size = sum(
            sum(file_info['size'] for file_info in files.values())
            for files in self.file_index.values()
        )
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'phone_files': len(self.file_index['phone']),
            'pc_files': len(self.file_index['pc']),
            'sync_files': len(self.file_index['sync']),
            'last_index_update': datetime.now()
        }
        
    def set_conflict_resolution(self, strategy: str):
        """Set conflict resolution strategy"""
        valid_strategies = ["newest_wins", "phone_wins", "pc_wins", "ask_user"]
        if strategy in valid_strategies:
            self.conflict_resolution = strategy
            self.sync_activity.emit(self.name, f"Conflict resolution set to: {strategy}")
            
    def sync_to_phone(self) -> bool:
        """Sync all files from sync folder to phone"""
        try:
            for rel_path, file_info in self.file_index['sync'].items():
                phone_path = os.path.join(self.phone_folder, rel_path)
                os.makedirs(os.path.dirname(phone_path), exist_ok=True)
                shutil.copy2(file_info['path'], phone_path)
                
            self.sync_activity.emit(self.name, "Synced all files to phone")
            self._build_file_index()
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to sync to phone: {str(e)}")
            return False
            
    def sync_to_pc(self) -> bool:
        """Sync all files from sync folder to PC"""
        try:
            for rel_path, file_info in self.file_index['sync'].items():
                pc_path = os.path.join(self.pc_folder, rel_path)
                os.makedirs(os.path.dirname(pc_path), exist_ok=True)
                shutil.copy2(file_info['path'], pc_path)
                
            self.sync_activity.emit(self.name, "Synced all files to PC")
            self._build_file_index()
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to sync to PC: {str(e)}")
            return False
            
    def get_file_tree(self) -> Dict[str, Any]:
        """Get hierarchical file structure"""
        def build_tree(files_dict):
            tree = {}
            for file_path in files_dict.keys():
                parts = file_path.split(os.sep)
                current = tree
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = files_dict[file_path]
            return tree
            
        return {
            'phone': build_tree(self.file_index['phone']),
            'pc': build_tree(self.file_index['pc']),
            'sync': build_tree(self.file_index['sync'])
        }