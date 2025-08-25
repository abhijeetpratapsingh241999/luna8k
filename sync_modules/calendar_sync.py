"""
Calendar Synchronization Module
Handles calendar and event synchronization between phone and PC
"""

import json
import sqlite3
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QLineEdit,
                             QMessageBox, QDialog, QFormLayout, QTextEdit, QComboBox,
                             QGroupBox, QSplitter, QHeaderView, QProgressBar, QCalendarWidget,
                             QDateEdit, QTimeEdit, QCheckBox, QSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QDate, QTime
from PyQt6.QtGui import QFont, QIcon
import os

class CalendarSyncModule(QWidget):
    def __init__(self):
        super().__init__()
        self.events = []
        self.sync_running = False
        self.sync_thread = None
        
        self.setup_ui()
        self.load_events()
        
    def setup_ui(self):
        """Setup the calendar sync user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Calendar Synchronization")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        self.sync_btn = QPushButton("🔄 Sync Calendar")
        self.sync_btn.clicked.connect(self.start_calendar_sync)
        header_layout.addWidget(self.sync_btn)
        
        self.add_event_btn = QPushButton("➕ Add Event")
        self.add_event_btn.clicked.connect(self.add_event)
        header_layout.addWidget(self.add_event_btn)
        
        self.import_btn = QPushButton("📥 Import")
        self.import_btn.clicked.connect(self.import_calendar)
        header_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_calendar)
        header_layout.addWidget(self.export_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Calendar widget and event list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Calendar widget
        calendar_group = QGroupBox("Calendar")
        calendar_layout = QVBoxLayout(calendar_group)
        
        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.clicked.connect(self.on_date_selected)
        calendar_layout.addWidget(self.calendar_widget)
        
        left_layout.addWidget(calendar_group)
        
        # Events for selected date
        events_group = QGroupBox("Events for Selected Date")
        events_layout = QVBoxLayout(events_group)
        
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(5)
        self.events_table.setHorizontalHeaderLabels([
            "Time", "Title", "Duration", "Status", "Last Sync"
        ])
        
        # Set column widths
        header = self.events_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.events_table.itemClicked.connect(self.on_event_selected)
        self.events_table.itemDoubleClicked.connect(self.edit_event)
        events_layout.addWidget(self.events_table)
        
        # Event actions
        actions_layout = QHBoxLayout()
        self.edit_event_btn = QPushButton("✏️ Edit")
        self.edit_event_btn.clicked.connect(self.edit_selected_event)
        self.delete_event_btn = QPushButton("🗑️ Delete")
        self.delete_event_btn.clicked.connect(self.delete_selected_event)
        
        actions_layout.addWidget(self.edit_event_btn)
        actions_layout.addWidget(self.delete_event_btn)
        actions_layout.addStretch()
        
        events_layout.addLayout(actions_layout)
        left_layout.addWidget(events_group)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Event details and sync status
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Event details group
        details_group = QGroupBox("Event Details")
        details_layout = QVBoxLayout(details_group)
        
        self.event_details = QTextEdit()
        self.event_details.setReadOnly(True)
        self.event_details.setMaximumHeight(200)
        details_layout.addWidget(self.event_details)
        
        right_layout.addWidget(details_group)
        
        # Sync status group
        status_group = QGroupBox("Sync Status")
        status_layout = QVBoxLayout(status_group)
        
        self.sync_progress = QProgressBar()
        status_layout.addWidget(self.sync_progress)
        
        self.status_label = QLabel("Ready to sync")
        status_layout.addWidget(self.status_label)
        
        # Sync options
        options_layout = QHBoxLayout()
        
        self.sync_mode_combo = QComboBox()
        self.sync_mode_combo.addItems(["Merge", "Phone to PC", "PC to Phone", "Replace All"])
        options_layout.addWidget(QLabel("Sync Mode:"))
        options_layout.addWidget(self.sync_mode_combo)
        
        status_layout.addLayout(options_layout)
        
        right_layout.addWidget(status_group)
        
        # Calendar statistics
        stats_group = QGroupBox("Calendar Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.total_events_label = QLabel("Total Events: 0")
        self.synced_events_label = QLabel("Synced: 0")
        self.pending_events_label = QLabel("Pending: 0")
        self.conflict_events_label = QLabel("Conflicts: 0")
        self.today_events_label = QLabel("Today's Events: 0")
        
        stats_layout.addWidget(self.total_events_label)
        stats_layout.addWidget(self.synced_events_label)
        stats_layout.addWidget(self.pending_events_label)
        stats_layout.addWidget(self.conflict_events_label)
        stats_layout.addWidget(self.today_events_label)
        
        right_layout.addWidget(stats_group)
        
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([500, 500])
        layout.addWidget(splitter)
        
        # Initialize with sample data
        self.initialize_sample_events()
        
        # Set current date
        self.on_date_selected(self.calendar_widget.selectedDate())
        
    def initialize_sample_events(self):
        """Initialize with sample event data"""
        today = datetime.now()
        sample_events = [
            {
                "id": 1,
                "title": "Team Meeting",
                "description": "Weekly team standup meeting",
                "date": today.strftime("%Y-%m-%d"),
                "start_time": "09:00",
                "end_time": "10:00",
                "duration": "1 hour",
                "location": "Conference Room A",
                "status": "Synced",
                "last_sync": today.strftime("%Y-%m-%d %H:%M:%S"),
                "reminder": "15 minutes before",
                "recurring": "Weekly"
            },
            {
                "id": 2,
                "title": "Client Presentation",
                "description": "Present quarterly results to client",
                "date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                "start_time": "14:00",
                "end_time": "15:30",
                "duration": "1.5 hours",
                "location": "Client Office",
                "status": "Pending",
                "last_sync": "Never",
                "reminder": "30 minutes before",
                "recurring": "None"
            },
            {
                "id": 3,
                "title": "Project Deadline",
                "description": "Submit final project deliverables",
                "date": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
                "start_time": "17:00",
                "end_time": "17:00",
                "duration": "All day",
                "location": "Office",
                "status": "Synced",
                "last_sync": (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "reminder": "1 day before",
                "recurring": "None"
            },
            {
                "id": 4,
                "title": "Lunch with Colleague",
                "description": "Team lunch at local restaurant",
                "date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
                "start_time": "12:00",
                "end_time": "13:00",
                "duration": "1 hour",
                "location": "Local Restaurant",
                "status": "Synced",
                "last_sync": today.strftime("%Y-%m-%d %H:%M:%S"),
                "reminder": "No reminder",
                "recurring": "None"
            },
            {
                "id": 5,
                "title": "Training Session",
                "description": "New software training for team",
                "date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
                "start_time": "10:00",
                "end_time": "16:00",
                "duration": "6 hours",
                "location": "Training Room",
                "status": "Conflict",
                "last_sync": (today - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                "reminder": "1 hour before",
                "recurring": "None"
            }
        ]
        
        for event in sample_events:
            self.events.append(event)
            
        self.update_statistics()
        
    def on_date_selected(self, date):
        """Handle date selection in calendar"""
        selected_date = date.toString("yyyy-MM-dd")
        self.filter_events_by_date(selected_date)
        
    def filter_events_by_date(self, date_str):
        """Filter events for the selected date"""
        filtered_events = [event for event in self.events if event["date"] == date_str]
        self.update_events_table(filtered_events)
        
        # Update today's events count
        today = datetime.now().strftime("%Y-%m-%d")
        today_events = [event for event in self.events if event["date"] == today]
        self.today_events_label.setText(f"Today's Events: {len(today_events)}")
        
    def update_events_table(self, events_list):
        """Update the events table with filtered events"""
        self.events_table.setRowCount(len(events_list))
        
        for row, event in enumerate(events_list):
            self.events_table.setItem(row, 0, QTableWidgetItem(event["start_time"]))
            self.events_table.setItem(row, 1, QTableWidgetItem(event["title"]))
            self.events_table.setItem(row, 2, QTableWidgetItem(event["duration"]))
            
            # Status with color coding
            status_item = QTableWidgetItem(event["status"])
            if event["status"] == "Synced":
                status_item.setBackground(Qt.GlobalColor.green)
            elif event["status"] == "Pending":
                status_item.setBackground(Qt.GlobalColor.yellow)
            elif event["status"] == "Conflict":
                status_item.setBackground(Qt.GlobalColor.red)
            self.events_table.setItem(row, 3, status_item)
            
            self.events_table.setItem(row, 4, QTableWidgetItem(event["last_sync"]))
            
    def on_event_selected(self, item):
        """Handle event selection"""
        row = item.row()
        if row < self.events_table.rowCount():
            event_title = self.events_table.item(row, 1).text()
            event = next((e for e in self.events if e["title"] == event_title), None)
            if event:
                self.display_event_details(event)
                
    def display_event_details(self, event):
        """Display event details in the details panel"""
        details = f"""Title: {event['title']}
