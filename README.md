# Phone-PC Sync Emulator Pro

A comprehensive software suite that emulates advanced phone-PC synchronization capabilities. This complex system simulates real-world device connectivity, file transfers, contact synchronization, message management, and device monitoring.

## 🚀 Features

### Core Functionality
- **Multi-Device Emulation**: Simulate multiple Android and iOS devices simultaneously
- **Real-time Synchronization**: Bidirectional sync of files, contacts, and messages
- **Advanced File Transfer**: Progress tracking, encryption, and integrity verification
- **Contact Management**: Merge, sync, and backup contact databases
- **Message Synchronization**: SMS/messaging history sync and management
- **Device Monitoring**: Real-time status, battery, storage, and usage analytics

### Technical Features
- **Modern GUI**: Dark-themed interface using CustomTkinter
- **REST API Backend**: Flask-based server with real-time WebSocket communication
- **Device Simulation**: Realistic phone behavior with usage patterns
- **Data Encryption**: Secure transfer protocols with cryptographic protection
- **Progress Tracking**: Real-time updates for all operations
- **System Monitoring**: Memory, CPU, and process management

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 1GB free disk space
- Windows, macOS, or Linux

### Dependencies
All dependencies are listed in `requirements.txt`:
```
Flask==2.3.3
Flask-CORS==4.0.0
Flask-SocketIO==5.3.6
customtkinter==5.2.0
Pillow==10.0.1
requests==2.31.0
python-socketio==5.9.0
psutil==5.9.5
watchdog==3.0.0
cryptography==41.0.7
qrcode==7.4.2
numpy==1.24.3
```

## 🛠️ Installation

1. **Clone or download the project**:
   ```bash
   # If using git
   git clone <repository-url>
   cd phone-pc-sync-emulator
   
   # Or download and extract the files
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python launcher.py
   ```

## 🎯 Quick Start

### Method 1: Using the Launcher (Recommended)
1. Run the launcher application:
   ```bash
   python launcher.py
   ```

2. In the launcher interface:
   - Click "Start All" to launch all components
   - Or start components individually (Server → Devices → GUI)
   - Monitor status and logs in real-time

### Method 2: Manual Component Startup
1. **Start the Sync Server** (Terminal 1):
   ```bash
   python sync_server.py
   ```

2. **Start Device Emulator** (Terminal 2):
   ```bash
   python device_emulator.py
   ```

3. **Launch Main Application** (Terminal 3):
   ```bash
   python main.py
   ```

## 📱 Using the Application

### 1. Device Connection
- **Scan for Devices**: Click "Scan for Devices" to discover virtual phones
- **Connect**: Select a device and click "Connect"
- **Monitor Status**: View real-time device information and battery levels

### 2. File Transfer
- **Send to Phone**: Select files from PC to transfer to connected device
- **Receive from Phone**: Download files from phone to PC
- **Sync Folders**: Bidirectional folder synchronization
- **Progress Tracking**: Monitor transfer progress in real-time

### 3. Contact Synchronization
- **View Contacts**: Browse contacts from both PC and phone
- **Sync Operations**: 
  - Sync to Phone: Upload PC contacts to device
  - Sync from Phone: Download device contacts to PC
  - Merge Contacts: Intelligent merging with duplicate detection

### 4. Message Management
- **Message History**: View SMS and messaging history
- **Sync Messages**: Synchronize message databases
- **Export**: Save message history to files
- **Send Test SMS**: Simulate sending messages

### 5. Device Information
- **Real-time Monitoring**: Battery, storage, signal strength
- **System Status**: CPU usage, memory consumption
- **Activity Logs**: Detailed operation history
- **Usage Analytics**: Device usage patterns and statistics

### 6. Configuration
- **Sync Settings**: Auto-sync, backup options, notifications
- **Connection Types**: USB, WiFi, Bluetooth, Cloud
- **Sync Frequency**: Manual to daily automatic sync
- **Security**: Encryption and authentication settings

## 🏗️ Architecture

### Component Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Launcher      │    │   Main GUI      │    │  Sync Server    │
│   (launcher.py) │────│   (main.py)     │────│ (sync_server.py)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                │                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Device Emulator │    │   Data Storage  │
                       │(device_emu.py)  │    │   (data/ dir)   │
                       └─────────────────┘    └─────────────────┘
