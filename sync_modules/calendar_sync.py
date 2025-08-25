"""
Calendar Synchronization Module
Handles calendar event synchronization between phone and PC.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid

from base_sync import BaseSyncModule

@dataclass
class CalendarEvent:
    """Calendar event data structure"""
    id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str
    attendees: List[str]
    reminder_minutes: int
    is_all_day: bool
    recurrence_rule: str
    priority: str
    status: str
    created_date: datetime
    modified_date: datetime
    source: str  # 'phone' or 'pc'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        data['created_date'] = self.created_date.isoformat()
        data['modified_date'] = self.modified_date.isoformat()
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalendarEvent':
        """Create event from dictionary"""
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        data['end_time'] = datetime.fromisoformat(data['end_time'])
        data['created_date'] = datetime.fromisoformat(data['created_date'])
        data['modified_date'] = datetime.fromisoformat(data['modified_date'])
        return cls(**data)

class CalendarSyncModule(BaseSyncModule):
    """Calendar synchronization module"""
    
    def __init__(self):
        super().__init__("calendar_sync")
        self.phone_events = {}
        self.pc_events = {}
        self.sync_events = {}
        self.event_id_counter = 1
        self.sync_strategy = "merge_all"
        
        # Load sample calendar events
        self._load_sample_events()
        
    def sync_data_type(self) -> str:
        return "calendar_events"
        
    def _load_sample_events(self):
        """Load sample calendar events for demonstration"""
        now = datetime.now()
        
        # Sample phone events
        self.phone_events = {
            "1": CalendarEvent(
                id="1",
                title="Team Meeting",
                description="Weekly team sync meeting",
                start_time=now.replace(hour=9, minute=0, second=0, microsecond=0),
                end_time=now.replace(hour=10, minute=0, second=0, microsecond=0),
                location="Conference Room A",
                attendees=["john.doe@email.com", "jane.smith@email.com"],
                reminder_minutes=15,
                is_all_day=False,
                recurrence_rule="FREQ=WEEKLY;BYDAY=MO",
                priority="high",
                status="confirmed",
                created_date=now - timedelta(days=7),
                modified_date=now - timedelta(days=1),
                source="phone"
            ),
            "2": CalendarEvent(
                id="2",
                title="Lunch with Client",
                description="Business lunch meeting",
                start_time=now.replace(hour=12, minute=30, second=0, microsecond=0),
                end_time=now.replace(hour=13, minute=30, second=0, microsecond=0),
                location="Downtown Restaurant",
                attendees=["client@company.com"],
                reminder_minutes=30,
                is_all_day=False,
                recurrence_rule="",
                priority="medium",
                status="confirmed",
                created_date=now - timedelta(days=3),
                modified_date=now - timedelta(days=2),
                source="phone"
            )
        }
        
        # Sample PC events
        self.pc_events = {
            "3": CalendarEvent(
                id="3",
                title="Project Deadline",
                description="Submit final project deliverables",
                start_time=now.replace(hour=17, minute=0, second=0, microsecond=0),
                end_time=now.replace(hour=18, minute=0, second=0, microsecond=0),
                location="Office",
                attendees=[],
                reminder_minutes=60,
                is_all_day=False,
                recurrence_rule="",
                priority="high",
                status="confirmed",
                created_date=now - timedelta(days=5),
                modified_date=now - timedelta(days=1),
                source="pc"
            ),
            "4": CalendarEvent(
                id="4",
                title="Doctor Appointment",
                description="Annual checkup",
                start_time=now.replace(hour=14, minute=0, second=0, microsecond=0),
                end_time=now.replace(hour=15, minute=0, second=0, microsecond=0),
                location="Medical Center",
                attendees=[],
                reminder_minutes=60,
                is_all_day=False,
                recurrence_rule="",
                priority="medium",
                status="confirmed",
                created_date=now - timedelta(days=10),
                modified_date=now - timedelta(days=5),
                source="pc"
            )
        }
        
        # Initialize sync events
        self._merge_events()
        
    def _merge_events(self):
        """Merge phone and PC events into sync events"""
        self.sync_events = {}
        
        # Add phone events
        for event_id, event in self.phone_events.items():
            sync_event = CalendarEvent(
                id=event_id,
                title=event.title,
                description=event.description,
                start_time=event.start_time,
                end_time=event.end_time,
                location=event.location,
                attendees=event.attendees.copy(),
                reminder_minutes=event.reminder_minutes,
                is_all_day=event.is_all_day,
                recurrence_rule=event.recurrence_rule,
                priority=event.priority,
                status=event.status,
                created_date=event.created_date,
                modified_date=event.modified_date,
                source="phone"
            )
            self.sync_events[event_id] = sync_event
            
        # Add PC events (check for duplicates)
        for event_id, event in self.pc_events.items():
            # Check if event already exists (by title, time, and location)
            existing_event = self._find_matching_event(event)
            
            if existing_event:
                # Merge with existing event
                self._merge_event_data(existing_event, event)
            else:
                # Add as new event
                sync_event = CalendarEvent(
                    id=event_id,
                    title=event.title,
                    description=event.description,
                    start_time=event.start_time,
                    end_time=event.end_time,
                    location=event.location,
                    attendees=event.attendees.copy(),
                    reminder_minutes=event.reminder_minutes,
                    is_all_day=event.is_all_day,
                    recurrence_rule=event.recurrence_rule,
                    priority=event.priority,
                    status=event.status,
                    created_date=event.created_date,
                    modified_date=event.modified_date,
                    source="pc"
                )
                self.sync_events[event_id] = sync_event
                
    def _find_matching_event(self, event: CalendarEvent) -> Optional[CalendarEvent]:
        """Find matching event in sync events"""
        for sync_event in self.sync_events.values():
            # Check by title and time (within 30 minutes)
            if (sync_event.title.lower() == event.title.lower() and
                abs((sync_event.start_time - event.start_time).total_seconds()) < 1800):
                return sync_event
                
            # Check by location and time
            if (sync_event.location.lower() == event.location.lower() and
                abs((sync_event.start_time - event.start_time).total_seconds()) < 1800):
                return sync_event
                
        return None
        
    def _merge_event_data(self, existing: CalendarEvent, new: CalendarEvent):
        """Merge new event data with existing event"""
        # Merge attendees
        for attendee in new.attendees:
            if attendee not in existing.attendees:
                existing.attendees.append(attendee)
                
        # Update other fields if new data is more recent
        if new.modified_date > existing.modified_date:
            if new.description:
                existing.description = new.description
            if new.location:
                existing.location = new.location
            if new.reminder_minutes:
                existing.reminder_minutes = new.reminder_minutes
            if new.priority:
                existing.priority = new.priority
            if new.status:
                existing.status = new.status
                
        existing.modified_date = datetime.now()
        existing.source = "merged"
        
    def get_sync_items(self) -> List[Dict[str, Any]]:
        """Get list of events that need synchronization"""
        sync_items = []
        
        # Check for new events in phone
        for event_id, event in self.phone_events.items():
            if event_id not in self.sync_events:
                sync_items.append({
                    'action': 'add_event',
                    'event': event,
                    'source': 'phone'
                })
                
        # Check for new events in PC
        for event_id, event in self.pc_events.items():
            if event_id not in self.sync_events:
                sync_items.append({
                    'action': 'add_event',
                    'event': event,
                    'source': 'pc'
                })
                
        # Check for updated events
        for event_id in set(self.phone_events.keys()) & set(self.pc_events.keys()):
            phone_event = self.phone_events[event_id]
            pc_event = self.pc_events[event_id]
            
            if phone_event.modified_date != pc_event.modified_date:
                sync_items.append({
                    'action': 'update_event',
                    'event_id': event_id,
                    'phone_event': phone_event,
                    'pc_event': pc_event
                })
                
        return sync_items
        
    def perform_sync(self, items: List[Dict[str, Any]]) -> bool:
        """Perform calendar synchronization"""
        try:
            for item in items:
                if item['action'] == 'add_event':
                    self._add_event_to_sync(item['event'])
                elif item['action'] == 'update_event':
                    self._update_event_in_sync(item)
                    
            # Update sync events
            self._merge_events()
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Calendar sync failed: {str(e)}")
            return False
            
    def _add_event_to_sync(self, event: CalendarEvent):
        """Add event to sync events"""
        event_id = str(self.event_id_counter)
        self.event_id_counter += 1
        
        sync_event = CalendarEvent(
            id=event_id,
            title=event.title,
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
            attendees=event.attendees.copy(),
            reminder_minutes=event.reminder_minutes,
            is_all_day=event.is_all_day,
            recurrence_rule=event.recurrence_rule,
            priority=event.priority,
            status=event.status,
            created_date=event.created_date,
            modified_date=datetime.now(),
            source=event.source
        )
        
        self.sync_events[event_id] = sync_event
        self.sync_activity.emit(self.name, f"Added event: {event.title}")
        
    def _update_event_in_sync(self, item: Dict[str, Any]):
        """Update event in sync events"""
        event_id = item['event_id']
        phone_event = item['phone_event']
        pc_event = item['pc_event']
        
        if event_id in self.sync_events:
            sync_event = self.sync_events[event_id]
            
            # Merge the updated data
            self._merge_event_data(sync_event, phone_event)
            self._merge_event_data(sync_event, pc_event)
            
            self.sync_activity.emit(self.name, f"Updated event: {sync_event.title}")
            
    def add_event(self, event_data: Dict[str, Any], source: str = "sync") -> str:
        """Add a new calendar event"""
        try:
            event_id = str(self.event_id_counter)
            self.event_id_counter += 1
            
            event = CalendarEvent(
                id=event_id,
                title=event_data.get('title', ''),
                description=event_data.get('description', ''),
                start_time=event_data.get('start_time', datetime.now()),
                end_time=event_data.get('end_time', datetime.now() + timedelta(hours=1)),
                location=event_data.get('location', ''),
                attendees=event_data.get('attendees', []),
                reminder_minutes=event_data.get('reminder_minutes', 15),
                is_all_day=event_data.get('is_all_day', False),
                recurrence_rule=event_data.get('recurrence_rule', ''),
                priority=event_data.get('priority', 'medium'),
                status=event_data.get('status', 'confirmed'),
                created_date=datetime.now(),
                modified_date=datetime.now(),
                source=source
            )
            
            if source == "phone":
                self.phone_events[event_id] = event
            elif source == "pc":
                self.pc_events[event_id] = event
            else:
                self.sync_events[event_id] = event
                
            self.sync_activity.emit(self.name, f"Added new event: {event.title}")
            return event_id
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to add event: {str(e)}")
            return ""
            
    def update_event(self, event_id: str, event_data: Dict[str, Any]) -> bool:
        """Update an existing calendar event"""
        try:
            if event_id in self.sync_events:
                event = self.sync_events[event_id]
                
                # Update fields
                for field, value in event_data.items():
                    if hasattr(event, field) and field not in ['id', 'created_date']:
                        setattr(event, field, value)
                        
                event.modified_date = datetime.now()
                
                self.sync_activity.emit(self.name, f"Updated event: {event.title}")
                return True
                
            return False
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to update event: {str(e)}")
            return False
            
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        try:
            # Remove from all event collections
            for event_dict in [self.phone_events, self.pc_events, self.sync_events]:
                if event_id in event_dict:
                    event = event_dict[event_id]
                    self.sync_activity.emit(self.name, f"Deleted event: {event.title}")
                    del event_dict[event_id]
                    
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to delete event: {str(e)}")
            return False
            
    def search_events(self, query: str) -> List[CalendarEvent]:
        """Search events by title, description, or location"""
        results = []
        query_lower = query.lower()
        
        for event in self.sync_events.values():
            # Search by title
            if query_lower in event.title.lower():
                results.append(event)
                continue
                
            # Search by description
            if query_lower in event.description.lower():
                results.append(event)
                continue
                
            # Search by location
            if query_lower in event.location.lower():
                results.append(event)
                continue
                
        return results
        
    def get_events_by_date_range(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """Get events within a date range"""
        results = []
        
        for event in self.sync_events.values():
            # Check if event overlaps with date range
            if (event.start_time <= end_date and event.end_time >= start_date):
                results.append(event)
                
        # Sort by start time
        results.sort(key=lambda x: x.start_time)
        return results
        
    def get_upcoming_events(self, days: int = 7) -> List[CalendarEvent]:
        """Get upcoming events within specified days"""
        now = datetime.now()
        end_date = now + timedelta(days=days)
        
        return self.get_events_by_date_range(now, end_date)
        
    def get_event_stats(self) -> Dict[str, Any]:
        """Get calendar synchronization statistics"""
        now = datetime.now()
        upcoming_events = self.get_upcoming_events(7)
        
        return {
            'total_events': len(self.sync_events),
            'phone_events': len(self.phone_events),
            'pc_events': len(self.pc_events),
            'merged_events': len([e for e in self.sync_events.values() if e.source == "merged"]),
            'upcoming_events': len(upcoming_events),
            'last_sync': self.last_sync_time
        }
        
    def export_events(self, file_path: str, format_type: str = "json") -> bool:
        """Export calendar events to file"""
        try:
            if format_type == "json":
                data = {
                    'events': [event.to_dict() for event in self.sync_events.values()],
                    'export_time': datetime.now().isoformat()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                    
            elif format_type == "ics":
                # Export as iCalendar format
                ics_content = self._generate_ics_content()
                with open(file_path, 'w') as f:
                    f.write(ics_content)
                    
            self.sync_activity.emit(self.name, f"Exported events to {file_path}")
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to export events: {str(e)}")
            return False
            
    def _generate_ics_content(self) -> str:
        """Generate iCalendar content"""
        ics_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Phone-PC Sync Emulator//Calendar Sync//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH"
        ]
        
        for event in self.sync_events.values():
            ics_lines.extend([
                "BEGIN:VEVENT",
                f"UID:{event.id}",
                f"DTSTART:{event.start_time.strftime('%Y%m%dT%H%M%S')}",
                f"DTEND:{event.end_time.strftime('%Y%m%dT%H%M%S')}",
                f"SUMMARY:{event.title}",
                f"DESCRIPTION:{event.description}",
                f"LOCATION:{event.location}",
                f"STATUS:{event.status.upper()}",
                f"PRIORITY:{event.priority.upper()}",
                "END:VEVENT"
            ])
            
        ics_lines.append("END:VCALENDAR")
        return "\r\n".join(ics_lines)
        
    def import_events(self, file_path: str, format_type: str = "json") -> bool:
        """Import calendar events from file"""
        try:
            if format_type == "json":
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                for event_data in data.get('events', []):
                    event = CalendarEvent.from_dict(event_data)
                    self.sync_events[event.id] = event
                    
            elif format_type == "ics":
                # Import from iCalendar format
                self._import_from_ics(file_path)
                
            self.sync_activity.emit(self.name, f"Imported events from {file_path}")
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to import events: {str(e)}")
            return False
            
    def _import_from_ics(self, file_path: str):
        """Import events from iCalendar file"""
        # Basic ICS parsing (simplified)
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Parse events (simplified implementation)
        # In a real implementation, you would use a proper ICS parser
        pass