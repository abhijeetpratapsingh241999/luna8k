#!/usr/bin/env python3
"""
Phone-PC Sync Emulator
A comprehensive emulator for simulating synchronization between mobile devices and computers.
"""

import sys
import os
import json
import logging
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QPushButton, QLabel, 
                             QProgressBar, QTextEdit, QListWidget, QTreeWidget,
                             QTreeWidgetItem, QSplitter, QFrame, QGroupBox,
                             QGridLayout, QCheckBox, QComboBox, QSpinBox,
                             QLineEdit, QMessageBox, QFileDialog, QStatusBar)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap

from sync_modules.file_sync import FileSyncModule
from sync_modules.contact_sync import ContactSyncModule
from sync_modules.calendar_sync import CalendarSyncModule
from sync_modules.media_sync import MediaSyncModule
from sync_modules.settings_manager import SettingsManager
from sync_modules.logger import SyncLogger

class SyncEmulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.logger = SyncLogger()
        self.sync_modules = {}
        self.sync_threads = {}
        self.init_ui()
        self.setup_sync_modules()
        self.setup_timers()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Phone-PC Sync Emulator v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #3c3c3c;
            }
            QTabBar::tab {
                background-color: #4a4a4a;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
        }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Sync modules
        left_panel = self.create_left_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Main content
        right_panel = self.create_right_panel()
        content_splitter.addWidget(right_panel)
        
        content_splitter.setSizes([400, 1000])
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Phone-PC Sync Emulator Started")
        
    def create_header(self):
        """Create the application header"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_frame.setStyleSheet("background-color: #1e1e1e; border: none;")
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("📱 Phone-PC Sync Emulator")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #0078d4; padding: 10px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Connection status
        self.connection_status = QLabel("🔴 Disconnected")
        self.connection_status.setStyleSheet("color: #ff4444; font-weight: bold; padding: 10px;")
        header_layout.addWidget(self.connection_status)
        
        # Sync status
        self.global_sync_status = QLabel("⏸️ Sync Paused")
        self.global_sync_status.setStyleSheet("color: #ffaa00; font-weight: bold; padding: 10px;")
        header_layout.addWidget(self.global_sync_status)
        
        return header_frame
        
    def create_left_panel(self):
        """Create the left panel with sync modules"""
        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        left_frame.setStyleSheet("background-color: #3c3c3c; border: 1px solid #555555;")
        
        left_layout = QVBoxLayout(left_frame)
        
        # Sync modules group
        modules_group = QGroupBox("Sync Modules")
        modules_layout = QVBoxLayout(modules_group)
        
        # File sync module
        self.file_sync_btn = QPushButton("📁 File Sync")
        self.file_sync_btn.setCheckable(True)
        self.file_sync_btn.clicked.connect(lambda: self.toggle_module('file_sync'))
        modules_layout.addWidget(self.file_sync_btn)
        
        # Contact sync module
        self.contact_sync_btn = QPushButton("👥 Contact Sync")
        self.contact_sync_btn.setCheckable(True)
        self.contact_sync_btn.clicked.connect(lambda: self.toggle_module('contact_sync'))
        modules_layout.addWidget(self.contact_sync_btn)
        
        # Calendar sync module
        self.calendar_sync_btn = QPushButton("📅 Calendar Sync")
        self.calendar_sync_btn.setCheckable(True)
        self.calendar_sync_btn.clicked.connect(lambda: self.toggle_module('calendar_sync'))
        modules_layout.addWidget(self.calendar_sync_btn)
        
        # Media sync module
        self.media_sync_btn = QPushButton("🎵 Media Sync")
        self.media_sync_btn.setCheckable(True)
        self.media_sync_btn.clicked.connect(lambda: self.toggle_module('media_sync'))
        modules_layout.addWidget(self.media_sync_btn)
        
        left_layout.addWidget(modules_group)
        
        # Global controls
        controls_group = QGroupBox("Global Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        self.start_all_btn = QPushButton("▶️ Start All Sync")
        self.start_all_btn.clicked.connect(self.start_all_sync)
        controls_layout.addWidget(self.start_all_btn)
        
        self.stop_all_btn = QPushButton("⏹️ Stop All Sync")
        self.stop_all_btn.clicked.connect(self.stop_all_sync)
        controls_layout.addWidget(self.stop_all_btn)
        
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self.show_settings)
        controls_layout.addWidget(self.settings_btn)
        
        left_layout.addWidget(controls_group)
        
        # Quick stats
        stats_group = QGroupBox("Quick Stats")
        stats_layout = QGridLayout(stats_group)
        
        stats_layout.addWidget(QLabel("Active Modules:"), 0, 0)
        self.active_modules_label = QLabel("0")
        self.active_modules_label.setStyleSheet("color: #00ff00; font-weight: bold;")
        stats_layout.addWidget(self.active_modules_label, 0, 1)
        
        stats_layout.addWidget(QLabel("Total Files:"), 1, 0)
        self.total_files_label = QLabel("0")
        stats_layout.addWidget(self.total_files_label, 1, 1)
        
        stats_layout.addWidget(QLabel("Sync Progress:"), 2, 0)
        self.global_progress = QProgressBar()
        self.global_progress.setRange(0, 100)
        stats_layout.addWidget(self.global_progress, 2, 1)
        
        left_layout.addWidget(stats_group)
        
        left_layout.addStretch()
        
        return left_frame
        
    def create_right_panel(self):
        """Create the right panel with main content"""
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        right_frame.setStyleSheet("background-color: #3c3c3c; border: 1px solid #555555;")
        
        right_layout = QVBoxLayout(right_frame)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Sync status tab
        self.sync_status_tab = self.create_sync_status_tab()
        self.tab_widget.addTab(self.sync_status_tab, "📊 Sync Status")
        
        # File browser tab
        self.file_browser_tab = self.create_file_browser_tab()
        self.tab_widget.addTab(self.file_browser_tab, "📁 File Browser")
        
        # Logs tab
        self.logs_tab = self.create_logs_tab()
        self.tab_widget.addTab(self.logs_tab, "📝 Logs")
        
        # Settings tab
        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
        
        right_layout.addWidget(self.tab_widget)
        
        return right_frame
        
    def create_sync_status_tab(self):
        """Create the sync status tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Module status grid
        status_group = QGroupBox("Module Status")
        status_layout = QGridLayout(status_group)
        
        # File sync status
        status_layout.addWidget(QLabel("File Sync:"), 0, 0)
        self.file_sync_status = QLabel("⏸️ Paused")
        self.file_sync_status.setStyleSheet("color: #ffaa00; font-weight: bold;")
        status_layout.addWidget(self.file_sync_status, 0, 1)
        
        self.file_sync_progress = QProgressBar()
        status_layout.addWidget(self.file_sync_progress, 0, 2)
        
        # Contact sync status
        status_layout.addWidget(QLabel("Contact Sync:"), 1, 0)
        self.contact_sync_status = QLabel("⏸️ Paused")
        self.contact_sync_status.setStyleSheet("color: #ffaa00; font-weight: bold;")
        status_layout.addWidget(self.contact_sync_status, 1, 1)
        
        self.contact_sync_progress = QProgressBar()
        status_layout.addWidget(self.contact_sync_progress, 1, 2)
        
        # Calendar sync status
        status_layout.addWidget(QLabel("Calendar Sync:"), 2, 0)
        self.calendar_sync_status = QLabel("⏸️ Paused")
        self.calendar_sync_status.setStyleSheet("color: #ffaa00; font-weight: bold;")
        status_layout.addWidget(self.calendar_sync_status, 2, 1)
        
        self.calendar_sync_progress = QProgressBar()
        status_layout.addWidget(self.calendar_sync_progress, 2, 2)
        
        # Media sync status
        status_layout.addWidget(QLabel("Media Sync:"), 3, 0)
        self.media_sync_status = QLabel("⏸️ Paused")
        self.media_sync_status.setStyleSheet("color: #ffaa00; font-weight: bold;")
        status_layout.addWidget(self.media_sync_status, 3, 1)
        
        self.media_sync_progress = QProgressBar()
        status_layout.addWidget(self.media_sync_progress, 3, 2)
        
        layout.addWidget(status_group)
        
        # Recent sync activity
        activity_group = QGroupBox("Recent Sync Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_list = QListWidget()
        self.activity_list.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
        activity_layout.addWidget(self.activity_list)
        
        layout.addWidget(activity_group)
        
        return tab
        
    def create_file_browser_tab(self):
        """Create the file browser tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # File browser controls
        controls_layout = QHBoxLayout()
        
        self.refresh_files_btn = QPushButton("🔄 Refresh")
        self.refresh_files_btn.clicked.connect(self.refresh_file_browser)
        controls_layout.addWidget(self.refresh_files_btn)
        
        self.add_file_btn = QPushButton("➕ Add File")
        self.add_file_btn.clicked.connect(self.add_file)
        controls_layout.addWidget(self.add_file_btn)
        
        self.sync_selected_btn = QPushButton("📱 Sync Selected")
        self.sync_selected_btn.clicked.connect(self.sync_selected_files)
        controls_layout.addWidget(self.sync_selected_btn)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # File tree
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["File Name", "Size", "Type", "Status", "Last Modified"])
        self.file_tree.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
        layout.addWidget(self.file_tree)
        
        return tab
        
    def create_logs_tab(self):
        """Create the logs tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Log controls
        log_controls = QHBoxLayout()
        
        self.clear_logs_btn = QPushButton("🗑️ Clear Logs")
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        log_controls.addWidget(self.clear_logs_btn)
        
        self.export_logs_btn = QPushButton("📤 Export Logs")
        self.export_logs_btn.clicked.connect(self.export_logs)
        log_controls.addWidget(self.export_logs_btn)
        
        log_controls.addStretch()
        
        layout.addLayout(log_controls)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("background-color: #2b2b2b; color: #00ff00; font-family: 'Courier New';")
        layout.addWidget(self.log_display)
        
        return tab
        
    def create_settings_tab(self):
        """Create the settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Sync settings
        sync_settings_group = QGroupBox("Sync Settings")
        sync_layout = QGridLayout(sync_settings_group)
        
        sync_layout.addWidget(QLabel("Auto-sync interval (minutes):"), 0, 0)
        self.auto_sync_interval = QSpinBox()
        self.auto_sync_interval.setRange(1, 1440)
        self.auto_sync_interval.setValue(30)
        sync_layout.addWidget(self.auto_sync_interval, 0, 1)
        
        sync_layout.addWidget(QLabel("Conflict resolution:"), 1, 0)
        self.conflict_resolution = QComboBox()
        self.conflict_resolution.addItems(["Phone wins", "PC wins", "Ask user", "Newest wins"])
        sync_layout.addWidget(self.conflict_resolution, 1, 1)
        
        sync_layout.addWidget(QLabel("Enable notifications:"), 2, 0)
        self.enable_notifications = QCheckBox()
        self.enable_notifications.setChecked(True)
        sync_layout.addWidget(self.enable_notifications, 2, 1)
        
        layout.addWidget(sync_settings_group)
        
        # Connection settings
        connection_group = QGroupBox("Connection Settings")
        connection_layout = QGridLayout(connection_group)
        
        connection_layout.addWidget(QLabel("Connection type:"), 0, 0)
        self.connection_type = QComboBox()
        self.connection_type.addItems(["USB", "WiFi", "Bluetooth", "Cloud"])
        connection_layout.addWidget(self.connection_type, 0, 1)
        
        connection_layout.addWidget(QLabel("Device name:"), 1, 0)
        self.device_name = QLineEdit("MyPhone")
        connection_layout.addWidget(self.device_name, 1, 1)
        
        connection_layout.addWidget(QLabel("Sync folder:"), 2, 0)
        self.sync_folder = QLineEdit("./sync_folder")
        connection_layout.addWidget(self.sync_folder, 2, 1)
        
        layout.addWidget(connection_group)
        
        # Save button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        return tab
        
    def setup_sync_modules(self):
        """Initialize sync modules"""
        self.sync_modules = {
            'file_sync': FileSyncModule(),
            'contact_sync': ContactSyncModule(),
            'calendar_sync': CalendarSyncModule(),
            'media_sync': MediaSyncModule()
        }
        
        # Connect module signals
        for name, module in self.sync_modules.items():
            module.sync_progress.connect(self.update_module_progress)
            module.sync_status.connect(self.update_module_status)
            module.sync_activity.connect(self.add_activity_log)
            
    def setup_timers(self):
        """Setup timers for periodic updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(1000)  # Update every second
        
    def toggle_module(self, module_name):
        """Toggle a sync module on/off"""
        if module_name in self.sync_modules:
            module = self.sync_modules[module_name]
            if module.is_running():
                module.stop_sync()
                self.update_button_state(module_name, False)
            else:
                module.start_sync()
                self.update_button_state(module_name, True)
                
    def update_button_state(self, module_name, is_running):
        """Update button state based on module status"""
        button_map = {
            'file_sync': self.file_sync_btn,
            'contact_sync': self.contact_sync_btn,
            'calendar_sync': self.calendar_sync_btn,
            'media_sync': self.media_sync_btn
        }
        
        if module_name in button_map:
            button = button_map[module_name]
            button.setChecked(is_running)
            button.setText(f"{'⏹️' if is_running else '▶️'} {button.text().split(' ', 1)[1]}")
            
    def start_all_sync(self):
        """Start all sync modules"""
        for name, module in self.sync_modules.items():
            if not module.is_running():
                module.start_sync()
                self.update_button_state(name, True)
                
    def stop_all_sync(self):
        """Stop all sync modules"""
        for name, module in self.sync_modules.items():
            if module.is_running():
                module.stop_sync()
                self.update_button_state(name, False)
                
    def show_settings(self):
        """Show settings dialog"""
        self.tab_widget.setCurrentIndex(3)
        
    def update_module_progress(self, module_name, progress):
        """Update progress bar for a specific module"""
        progress_map = {
            'file_sync': self.file_sync_progress,
            'contact_sync': self.contact_sync_progress,
            'calendar_sync': self.calendar_sync_progress,
            'media_sync': self.media_sync_progress
        }
        
        if module_name in progress_map:
            progress_map[module_name].setValue(progress)
            
    def update_module_status(self, module_name, status):
        """Update status label for a specific module"""
        status_map = {
            'file_sync': self.file_sync_status,
            'contact_sync': self.contact_sync_status,
            'calendar_sync': self.calendar_sync_status,
            'media_sync': self.media_sync_status
        }
        
        if module_name in status_map:
            status_map[module_name].setText(status)
            
    def add_activity_log(self, module_name, activity):
        """Add activity to the activity list"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_list.insertItem(0, f"[{timestamp}] {module_name}: {activity}")
        
        # Limit list size
        if self.activity_list.count() > 100:
            self.activity_list.takeItem(self.activity_list.count() - 1)
            
    def refresh_file_browser(self):
        """Refresh the file browser"""
        # Implementation for refreshing file list
        pass
        
    def add_file(self):
        """Add a new file to sync"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Sync")
        if file_path:
            # Implementation for adding file
            pass
            
    def sync_selected_files(self):
        """Sync selected files"""
        # Implementation for syncing selected files
        pass
        
    def clear_logs(self):
        """Clear the log display"""
        self.log_display.clear()
        
    def export_logs(self):
        """Export logs to file"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Logs", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.log_display.toPlainText())
                
    def save_settings(self):
        """Save application settings"""
        # Implementation for saving settings
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        
    def update_ui(self):
        """Update UI elements periodically"""
        # Update active modules count
        active_count = sum(1 for module in self.sync_modules.values() if module.is_running())
        self.active_modules_label.setText(str(active_count))
        
        # Update global progress
        total_progress = sum(module.get_progress() for module in self.sync_modules.values())
        avg_progress = total_progress // len(self.sync_modules)
        self.global_progress.setValue(avg_progress)
        
        # Update connection status
        if active_count > 0:
            self.connection_status.setText("🟢 Connected")
            self.connection_status.setStyleSheet("color: #00ff00; font-weight: bold; padding: 10px;")
            self.global_sync_status.setText("🔄 Syncing")
            self.global_sync_status.setStyleSheet("color: #00ff00; font-weight: bold; padding: 10px;")
        else:
            self.connection_status.setText("🔴 Disconnected")
            self.connection_status.setStyleSheet("color: #ff4444; font-weight: bold; padding: 10px;")
            self.global_sync_status.setText("⏸️ Sync Paused")
            self.global_sync_status.setStyleSheet("color: #ffaa00; font-weight: bold; padding: 10px;")
            
    def closeEvent(self, event):
        """Handle application close event"""
        # Stop all sync modules
        self.stop_all_sync()
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Phone-PC Sync Emulator")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("SyncEmulator")
    
    # Create and show main window
    window = SyncEmulator()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()