```

### Key Components

#### 1. Launcher (`launcher.py`)
- **Purpose**: Unified control center for all components
- **Features**: Process management, status monitoring, system info
- **Benefits**: Simplified startup, centralized logging

#### 2. Main GUI (`main.py`)
- **Purpose**: Primary user interface
- **Framework**: CustomTkinter with modern dark theme
- **Features**: Tabbed interface, real-time updates, progress tracking

#### 3. Sync Server (`sync_server.py`)
- **Purpose**: Backend API and real-time communication
- **Framework**: Flask with SocketIO
- **Features**: RESTful API, WebSocket events, data management

#### 4. Device Emulator (`device_emulator.py`)
- **Purpose**: Virtual phone device simulation
- **Features**: Realistic behavior, data generation, usage patterns
- **Simulation**: Battery drain, file creation, message generation

## 📊 Data Management

### Directory Structure
```
data/
├── devices/           # Virtual device data
│   ├── <device-id>/
│   │   ├── files.json     # File listings
│   │   ├── contacts.json  # Contact database
│   │   ├── messages.json  # Message history
│   │   └── apps.json      # Installed applications
├── transfers/         # File transfer cache
├── backups/          # Data backups
└── sync_cache/       # Synchronization cache
```

### Data Formats
- **JSON**: Human-readable configuration and data files
- **Binary**: File content and media (simulated)
- **Logs**: Plain text activity and error logs
- **Checksums**: MD5 hashes for integrity verification

## 🔧 Advanced Configuration

### Server Configuration
Modify `sync_server.py` for custom settings:
```python
# Change server host/port
server = SyncServer(host='0.0.0.0', port=8080)

# Modify encryption settings
cipher_suite = Fernet(custom_key)
```

### Device Simulation
Customize device behavior in `device_emulator.py`:
```python
# Battery drain rate (% per minute)
battery_drain_rate = 0.2

# Usage pattern frequency
usage_frequency = 30  # seconds between activities
```

### GUI Themes
Modify appearance in `main.py`:
```python
# Change theme
ctk.set_appearance_mode("light")  # or "dark", "system"
ctk.set_default_color_theme("green")  # or "blue", "dark-blue"
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: ModuleNotFoundError for required packages
**Solution**: 
```bash
pip install -r requirements.txt --upgrade
```

#### 2. Port Already in Use
**Problem**: Server fails to start (port 5000 busy)
**Solution**: Modify port in `sync_server.py` or kill existing process

#### 3. Permission Errors
**Problem**: Cannot create data directories
**Solution**: Run with appropriate permissions or change data directory

#### 4. GUI Not Displaying
**Problem**: CustomTkinter interface issues
**Solution**: 
- Update tkinter: `pip install tkinter --upgrade`
- Check display settings on Linux: `export DISPLAY=:0`

### Performance Optimization

#### For Low-End Systems
- Reduce device simulation frequency
- Lower file generation counts
- Disable real-time monitoring
- Use fewer virtual devices

#### For Development
- Enable debug mode in server
- Increase logging verbosity
- Use development database
- Enable hot reload

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Install development dependencies
4. Run tests
5. Submit pull request

### Code Style
- Follow PEP 8 standards
- Use type hints where applicable
- Document functions and classes
- Write unit tests for new features

## 📝 License

This project is provided as-is for educational and demonstration purposes. 

## 🆘 Support

### Getting Help
1. Check this README for common solutions
2. Review error logs in the launcher
3. Verify all dependencies are installed
4. Ensure Python 3.8+ is being used

### Reporting Issues
When reporting problems, please include:
- Operating system and version
- Python version
- Complete error messages
- Steps to reproduce the issue
- Screenshots if applicable

## 🔮 Future Enhancements

### Planned Features
- **Cross-platform notifications**
- **Cloud synchronization backends**
- **Plugin system for custom sync types**
- **Advanced conflict resolution**
- **Multi-language support**
- **Network discovery protocols**
- **Backup and restore wizards**
- **Performance analytics dashboard**

### Technical Improvements
- **Database backend options**
- **Improved encryption algorithms**
- **Compression for large transfers**
- **Delta synchronization**
- **Automatic conflict resolution**
- **Background service mode**

---

**Phone-PC Sync Emulator Pro** - A sophisticated demonstration of modern synchronization technology.