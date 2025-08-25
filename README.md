# Phone-PC Sync Emulator

A comprehensive emulation of phone-to-computer synchronization processes with a modern GUI interface.

## Features

### 🔌 Multiple Sync Protocols
- **USB**: High-speed, reliable connection (480 Mbps)
- **Bluetooth**: Wireless convenience (24 Mbps)
- **WiFi**: Network-based synchronization (100 Mbps)
- **NFC**: Contactless transfer (0.424 Mbps)

### 📱 Device Emulation
- **Phone Emulator**: Realistic Android device simulation
  - Battery level simulation with charging states
  - Signal strength variations
  - Storage management
  - Sample data (files, contacts, calendar events)
- **PC Emulator**: Windows system simulation
  - CPU and memory usage monitoring
  - System health assessment
  - Storage analytics
  - Performance metrics

### 🔄 Synchronization Types
- **Full Sync**: Complete data synchronization
- **Incremental Sync**: Only changed files
- **Selective Sync**: User-selected items
- **Real-time Progress**: Live sync status monitoring

### 🎛️ Advanced Controls
- **Conflict Resolution**: Multiple strategies (newer wins, device priority, user choice)
- **Auto-sync**: Scheduled synchronization
- **File Filtering**: Size limits and type exclusions
- **Retry Logic**: Automatic error recovery

### 📊 Comprehensive Monitoring
- **Real-time Progress**: File-by-file progress tracking
- **Performance Metrics**: Transfer speeds and ETA
- **Statistics**: Sync history and analytics
- **Logging**: Detailed event logging with filtering

### 🖥️ Modern GUI Interface
- **Tabbed Interface**: Organized sections for different functions
- **Device Panels**: Real-time device information display
- **Progress Tracking**: Visual progress bars and statistics
- **Log Viewer**: Advanced log management with search and export

## Installation

### Prerequisites
- Python 3.8 or higher
- tkinter (usually included with Python)
- psutil (for system monitoring)

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd phone-pc-sync-emulator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

### Getting Started
1. **Launch the Application**: Run `main.py` to start the emulator
2. **Connect Devices**: Click "Connect" to establish device connection
3. **Configure Sync**: Choose sync type and options
4. **Start Synchronization**: Click "Start Sync" to begin the process
5. **Monitor Progress**: Watch real-time progress in the progress panel
6. **View Logs**: Check the logs tab for detailed information

### Configuration
The application uses a configuration file (`config.ini`) that can be customized:
- Sync preferences
- Protocol settings
- UI options
- Logging parameters

### Sync Options
- **Data Types**: Files, contacts, calendar events
- **Direction**: Phone to PC, PC to Phone, or bidirectional
- **Conflict Resolution**: Choose how to handle file conflicts
- **File Filters**: Set size limits and exclude file types

## Architecture

### Core Components
- **SyncManager**: Central synchronization orchestration
- **Device Emulators**: Phone and PC simulation
- **Protocol Manager**: Connection protocol handling
- **GUI Framework**: Modern tkinter-based interface

### Data Models
- **Device**: Base device class with common functionality
- **SyncSession**: Synchronization session tracking
- **FileInfo**: File metadata and sync status
- **Contact/CalendarEvent**: Personal data models

### Design Patterns
- **Observer Pattern**: Event-driven updates
- **Factory Pattern**: Device and protocol creation
- **Strategy Pattern**: Different sync algorithms
- **MVC Pattern**: GUI separation of concerns

## Development

### Project Structure
```
src/
├── core/           # Core synchronization logic
├── emulators/      # Device emulation
├── gui/           # User interface components
├── models/        # Data models
├── sync_protocols/ # Protocol implementations
└── utils/         # Utility functions
```

### Adding New Features
1. **Protocols**: Extend `ProtocolManager` and add new protocol classes
2. **Device Types**: Create new emulator classes inheriting from `Device`
3. **Sync Types**: Implement new sync strategies in `SyncManager`
4. **GUI Components**: Add new panels to the main interface

### Testing
The emulator includes comprehensive error handling and logging:
- Simulated device failures
- Network interruption handling
- Error recovery mechanisms
- Performance monitoring

## Configuration Options

### Sync Settings
```ini
[Sync]
default_sync_type = incremental
auto_sync_interval = 30
max_file_size = 100
conflict_resolution = newer_wins
retry_attempts = 3
retry_delay = 5
```

### Protocol Settings
```ini
[Protocols]
preferred_protocol = USB
usb_speed = 480
bluetooth_speed = 24
wifi_speed = 100
nfc_speed = 0.424
```

### UI Settings
```ini
[UI]
theme = default
window_width = 1200
window_height = 800
auto_refresh = true
refresh_interval = 1000
```

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **GUI Issues**: Check tkinter installation
3. **Performance**: Adjust refresh intervals in configuration
4. **Logging**: Check log file permissions and disk space

### Debug Mode
Enable debug logging in the configuration:
```ini
[General]
debug_mode = true
log_level = DEBUG
```

## Contributing

### Guidelines
1. Follow PEP 8 coding standards
2. Add comprehensive error handling
3. Include logging for debugging
4. Update documentation for new features
5. Test with different Python versions

### Areas for Enhancement
- **Cloud Sync**: Add cloud storage integration
- **Mobile App**: Companion mobile application
- **API Integration**: RESTful API for external tools
- **Plugin System**: Extensible architecture
- **Performance Optimization**: Enhanced algorithms

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python and tkinter
- Inspired by real-world synchronization challenges
- Designed for educational and development purposes

## Support

For issues, questions, or contributions:
- Check the logs for detailed error information
- Review the configuration settings
- Consult the troubleshooting section
- Open an issue in the repository

---

**Note**: This is an emulation system designed for development, testing, and educational purposes. It does not perform actual device synchronization.
