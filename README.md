# 📱 Phone-PC Sync Emulator

A comprehensive and sophisticated application that simulates synchronization between mobile devices and computers. This emulator provides a realistic experience of managing file transfers, contact synchronization, calendar management, and device monitoring in a phone-PC sync environment.

## ✨ Features

### 🔄 Core Synchronization
- **File Synchronization**: Bidirectional file sync with conflict resolution
- **Contact Management**: Import/export contacts, duplicate detection, and merging
- **Calendar Sync**: Event synchronization with recurring event support
- **Device Management**: Real-time device status monitoring and connection management

### 🎯 Advanced Capabilities
- **Multi-Device Support**: Handle multiple devices simultaneously
- **Conflict Resolution**: Smart conflict detection and resolution strategies
- **Auto-Sync**: Configurable automatic synchronization intervals
- **Progress Tracking**: Real-time sync progress monitoring
- **Error Handling**: Comprehensive error logging and recovery

### 🛠️ Technical Features
- **Database Storage**: SQLite-based data persistence
- **Logging System**: Multi-level logging with rotation
- **Threading**: Asynchronous sync operations
- **Configuration Management**: Flexible sync settings and preferences
- **Backup System**: Automatic backup creation before sync operations

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- PyQt6 for the GUI
- Linux, Windows, or macOS

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd phone-pc-sync-emulator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
phone-pc-sync-emulator/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── sync_modules/          # Core synchronization modules
│   ├── __init__.py
│   ├── file_sync.py       # File synchronization logic
│   ├── contact_sync.py    # Contact management
│   ├── calendar_sync.py   # Calendar synchronization
│   ├── device_manager.py  # Device detection and management
│   └── sync_engine.py     # Main sync coordination engine
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── database.py        # Database management
│   └── logger.py          # Comprehensive logging system
└── logs/                  # Application logs (created at runtime)
```

## 🎮 Usage Guide

### Main Interface
The application features a modern, tabbed interface with:

- **Device Panel**: Shows connected devices and their status
- **File Sync Tab**: Manage file synchronization operations
- **Contacts Tab**: Handle contact import/export and sync
- **Calendar Tab**: Manage calendar events and synchronization
- **Settings Tab**: Configure sync preferences and options

### Starting a Sync
1. Connect a device (simulated)
2. Select sync options (files, contacts, calendar)
3. Click "Start Sync" to begin synchronization
4. Monitor progress in real-time
5. Review sync results and logs

### Configuration
- **Auto-sync**: Enable automatic synchronization every 5 minutes
- **Sync Options**: Choose which data types to synchronize
- **Conflict Resolution**: Set how to handle sync conflicts
- **Backup Settings**: Configure automatic backup creation

## 🔧 Configuration Options

### Sync Settings
- `sync_auto_enabled`: Enable/disable automatic synchronization
- `sync_interval_minutes`: Time between auto-sync operations
- `max_concurrent_syncs`: Maximum simultaneous sync operations
- `sync_timeout_minutes`: Timeout for sync operations
- `backup_before_sync`: Create backups before syncing

### File Sync Options
- `include_hidden`: Include hidden files and directories
- `exclude_patterns`: File patterns to exclude from sync
- `max_file_size`: Maximum file size for synchronization
- `sync_direction`: Bidirectional, device-to-PC, or PC-to-device
- `conflict_resolution`: How to handle file conflicts

### Contact Sync Options
- `merge_duplicates`: Automatically merge duplicate contacts
- `sync_deleted`: Synchronize contact deletions
- `validate_emails`: Validate email addresses
- `validate_phones`: Validate phone numbers

## 📊 Monitoring and Logging

### Real-time Monitoring
- Device connection status
- Sync operation progress
- Battery and storage levels
- Transfer speeds and performance metrics

### Comprehensive Logging
- **Sync Logs**: All synchronization operations
- **Error Logs**: Error tracking and debugging
- **Device Logs**: Device connection events
- **Performance Logs**: Sync performance metrics
- **Debug Logs**: Detailed debugging information

### Log Management
- Automatic log rotation
- Configurable log retention
- Export capabilities
- Search and filtering

## 🧪 Simulation Features

### Device Simulation
- **iPhone 15 Pro**: iOS device with realistic specifications
- **Samsung Galaxy S24**: Android device simulation
- **Dynamic Status**: Battery, storage, and connection changes
- **Connection Types**: USB, WiFi, and Bluetooth simulation

### Sync Simulation
- **Realistic Timing**: Simulated file transfer delays
- **Progress Updates**: Real-time progress tracking
- **Error Simulation**: Occasional sync errors for testing
- **Conflict Generation**: Simulated data conflicts

## 🔒 Security Features

- **Device Trust**: Trusted device management
- **Secure Connections**: Simulated encryption and security
- **Access Control**: User permission management
- **Audit Logging**: Comprehensive security event logging

## 📈 Performance Features

- **Multi-threading**: Concurrent sync operations
- **Queue Management**: Priority-based sync queuing
- **Resource Monitoring**: Memory and CPU usage tracking
- **Optimization**: Efficient data processing algorithms

## 🐛 Troubleshooting

### Common Issues
1. **Import Errors**: Check file formats and permissions
2. **Sync Failures**: Review error logs for specific issues
3. **Performance Issues**: Monitor system resources
4. **Database Errors**: Check database file permissions

### Debug Mode
Enable debug logging for detailed troubleshooting:
```python
logger.setLevel(logging.DEBUG)
```

### Log Analysis
Use the built-in log analysis tools:
- Search logs for specific errors
- Export logs for external analysis
- Monitor log file sizes and rotation

## 🔮 Future Enhancements

- **Cloud Integration**: Google Drive, iCloud, OneDrive support
- **Mobile App**: Companion mobile application
- **API Support**: REST API for external integrations
- **Advanced Analytics**: Detailed sync performance analytics
- **Plugin System**: Extensible architecture for custom sync modules

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for:
- Code style and standards
- Testing requirements
- Documentation updates
- Feature proposals

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- PyQt6 team for the excellent GUI framework
- SQLite developers for the robust database engine
- Python community for the rich ecosystem of libraries

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation and logs
- Review the troubleshooting section

---

**Note**: This is a simulation/emulator application designed for testing, development, and educational purposes. It does not perform actual device synchronization but provides a realistic environment for testing sync logic and user interfaces.
