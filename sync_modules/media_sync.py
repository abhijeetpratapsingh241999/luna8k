"""
Media Synchronization Module
Handles media file synchronization between phone and PC.
"""

import os
import shutil
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import mimetypes
import json
from dataclasses import dataclass

from base_sync import BaseSyncModule

@dataclass
class MediaFile:
    """Media file data structure"""
    id: str
    filename: str
    file_path: str
    file_size: int
    file_type: str  # 'music', 'photo', 'video'
    mime_type: str
    duration: Optional[float]  # for audio/video files
    width: Optional[int]  # for photos/videos
    height: Optional[int]  # for photos/videos
    artist: Optional[str]  # for music files
    album: Optional[str]  # for music files
    title: Optional[str]  # for music files
    bitrate: Optional[int]  # for audio/video files
    created_date: datetime
    modified_date: datetime
    source: str  # 'phone' or 'pc'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert media file to dictionary"""
        data = {
            'id': self.id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'duration': self.duration,
            'width': self.width,
            'height': self.height,
            'artist': self.artist,
            'album': self.album,
            'title': self.title,
            'bitrate': self.bitrate,
            'created_date': self.created_date.isoformat(),
            'modified_date': self.modified_date.isoformat(),
            'source': self.source
        }
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MediaFile':
        """Create media file from dictionary"""
        data['created_date'] = datetime.fromisoformat(data['created_date'])
        data['modified_date'] = datetime.fromisoformat(data['modified_date'])
        return cls(**data)

