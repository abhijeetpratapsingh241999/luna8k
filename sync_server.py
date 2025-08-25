#!/usr/bin/env python3
"""
Sync Server - Backend component for Phone-PC Sync Emulator
Handles device communication, file transfers, and data synchronization
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import os
import time
import threading
import uuid
from datetime import datetime
from pathlib import Path
import hashlib
import shutil
from cryptography.fernet import Fernet
import psutil
import base64

class SyncServer:
    def __init__(self, host='localhost', port=5000):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'phone_pc_sync_secret_key'
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        self.host = host
        self.port = port
        
        # Data directories
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / "devices").mkdir(exist_ok=True)
        (self.data_dir / "transfers").mkdir(exist_ok=True)
        (self.data_dir / "backups").mkdir(exist_ok=True)
        (self.data_dir / "sync_cache").mkdir(exist_ok=True)
        
        # Server state
        self.connected_devices = {}
        self.active_transfers = {}
        self.sync_sessions = {}
        
        # Encryption key for secure transfers
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        self.setup_routes()
        self.setup_socketio_events()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Get server status"""
            return jsonify({
                'status': 'running',
                'connected_devices': len(self.connected_devices),
                'active_transfers': len(self.active_transfers),
                'uptime': self.get_uptime(),
                'memory_usage': psutil.virtual_memory().percent,
                'cpu_usage': psutil.cpu_percent()
            })
            
        @self.app.route('/api/devices', methods=['GET'])
        def get_devices():
            """Get list of connected devices"""
            devices = []
            for device_id, device_info in self.connected_devices.items():
                devices.append({
                    'id': device_id,
                    'name': device_info.get('name', 'Unknown'),
                    'type': device_info.get('type', 'Unknown'),
                    'status': device_info.get('status', 'Unknown'),
                    'battery': device_info.get('battery', 0),
                    'storage_used': device_info.get('storage_used', 0),
                    'last_sync': device_info.get('last_sync', 'Never')
                })
            return jsonify(devices)
            
        @self.app.route('/api/devices/<device_id>/connect', methods=['POST'])
        def connect_device(device_id):
            """Connect a device"""
            data = request.get_json()
            
            device_info = {
                'id': device_id,
                'name': data.get('name', f'Device-{device_id[:8]}'),
                'type': data.get('type', 'Android'),
                'status': 'Connected',
                'battery': data.get('battery', 100),
                'storage_used': data.get('storage_used', 50),
                'connected_at': datetime.now().isoformat(),
                'last_sync': datetime.now().isoformat(),
                'capabilities': data.get('capabilities', ['file_transfer', 'contacts', 'messages'])
            }
            
            self.connected_devices[device_id] = device_info
            
            # Create device data directory
            device_dir = self.data_dir / "devices" / device_id
            device_dir.mkdir(exist_ok=True)
            
            # Save device info
            with open(device_dir / "info.json", "w") as f:
                json.dump(device_info, f, indent=2)
                
            # Initialize device data
            self.initialize_device_data(device_id)
            
            self.socketio.emit('device_connected', device_info)
            
            return jsonify({'status': 'success', 'device': device_info})
            
        @self.app.route('/api/devices/<device_id>/disconnect', methods=['POST'])
        def disconnect_device(device_id):
            """Disconnect a device"""
            if device_id in self.connected_devices:
                device_info = self.connected_devices[device_id]
                del self.connected_devices[device_id]
                
                self.socketio.emit('device_disconnected', {'id': device_id, 'name': device_info.get('name')})
                
                return jsonify({'status': 'success', 'message': 'Device disconnected'})
            else:
                return jsonify({'status': 'error', 'message': 'Device not found'}), 404
                
        @self.app.route('/api/devices/<device_id>/files', methods=['GET'])
        def get_device_files(device_id):
            """Get files from a device"""
            if device_id not in self.connected_devices:
                return jsonify({'status': 'error', 'message': 'Device not connected'}), 404
                
            device_dir = self.data_dir / "devices" / device_id
            files_file = device_dir / "files.json"
            
            if files_file.exists():
                with open(files_file, "r") as f:
                    files = json.load(f)
            else:
                files = self.get_sample_files()
                with open(files_file, "w") as f:
                    json.dump(files, f, indent=2)
                    
            return jsonify(files)
            
        @self.app.route('/api/devices/<device_id>/contacts', methods=['GET'])
        def get_device_contacts(device_id):
            """Get contacts from a device"""
            if device_id not in self.connected_devices:
                return jsonify({'status': 'error', 'message': 'Device not connected'}), 404
                
            device_dir = self.data_dir / "devices" / device_id
            contacts_file = device_dir / "contacts.json"
            
            if contacts_file.exists():
                with open(contacts_file, "r") as f:
                    contacts = json.load(f)
            else:
                contacts = self.get_sample_contacts()
                with open(contacts_file, "w") as f:
                    json.dump(contacts, f, indent=2)
                    
            return jsonify(contacts)
            
        @self.app.route('/api/devices/<device_id>/messages', methods=['GET'])
        def get_device_messages(device_id):
            """Get messages from a device"""
            if device_id not in self.connected_devices:
                return jsonify({'status': 'error', 'message': 'Device not connected'}), 404
                
            device_dir = self.data_dir / "devices" / device_id
            messages_file = device_dir / "messages.json"
            
            if messages_file.exists():
                with open(messages_file, "r") as f:
                    messages = json.load(f)
            else:
                messages = self.get_sample_messages()
                with open(messages_file, "w") as f:
                    json.dump(messages, f, indent=2)
                    
            return jsonify(messages)
            
        @self.app.route('/api/transfer/start', methods=['POST'])
        def start_transfer():
            """Start a file transfer"""
            data = request.get_json()
            
            transfer_id = str(uuid.uuid4())
            transfer_info = {
                'id': transfer_id,
                'device_id': data.get('device_id'),
                'operation': data.get('operation'),  # 'upload', 'download', 'sync'
                'files': data.get('files', []),
                'status': 'started',
                'progress': 0,
                'total_size': data.get('total_size', 0),
                'transferred': 0,
                'start_time': datetime.now().isoformat()
            }
            
            self.active_transfers[transfer_id] = transfer_info
            
            # Start transfer simulation in background
            threading.Thread(target=self.simulate_transfer, args=(transfer_id,)).start()
            
            return jsonify({'status': 'success', 'transfer_id': transfer_id})
            
        @self.app.route('/api/transfer/<transfer_id>/status', methods=['GET'])
        def get_transfer_status(transfer_id):
            """Get transfer status"""
            if transfer_id in self.active_transfers:
                return jsonify(self.active_transfers[transfer_id])
            else:
                return jsonify({'status': 'error', 'message': 'Transfer not found'}), 404
                
        @self.app.route('/api/sync/start', methods=['POST'])
        def start_sync():
            """Start synchronization"""
            data = request.get_json()
            
            sync_id = str(uuid.uuid4())
            sync_info = {
                'id': sync_id,
                'device_id': data.get('device_id'),
                'sync_type': data.get('sync_type'),  # 'contacts', 'messages', 'files', 'all'
                'direction': data.get('direction'),  # 'to_device', 'from_device', 'bidirectional'
                'status': 'started',
                'progress': 0,
                'start_time': datetime.now().isoformat()
            }
            
            self.sync_sessions[sync_id] = sync_info
            
            # Start sync simulation in background
            threading.Thread(target=self.simulate_sync, args=(sync_id,)).start()
            
            return jsonify({'status': 'success', 'sync_id': sync_id})
            
        @self.app.route('/api/sync/<sync_id>/status', methods=['GET'])
        def get_sync_status(sync_id):
            """Get sync status"""
            if sync_id in self.sync_sessions:
                return jsonify(self.sync_sessions[sync_id])
            else:
                return jsonify({'status': 'error', 'message': 'Sync session not found'}), 404
                
    def setup_socketio_events(self):
        """Setup SocketIO events for real-time communication"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print("Client connected")
            emit('connected', {'status': 'success'})
            
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print("Client disconnected")
            
        @self.socketio.on('device_scan')
        def handle_device_scan():
            """Handle device scan request"""
            # Simulate device discovery
            devices = [
                {
                    'id': str(uuid.uuid4()),
                    'name': 'Samsung Galaxy S21',
                    'type': 'Android',
                    'battery': 85,
                    'signal': 4
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'iPhone 13 Pro',
                    'type': 'iOS',
                    'battery': 92,
                    'signal': 5
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'OnePlus 9',
                    'type': 'Android',
                    'battery': 67,
                    'signal': 3
                }
            ]
            
            emit('devices_found', devices)
            
        @self.socketio.on('send_message')
        def handle_send_message(data):
            """Handle sending a message to device"""
            device_id = data.get('device_id')
            message = data.get('message')
            
            if device_id in self.connected_devices:
                # Simulate message sending
                response = {
                    'status': 'sent',
                    'message_id': str(uuid.uuid4()),
                    'timestamp': datetime.now().isoformat()
                }
                emit('message_sent', response)
            else:
                emit('error', {'message': 'Device not connected'})
                
    def initialize_device_data(self, device_id):
        """Initialize sample data for a new device"""
        device_dir = self.data_dir / "devices" / device_id
        
        # Create sample files
        files = self.get_sample_files()
        with open(device_dir / "files.json", "w") as f:
            json.dump(files, f, indent=2)
            
        # Create sample contacts
        contacts = self.get_sample_contacts()
        with open(device_dir / "contacts.json", "w") as f:
            json.dump(contacts, f, indent=2)
            
        # Create sample messages
        messages = self.get_sample_messages()
        with open(device_dir / "messages.json", "w") as f:
            json.dump(messages, f, indent=2)
            
    def get_sample_files(self):
        """Get sample file structure"""
        return {
            "folders": [
                {
                    "name": "DCIM",
                    "type": "folder",
                    "size": 0,
                    "modified": "2024-01-15T14:30:00",
                    "files": [
                        {
                            "name": "IMG_001.jpg",
                            "type": "image",
                            "size": 2097152,
                            "modified": "2024-01-15T14:25:00"
                        },
                        {
                            "name": "IMG_002.jpg",
                            "type": "image",
                            "size": 1932735,
                            "modified": "2024-01-15T14:26:00"
                        }
                    ]
                },
                {
                    "name": "Downloads",
                    "type": "folder",
                    "size": 0,
                    "modified": "2024-01-15T15:00:00",
                    "files": [
                        {
                            "name": "app.apk",
                            "type": "application",
                            "size": 26542080,
                            "modified": "2024-01-14T10:15:00"
                        },
                        {
                            "name": "document.pdf",
                            "type": "document",
                            "size": 1258291,
                            "modified": "2024-01-13T16:45:00"
                        }
                    ]
                }
            ]
        }
        
    def get_sample_contacts(self):
        """Get sample contacts"""
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "Alice Brown",
                "phone": "+1-555-1111",
                "email": "alice@phone.com",
                "photo": None,
                "created": "2024-01-01T00:00:00",
                "modified": "2024-01-15T10:00:00"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Bob Green",
                "phone": "+1-555-2222",
                "email": "bob@phone.com",
                "photo": None,
                "created": "2024-01-02T00:00:00",
                "modified": "2024-01-14T15:30:00"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Carol White",
                "phone": "+1-555-3333",
                "email": "carol@phone.com",
                "photo": None,
                "created": "2024-01-03T00:00:00",
                "modified": "2024-01-13T09:15:00"
            }
        ]
        
    def get_sample_messages(self):
        """Get sample messages"""
        return [
            {
                "id": str(uuid.uuid4()),
                "contact": "Alice Brown",
                "message": "Hey, how are you doing?",
                "timestamp": "2024-01-15T10:30:00",
                "type": "received",
                "read": True
            },
            {
                "id": str(uuid.uuid4()),
                "contact": "Bob Green",
                "message": "Meeting at 3 PM today",
                "timestamp": "2024-01-15T11:15:00",
                "type": "received",
                "read": True
            },
            {
                "id": str(uuid.uuid4()),
                "contact": "Carol White",
                "message": "Thanks for the help!",
                "timestamp": "2024-01-15T14:45:00",
                "type": "sent",
                "read": True
            }
        ]
        
    def simulate_transfer(self, transfer_id):
        """Simulate file transfer progress"""
        if transfer_id not in self.active_transfers:
            return
            
        transfer = self.active_transfers[transfer_id]
        total_steps = 10
        
        for step in range(total_steps + 1):
            if transfer_id not in self.active_transfers:
                break
                
            progress = step / total_steps
            transfer['progress'] = progress * 100
            transfer['transferred'] = int(transfer['total_size'] * progress)
            
            if step == total_steps:
                transfer['status'] = 'completed'
                transfer['end_time'] = datetime.now().isoformat()
            else:
                transfer['status'] = 'in_progress'
                
            # Emit progress update
            self.socketio.emit('transfer_progress', transfer)
            
            time.sleep(0.5)  # Simulate transfer time
            
        # Clean up completed transfer after a delay
        if transfer_id in self.active_transfers:
            threading.Timer(30.0, lambda: self.active_transfers.pop(transfer_id, None)).start()
            
    def simulate_sync(self, sync_id):
        """Simulate synchronization progress"""
        if sync_id not in self.sync_sessions:
            return
            
        sync = self.sync_sessions[sync_id]
        total_steps = 8
        
        steps = [
            "Analyzing data...",
            "Comparing timestamps...",
            "Identifying changes...",
            "Preparing sync...",
            "Transferring data...",
            "Updating indexes...",
            "Verifying integrity...",
            "Finalizing sync..."
        ]
        
        for i, step_desc in enumerate(steps):
            if sync_id not in self.sync_sessions:
                break
                
            progress = (i + 1) / total_steps
            sync['progress'] = progress * 100
            sync['current_step'] = step_desc
            sync['status'] = 'in_progress'
            
            # Emit progress update
            self.socketio.emit('sync_progress', sync)
            
            time.sleep(1.0)  # Simulate sync time
            
        # Complete sync
        if sync_id in self.sync_sessions:
            sync['status'] = 'completed'
            sync['end_time'] = datetime.now().isoformat()
            sync['progress'] = 100
            
            # Update device last sync time
            device_id = sync.get('device_id')
            if device_id in self.connected_devices:
                self.connected_devices[device_id]['last_sync'] = datetime.now().isoformat()
                
            self.socketio.emit('sync_completed', sync)
            
        # Clean up completed sync after a delay
        threading.Timer(60.0, lambda: self.sync_sessions.pop(sync_id, None)).start()
        
    def get_uptime(self):
        """Get server uptime"""
        if not hasattr(self, 'start_time'):
            self.start_time = datetime.now()
        
        uptime = datetime.now() - self.start_time
        return str(uptime).split('.')[0]  # Remove microseconds
        
    def run(self, debug=False):
        """Run the sync server"""
        print(f"Starting Phone-PC Sync Server on {self.host}:{self.port}")
        self.start_time = datetime.now()
        self.socketio.run(self.app, host=self.host, port=self.port, debug=debug)

if __name__ == "__main__":
    server = SyncServer()
    server.run(debug=True)