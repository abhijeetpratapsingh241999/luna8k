"""
Calendar Synchronization Module
Handles calendar events and synchronization between mobile device and PC.
"""

import json
import csv
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
import re
from dateutil import parser as date_parser

class CalendarEvent:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.start_time = kwargs.get('start_time')
        self.end_time = kwargs.get('end_time')
        self.all_day = kwargs.get('all_day', False)
        self.location = kwargs.get('location', '')
        self.attendees = kwargs.get('attendees', [])
        self.reminders = kwargs.get('reminders', [])
        self.recurrence = kwargs.get('recurrence', {})  # RRULE format
        self.priority = kwargs.get('priority', 'normal')  # 'low', 'normal', 'high'
        self.status = kwargs.get('status', 'confirmed')  # 'tentative', 'confirmed', 'cancelled'
        self.calendar_id = kwargs.get('calendar_id', 'default')
        self.created = kwargs.get('created', datetime.now())
        self.modified = kwargs.get('modified', datetime.now())
        self.source = kwargs.get('source', 'unknown')  # 'device', 'pc', 'cloud'
        
    def to_dict(self) -> Dict:
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'all_day': self.all_day,
            'location': self.location,
            'attendees': self.attendees,
            'reminders': self.reminders,
            'recurrence': self.recurrence,
            'priority': self.priority,
            'status': self.status,
            'calendar_id': self.calendar_id,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'source': self.source
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'CalendarEvent':
        """Create event from dictionary"""
        # Parse datetime fields
        for field in ['start_time', 'end_time', 'created', 'modified']:
            if field in data and data[field]:
                try:
                    data[field] = date_parser.parse(data[field])
                except ValueError:
                    data[field] = None
                    
        return cls(**data)
        
    def get_duration(self) -> Optional[timedelta]:
        """Get duration of event"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
        
    def is_recurring(self) -> bool:
        """Check if event is recurring"""
        return bool(self.recurrence)
        
    def get_next_occurrence(self, after_date: datetime = None) -> Optional[datetime]:
        """Get next occurrence of recurring event"""
        if not self.is_recurring():
            return self.start_time
            
        if after_date is None:
            after_date = datetime.now()
            
        # Simple RRULE parsing for common patterns
        rrule = self.recurrence.get('FREQ', '').upper()
        interval = self.recurrence.get('INTERVAL', 1)
        
        if rrule == 'DAILY':
            next_date = self.start_time
            while next_date <= after_date:
                next_date += timedelta(days=interval)
            return next_date
        elif rrule == 'WEEKLY':
            next_date = self.start_time
            while next_date <= after_date:
                next_date += timedelta(weeks=interval)
            return next_date
        elif rrule == 'MONTHLY':
            next_date = self.start_date
            while next_date <= after_date:
                # Simple month increment
                if next_date.month == 12:
                    next_date = next_date.replace(year=next_date.year + 1, month=1)
                else:
                    next_date = next_date.replace(month=next_date.month + interval)
            return next_date
        elif rrule == 'YEARLY':
            next_date = self.start_time
            while next_date <= after_date:
                next_date = next_date.replace(year=next_date.year + interval)
            return next_date
            
        return self.start_time
        
    def is_conflicting_with(self, other: 'CalendarEvent') -> bool:
        """Check if this event conflicts with another"""
        if not self.start_time or not self.end_time or not other.start_time or not other.end_time:
            return False
            
        # Check for overlap
        return (self.start_time < other.end_time and self.end_time > other.start_time)
        
    def get_reminder_times(self) -> List[datetime]:
        """Get list of reminder times"""
        reminder_times = []
        if self.start_time:
            for reminder in self.reminders:
                if isinstance(reminder, dict) and 'minutes_before' in reminder:
                    reminder_time = self.start_time - timedelta(minutes=reminder['minutes_before'])
                    reminder_times.append(reminder_time)
        return reminder_times

class Calendar:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'default')
        self.name = kwargs.get('name', 'Default Calendar')
        self.color = kwargs.get('color', '#4285f4')
        self.description = kwargs.get('description', '')
        self.is_primary = kwargs.get('is_primary', False)
        self.is_visible = kwargs.get('is_visible', True)
        self.sync_enabled = kwargs.get('sync_enabled', True)
        self.created = kwargs.get('created', datetime.now())
        self.modified = kwargs.get('modified', datetime.now())
        
    def to_dict(self) -> Dict:
        """Convert calendar to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'is_primary': self.is_primary,
            'is_visible': self.is_visible,
            'sync_enabled': self.sync_enabled,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat()
        }