class MediaSyncModule(BaseSyncModule):
    """Media synchronization module"""
    
    def __init__(self):
        super().__init__("media_sync")
        self.phone_media = {}
        self.pc_media = {}
        self.sync_media = {}
        self.media_id_counter = 1
        
        # Media directories
        self.phone_media_dir = "./phone_media"
        self.pc_media_dir = "./pc_media"
        self.sync_media_dir = "./sync_media"
        
        # Supported media types
        self.supported_types = {
            'music': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            'photo': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']
        }
        
        # Create necessary directories
        self._create_directories()
        
        # Load sample media files
        self._load_sample_media()
        
    def sync_data_type(self) -> str:
        return "media_files"
        
    def _create_directories(self):
        """Create necessary directories for media sync"""
        for media_type in self.supported_types.keys():
            for base_dir in [self.phone_media_dir, self.pc_media_dir, self.sync_media_dir]:
                media_dir = os.path.join(base_dir, media_type)
                Path(media_dir).mkdir(parents=True, exist_ok=True)
                
    def _load_sample_media(self):
        """Load sample media files for demonstration"""
        now = datetime.now()
        
        # Sample phone media
        self.phone_media = {
            "1": MediaFile(
                id="1",
                filename="vacation_photo.jpg",
                file_path=os.path.join(self.phone_media_dir, "photo", "vacation_photo.jpg"),
                file_size=2048576,  # 2MB
                file_type="photo",
                mime_type="image/jpeg",
                duration=None,
                width=1920,
                height=1080,
                artist=None,
                album=None,
                title=None,
                bitrate=None,
                created_date=now - timedelta(days=5),
                modified_date=now - timedelta(days=2),
                source="phone"
            ),
            "2": MediaFile(
                id="2",
                filename="favorite_song.mp3",
                file_path=os.path.join(self.phone_media_dir, "music", "favorite_song.mp3"),
                file_size=5120000,  # 5MB
                file_type="music",
                mime_type="audio/mpeg",
                duration=180.5,  # 3 minutes
                width=None,
                height=None,
                artist="Popular Artist",
                album="Greatest Hits",
                title="Favorite Song",
                bitrate=320,
                created_date=now - timedelta(days=10),
                modified_date=now - timedelta(days=7),
                source="phone"
            )
        }
        
        # Sample PC media
        self.pc_media = {
            "3": MediaFile(
                id="3",
                filename="work_video.mp4",
                file_path=os.path.join(self.pc_media_dir, "video", "work_video.mp4"),
                file_size=15728640,  # 15MB
                file_type="video",
                mime_type="video/mp4",
                duration=120.0,  # 2 minutes
                width=1280,
                height=720,
                artist=None,
                album=None,
                title="Work Presentation",
                bitrate=1000,
                created_date=now - timedelta(days=3),
                modified_date=now - timedelta(days=1),
                source="pc"
            ),
            "4": MediaFile(
                id="4",
                filename="family_photo.png",
                file_path=os.path.join(self.pc_media_dir, "photo", "family_photo.png"),
                file_size=1048576,  # 1MB
                file_type="photo",
                mime_type="image/png",
                duration=None,
                width=800,
                height=600,
                artist=None,
                album=None,
                title=None,
                bitrate=None,
                created_date=now - timedelta(days=15),
                modified_date=now - timedelta(days=12),
                source="pc"
            )
        }
        
        # Initialize sync media
        self._merge_media()
        
    def _merge_media(self):
        """Merge phone and PC media into sync media"""
        self.sync_media = {}
        
        # Add phone media
        for media_id, media in self.phone_media.items():
            sync_media = MediaFile(
                id=media_id,
                filename=media.filename,
                file_path=media.file_path,
                file_size=media.file_size,
                file_type=media.file_type,
                mime_type=media.mime_type,
                duration=media.duration,
                width=media.width,
                height=media.height,
                artist=media.artist,
                album=media.album,
                title=media.title,
                bitrate=media.bitrate,
                created_date=media.created_date,
                modified_date=media.modified_date,
                source="phone"
            )
            self.sync_media[media_id] = sync_media
            
        # Add PC media (check for duplicates)
        for media_id, media in self.pc_media.items():
            # Check if media already exists (by filename and type)
            existing_media = self._find_matching_media(media)
            
            if existing_media:
                # Merge with existing media
                self._merge_media_data(existing_media, media)
            else:
                # Add as new media
                sync_media = MediaFile(
                    id=media_id,
                    filename=media.filename,
                    file_path=media.file_path,
                    file_size=media.file_size,
                    file_type=media.file_type,
                    mime_type=media.mime_type,
                    duration=media.duration,
                    width=media.width,
                    height=media.height,
                    artist=media.artist,
                    album=media.album,
                    title=media.title,
                    bitrate=media.bitrate,
                    created_date=media.created_date,
                    modified_date=media.modified_date,
                    source="pc"
                )
                self.sync_media[media_id] = sync_media
                
    def _find_matching_media(self, media: MediaFile) -> Optional[MediaFile]:
        """Find matching media in sync media"""
        for sync_media in self.sync_media.values():
            # Check by filename and type
            if (sync_media.filename.lower() == media.filename.lower() and
                sync_media.file_type == media.file_type):
                return sync_media
                
        return None
        
    def _merge_media_data(self, existing: MediaFile, new: MediaFile):
        """Merge new media data with existing media"""
        # Update metadata if new data is more recent
        if new.modified_date > existing.modified_date:
            if new.artist:
                existing.artist = new.artist
            if new.album:
                existing.album = new.album
            if new.title:
                existing.title = new.title
            if new.bitrate:
                existing.bitrate = new.bitrate
                
        existing.modified_date = datetime.now()
        existing.source = "merged"
        
    def get_sync_items(self) -> List[Dict[str, Any]]:
        """Get list of media files that need synchronization"""
        sync_items = []
        
        # Check for new media in phone
        for media_id, media in self.phone_media.items():
            if media_id not in self.sync_media:
                sync_items.append({
                    'action': 'add_media',
                    'media': media,
                    'source': 'phone'
                })
                
        # Check for new media in PC
        for media_id, media in self.pc_media.items():
            if media_id not in self.sync_media:
                sync_items.append({
                    'action': 'add_media',
                    'media': media,
                    'source': 'pc'
                })
                
        # Check for updated media
        for media_id in set(self.phone_media.keys()) & set(self.pc_media.keys()):
            phone_media = self.phone_media[media_id]
            pc_media = self.pc_media[media_id]
            
            if phone_media.modified_date != pc_media.modified_date:
                sync_items.append({
                    'action': 'update_media',
                    'media_id': media_id,
                    'phone_media': phone_media,
                    'pc_media': pc_media
                })
                
        return sync_items
        
    def perform_sync(self, items: List[Dict[str, Any]]) -> bool:
        """Perform media synchronization"""
        try:
            for item in items:
                if item['action'] == 'add_media':
                    self._add_media_to_sync(item['media'])
                elif item['action'] == 'update_media':
                    self._update_media_in_sync(item)
                    
            # Update sync media
            self._merge_media()
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Media sync failed: {str(e)}")
            return False
            
    def _add_media_to_sync(self, media: MediaFile):
        """Add media to sync media"""
        media_id = str(self.media_id_counter)
        self.media_id_counter += 1
        
        # Copy file to sync directory
        sync_path = os.path.join(self.sync_media_dir, media.file_type, media.filename)
        os.makedirs(os.path.dirname(sync_path), exist_ok=True)
        
        try:
            shutil.copy2(media.file_path, sync_path)
        except FileNotFoundError:
            # File doesn't exist, create empty file for demo
            Path(sync_path).touch()
            
        sync_media = MediaFile(
            id=media_id,
            filename=media.filename,
            file_path=sync_path,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
            duration=media.duration,
            width=media.width,
            height=media.height,
            artist=media.artist,
            album=media.album,
            title=media.title,
            bitrate=media.bitrate,
            created_date=media.created_date,
            modified_date=datetime.now(),
            source=media.source
        )
        
        self.sync_media[media_id] = sync_media
        self.sync_activity.emit(self.name, f"Added media: {media.filename}")
        
    def _update_media_in_sync(self, item: Dict[str, Any]):
        """Update media in sync media"""
        media_id = item['media_id']
        phone_media = item['phone_media']
        pc_media = item['pc_media']
        
        if media_id in self.sync_media:
            sync_media = self.sync_media[media_id]
            
            # Merge the updated data
            self._merge_media_data(sync_media, phone_media)
            self._merge_media_data(sync_media, pc_media)
            
            self.sync_activity.emit(self.name, f"Updated media: {sync_media.filename}")
            
    def add_media_file(self, file_path: str, source: str = "sync") -> str:
        """Add a new media file"""
        try:
            if not os.path.exists(file_path):
                return ""
                
            # Determine media type
            file_ext = os.path.splitext(file_path)[1].lower()
            media_type = None
            
            for type_name, extensions in self.supported_types.items():
                if file_ext in extensions:
                    media_type = type_name
                    break
                    
            if not media_type:
                self.sync_error.emit(self.name, f"Unsupported file type: {file_ext}")
                return ""
                
            # Get file information
            stat = os.stat(file_path)
            filename = os.path.basename(file_path)
            
            # Create media file object
            media_id = str(self.media_id_counter)
            self.media_id_counter += 1
            
            media = MediaFile(
                id=media_id,
                filename=filename,
                file_path=file_path,
                file_size=stat.st_size,
                file_type=media_type,
                mime_type=mimetypes.guess_type(file_path)[0] or "application/octet-stream",
                duration=None,
                width=None,
                height=None,
                artist=None,
                album=None,
                title=None,
                bitrate=None,
                created_date=datetime.fromtimestamp(stat.st_ctime),
                modified_date=datetime.fromtimestamp(stat.st_mtime),
                source=source
            )
            
            # Add to appropriate collection
            if source == "phone":
                self.phone_media[media_id] = media
            elif source == "pc":
                self.pc_media[media_id] = media
            else:
                self.sync_media[media_id] = media
                
            self.sync_activity.emit(self.name, f"Added new media: {filename}")
            return media_id
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to add media: {str(e)}")
            return ""
            
    def remove_media(self, media_id: str) -> bool:
        """Remove a media file"""
        try:
            # Remove from all media collections
            for media_dict in [self.phone_media, self.pc_media, self.sync_media]:
                if media_id in media_dict:
                    media = media_dict[media_id]
                    self.sync_activity.emit(self.name, f"Removed media: {media.filename}")
                    del media_dict[media_id]
                    
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to remove media: {str(e)}")
            return False
            
    def search_media(self, query: str, media_type: Optional[str] = None) -> List[MediaFile]:
        """Search media files by filename, artist, album, or title"""
        results = []
        query_lower = query.lower()
        
        for media in self.sync_media.values():
            # Filter by media type if specified
            if media_type and media.file_type != media_type:
                continue
                
            # Search by filename
            if query_lower in media.filename.lower():
                results.append(media)
                continue
                
            # Search by artist
            if media.artist and query_lower in media.artist.lower():
                results.append(media)
                continue
                
            # Search by album
            if media.album and query_lower in media.album.lower():
                results.append(media)
                continue
                
            # Search by title
            if media.title and query_lower in media.title.lower():
                results.append(media)
                continue
                
        return results
        
    def get_media_by_type(self, media_type: str) -> List[MediaFile]:
        """Get all media files of a specific type"""
        return [media for media in self.sync_media.values() if media.file_type == media_type]
        
    def get_media_stats(self) -> Dict[str, Any]:
        """Get media synchronization statistics"""
        total_size = sum(media.file_size for media in self.sync_media.values())
        
        stats = {
            'total_files': len(self.sync_media),
            'total_size': total_size,
            'phone_media': len(self.phone_media),
            'pc_media': len(self.pc_media),
            'merged_media': len([m for m in self.sync_media.values() if m.source == "merged"]),
            'last_sync': self.last_sync_time
        }
        
        # Add stats by type
        for media_type in self.supported_types.keys():
            type_media = self.get_media_by_type(media_type)
            stats[f'{media_type}_count'] = len(type_media)
            stats[f'{media_type}_size'] = sum(m.file_size for m in type_media)
            
        return stats
        
    def export_media_list(self, file_path: str, format_type: str = "json") -> bool:
        """Export media file list to file"""
        try:
            if format_type == "json":
                data = {
                    'media_files': [media.to_dict() for media in self.sync_media.values()],
                    'export_time': datetime.now().isoformat()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                    
            elif format_type == "csv":
                import csv
                
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    # Write header
                    writer.writerow(['Filename', 'Type', 'Size (bytes)', 'Artist', 'Album', 'Title', 'Duration', 'Source'])
                    
                    # Write media files
                    for media in self.sync_media.values():
                        writer.writerow([
                            media.filename,
                            media.file_type,
                            media.file_size,
                            media.artist or '',
                            media.album or '',
                            media.title or '',
                            media.duration or '',
                            media.source
                        ])
                        
            self.sync_activity.emit(self.name, f"Exported media list to {file_path}")
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to export media list: {str(e)}")
            return False
            
    def import_media_list(self, file_path: str, format_type: str = "json") -> bool:
        """Import media file list from file"""
        try:
            if format_type == "json":
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                for media_data in data.get('media_files', []):
                    media = MediaFile.from_dict(media_data)
                    self.sync_media[media.id] = media
                    
            elif format_type == "csv":
                import csv
                
                with open(file_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Create basic media file from CSV data
                        media_data = {
                            'filename': row['Filename'],
                            'file_type': row['Type'],
                            'file_size': int(row['Size (bytes)']) if row['Size (bytes)'] else 0,
                            'artist': row['Artist'] if row['Artist'] else None,
                            'album': row['Album'] if row['Album'] else None,
                            'title': row['Title'] if row['Title'] else None,
                            'duration': float(row['Duration']) if row['Duration'] else None,
                            'source': row['Source']
                        }
                        
                        # Create a dummy file path for demo purposes
                        dummy_path = os.path.join(self.sync_media_dir, media_data['file_type'], media_data['filename'])
                        
                        media = MediaFile(
                            id=str(self.media_id_counter),
                            filename=media_data['filename'],
                            file_path=dummy_path,
                            file_size=media_data['file_size'],
                            file_type=media_data['file_type'],
                            mime_type=mimetypes.guess_type(dummy_path)[0] or "application/octet-stream",
                            duration=media_data['duration'],
                            width=None,
                            height=None,
                            artist=media_data['artist'],
                            album=media_data['album'],
                            title=media_data['title'],
                            bitrate=None,
                            created_date=datetime.now(),
                            modified_date=datetime.now(),
                            source=media_data['source']
                        )
                        
                        self.sync_media[media.id] = media
                        self.media_id_counter += 1
                        
            self.sync_activity.emit(self.name, f"Imported media list from {file_path}")
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to import media list: {str(e)}")
            return False
            
    def get_duplicate_media(self) -> List[List[MediaFile]]:
        """Find duplicate media files based on filename and type"""
        duplicates = []
        seen = {}
        
        for media in self.sync_media.values():
            key = (media.filename.lower(), media.file_type)
            if key in seen:
                # Check if we already have a group for this duplicate
                found_group = False
                for group in duplicates:
                    if any(m.filename.lower() == media.filename.lower() and m.file_type == media.file_type for m in group):
                        group.append(media)
                        found_group = True
                        break
                        
                if not found_group:
                    # Create new group with both files
                    duplicates.append([seen[key], media])
            else:
                seen[key] = media
                
        return [group for group in duplicates if len(group) > 1]
        
    def cleanup_duplicates(self, strategy: str = "keep_newest") -> int:
        """Clean up duplicate media files"""
        duplicates = self.get_duplicate_media()
        removed_count = 0
        
        for group in duplicates:
            if strategy == "keep_newest":
                # Keep the most recently modified file
                newest = max(group, key=lambda x: x.modified_date)
                for media in group:
                    if media.id != newest.id:
                        self.remove_media(media.id)
                        removed_count += 1
                        
            elif strategy == "keep_largest":
                # Keep the largest file
                largest = max(group, key=lambda x: x.file_size)
                for media in group:
                    if media.id != largest.id:
                        self.remove_media(media.id)
                        removed_count += 1
                        
        if removed_count > 0:
            self.sync_activity.emit(self.name, f"Cleaned up {removed_count} duplicate files")
            
        return removed_count