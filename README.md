# 📱 Phone-PC Sync Emulator

A comprehensive and sophisticated emulator for simulating synchronization between mobile devices and computers. This application provides a realistic simulation of various sync processes including file synchronization, contact management, calendar events, and media files.

## ✨ Features

### 🔄 Multi-Module Synchronization
- **File Sync Module**: Handles document, image, and general file synchronization
- **Contact Sync Module**: Manages contact information with duplicate detection and merging
- **Calendar Sync Module**: Synchronizes calendar events with conflict resolution
- **Media Sync Module**: Handles music, photos, and video synchronization

### 🎯 Advanced Sync Capabilities
- **Conflict Resolution**: Multiple strategies (newest wins, phone wins, PC wins, ask user)
- **Duplicate Detection**: Intelligent merging of duplicate contacts and events
- **Real-time Monitoring**: Live sync status and progress tracking
- **Auto-sync**: Configurable automatic synchronization intervals
- **Error Handling**: Comprehensive error logging and recovery

### 🖥️ Modern User Interface
- **Dark Theme**: Professional dark mode interface
- **Tabbed Interface**: Organized sections for different sync types
- **Real-time Updates**: Live progress bars and status indicators
- **Responsive Design**: Adaptive layout for different screen sizes
- **Activity Logging**: Comprehensive sync activity tracking

### ⚙️ Configuration & Settings
- **Flexible Settings**: Extensive customization options
- **Profile Management**: Multiple sync profiles support
- **Import/Export**: Settings and data import/export functionality
- **Validation**: Settings validation and error checking

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- PyQt6 (for GUI)
- Linux/macOS/Windows support

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd phone-pc-sync-emulator

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Manual Installation
```bash
# Install PyQt6
pip install PyQt6

# Install additional dependencies
pip install cryptography psutil watchdog python-dateutil pytz rich
```

## 🏗️ Architecture

### Core Components
```
sync_modules/
├── base_sync.py          # Base sync module class
├── file_sync.py          # File synchronization
├── contact_sync.py       # Contact management
├── calendar_sync.py      # Calendar events
├── media_sync.py         # Media files
├── settings_manager.py   # Configuration management
└── logger.py            # Logging system
```

### Design Patterns
- **Modular Architecture**: Each sync type is a separate module
- **Observer Pattern**: Real-time UI updates via signals
- **Factory Pattern**: Dynamic module creation and management
- **Strategy Pattern**: Configurable conflict resolution strategies

## 📖 Usage

### Starting the Application
1. Launch the application: `python main.py`
2. The main window will open with the sync dashboard
3. Configure your sync settings in the Settings tab
4. Start individual sync modules or use "Start All Sync"

### Sync Module Management
- **File Sync**: Toggle file synchronization on/off
- **Contact Sync**: Manage contact database and sync
- **Calendar Sync**: Handle calendar events and appointments
- **Media Sync**: Synchronize music, photos, and videos

### Monitoring & Control
- **Real-time Status**: View current sync status for each module
- **Progress Tracking**: Monitor sync progress with visual indicators
- **Activity Logs**: Review recent sync activities and events
- **Error Handling**: View and resolve sync conflicts and errors

## 🔧 Configuration

### Sync Settings
```json
{
  "sync": {
    "auto_sync_interval": 30,
    "conflict_resolution": "newest_wins",
    "enable_notifications": true
  },
  "connection": {
    "connection_type": "USB",
    "device_name": "MyPhone",
    "sync_folder": "./sync_folder"
  }
}
```

### File Sync Options
- Supported file extensions
- Maximum file size limits
- Hidden file inclusion
- Timestamp preservation

### Contact Sync Options
- Duplicate merging strategies
- Photo synchronization
- Contact limits and filtering

## 📊 Data Management

### Supported Formats
- **Files**: TXT, DOC, DOCX, PDF, JPG, PNG, MP3, MP4, ZIP
- **Contacts**: JSON, CSV export/import
- **Calendar**: JSON, iCalendar (ICS) export/import
- **Media**: Music, photos, videos with metadata

### Data Export/Import
- Export sync data to various formats
- Import data from external sources
- Backup and restore functionality
- Data validation and integrity checks

## 🐛 Troubleshooting

### Common Issues
1. **Module Not Starting**: Check if dependencies are installed
2. **Sync Errors**: Review logs in the Logs tab
3. **Performance Issues**: Adjust sync intervals and file size limits
4. **UI Problems**: Verify PyQt6 installation

### Debug Mode
Enable debug logging in the Settings tab for detailed troubleshooting information.

### Log Files
Logs are stored in `./logs/sync.log` with configurable retention policies.

## 🧪 Testing

### Sample Data
The application includes sample data for demonstration:
- Sample contacts with realistic information
- Calendar events for testing
- Media file metadata examples
- File synchronization scenarios

### Test Scenarios
- **Conflict Resolution**: Test different conflict resolution strategies
- **Large File Handling**: Verify performance with large files
- **Error Recovery**: Test error handling and recovery mechanisms
- **UI Responsiveness**: Verify interface performance during sync

## 🔒 Security Features

### Data Protection
- Optional data encryption
- Session timeout management
- IP address restrictions
- Authentication requirements

### Privacy
- Local data storage
- No external data transmission
- Configurable logging levels
- Data export controls

## 📈 Performance

### Optimization Features
- **Efficient Algorithms**: Optimized sync algorithms
- **Memory Management**: Smart memory usage for large datasets
- **Background Processing**: Non-blocking sync operations
- **Caching**: Intelligent data caching for performance

### Monitoring
- Performance metrics logging
- Resource usage tracking
- Sync duration analysis
- Bottleneck identification

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests and documentation
5. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include comprehensive docstrings
- Write unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- PyQt6 team for the excellent GUI framework
- Python community for various utility libraries
- Open source contributors and testers

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation
- Contact the development team

---

**Note**: This is a simulation/emulator application designed for testing and demonstration purposes. It does not perform actual device synchronization but provides a realistic simulation of the sync process.
