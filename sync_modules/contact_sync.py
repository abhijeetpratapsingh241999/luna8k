"""
Contact Synchronization Module
Handles contact synchronization between phone and PC
"""

import json
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QLineEdit,
                             QMessageBox, QDialog, QFormLayout, QTextEdit, QComboBox,
                             QGroupBox, QSplitter, QHeaderView, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon
import os

class ContactSyncModule(QWidget):
    def __init__(self):
        super().__init__()
        self.contacts = []
        self.sync_running = False
        self.sync_thread = None
        
        self.setup_ui()
        self.load_contacts()
        
    def setup_ui(self):
        """Setup the contact sync user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Contact Synchronization")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        self.sync_btn = QPushButton("🔄 Sync Contacts")
        self.sync_btn.clicked.connect(self.start_contact_sync)
        header_layout.addWidget(self.sync_btn)
        
        self.add_contact_btn = QPushButton("➕ Add Contact")
        self.add_contact_btn.clicked.connect(self.add_contact)
        header_layout.addWidget(self.add_contact_btn)
        
        self.import_btn = QPushButton("📥 Import")
        self.import_btn.clicked.connect(self.import_contacts)
        header_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_contacts)
        header_layout.addWidget(self.export_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Contact list and search
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Search group
        search_group = QGroupBox("Search Contacts")
        search_layout = QVBoxLayout(search_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, phone, or email...")
        self.search_input.textChanged.connect(self.filter_contacts)
        search_layout.addWidget(self.search_input)
        
        left_layout.addWidget(search_group)
        
        # Contacts table
        contacts_group = QGroupBox("Contacts")
        contacts_layout = QVBoxLayout(contacts_group)
        
        self.contacts_table = QTableWidget()
        self.contacts_table.setColumnCount(6)
        self.contacts_table.setHorizontalHeaderLabels([
            "Name", "Phone", "Email", "Company", "Last Sync", "Status"
        ])
        
        # Set column widths
        header = self.contacts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.contacts_table.itemClicked.connect(self.on_contact_selected)
        self.contacts_table.itemDoubleClicked.connect(self.edit_contact)
        contacts_layout.addWidget(self.contacts_table)
        
        # Contact actions
        actions_layout = QHBoxLayout()
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.clicked.connect(self.edit_selected_contact)
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self.delete_selected_contact)
        
        actions_layout.addWidget(self.edit_btn)
        actions_layout.addWidget(self.delete_btn)
        actions_layout.addStretch()
        
        contacts_layout.addLayout(actions_layout)
        left_layout.addWidget(contacts_group)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Contact details and sync status
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Contact details group
        details_group = QGroupBox("Contact Details")
        details_layout = QVBoxLayout(details_group)
        
        self.contact_details = QTextEdit()
        self.contact_details.setReadOnly(True)
        self.contact_details.setMaximumHeight(200)
        details_layout.addWidget(self.contact_details)
        
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
        
        # Sync statistics
        stats_group = QGroupBox("Sync Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.total_contacts_label = QLabel("Total Contacts: 0")
        self.synced_contacts_label = QLabel("Synced: 0")
        self.pending_contacts_label = QLabel("Pending: 0")
        self.conflict_contacts_label = QLabel("Conflicts: 0")
        
        stats_layout.addWidget(self.total_contacts_label)
        stats_layout.addWidget(self.synced_contacts_label)
        stats_layout.addWidget(self.pending_contacts_label)
        stats_layout.addWidget(self.conflict_contacts_label)
        
        right_layout.addWidget(stats_group)
        
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([600, 400])
        layout.addWidget(splitter)
        
        # Initialize with sample data
        self.initialize_sample_contacts()
        
    def initialize_sample_contacts(self):
        """Initialize with sample contact data"""
        sample_contacts = [
            {
                "name": "John Doe",
                "phone": "+1-555-0123",
                "email": "john.doe@email.com",
                "company": "Tech Corp",
                "last_sync": "2024-01-15 10:30:00",
                "status": "Synced",
                "notes": "Software Engineer, prefers email communication"
            },
            {
                "name": "Jane Smith",
                "phone": "+1-555-0456",
                "email": "jane.smith@email.com",
                "company": "Design Studio",
                "last_sync": "2024-01-14 15:45:00",
                "status": "Synced",
                "notes": "Graphic Designer, works remotely"
            },
            {
                "name": "Mike Johnson",
                "phone": "+1-555-0789",
                "email": "mike.j@email.com",
                "company": "Marketing Inc",
                "last_sync": "2024-01-13 09:15:00",
                "status": "Pending",
                "notes": "Marketing Manager, prefers phone calls"
            },
            {
                "name": "Sarah Wilson",
                "phone": "+1-555-0321",
                "email": "sarah.w@email.com",
                "company": "Consulting Group",
                "last_sync": "2024-01-12 14:20:00",
                "status": "Synced",
                "notes": "Business Consultant, available weekdays only"
            },
            {
                "name": "David Brown",
                "phone": "+1-555-0654",
                "email": "david.brown@email.com",
                "company": "Startup XYZ",
                "last_sync": "2024-01-11 11:00:00",
                "status": "Conflict",
                "notes": "CEO, very busy schedule"
            }
        ]
        
        for contact in sample_contacts:
            self.contacts.append(contact)
            
        self.update_contacts_table()
        self.update_statistics()
        
    def update_contacts_table(self):
        """Update the contacts table with current data"""
        self.contacts_table.setRowCount(len(self.contacts))
        
        for row, contact in enumerate(self.contacts):
            self.contacts_table.setItem(row, 0, QTableWidgetItem(contact["name"]))
            self.contacts_table.setItem(row, 1, QTableWidgetItem(contact["phone"]))
            self.contacts_table.setItem(row, 2, QTableWidgetItem(contact["email"]))
            self.contacts_table.setItem(row, 3, QTableWidgetItem(contact["company"]))
            self.contacts_table.setItem(row, 4, QTableWidgetItem(contact["last_sync"]))
            
            # Status with color coding
            status_item = QTableWidgetItem(contact["status"])
            if contact["status"] == "Synced":
                status_item.setBackground(Qt.GlobalColor.green)
            elif contact["status"] == "Pending":
                status_item.setBackground(Qt.GlobalColor.yellow)
            elif contact["status"] == "Conflict":
                status_item.setBackground(Qt.GlobalColor.red)
            self.contacts_table.setItem(row, 5, status_item)
            
    def filter_contacts(self):
        """Filter contacts based on search input"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.contacts_table.rowCount()):
            name = self.contacts_table.item(row, 0).text().lower()
            phone = self.contacts_table.item(row, 1).text().lower()
            email = self.contacts_table.item(row, 2).text().lower()
            
            if (search_text in name or search_text in phone or search_text in email):
                self.contacts_table.setRowHidden(row, False)
            else:
                self.contacts_table.setRowHidden(row, True)
                
    def on_contact_selected(self, item):
        """Handle contact selection"""
        row = item.row()
        if row < len(self.contacts):
            contact = self.contacts[row]
            self.display_contact_details(contact)
            
    def display_contact_details(self, contact):
        """Display contact details in the details panel"""
        details = f"""Name: {contact['name']}
Phone: {contact['phone']}
Email: {contact['email']}
Company: {contact['company']}
Last Sync: {contact['last_sync']}
Status: {contact['status']}

Notes: {contact['notes']}"""
        
        self.contact_details.setText(details)
        
    def add_contact(self):
        """Add a new contact"""
        dialog = ContactDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            contact_data = dialog.get_contact_data()
            contact_data["last_sync"] = "Never"
            contact_data["status"] = "Pending"
            
            self.contacts.append(contact_data)
            self.update_contacts_table()
            self.update_statistics()
            
    def edit_contact(self):
        """Edit the selected contact"""
        current_row = self.contacts_table.currentRow()
        if current_row >= 0 and current_row < len(self.contacts):
            contact = self.contacts[current_row]
            dialog = ContactDialog(self, contact)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_contact = dialog.get_contact_data()
                updated_contact["last_sync"] = contact["last_sync"]
                updated_contact["status"] = contact["status"]
                updated_contact["notes"] = contact["notes"]
                
                self.contacts[current_row] = updated_contact
                self.update_contacts_table()
                self.display_contact_details(updated_contact)
                
    def edit_selected_contact(self):
        """Edit the currently selected contact"""
        self.edit_contact()
        
    def delete_selected_contact(self):
        """Delete the selected contact"""
        current_row = self.contacts_table.currentRow()
        if current_row >= 0 and current_row < len(self.contacts):
            contact_name = self.contacts[current_row]["name"]
            reply = QMessageBox.question(self, "Delete Contact", 
                                       f"Are you sure you want to delete {contact_name}?",
                                       QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                del self.contacts[current_row]
                self.update_contacts_table()
                self.update_statistics()
                self.contact_details.clear()
                
    def start_contact_sync(self):
        """Start contact synchronization"""
        if self.sync_running:
            return
            
        self.sync_running = True
        self.sync_btn.setText("⏹️ Stop Sync")
        self.sync_btn.clicked.disconnect()
        self.sync_btn.clicked.connect(self.stop_contact_sync)
        
        # Start sync thread
        self.sync_thread = ContactSyncThread(self.contacts, self.sync_mode_combo.currentText())
        self.sync_thread.progress_updated.connect(self.update_sync_progress)
        self.sync_thread.sync_completed.connect(self.on_sync_completed)
        self.sync_thread.start()
        
    def stop_contact_sync(self):
        """Stop contact synchronization"""
        if self.sync_thread and self.sync_thread.isRunning():
            self.sync_thread.terminate()
            self.sync_thread.wait()
            
        self.sync_running = False
        self.sync_btn.setText("🔄 Sync Contacts")
        self.sync_btn.clicked.disconnect()
        self.sync_btn.clicked.connect(self.start_contact_sync)
        
        self.status_label.setText("Sync stopped")
        self.sync_progress.setValue(0)
        
    def update_sync_progress(self, value, status):
        """Update sync progress and status"""
        self.sync_progress.setValue(value)
        self.status_label.setText(status)
        
    def on_sync_completed(self, success, message, updated_contacts):
        """Handle sync completion"""
        self.sync_running = False
        self.sync_btn.setText("🔄 Sync Contacts")
        self.sync_btn.clicked.disconnect()
        self.sync_btn.clicked.connect(self.start_contact_sync)
        
        if success:
            self.contacts = updated_contacts
            self.update_contacts_table()
            self.update_statistics()
            self.status_label.setText("Sync completed successfully")
            self.sync_progress.setValue(100)
            QMessageBox.information(self, "Sync Complete", message)
        else:
            self.status_label.setText("Sync failed")
            self.sync_progress.setValue(0)
            QMessageBox.warning(self, "Sync Failed", message)
            
    def update_statistics(self):
        """Update sync statistics"""
        total = len(self.contacts)
        synced = sum(1 for c in self.contacts if c["status"] == "Synced")
        pending = sum(1 for c in self.contacts if c["status"] == "Pending")
        conflicts = sum(1 for c in self.contacts if c["status"] == "Conflict")
        
        self.total_contacts_label.setText(f"Total Contacts: {total}")
        self.synced_contacts_label.setText(f"Synced: {synced}")
        self.pending_contacts_label.setText(f"Pending: {pending}")
        self.conflict_contacts_label.setText(f"Conflicts: {conflicts}")
        
    def import_contacts(self):
        """Import contacts from file"""
        # Implementation for contact import
        QMessageBox.information(self, "Import", "Contact import functionality would be implemented here")
        
    def export_contacts(self):
        """Export contacts to file"""
        # Implementation for contact export
        QMessageBox.information(self, "Export", "Contact export functionality would be implemented here")
        
    def load_contacts(self):
        """Load contacts from storage"""
        try:
            if os.path.exists("contacts.json"):
                with open("contacts.json", "r") as f:
                    self.contacts = json.load(f)
        except Exception as e:
            print(f"Error loading contacts: {e}")
            self.contacts = []
            
    def save_contacts(self):
        """Save contacts to storage"""
        try:
            with open("contacts.json", "w") as f:
                json.dump(self.contacts, f, indent=2)
        except Exception as e:
            print(f"Error saving contacts: {e}")


class ContactDialog(QDialog):
    """Dialog for adding/editing contacts"""
    def __init__(self, parent=None, contact=None):
        super().__init__(parent)
        self.contact = contact
        self.setup_ui()
        
        if contact:
            self.setWindowTitle("Edit Contact")
            self.populate_fields(contact)
        else:
            self.setWindowTitle("Add New Contact")
            
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.company_input = QLineEdit()
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Company:", self.company_input)
        form_layout.addRow("Notes:", self.notes_input)
        
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
        
    def populate_fields(self, contact):
        """Populate form fields with contact data"""
        self.name_input.setText(contact.get("name", ""))
        self.phone_input.setText(contact.get("phone", ""))
        self.email_input.setText(contact.get("email", ""))
        self.company_input.setText(contact.get("company", ""))
        self.notes_input.setText(contact.get("notes", ""))
        
    def get_contact_data(self):
        """Get contact data from form fields"""
        return {
            "name": self.name_input.text(),
            "phone": self.phone_input.text(),
            "email": self.email_input.text(),
            "company": self.company_input.text(),
            "notes": self.notes_input.toPlainText()
        }


class ContactSyncThread(QThread):
    """Thread for handling contact synchronization"""
    progress_updated = pyqtSignal(int, str)
    sync_completed = pyqtSignal(bool, str, list)
    
    def __init__(self, contacts, sync_mode):
        super().__init__()
        self.contacts = contacts
        self.sync_mode = sync_mode
        self.running = True
        
    def run(self):
        """Main sync thread execution"""
        try:
            total_contacts = len(self.contacts)
            processed = 0
            
            # Simulate sync process
            for i, contact in enumerate(self.contacts):
                if not self.running:
                    break
                    
                # Update progress
                progress = int((i / total_contacts) * 100) if total_contacts > 0 else 0
                self.progress_updated.emit(progress, f"Syncing contact: {contact['name']}")
                
                # Simulate sync work
                self.msleep(300)
                
                # Update contact status
                if contact["status"] == "Pending":
                    contact["status"] = "Synced"
                    contact["last_sync"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                processed += 1
                
            if self.running:
                self.sync_completed.emit(True, f"Successfully synced {processed} contacts", self.contacts)
            else:
                self.sync_completed.emit(False, "Sync was interrupted", self.contacts)
                
        except Exception as e:
            self.sync_completed.emit(False, f"Sync error: {str(e)}", self.contacts)
            
    def stop(self):
        """Stop the sync thread"""
        self.running = False