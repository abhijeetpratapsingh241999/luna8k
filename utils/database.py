"""
Database Manager Utility
Handles database operations for storing sync data and configuration.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import threading

class DatabaseManager:
    def __init__(self, db_path: str = "sync_emulator.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
        
    def _init_database(self):
        """Initialize database and create tables"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Create sync history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sync_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        operation_type TEXT NOT NULL,
                        device_id TEXT,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        status TEXT NOT NULL,
                        progress INTEGER DEFAULT 0,
                        total_items INTEGER DEFAULT 0,
                        processed_items INTEGER DEFAULT 0,
                        errors TEXT,
                        warnings TEXT,
                        metadata TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create device info table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS device_info (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        model TEXT,
                        manufacturer TEXT,
                        os_type TEXT,
                        os_version TEXT,
                        serial_number TEXT,
                        imei TEXT,
                        mac_address TEXT,
                        connection_type TEXT,
                        connection_status TEXT DEFAULT 'disconnected',
                        battery_level INTEGER DEFAULT 0,
                        battery_charging BOOLEAN DEFAULT 0,
                        storage_total INTEGER DEFAULT 0,
                        storage_available INTEGER DEFAULT 0,
                        last_seen TEXT,
                        is_trusted BOOLEAN DEFAULT 0,
                        sync_enabled BOOLEAN DEFAULT 1,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create sync configuration table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sync_config (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        description TEXT,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create contacts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS contacts (
                        id TEXT PRIMARY KEY,
                        first_name TEXT,
                        last_name TEXT,
                        company TEXT,
                        job_title TEXT,
                        emails TEXT,
                        phones TEXT,
                        addresses TEXT,
                        birthday TEXT,
                        notes TEXT,
                        source TEXT DEFAULT 'pc',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create calendar events table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS calendar_events (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT,
                        start_time TEXT,
                        end_time TEXT,
                        all_day BOOLEAN DEFAULT 0,
                        location TEXT,
                        attendees TEXT,
                        reminders TEXT,
                        recurrence TEXT,
                        priority TEXT DEFAULT 'normal',
                        status TEXT DEFAULT 'confirmed',
                        calendar_id TEXT DEFAULT 'default',
                        source TEXT DEFAULT 'pc',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create file sync records table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS file_sync_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path TEXT NOT NULL,
                        file_hash TEXT,
                        file_size INTEGER,
                        last_modified TEXT,
                        sync_status TEXT DEFAULT 'pending',
                        device_id TEXT,
                        sync_direction TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Insert default configuration
                self._insert_default_config(cursor)
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            
    def _insert_default_config(self, cursor):
        """Insert default configuration values"""
        default_config = [
            ('sync_auto_enabled', 'false', 'Enable automatic synchronization'),
            ('sync_interval_minutes', '15', 'Synchronization interval in minutes'),
            ('max_concurrent_syncs', '3', 'Maximum concurrent synchronization operations'),
            ('sync_timeout_minutes', '30', 'Synchronization timeout in minutes'),
            ('backup_before_sync', 'true', 'Create backup before synchronization'),
            ('merge_duplicates', 'true', 'Merge duplicate contacts and events'),
            ('sync_deleted_items', 'true', 'Synchronize deleted items'),
            ('file_sync_enabled', 'true', 'Enable file synchronization'),
            ('contact_sync_enabled', 'true', 'Enable contact synchronization'),
            ('calendar_sync_enabled', 'true', 'Enable calendar synchronization')
        ]
        
        for key, value, description in default_config:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO sync_config (key, value, description)
                    VALUES (?, ?, ?)
                ''', (key, value, description))
            except sqlite3.IntegrityError:
                pass  # Key already exists
                
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """Execute a SELECT query and return results"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = cursor.fetchall()
                conn.close()
                return results
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
            
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Execute an UPDATE/INSERT/DELETE query"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print(f"Error executing update: {e}")
            return False
            
    def save_sync_history(self, sync_data: Dict) -> bool:
        """Save sync history record"""
        try:
            query = '''
                INSERT INTO sync_history (
                    operation_type, device_id, start_time, end_time, status,
                    progress, total_items, processed_items, errors, warnings, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                sync_data.get('operation_type', 'unknown'),
                sync_data.get('device_id'),
                sync_data.get('start_time', datetime.now().isoformat()),
                sync_data.get('end_time'),
                sync_data.get('status', 'unknown'),
                sync_data.get('progress', 0),
                sync_data.get('total_items', 0),
                sync_data.get('processed_items', 0),
                json.dumps(sync_data.get('errors', [])),
                json.dumps(sync_data.get('warnings', [])),
                json.dumps(sync_data.get('metadata', {}))
            )
            
            return self.execute_update(query, params)
            
        except Exception as e:
            print(f"Error saving sync history: {e}")
            return False
            
    def get_sync_history(self, limit: int = 100, operation_type: str = None) -> List[Dict]:
        """Get sync history records"""
        try:
            query = "SELECT * FROM sync_history"
            params = []
            
            if operation_type:
                query += " WHERE operation_type = ?"
                params.append(operation_type)
                
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            results = self.execute_query(query, tuple(params))
            
            history = []
            for row in results:
                history.append({
                    'id': row[0],
                    'operation_type': row[1],
                    'device_id': row[2],
                    'start_time': row[3],
                    'end_time': row[4],
                    'status': row[5],
                    'progress': row[6],
                    'total_items': row[7],
                    'processed_items': row[8],
                    'errors': json.loads(row[9]) if row[9] else [],
                    'warnings': json.loads(row[10]) if row[10] else [],
                    'metadata': json.loads(row[11]) if row[11] else {},
                    'created_at': row[12]
                })
                
            return history
            
        except Exception as e:
            print(f"Error getting sync history: {e}")
            return []
            
    def save_device_info(self, device_data: Dict) -> bool:
        """Save or update device information"""
        try:
            query = '''
                INSERT OR REPLACE INTO device_info (
                    id, name, model, manufacturer, os_type, os_version,
                    serial_number, imei, mac_address, connection_type,
                    connection_status, battery_level, battery_charging,
                    storage_total, storage_available, last_seen,
                    is_trusted, sync_enabled, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                device_data.get('id'),
                device_data.get('name'),
                device_data.get('model'),
                device_data.get('manufacturer'),
                device_data.get('os_type'),
                device_data.get('os_version'),
                device_data.get('serial_number'),
                device_data.get('imei'),
                device_data.get('mac_address'),
                device_data.get('connection_type'),
                device_data.get('connection_status'),
                device_data.get('battery_level', 0),
                device_data.get('battery_charging', False),
                device_data.get('storage_total', 0),
                device_data.get('storage_available', 0),
                device_data.get('last_seen', datetime.now().isoformat()),
                device_data.get('is_trusted', False),
                device_data.get('sync_enabled', True),
                datetime.now().isoformat()
            )
            
            return self.execute_update(query, params)
            
        except Exception as e:
            print(f"Error saving device info: {e}")
            return False
            
    def get_device_info(self, device_id: str = None) -> List[Dict]:
        """Get device information"""
        try:
            if device_id:
                query = "SELECT * FROM device_info WHERE id = ?"
                params = (device_id,)
            else:
                query = "SELECT * FROM device_info ORDER BY updated_at DESC"
                params = ()
                
            results = self.execute_query(query, params)
            
            devices = []
            for row in results:
                devices.append({
                    'id': row[0],
                    'name': row[1],
                    'model': row[2],
                    'manufacturer': row[3],
                    'os_type': row[4],
                    'os_version': row[5],
                    'serial_number': row[6],
                    'imei': row[7],
                    'mac_address': row[8],
                    'connection_type': row[9],
                    'connection_status': row[10],
                    'battery_level': row[11],
                    'battery_charging': bool(row[12]),
                    'storage_total': row[13],
                    'storage_available': row[14],
                    'last_seen': row[15],
                    'is_trusted': bool(row[16]),
                    'sync_enabled': bool(row[17]),
                    'created_at': row[18],
                    'updated_at': row[19]
                })
                
            return devices
            
        except Exception as e:
            print(f"Error getting device info: {e}")
            return []
            
    def save_contact(self, contact_data: Dict) -> bool:
        """Save or update contact information"""
        try:
            query = '''
                INSERT OR REPLACE INTO contacts (
                    id, first_name, last_name, company, job_title,
                    emails, phones, addresses, birthday, notes,
                    source, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                contact_data.get('id'),
                contact_data.get('first_name'),
                contact_data.get('last_name'),
                contact_data.get('company'),
                contact_data.get('job_title'),
                json.dumps(contact_data.get('emails', [])),
                json.dumps(contact_data.get('phones', [])),
                json.dumps(contact_data.get('addresses', [])),
                contact_data.get('birthday'),
                contact_data.get('notes'),
                contact_data.get('source', 'pc'),
                datetime.now().isoformat()
            )
            
            return self.execute_update(query, params)
            
        except Exception as e:
            print(f"Error saving contact: {e}")
            return False
            
    def get_contacts(self, contact_id: str = None) -> List[Dict]:
        """Get contact information"""
        try:
            if contact_id:
                query = "SELECT * FROM contacts WHERE id = ?"
                params = (contact_id,)
            else:
                query = "SELECT * FROM contacts ORDER BY last_name, first_name"
                params = ()
                
            results = self.execute_query(query, params)
            
            contacts = []
            for row in results:
                contacts.append({
                    'id': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'company': row[3],
                    'job_title': row[4],
                    'emails': json.loads(row[5]) if row[5] else [],
                    'phones': json.loads(row[6]) if row[6] else [],
                    'addresses': json.loads(row[7]) if row[7] else [],
                    'birthday': row[8],
                    'notes': row[9],
                    'source': row[10],
                    'created_at': row[11],
                    'updated_at': row[12]
                })
                
            return contacts
            
        except Exception as e:
            print(f"Error getting contacts: {e}")
            return []
            
    def save_calendar_event(self, event_data: Dict) -> bool:
        """Save or update calendar event"""
        try:
            query = '''
                INSERT OR REPLACE INTO calendar_events (
                    id, title, description, start_time, end_time,
                    all_day, location, attendees, reminders, recurrence,
                    priority, status, calendar_id, source, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                event_data.get('id'),
                event_data.get('title'),
                event_data.get('description'),
                event_data.get('start_time'),
                event_data.get('end_time'),
                event_data.get('all_day', False),
                event_data.get('location'),
                json.dumps(event_data.get('attendees', [])),
                json.dumps(event_data.get('reminders', [])),
                json.dumps(event_data.get('recurrence', {})),
                event_data.get('priority', 'normal'),
                event_data.get('status', 'confirmed'),
                event_data.get('calendar_id', 'default'),
                event_data.get('source', 'pc'),
                datetime.now().isoformat()
            )
            
            return self.execute_update(query, params)
            
        except Exception as e:
            print(f"Error saving calendar event: {e}")
            return False
            
    def get_calendar_events(self, event_id: str = None, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get calendar events"""
        try:
            query = "SELECT * FROM calendar_events"
            params = []
            conditions = []
            
            if event_id:
                conditions.append("id = ?")
                params.append(event_id)
                
            if start_date:
                conditions.append("start_time >= ?")
                params.append(start_date)
                
            if end_date:
                conditions.append("end_time <= ?")
                params.append(end_date)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY start_time"
            
            results = self.execute_query(query, tuple(params))
            
            events = []
            for row in results:
                events.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'start_time': row[3],
                    'end_time': row[4],
                    'all_day': bool(row[5]),
                    'location': row[6],
                    'attendees': json.loads(row[7]) if row[7] else [],
                    'reminders': json.loads(row[8]) if row[8] else [],
                    'recurrence': json.loads(row[9]) if row[9] else {},
                    'priority': row[10],
                    'status': row[11],
                    'calendar_id': row[12],
                    'source': row[13],
                    'created_at': row[14],
                    'updated_at': row[15]
                })
                
            return events
            
        except Exception as e:
            print(f"Error getting calendar events: {e}")
            return []
            
    def get_config_value(self, key: str, default: str = None) -> str:
        """Get configuration value"""
        try:
            query = "SELECT value FROM sync_config WHERE key = ?"
            results = self.execute_query(query, (key,))
            
            if results:
                return results[0][0]
            return default
            
        except Exception as e:
            print(f"Error getting config value: {e}")
            return default
            
    def set_config_value(self, key: str, value: str, description: str = None) -> bool:
        """Set configuration value"""
        try:
            query = '''
                INSERT OR REPLACE INTO sync_config (key, value, description, updated_at)
                VALUES (?, ?, ?, ?)
            '''
            
            params = (key, value, description, datetime.now().isoformat())
            return self.execute_update(query, params)
            
        except Exception as e:
            print(f"Error setting config value: {e}")
            return False
            
    def get_sync_statistics(self) -> Dict:
        """Get synchronization statistics"""
        try:
            stats = {}
            
            # Total sync operations
            results = self.execute_query("SELECT COUNT(*) FROM sync_history")
            if results:
                stats['total_syncs'] = results[0][0]
                
            # Successful syncs
            results = self.execute_query("SELECT COUNT(*) FROM sync_history WHERE status = 'completed'")
            if results:
                stats['successful_syncs'] = results[0][0]
                
            # Failed syncs
            results = self.execute_query("SELECT COUNT(*) FROM sync_history WHERE status = 'failed'")
            if results:
                stats['failed_syncs'] = results[0][0]
                
            # Total contacts
            results = self.execute_query("SELECT COUNT(*) FROM contacts")
            if results:
                stats['total_contacts'] = results[0][0]
                
            # Total calendar events
            results = self.execute_query("SELECT COUNT(*) FROM calendar_events")
            if results:
                stats['total_events'] = results[0][0]
                
            # Total devices
            results = self.execute_query("SELECT COUNT(*) FROM device_info")
            if results:
                stats['total_devices'] = results[0][0]
                
            return stats
            
        except Exception as e:
            print(f"Error getting sync statistics: {e}")
            return {}
            
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Error backing up database: {e}")
            return False
            
    def clear_old_records(self, days_to_keep: int = 30) -> bool:
        """Clear old sync history records"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            query = "DELETE FROM sync_history WHERE created_at < ?"
            return self.execute_update(query, (cutoff_date.isoformat(),))
        except Exception as e:
            print(f"Error clearing old records: {e}")
            return False
            
    def get_database_size(self) -> int:
        """Get database file size in bytes"""
        try:
            if os.path.exists(self.db_path):
                return os.path.getsize(self.db_path)
            return 0
        except Exception as e:
            print(f"Error getting database size: {e}")
            return 0