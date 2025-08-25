#!/usr/bin/env python3
"""
Phone-PC Sync Emulator
A comprehensive application that simulates synchronization between mobile devices and computers.
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
                             QHBoxLayout, QWidget, QLabel, QPushButton, QProgressBar,
                             QTextEdit, QListWidget, QTreeWidget, QTreeWidgetItem,
                             QStatusBar, QMenuBar, QMessageBox, QFileDialog, QSplitter)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QDateTime
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor
import json
import sqlite3
from datetime import datetime, timedelta
import random

# Import our custom modules
from sync_modules.file_sync import FileSyncModule
from sync_modules.contact_sync import ContactSyncModule
from sync_modules.calendar_sync import CalendarSyncModule
from sync_modules.device_manager import DeviceManager
from sync_modules.sync_engine import SyncEngine
from utils.database import DatabaseManager
from utils.logger import Logger

class PhonePCSyncEmulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phone-PC Sync Emulator v2.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.logger = Logger()
        self.device_manager = DeviceManager()
        self.sync_engine = SyncEngine()
        
        # Initialize sync modules
        self.file_sync = FileSyncModule()
        self.contact_sync = ContactSyncModule()
        self.calendar_sync = CalendarSyncModule()
        
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.setup_timers()
        
        # Load initial data
        self.load_initial_data()
        
    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("📱 Phone-PC Sync Emulator")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        header_layout.addWidget(title_label)
        
        # Device status
        self.device_status_label = QLabel("📱 Device: Disconnected")
        self.device_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        header_layout.addWidget(self.device_status_label)
        
        # Sync button
        self.sync_button = QPushButton("🔄 Start Sync")
        self.sync_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.sync_button.clicked.connect(self.start_sync)
        header_layout.addWidget(self.sync_button)
        
        main_layout.addLayout(header_layout)
        
        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Device info and sync status
        left_panel = self.create_left_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Tabs for different sync modules
        right_panel = self.create_right_panel()
        content_splitter.addWidget(right_panel)
        
        content_splitter.setSizes([400, 1000])
        main_layout.addWidget(content_splitter)
        
    def create_left_panel(self):
        """Create the left panel with device info and sync status"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Device info section
        device_group = QWidget()
        device_layout = QVBoxLayout(device_group)
        
        device_title = QLabel("📱 Device Information")
        device_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        device_layout.addWidget(device_title)
        
        self.device_name_label = QLabel("Name: iPhone 15 Pro")
        self.device_model_label = QLabel("Model: A3102")
        self.device_os_label = QLabel("OS: iOS 17.2")
        self.device_storage_label = QLabel("Storage: 128GB (45GB free)")
        self.device_battery_label = QLabel("Battery: 87%")
        
        for label in [self.device_name_label, self.device_model_label, 
                     self.device_os_label, self.device_storage_label, 
                     self.device_battery_label]:
            label.setStyleSheet("padding: 5px; background-color: #f8f9fa; border-radius: 3px;")
            device_layout.addWidget(label)
        
        layout.addWidget(device_group)
        
        # Sync status section
        sync_group = QWidget()
        sync_layout = QVBoxLayout(sync_group)
        
        sync_title = QLabel("🔄 Sync Status")
        sync_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        sync_layout.addWidget(sync_title)
        
        self.sync_progress = QProgressBar()
        self.sync_progress.setRange(0, 100)
        self.sync_progress.setValue(0)
        sync_layout.addWidget(self.sync_progress)
        
        self.sync_status_label = QLabel("Ready to sync")
        self.sync_status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        sync_layout.addWidget(self.sync_status_label)
        
        layout.addWidget(sync_group)
        
        # Recent syncs
        recent_group = QWidget()
        recent_layout = QVBoxLayout(recent_group)
        
        recent_title = QLabel("📋 Recent Syncs")
        recent_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        recent_layout.addWidget(recent_title)
        
        self.recent_syncs_list = QListWidget()
        self.recent_syncs_list.setMaximumHeight(200)
        recent_layout.addWidget(self.recent_syncs_list)
        
        layout.addWidget(recent_group)
        
        layout.addStretch()
        return panel
        
    def create_right_panel(self):
        """Create the right panel with tabs for different sync modules"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # File sync tab
        self.tab_widget.addTab(self.create_file_sync_tab(), "📁 File Sync")
        
        # Contact sync tab
        self.tab_widget.addTab(self.create_contact_sync_tab(), "👥 Contacts")
        
        # Calendar sync tab
        self.tab_widget.addTab(self.create_calendar_sync_tab(), "📅 Calendar")
        
        # Settings tab
        self.tab_widget.addTab(self.create_settings_tab(), "⚙️ Settings")
        
        layout.addWidget(self.tab_widget)
        return panel
        
    def create_file_sync_tab(self):
        """Create the file synchronization tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # File sync controls
        controls_layout = QHBoxLayout()
        
        self.scan_files_btn = QPushButton("🔍 Scan Files")
        self.scan_files_btn.clicked.connect(self.scan_files)
        controls_layout.addWidget(self.scan_files_btn)
        
        self.sync_files_btn = QPushButton("📤 Sync Files")
        self.sync_files_btn.clicked.connect(self.sync_files)
        controls_layout.addWidget(self.sync_files_btn)
        
        self.select_folder_btn = QPushButton("📁 Select Folder")
        self.select_folder_btn.clicked.connect(self.select_sync_folder)
        controls_layout.addWidget(self.select_folder_btn)
        
        layout.addLayout(controls_layout)
        
        # File tree
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["File/Folder", "Size", "Status", "Last Modified"])
        layout.addWidget(self.file_tree)
        
        # Sync log
        log_label = QLabel("Sync Log:")
        layout.addWidget(log_label)
        
        self.file_sync_log = QTextEdit()
        self.file_sync_log.setMaximumHeight(150)
        self.file_sync_log.setReadOnly(True)
        layout.addWidget(self.file_sync_log)
        
        return tab
        
    def create_contact_sync_tab(self):
        """Create the contact synchronization tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Contact controls
        controls_layout = QHBoxLayout()
        
        self.add_contact_btn = QPushButton("➕ Add Contact")
        self.add_contact_btn.clicked.connect(self.add_contact)
        controls_layout.addWidget(self.add_contact_btn)
        
        self.import_contacts_btn = QPushButton("📥 Import Contacts")
        self.import_contacts_btn.clicked.connect(self.import_contacts)
        controls_layout.addWidget(self.import_contacts_btn)
        
        self.export_contacts_btn = QPushButton("📤 Export Contacts")
        self.export_contacts_btn.clicked.connect(self.export_contacts)
        controls_layout.addWidget(self.export_contacts_btn)
        
        layout.addLayout(controls_layout)
        
        # Contact list
        self.contact_list = QListWidget()
        layout.addWidget(self.contact_list)
        
        return tab
        
    def create_calendar_sync_tab(self):
        """Create the calendar synchronization tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Calendar controls
        controls_layout = QHBoxLayout()
        
        self.add_event_btn = QPushButton("➕ Add Event")
        self.add_event_btn.clicked.connect(self.add_calendar_event)
        controls_layout.addWidget(self.add_event_btn)
        
        self.sync_calendar_btn = QPushButton("🔄 Sync Calendar")
        self.sync_calendar_btn.clicked.connect(self.sync_calendar)
        controls_layout.addWidget(self.sync_calendar_btn)
        
        layout.addLayout(controls_layout)
        
        # Calendar view
        self.calendar_tree = QTreeWidget()
        self.calendar_tree.setHeaderLabels(["Date", "Event", "Time", "Status"])
        layout.addWidget(self.calendar_tree)
        
        return tab
        
    def create_settings_tab(self):
        """Create the settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Sync settings
        settings_label = QLabel("Sync Settings:")
        settings_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(settings_label)
        
        # Auto-sync checkbox
        self.auto_sync_checkbox = QPushButton("🔄 Auto-sync (Every 5 minutes)")
        self.auto_sync_checkbox.setCheckable(True)
        self.auto_sync_checkbox.clicked.connect(self.toggle_auto_sync)
        layout.addWidget(self.auto_sync_checkbox)
        
        # Sync options
        self.sync_photos_checkbox = QPushButton("📸 Sync Photos")
        self.sync_photos_checkbox.setCheckable(True)
        self.sync_photos_checkbox.setChecked(True)
        layout.addWidget(self.sync_photos_checkbox)
        
        self.sync_music_checkbox = QPushButton("🎵 Sync Music")
        self.sync_music_checkbox.setCheckable(True)
        self.sync_music_checkbox.setChecked(True)
        layout.addWidget(self.sync_music_checkbox)
        
        self.sync_documents_checkbox = QPushButton("📄 Sync Documents")
        self.sync_documents_checkbox.setCheckable(True)
        self.sync_documents_checkbox.setChecked(True)
        layout.addWidget(self.sync_documents_checkbox)
        
        layout.addStretch()
        return tab
        
    def setup_menu(self):
        """Setup the application menu"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_sync_action = file_menu.addAction("New Sync Session")
        new_sync_action.triggered.connect(self.new_sync_session)
        
        export_log_action = file_menu.addAction("Export Log")
        export_log_action.triggered.connect(self.export_log)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        device_manager_action = tools_menu.addAction("Device Manager")
        device_manager_action.triggered.connect(self.open_device_manager)
        
        sync_history_action = tools_menu.addAction("Sync History")
        sync_history_action.triggered.connect(self.open_sync_history)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)
        
    def setup_status_bar(self):
        """Setup the status bar"""
        self.statusBar().showMessage("Ready")
        
    def setup_timers(self):
        """Setup application timers"""
        # Update device status every 2 seconds
        self.device_timer = QTimer()
        self.device_timer.timeout.connect(self.update_device_status)
        self.device_timer.start(2000)
        
        # Auto-sync timer
        self.auto_sync_timer = QTimer()
        self.auto_sync_timer.timeout.connect(self.auto_sync)
        
    def load_initial_data(self):
        """Load initial data for the application"""
        # Load sample contacts
        self.load_sample_contacts()
        
        # Load sample calendar events
        self.load_sample_calendar_events()
        
        # Load recent syncs
        self.load_recent_syncs()
        
    def load_sample_contacts(self):
        """Load sample contacts for demonstration"""
        sample_contacts = [
            "John Doe - +1 (555) 123-4567",
            "Jane Smith - +1 (555) 987-6543",
            "Bob Johnson - +1 (555) 456-7890",
            "Alice Brown - +1 (555) 789-0123",
            "Charlie Wilson - +1 (555) 321-6540"
        ]
        
        for contact in sample_contacts:
            self.contact_list.addItem(contact)
            
    def load_sample_calendar_events(self):
        """Load sample calendar events for demonstration"""
        today = datetime.now()
        
        events = [
            (today + timedelta(days=1), "Team Meeting", "9:00 AM", "Pending"),
            (today + timedelta(days=2), "Doctor Appointment", "2:30 PM", "Pending"),
            (today + timedelta(days=3), "Project Deadline", "5:00 PM", "Pending"),
            (today + timedelta(days=5), "Weekend Trip", "10:00 AM", "Pending")
        ]
        
        for date, event, time, status in events:
            item = QTreeWidgetItem([date.strftime("%Y-%m-%d"), event, time, status])
            self.calendar_tree.addTopLevelItem(item)
            
    def load_recent_syncs(self):
        """Load recent sync history"""
        recent_syncs = [
            "2024-01-15 14:30 - Full sync completed (2.3GB)",
            "2024-01-14 09:15 - Contact sync completed (45 contacts)",
            "2024-01-13 16:45 - Calendar sync completed (12 events)",
            "2024-01-12 11:20 - File sync completed (156 files)"
        ]
        
        for sync in recent_syncs:
            self.recent_syncs_list.addItem(sync)
            
    def start_sync(self):
        """Start the synchronization process"""
        self.sync_button.setEnabled(False)
        self.sync_button.setText("🔄 Syncing...")
        self.sync_status_label.setText("Synchronizing...")
        self.sync_status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        
        # Simulate sync process
        self.sync_progress.setValue(0)
        
        # Create sync thread
        self.sync_thread = SyncThread()
        self.sync_thread.progress_update.connect(self.update_sync_progress)
        self.sync_thread.sync_complete.connect(self.sync_completed)
        self.sync_thread.start()
        
    def update_sync_progress(self, value):
        """Update sync progress bar"""
        self.sync_progress.setValue(value)
        
    def sync_completed(self, success):
        """Handle sync completion"""
        self.sync_button.setEnabled(True)
        self.sync_button.setText("🔄 Start Sync")
        
        if success:
            self.sync_status_label.setText("Sync completed successfully!")
            self.sync_status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.statusBar().showMessage("Sync completed successfully")
        else:
            self.sync_status_label.setText("Sync failed!")
            self.sync_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.statusBar().showMessage("Sync failed")
            
        # Add to recent syncs
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        sync_entry = f"{timestamp} - {'Full sync completed' if success else 'Sync failed'}"
        self.recent_syncs_list.insertItem(0, sync_entry)
        
    def update_device_status(self):
        """Update device status information"""
        # Simulate device status changes
        battery_levels = [87, 86, 85, 84, 83]
        current_battery = random.choice(battery_levels)
        
        self.device_battery_label.setText(f"Battery: {current_battery}%")
        
        # Simulate connection status
        if random.random() > 0.1:  # 90% chance of being connected
            self.device_status_label.setText("📱 Device: Connected")
            self.device_status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.device_status_label.setText("📱 Device: Disconnected")
            self.device_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            
    def scan_files(self):
        """Scan for files to sync"""
        self.file_sync_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Scanning for files...")
        
        # Simulate file scanning
        sample_files = [
            "Documents/Work/Report.pdf",
            "Photos/Vacation/IMG_001.jpg",
            "Music/Playlist/ song.mp3",
            "Videos/Movie.mp4"
        ]
        
        self.file_tree.clear()
        for file_path in sample_files:
            parts = file_path.split('/')
            parent = None
            
            for i, part in enumerate(parts):
                if i == 0:
                    # Root level
                    items = self.file_tree.findItems(part, Qt.MatchFlag.MatchExactly, 0)
                    if not items:
                        item = QTreeWidgetItem([part, "", "Folder", ""])
                        self.file_tree.addTopLevelItem(item)
                        parent = item
                    else:
                        parent = items[0]
                else:
                    # Check if child exists
                    found = False
                    for j in range(parent.childCount()):
                        if parent.child(j).text(0) == part:
                            parent = parent.child(j)
                            found = True
                            break
                    
                    if not found:
                        if i == len(parts) - 1:
                            # File
                            size = f"{random.randint(1, 100)}MB"
                            status = "Pending"
                            modified = datetime.now().strftime("%Y-%m-%d %H:%M")
                            item = QTreeWidgetItem([part, size, status, modified])
                        else:
                            # Folder
                            item = QTreeWidgetItem([part, "", "Folder", ""])
                        
                        parent.addChild(item)
                        parent = item
                        
        self.file_sync_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(sample_files)} files to sync")
        
    def sync_files(self):
        """Sync files between device and PC"""
        self.file_sync_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting file sync...")
        
        # Simulate file sync process
        total_files = self.file_tree.topLevelItemCount()
        for i in range(total_files):
            self.file_sync_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Syncing file {i+1}/{total_files}")
            
        self.file_sync_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] File sync completed")
        
    def select_sync_folder(self):
        """Select folder for synchronization"""
        folder = QFileDialog.getExistingDirectory(self, "Select Sync Folder")
        if folder:
            self.file_sync_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Selected sync folder: {folder}")
            
    def add_contact(self):
        """Add a new contact"""
        # This would typically open a dialog
        self.contact_list.addItem("New Contact - +1 (555) 000-0000")
        
    def import_contacts(self):
        """Import contacts from file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Contacts", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            self.contact_list.addItem(f"Imported contacts from {file_path}")
            
    def export_contacts(self):
        """Export contacts to file"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Contacts", "contacts.csv", "CSV Files (*.csv)")
        if file_path:
            self.statusBar().showMessage(f"Contacts exported to {file_path}")
            
    def add_calendar_event(self):
        """Add a new calendar event"""
        # This would typically open a dialog
        today = datetime.now() + timedelta(days=1)
        item = QTreeWidgetItem([today.strftime("%Y-%m-%d"), "New Event", "12:00 PM", "Pending"])
        self.calendar_tree.addTopLevelItem(item)
        
    def sync_calendar(self):
        """Sync calendar events"""
        self.statusBar().showMessage("Calendar sync completed")
        
    def toggle_auto_sync(self):
        """Toggle auto-sync functionality"""
        if self.auto_sync_checkbox.isChecked():
            self.auto_sync_timer.start(300000)  # 5 minutes
            self.statusBar().showMessage("Auto-sync enabled")
        else:
            self.auto_sync_timer.stop()
            self.statusBar().showMessage("Auto-sync disabled")
            
    def auto_sync(self):
        """Perform automatic synchronization"""
        self.statusBar().showMessage("Auto-sync in progress...")
        # This would trigger the actual sync process
        
    def new_sync_session(self):
        """Start a new sync session"""
        self.sync_progress.setValue(0)
        self.sync_status_label.setText("Ready to sync")
        self.sync_status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        self.statusBar().showMessage("New sync session started")
        
    def export_log(self):
        """Export sync log to file"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Log", "sync_log.txt", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.file_sync_log.toPlainText())
            self.statusBar().showMessage(f"Log exported to {file_path}")
            
    def open_device_manager(self):
        """Open device manager dialog"""
        QMessageBox.information(self, "Device Manager", "Device Manager functionality would be implemented here.")
        
    def open_sync_history(self):
        """Open sync history dialog"""
        QMessageBox.information(self, "Sync History", "Sync History functionality would be implemented here.")
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Phone-PC Sync Emulator", 
                         "Phone-PC Sync Emulator v2.0\n\n"
                         "A comprehensive application that simulates synchronization "
                         "between mobile devices and computers.\n\n"
                         "Features include:\n"
                         "• File synchronization\n"
                         "• Contact management\n"
                         "• Calendar synchronization\n"
                         "• Device status monitoring\n"
                         "• Sync history and logging")

class SyncThread(QThread):
    """Thread for handling synchronization process"""
    progress_update = pyqtSignal(int)
    sync_complete = pyqtSignal(bool)
    
    def run(self):
        """Run the sync process"""
        try:
            # Simulate sync process with progress updates
            for i in range(101):
                self.progress_update.emit(i)
                self.msleep(50)  # 50ms delay between updates
                
            self.sync_complete.emit(True)
        except Exception as e:
            print(f"Sync error: {e}")
            self.sync_complete.emit(False)

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = PhonePCSyncEmulator()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()