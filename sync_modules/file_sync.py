"""
File Synchronization Module
Handles file synchronization between phone and PC
"""

import os
import shutil
import hashlib
import json
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem, QProgressBar,
                             QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem,
                             QSplitter, QGroupBox, QTextEdit, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon

class FileSyncModule(QWidget):
    def __init__(self):
        super().__init__()
        self.sync_running = False
        self.sync_thread = None
        self.file_database = {}
        self.sync_history = []
        
        self.setup_ui()
        self.load_file_database()
        
    def setup_ui(self):
        """Setup the file sync user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("File Synchronization")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        self.sync_btn = QPushButton("🔄 Sync Files")
        self.sync_btn.clicked.connect(self.start_file_sync)
        header_layout.addWidget(self.sync_btn)
        
        self.add_folder_btn = QPushButton("📁 Add Folder")
        self.add_folder_btn.clicked.connect(self.add_sync_folder)
        header_layout.addWidget(self.add_folder_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Sync folders and status
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Sync folders group
        folders_group = QGroupBox("Sync Folders")
        folders_layout = QVBoxLayout(folders_group)
        
        self.folders_list = QListWidget()
        self.folders_list.itemClicked.connect(self.on_folder_selected)
        folders_layout.addWidget(self.folders_list)
        
        folders_btn_layout = QHBoxLayout()
        self.add_folder_btn2 = QPushButton("Add")
        self.add_folder_btn2.clicked.connect(self.add_sync_folder)
        self.remove_folder_btn = QPushButton("Remove")
        self.remove_folder_btn.clicked.connect(self.remove_sync_folder)
        
        folders_btn_layout.addWidget(self.add_folder_btn2)
        folders_btn_layout.addWidget(self.remove_folder_btn)
        folders_layout.addLayout(folders_btn_layout)
        
        left_layout.addWidget(folders_group)
        
        # Sync status group
        status_group = QGroupBox("Sync Status")
        status_layout = QVBoxLayout(status_group)
        
        self.sync_progress = QProgressBar()
        status_layout.addWidget(self.sync_progress)
        
        self.status_label = QLabel("Ready to sync")
        status_layout.addWidget(self.status_label)
        
        left_layout.addWidget(status_group)
        
        splitter.addWidget(left_panel)
        
        # Right panel - File tree and details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # File tree group
        tree_group = QGroupBox("File Structure")
        tree_layout = QVBoxLayout(tree_group)
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["File/Folder", "Size", "Status", "Last Modified"])
        self.file_tree.itemClicked.connect(self.on_file_selected)
        tree_layout.addWidget(self.file_tree)
        
        right_layout.addWidget(tree_group)
        
        # File details group
        details_group = QGroupBox("File Details")
        details_layout = QVBoxLayout(details_group)
        
        self.file_details = QTextEdit()
        self.file_details.setMaximumHeight(150)
        self.file_details.setReadOnly(True)
        details_layout.addWidget(self.file_details)
        
        right_layout.addWidget(details_group)
        
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([300, 600])
        layout.addWidget(splitter)
        
        # Bottom panel - Sync options and history
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)
        
        # Sync options
        options_group = QGroupBox("Sync Options")
        options_layout = QVBoxLayout(options_group)
        
        self.sync_mode_combo = QComboBox()
        self.sync_mode_combo.addItems(["Bidirectional", "Phone to PC", "PC to Phone", "Manual"])
        options_layout.addWidget(QLabel("Sync Mode:"))
        options_layout.addWidget(self.sync_mode_combo)
        
        self.auto_sync_checkbox = QPushButton("🔄 Auto-sync")
        self.auto_sync_checkbox.setCheckable(True)
        self.auto_sync_checkbox.clicked.connect(self.toggle_auto_sync)
        options_layout.addWidget(self.auto_sync_checkbox)
        
        bottom_layout.addWidget(options_group)
        
        # Sync history
        history_group = QGroupBox("Sync History")
        history_layout = QVBoxLayout(history_group)
        
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(100)
        history_layout.addWidget(self.history_list)
        
        bottom_layout.addWidget(history_group)
        
        layout.addWidget(bottom_panel)
        
        # Initialize with sample data
        self.initialize_sample_data()
        
    def initialize_sample_data(self):
        """Initialize with sample sync folders and files"""
        sample_folders = [
            "Documents",
            "Pictures", 
            "Music",
            "Downloads"
        ]
        
        for folder in sample_folders:
            item = QListWidgetItem(f"📁 {folder}")
            item.setData(Qt.ItemDataRole.UserRole, folder)
            self.folders_list.addItem(item)
            
        # Add sample files to tree
        self.populate_file_tree()
        
    def populate_file_tree(self):
        """Populate the file tree with sample data"""
        self.file_tree.clear()
        
        # Sample file structure
        sample_files = {
            "Documents": [
                ("report.pdf", "2.5 MB", "Synced", "2024-01-15"),
                ("presentation.pptx", "15.2 MB", "Pending", "2024-01-14"),
                ("notes.txt", "1.2 KB", "Synced", "2024-01-13")
            ],
            "Pictures": [
                ("vacation.jpg", "3.8 MB", "Synced", "2024-01-15"),
                ("family.png", "2.1 MB", "Synced", "2024-01-14"),
                ("screenshot.png", "856 KB", "Pending", "2024-01-13")
            ],
            "Music": [
                ("song1.mp3", "4.2 MB", "Synced", "2024-01-15"),
                ("song2.mp3", "3.9 MB", "Synced", "2024-01-14"),
                ("playlist.m3u", "2.1 KB", "Synced", "2024-01-13")
            ]
        }
        
        for folder, files in sample_files.items():
            folder_item = QTreeWidgetItem([folder, "", "", ""])
            folder_item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_DirIcon))
            
            for filename, size, status, modified in files:
                file_item = QTreeWidgetItem([filename, size, status, modified])
                file_item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
                folder_item.addChild(file_item)
                
            self.file_tree.addTopLevelItem(folder_item)
            
        self.file_tree.expandAll()
        
    def add_sync_folder(self):
        """Add a new folder to sync"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Sync")
        if folder_path:
            folder_name = os.path.basename(folder_path)
            item = QListWidgetItem(f"📁 {folder_name}")
            item.setData(Qt.ItemDataRole.UserRole, folder_path)
            self.folders_list.addItem(item)
            
            # Add to database
            self.file_database[folder_path] = {
                "path": folder_path,
                "name": folder_name,
                "last_sync": None,
                "files": []
            }
            
            self.save_file_database()
            
    def remove_sync_folder(self):
        """Remove a folder from sync"""
        current_item = self.folders_list.currentItem()
        if current_item:
            folder_path = current_item.data(Qt.ItemDataRole.UserRole)
            if folder_path in self.file_database:
                del self.file_database[folder_path]
                self.save_file_database()
                
            self.folders_list.takeItem(self.folders_list.row(current_item))
            
    def on_folder_selected(self, item):
        """Handle folder selection"""
        folder_path = item.data(Qt.ItemDataRole.UserRole)
        self.status_label.setText(f"Selected folder: {folder_path}")
        
    def on_file_selected(self, item, column):
        """Handle file selection in tree"""
        if item.parent():  # It's a file
            filename = item.text(0)
            size = item.text(1)
            status = item.text(2)
            modified = item.text(3)
            
            details = f"""File: {filename}
Size: {size}
Status: {status}
Last Modified: {modified}
Path: /Documents/{filename}

This file is currently {status.lower()} with the device.
Last synchronization attempt was on {modified}."""
            
            self.file_details.setText(details)
            
    def start_file_sync(self):
        """Start the file synchronization process"""
        if self.sync_running:
            return
            
        self.sync_running = True
        self.sync_btn.setText("⏹️ Stop Sync")
        self.sync_btn.clicked.disconnect()
        self.sync_btn.clicked.connect(self.stop_file_sync)
        
        # Start sync thread
        self.sync_thread = FileSyncThread(self.file_database)
        self.sync_thread.progress_updated.connect(self.update_sync_progress)
        self.sync_thread.sync_completed.connect(self.on_sync_completed)
        self.sync_thread.start()
        
    def stop_file_sync(self):
        """Stop the file synchronization process"""
        if self.sync_thread and self.sync_thread.isRunning():
            self.sync_thread.terminate()
            self.sync_thread.wait()
            
        self.sync_running = False
        self.sync_btn.setText("🔄 Sync Files")
        self.sync_btn.clicked.disconnect()
        self.sync_btn.clicked.connect(self.start_file_sync)
        
        self.status_label.setText("Sync stopped")
        self.sync_progress.setValue(0)
        
    def update_sync_progress(self, value, status):
        """Update sync progress bar and status"""
        self.sync_progress.setValue(value)
        self.status_label.setText(status)
        
    def on_sync_completed(self, success, message):
        """Handle sync completion"""
        self.sync_running = False
        self.sync_btn.setText("🔄 Sync Files")
        self.sync_btn.clicked.disconnect()
        self.sync_btn.clicked.connect(self.start_file_sync)
        
        if success:
            self.status_label.setText("Sync completed successfully")
            self.sync_progress.setValue(100)
            QMessageBox.information(self, "Sync Complete", message)
        else:
            self.status_label.setText("Sync failed")
            self.sync_progress.setValue(0)
            QMessageBox.warning(self, "Sync Failed", message)
            
        # Add to history
        self.add_sync_history(success, message)
        
    def toggle_auto_sync(self):
        """Toggle auto-sync functionality"""
        if self.auto_sync_checkbox.isChecked():
            self.auto_sync_checkbox.setText("🔄 Auto-sync: ON")
            # Start auto-sync timer
            self.auto_sync_timer = QTimer()
            self.auto_sync_timer.timeout.connect(self.auto_sync)
            self.auto_sync_timer.start(300000)  # 5 minutes
        else:
            self.auto_sync_checkbox.setText("🔄 Auto-sync")
            if hasattr(self, 'auto_sync_timer'):
                self.auto_sync_timer.stop()
                
    def auto_sync(self):
        """Perform automatic synchronization"""
        if not self.sync_running:
            self.start_file_sync()
            
    def add_sync_history(self, success, message):
        """Add entry to sync history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "✅ Success" if success else "❌ Failed"
        entry = f"{timestamp} - {status}: {message}"
        
        item = QListWidgetItem(entry)
        self.history_list.insertItem(0, item)
        
        # Keep only last 50 entries
        while self.history_list.count() > 50:
            self.history_list.takeItem(self.history_list.count() - 1)
            
    def load_file_database(self):
        """Load file database from storage"""
        try:
            if os.path.exists("file_database.json"):
                with open("file_database.json", "r") as f:
                    self.file_database = json.load(f)
        except Exception as e:
            print(f"Error loading file database: {e}")
            self.file_database = {}
            
    def save_file_database(self):
        """Save file database to storage"""
        try:
            with open("file_database.json", "w") as f:
                json.dump(self.file_database, f, indent=2)
        except Exception as e:
            print(f"Error saving file database: {e}")


class FileSyncThread(QThread):
    """Thread for handling file synchronization"""
    progress_updated = pyqtSignal(int, str)
    sync_completed = pyqtSignal(bool, str)
    
    def __init__(self, file_database):
        super().__init__()
        self.file_database = file_database
        self.running = True
        
    def run(self):
        """Main sync thread execution"""
        try:
            total_files = sum(len(folder_data.get("files", [])) for folder_data in self.file_database.values())
            processed_files = 0
            
            for folder_path, folder_data in self.file_database.items():
                if not self.running:
                    break
                    
                self.progress_updated.emit(
                    int((processed_files / total_files) * 100) if total_files > 0 else 0,
                    f"Syncing folder: {folder_data['name']}"
                )
                
                # Simulate file processing
                for i in range(5):
                    if not self.running:
                        break
                    self.msleep(200)  # Simulate work
                    processed_files += 1
                    
                    progress = int((processed_files / total_files) * 100) if total_files > 0 else 0
                    self.progress_updated.emit(progress, f"Processing files... ({processed_files}/{total_files})")
                    
            if self.running:
                self.sync_completed.emit(True, f"Successfully synced {processed_files} files")
            else:
                self.sync_completed.emit(False, "Sync was interrupted")
                
        except Exception as e:
            self.sync_completed.emit(False, f"Sync error: {str(e)}")
            
    def stop(self):
        """Stop the sync thread"""
        self.running = False