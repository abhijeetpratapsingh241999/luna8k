#!/usr/bin/env python3
"""
Phone-PC Sync Emulator
A comprehensive emulator for simulating synchronization between mobile devices and computers.
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
                             QHBoxLayout, QWidget, QLabel, QPushButton, QStatusBar,
                             QMessageBox, QSystemTrayIcon, QMenu, QAction)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor
from PyQt6.QtWidgets import QStyle

# Import our modules
from sync_modules.file_sync import FileSyncModule
from sync_modules.contact_sync import ContactSyncModule
from sync_modules.calendar_sync import CalendarSyncModule
from sync_modules.device_manager import DeviceManager
from sync_modules.sync_engine import SyncEngine
from utils.config_manager import ConfigManager
from utils.logger import Logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phone-PC Sync Emulator v2.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.logger = Logger()
        self.device_manager = DeviceManager()
        self.sync_engine = SyncEngine()
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.setup_system_tray()
        
        # Apply theme
        self.apply_theme()
        
        # Start background processes
        self.start_background_processes()
        
    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Phone-PC Sync Emulator")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Sync status indicator
        self.sync_status_btn = QPushButton("🔄 Sync Status: Ready")
        self.sync_status_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(self.sync_status_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tab widget for different sync modules
        self.tab_widget = QTabWidget()
        
        # File sync tab
        self.file_sync_module = FileSyncModule()
        self.tab_widget.addTab(self.file_sync_module, "📁 File Sync")
        
        # Contact sync tab
        self.contact_sync_module = ContactSyncModule()
        self.tab_widget.addTab(self.contact_sync_module, "👥 Contacts")
        
        # Calendar sync tab
        self.calendar_sync_module = CalendarSyncModule()
        self.tab_widget.addTab(self.calendar_sync_module, "📅 Calendar")
        
        # Device management tab
        self.device_tab = self.device_manager.get_widget()
        self.tab_widget.addTab(self.device_tab, "📱 Devices")
        
        main_layout.addWidget(self.tab_widget)
        
        # Control panel
        control_layout = QHBoxLayout()
        
        self.start_sync_btn = QPushButton("🚀 Start Sync")
        self.start_sync_btn.clicked.connect(self.start_sync)
        self.start_sync_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        self.stop_sync_btn = QPushButton("⏹️ Stop Sync")
        self.stop_sync_btn.clicked.connect(self.stop_sync)
        self.stop_sync_btn.setEnabled(False)
        self.stop_sync_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self.show_settings)
        
        control_layout.addWidget(self.start_sync_btn)
        control_layout.addWidget(self.stop_sync_btn)
        control_layout.addWidget(self.settings_btn)
        control_layout.addStretch()
        
        main_layout.addLayout(control_layout)
        
    def setup_menu(self):
        """Setup the application menu"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        new_sync_action = QAction('&New Sync Session', self)
        new_sync_action.setShortcut('Ctrl+N')
        new_sync_action.triggered.connect(self.new_sync_session)
        file_menu.addAction(new_sync_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        log_viewer_action = QAction('&Log Viewer', self)
        log_viewer_action.triggered.connect(self.show_log_viewer)
        tools_menu.addAction(log_viewer_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status indicators
        self.device_status_label = QLabel("📱 No devices connected")
        self.sync_progress_label = QLabel("Sync Progress: 0%")
        self.last_sync_label = QLabel("Last Sync: Never")
        
        self.status_bar.addWidget(self.device_status_label)
        self.status_bar.addPermanentWidget(self.sync_progress_label)
        self.status_bar.addPermanentWidget(self.last_sync_label)
        
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        # Tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def apply_theme(self):
        """Apply the application theme"""
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
        """)
        
    def start_background_processes(self):
        """Start background processes and timers"""
        # Update timer for status updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # Update every second
        
    def start_sync(self):
        """Start the synchronization process"""
        try:
            self.sync_engine.start_sync()
            self.start_sync_btn.setEnabled(False)
            self.stop_sync_btn.setEnabled(True)
            self.sync_status_btn.setText("🔄 Sync Status: Running")
            self.sync_status_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
            self.logger.log("Sync process started", "INFO")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start sync: {str(e)}")
            
    def stop_sync(self):
        """Stop the synchronization process"""
        try:
            self.sync_engine.stop_sync()
            self.start_sync_btn.setEnabled(True)
            self.stop_sync_btn.setEnabled(False)
            self.sync_status_btn.setText("🔄 Sync Status: Stopped")
            self.sync_status_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
            self.logger.log("Sync process stopped", "INFO")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop sync: {str(e)}")
            
    def update_status(self):
        """Update status information"""
        # Update device status
        connected_devices = self.device_manager.get_connected_devices()
        if connected_devices:
            self.device_status_label.setText(f"📱 {len(connected_devices)} device(s) connected")
        else:
            self.device_status_label.setText("📱 No devices connected")
            
        # Update sync progress
        progress = self.sync_engine.get_progress()
        self.sync_progress_label.setText(f"Sync Progress: {progress}%")
        
        # Update last sync time
        last_sync = self.sync_engine.get_last_sync_time()
        if last_sync:
            self.last_sync_label.setText(f"Last Sync: {last_sync}")
            
    def new_sync_session(self):
        """Create a new sync session"""
        # Implementation for new sync session
        pass
        
    def show_settings(self):
        """Show settings dialog"""
        # Implementation for settings dialog
        pass
        
    def show_log_viewer(self):
        """Show log viewer"""
        # Implementation for log viewer
        pass
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Phone-PC Sync Emulator",
                         "Phone-PC Sync Emulator v2.0\n\n"
                         "A comprehensive emulator for simulating synchronization "
                         "between mobile devices and computers.\n\n"
                         "Features:\n"
                         "• File synchronization\n"
                         "• Contact management\n"
                         "• Calendar sync\n"
                         "• Device management\n"
                         "• Real-time monitoring")
                         
    def closeEvent(self, event):
        """Handle application close event"""
        reply = QMessageBox.question(self, 'Exit', 
                                   'Are you sure you want to exit?',
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Cleanup
            self.sync_engine.stop_sync()
            self.logger.log("Application closed", "INFO")
            event.accept()
        else:
            event.ignore()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Phone-PC Sync Emulator")
    app.setApplicationVersion("2.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()