Date: {event['date']}
Time: {event['start_time']} - {event['end_time']}
Duration: {event['duration']}
Location: {event['location']}
Status: {event['status']}
Last Sync: {event['last_sync']}
Reminder: {event['reminder']}
Recurring: {event['recurring']}

Description: {event['description']}"""
        
        self.event_details.setText(details)
        
    def add_event(self):
        """Add a new event"""
        dialog = EventDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            event_data = dialog.get_event_data()
            event_data["id"] = max([e["id"] for e in self.events], default=0) + 1
            event_data["status"] = "Pending"
            event_data["last_sync"] = "Never"
            
            self.events.append(event_data)
            self.update_statistics()
            
            # Refresh current date view
            current_date = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")
            self.filter_events_by_date(current_date)
            
    def edit_event(self):
        """Edit the selected event"""
        current_row = self.events_table.currentRow()
        if current_row >= 0 and current_row < self.events_table.rowCount():
            event_title = self.events_table.item(current_row, 1).text()
            event = next((e for e in self.events if e["title"] == event_title), None)
            if event:
                dialog = EventDialog(self, event)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    updated_event = dialog.get_event_data()
                    updated_event["id"] = event["id"]
                    updated_event["status"] = event["status"]
                    updated_event["last_sync"] = event["last_sync"]
                    
                    # Update event in list
                    event_index = next((i for i, e in enumerate(self.events) if e["id"] == event["id"]), -1)
                    if event_index >= 0:
                        self.events[event_index] = updated_event
                        
                    # Refresh views
                    current_date = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")
                    self.filter_events_by_date(current_date)
                    self.display_event_details(updated_event)
                    
    def edit_selected_event(self):
        """Edit the currently selected event"""
        self.edit_event()
        
    def delete_selected_event(self):
        """Delete the selected event"""
        current_row = self.events_table.currentRow()
        if current_row >= 0 and current_row < self.events_table.rowCount():
            event_title = self.events_table.item(current_row, 1).text()
            event = next((e for e in self.events if e["title"] == event_title), None)
            
            if event:
                reply = QMessageBox.question(self, "Delete Event", 
                                           f"Are you sure you want to delete '{event_title}'?",
                                           QMessageBox.StandardButton.Yes | 
                                           QMessageBox.StandardButton.No)
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Remove event from list
                    self.events = [e for e in self.events if e["id"] != event["id"]]
                    self.update_statistics()
                    
                    # Refresh views
                    current_date = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")
                    self.filter_events_by_date(current_date)
                    self.event_details.clear()
                    
    def start_calendar_sync(self):
        """Start calendar synchronization"""
        if self.sync_running:
            return
            
        self.sync_running = True
        self.sync_btn.setText("⏹️ Stop Sync")
        self.sync_btn.clicked.disconnect()
        self.sync_btn.clicked.connect(self.stop_calendar_sync)
        
        # Start sync thread
        self.sync_thread = CalendarSyncThread(self.events, self.sync_mode_combo.currentText())
        self.sync_thread.progress_updated.connect(self.update_sync_progress)
        self.sync_thread.sync_completed.connect(self.on_sync_completed)
        self.sync_thread.start()
        
    def stop_calendar_sync(self):
        """Stop calendar synchronization"""
        if self.sync_thread and self.sync_thread.isRunning():
            self.sync_thread.terminate()
            self.sync_thread.wait()
            
        self.sync_running = False
        self.sync_btn.setText("🔄 Sync Calendar")
        self.sync_btn.clicked.disconnect()
        self.sync_btn.clicked.connect(self.start_calendar_sync)
        
        self.status_label.setText("Sync stopped")
        self.sync_progress.setValue(0)
        
    def update_sync_progress(self, value, status):
        """Update sync progress and status"""
        self.sync_progress.setValue(value)
        self.status_label.setText(status)
        
    def on_sync_completed(self, success, message, updated_events):
        """Handle sync completion"""
        self.sync_running = False
        self.sync_btn.setText("🔄 Sync Calendar")
        self.sync_btn.clicked.disconnect()
        self.sync_btn.clicked.connect(self.start_calendar_sync)
        
        if success:
            self.events = updated_events
            self.update_statistics()
            
            # Refresh current view
            current_date = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")
            self.filter_events_by_date(current_date)
            
            self.status_label.setText("Sync completed successfully")
            self.sync_progress.setValue(100)
            QMessageBox.information(self, "Sync Complete", message)
        else:
            self.status_label.setText("Sync failed")
            self.sync_progress.setValue(0)
            QMessageBox.warning(self, "Sync Failed", message)
            
    def update_statistics(self):
        """Update calendar statistics"""
        total = len(self.events)
        synced = sum(1 for e in self.events if e["status"] == "Synced")
        pending = sum(1 for e in self.events if e["status"] == "Pending")
        conflicts = sum(1 for e in self.events if e["status"] == "Conflict")
        
        self.total_events_label.setText(f"Total Events: {total}")
        self.synced_events_label.setText(f"Synced: {synced}")
        self.pending_events_label.setText(f"Pending: {pending}")
        self.conflict_events_label.setText(f"Conflicts: {conflicts}")
        
    def import_calendar(self):
        """Import calendar from file"""
        QMessageBox.information(self, "Import", "Calendar import functionality would be implemented here")
        
    def export_calendar(self):
        """Export calendar to file"""
        QMessageBox.information(self, "Export", "Calendar export functionality would be implemented here")
        
    def load_events(self):
        """Load events from storage"""
        try:
            if os.path.exists("calendar_events.json"):
                with open("calendar_events.json", "r") as f:
                    self.events = json.load(f)
        except Exception as e:
            print(f"Error loading events: {e}")
            self.events = []
            
    def save_events(self):
        """Save events to storage"""
        try:
            with open("calendar_events.json", "w") as f:
                json.dump(self.events, f, indent=2)
        except Exception as e:
            print(f"Error saving events: {e}")


class EventDialog(QDialog):
    """Dialog for adding/editing events"""
    def __init__(self, parent=None, event=None):
        super().__init__(parent)
        self.event = event
        self.setup_ui()
        
        if event:
            self.setWindowTitle("Edit Event")
            self.populate_fields(event)
        else:
            self.setWindowTitle("Add New Event")
            
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setModal(True)
        self.setFixedSize(450, 400)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.start_time_input = QTimeEdit()
        self.start_time_input.setTime(QTime(9, 0))
        self.end_time_input = QTimeEdit()
        self.end_time_input.setTime(QTime(10, 0))
        self.location_input = QLineEdit()
        self.reminder_input = QComboBox()
        self.reminder_input.addItems(["No reminder", "5 minutes before", "15 minutes before", "30 minutes before", "1 hour before", "1 day before"])
        self.recurring_input = QComboBox()
        self.recurring_input.addItems(["None", "Daily", "Weekly", "Monthly", "Yearly"])
        
        form_layout.addRow("Title:", self.title_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Date:", self.date_input)
        form_layout.addRow("Start Time:", self.start_time_input)
        form_layout.addRow("End Time:", self.end_time_input)
        form_layout.addRow("Location:", self.location_input)
        form_layout.addRow("Reminder:", self.reminder_input)
        form_layout.addRow("Recurring:", self.recurring_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
    def populate_fields(self, event):
        """Populate form fields with event data"""
        self.title_input.setText(event.get("title", ""))
        self.description_input.setText(event.get("description", ""))
        
        # Parse date and time
        try:
            event_date = QDate.fromString(event.get("date", ""), "yyyy-MM-dd")
            if event_date.isValid():
                self.date_input.setDate(event_date)
        except:
            pass
            
        try:
            start_time = QTime.fromString(event.get("start_time", ""), "HH:mm")
            if start_time.isValid():
                self.start_time_input.setTime(start_time)
        except:
            pass
            
        try:
            end_time = QTime.fromString(event.get("end_time", ""), "HH:mm")
            if end_time.isValid():
                self.end_time_input.setTime(end_time)
        except:
            pass
            
        self.location_input.setText(event.get("location", ""))
        
        reminder_text = event.get("reminder", "No reminder")
        index = self.reminder_input.findText(reminder_text)
        if index >= 0:
            self.reminder_input.setCurrentIndex(index)
            
        recurring_text = event.get("recurring", "None")
        index = self.recurring_input.findText(recurring_text)
        if index >= 0:
            self.recurring_input.setCurrentIndex(index)
            
    def get_event_data(self):
        """Get event data from form fields"""
        start_time = self.start_time_input.time()
        end_time = self.end_time_input.time()
        
        # Calculate duration
        start_minutes = start_time.hour() * 60 + start_time.minute()
        end_minutes = end_time.hour() * 60 + end_time.minute()
        duration_minutes = end_minutes - start_minutes
        
        if duration_minutes <= 0:
            duration_minutes = 24 * 60 + duration_minutes  # Handle overnight events
            
        if duration_minutes >= 24 * 60:
            duration = "All day"
        elif duration_minutes >= 60:
            hours = duration_minutes // 60
            minutes = duration_minutes % 60
            duration = f"{hours} hour{'s' if hours > 1 else ''}"
            if minutes > 0:
                duration += f" {minutes} minute{'s' if minutes > 1 else ''}"
        else:
            duration = f"{duration_minutes} minute{'s' if duration_minutes > 1 else ''}"
            
        return {
            "title": self.title_input.text(),
            "description": self.description_input.toPlainText(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "start_time": self.start_time_input.time().toString("HH:mm"),
            "end_time": self.end_time_input.time().toString("HH:mm"),
            "duration": duration,
            "location": self.location_input.text(),
            "reminder": self.reminder_input.currentText(),
            "recurring": self.recurring_input.currentText()
        }


class CalendarSyncThread(QThread):
    """Thread for handling calendar synchronization"""
    progress_updated = pyqtSignal(int, str)
    sync_completed = pyqtSignal(bool, str, list)
    
    def __init__(self, events, sync_mode):
        super().__init__()
        self.events = events
        self.sync_mode = sync_mode
        self.running = True
        
    def run(self):
        """Main sync thread execution"""
        try:
            total_events = len(self.events)
            processed = 0
            
            # Simulate sync process
            for i, event in enumerate(self.events):
                if not self.running:
                    break
                    
                # Update progress
                progress = int((i / total_events) * 100) if total_events > 0 else 0
                self.progress_updated.emit(progress, f"Syncing event: {event['title']}")
                
                # Simulate sync work
                self.msleep(400)
                
                # Update event status
                if event["status"] == "Pending":
                    event["status"] = "Synced"
                    event["last_sync"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                processed += 1
                
            if self.running:
                self.sync_completed.emit(True, f"Successfully synced {processed} events", self.events)
            else:
                self.sync_completed.emit(False, "Sync was interrupted", self.events)
                
        except Exception as e:
            self.sync_completed.emit(False, f"Sync error: {str(e)}", self.events)
            
    def stop(self):
        """Stop the sync thread"""
        self.running = False