class CalendarSyncModule:
    def __init__(self):
        self.events: List[CalendarEvent] = []
        self.calendars: List[Calendar] = []
        self.sync_config = {
            'sync_deleted': True,
            'backup_before_sync': True,
            'resolve_conflicts': 'newer_wins',  # 'newer_wins', 'device_wins', 'pc_wins'
            'sync_recurring': True,
            'sync_reminders': True,
            'sync_attendees': True,
            'max_sync_days': 365,  # Days to look back/forward for sync
            'sync_frequency': 'manual'  # 'manual', 'hourly', 'daily'
        }
        
        self.sync_history = []
        self.conflicting_events = []
        
        # Initialize default calendar
        self._init_default_calendar()
        
    def _init_default_calendar(self):
        """Initialize default calendar"""
        default_calendar = Calendar(
            id='default',
            name='Default Calendar',
            color='#4285f4',
            is_primary=True
        )
        self.calendars.append(default_calendar)
        
    def add_event(self, event: CalendarEvent) -> bool:
        """Add a new calendar event"""
        try:
            # Validate event data
            if not self._validate_event(event):
                return False
                
            # Check for conflicts
            conflicts = self._find_conflicts(event)
            if conflicts:
                self.conflicting_events.append({
                    'new_event': event,
                    'conflicting_events': conflicts,
                    'timestamp': datetime.now()
                })
                
            # Generate ID if not provided
            if not event.id:
                event.id = self._generate_event_id()
                
            event.created = datetime.now()
            event.modified = datetime.now()
            
            self.events.append(event)
            return True
            
        except Exception as e:
            print(f"Error adding event: {e}")
            return False
            
    def update_event(self, event_id: str, updates: Dict) -> bool:
        """Update an existing event"""
        try:
            event = self._find_event_by_id(event_id)
            if not event:
                return False
                
            # Update fields
            for key, value in updates.items():
                if hasattr(event, key):
                    setattr(event, key, value)
                    
            event.modified = datetime.now()
            return True
            
        except Exception as e:
            print(f"Error updating event: {e}")
            return False
            
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        try:
            event = self._find_event_by_id(event_id)
            if event:
                self.events.remove(event)
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
            
    def _validate_event(self, event: CalendarEvent) -> bool:
        """Validate event data"""
        # Check required fields
        if not event.title:
            print("Event must have a title")
            return False
            
        if not event.start_time:
            print("Event must have a start time")
            return False
            
        # Check time logic
        if event.end_time and event.start_time >= event.end_time:
            print("End time must be after start time")
            return False
            
        # Validate reminders
        if event.reminders:
            for reminder in event.reminders:
                if isinstance(reminder, dict) and 'minutes_before' in reminder:
                    if reminder['minutes_before'] < 0:
                        print("Reminder time must be positive")
                        return False
                        
        return True
        
    def _find_conflicts(self, event: CalendarEvent) -> List[CalendarEvent]:
        """Find events that conflict with the given event"""
        conflicts = []
        for existing_event in self.events:
            if existing_event.id != event.id and event.is_conflicting_with(existing_event):
                conflicts.append(existing_event)
        return conflicts
        
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import uuid
        return str(uuid.uuid4())
        
    def _find_event_by_id(self, event_id: str) -> Optional[CalendarEvent]:
        """Find event by ID"""
        for event in self.events:
            if event.id == event_id:
                return event
        return None
        
    def search_events(self, query: str, start_date: datetime = None, end_date: datetime = None) -> List[CalendarEvent]:
        """Search events by title, description, or location within date range"""
        query = query.lower()
        results = []
        
        for event in self.events:
            # Check date range
            if start_date and event.start_time and event.start_time < start_date:
                continue
            if end_date and event.start_time and event.start_time > end_date:
                continue
                
            # Check text search
            if (query in event.title.lower() or
                query in event.description.lower() or
                query in event.location.lower()):
                results.append(event)
                
        return results
        
    def get_events_for_date(self, target_date: date) -> List[CalendarEvent]:
        """Get all events for a specific date"""
        results = []
        target_datetime = datetime.combine(target_date, datetime.min.time())
        next_day = target_datetime + timedelta(days=1)
        
        for event in self.events:
            if event.start_time and event.start_time < next_day:
                if event.end_time and event.end_time > target_datetime:
                    results.append(event)
                elif event.all_day and event.start_time.date() == target_date:
                    results.append(event)
                    
        return results
        
    def get_events_for_week(self, start_date: date) -> List[CalendarEvent]:
        """Get all events for a week starting from start_date"""
        results = []
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = start_datetime + timedelta(days=7)
        
        for event in self.events:
            if event.start_time and event.start_time < end_datetime:
                if event.end_time and event.end_time > start_datetime:
                    results.append(event)
                    
        return results
        
    def import_events_csv(self, file_path: str, source: str = 'pc') -> Dict:
        """Import events from CSV file"""
        import_results = {
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'errors_list': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Parse dates
                        start_time = None
                        end_time = None
                        
                        if row.get('Start Date') and row.get('Start Time'):
                            start_str = f"{row['Start Date']} {row['Start Time']}"
                            try:
                                start_time = date_parser.parse(start_str)
                            except ValueError:
                                start_time = None
                                
                        if row.get('End Date') and row.get('End Time'):
                            end_str = f"{row['End Date']} {row['End Time']}"
                            try:
                                end_time = date_parser.parse(end_str)
                            except ValueError:
                                end_time = None
                                
                        # Create event
                        event_data = {
                            'title': row.get('Title', ''),
                            'description': row.get('Description', ''),
                            'start_time': start_time,
                            'end_time': end_time,
                            'location': row.get('Location', ''),
                            'all_day': row.get('All Day', '').lower() == 'true',
                            'source': source
                        }
                        
                        # Clean up empty values
                        event_data = {k: v for k, v in event_data.items() if v}
                        
                        event = CalendarEvent(**event_data)
                        
                        if self.add_event(event):
                            import_results['imported'] += 1
                        else:
                            import_results['skipped'] += 1
                            
                    except Exception as e:
                        import_results['errors'] += 1
                        import_results['errors_list'].append(f"Row {row_num}: {str(e)}")
                        
        except Exception as e:
            import_results['errors'] += 1
            import_results['errors_list'].append(f"File error: {str(e)}")
            
        return import_results
        
    def export_events_csv(self, file_path: str, start_date: datetime = None, end_date: datetime = None) -> bool:
        """Export events to CSV file"""
        try:
            # Filter events by date range
            events_to_export = self.events
            if start_date or end_date:
                events_to_export = self.search_events('', start_date, end_date)
                
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['Title', 'Description', 'Start Date', 'Start Time', 
                            'End Date', 'End Time', 'Location', 'All Day', 'Status', 'Created', 'Modified']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for event in events_to_export:
                    writer.writerow({
                        'Title': event.title,
                        'Description': event.description,
                        'Start Date': event.start_time.strftime('%Y-%m-%d') if event.start_time else '',
                        'Start Time': event.start_time.strftime('%H:%M') if event.start_time and not event.all_day else '',
                        'End Date': event.end_time.strftime('%Y-%m-%d') if event.end_time else '',
                        'End Time': event.end_time.strftime('%H:%M') if event.end_time and not event.all_day else '',
                        'Location': event.location,
                        'All Day': 'True' if event.all_day else 'False',
                        'Status': event.status,
                        'Created': event.created.strftime('%Y-%m-%d %H:%M:%S'),
                        'Modified': event.modified.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
            return True
            
        except Exception as e:
            print(f"Error exporting events: {e}")
            return False
            
    def sync_with_device(self, device_events: List[CalendarEvent]) -> Dict:
        """Synchronize events with device"""
        sync_results = {
            'added': 0,
            'updated': 0,
            'deleted': 0,
            'conflicts': 0,
            'start_time': datetime.now(),
            'end_time': None
        }
        
        try:
            # Create backup if configured
            if self.sync_config['backup_before_sync']:
                self._create_backup()
                
            # Find new events on device
            for device_event in device_events:
                if not self._find_event_by_id(device_event.id):
                    device_event.source = 'device'
                    if self.add_event(device_event):
                        sync_results['added'] += 1
                        
            # Find events deleted on device
            if self.sync_config['sync_deleted']:
                device_event_ids = {e.id for e in device_events if e.id}
                for event in self.events[:]:  # Copy list to avoid modification during iteration
                    if event.source == 'device' and event.id not in device_event_ids:
                        self.events.remove(event)
                        sync_results['deleted'] += 1
                        
        except Exception as e:
            print(f"Error during calendar sync: {e}")
            
        sync_results['end_time'] = datetime.now()
        sync_results['duration'] = sync_results['end_time'] - sync_results['start_time']
        
        # Add to sync history
        self.sync_history.append(sync_results)
        
        return sync_results
        
    def _create_backup(self):
        """Create backup of current events"""
        backup_file = f"calendar_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            events_data = [event.to_dict() for event in self.events]
            calendars_data = [cal.to_dict() for cal in self.calendars]
            
            backup_data = {
                'events': events_data,
                'calendars': calendars_data,
                'backup_time': datetime.now().isoformat()
            }
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
        except Exception as e:
            print(f"Error creating backup: {e}")
            
    def get_calendar_summary(self) -> Dict:
        """Get summary of calendar data"""
        return {
            'total_events': len(self.events),
            'total_calendars': len(self.calendars),
            'events_today': len(self.get_events_for_date(date.today())),
            'events_this_week': len(self.get_events_for_week(date.today())),
            'recurring_events': len([e for e in self.events if e.is_recurring()]),
            'conflicts_found': len(self.conflicting_events),
            'last_sync': self.sync_history[-1]['end_time'] if self.sync_history else None
        }
        
    def add_calendar(self, calendar: Calendar) -> bool:
        """Add a new calendar"""
        try:
            if not calendar.id:
                calendar.id = self._generate_calendar_id()
                
            calendar.created = datetime.now()
            calendar.modified = datetime.now()
            
            self.calendars.append(calendar)
            return True
            
        except Exception as e:
            print(f"Error adding calendar: {e}")
            return False
            
    def _generate_calendar_id(self) -> str:
        """Generate unique calendar ID"""
        import uuid
        return str(uuid.uuid4())
        
    def get_events_by_calendar(self, calendar_id: str) -> List[CalendarEvent]:
        """Get events for a specific calendar"""
        return [e for e in self.events if e.calendar_id == calendar_id]
        
    def clear_events(self):
        """Clear all events"""
        self.events.clear()
        self.conflicting_events.clear()
        self.sync_history.clear()