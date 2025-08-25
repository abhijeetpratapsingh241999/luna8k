"""
Protocol Manager
Handles different synchronization protocols
"""

import time
import random
from typing import Dict, List, Optional
from enum import Enum

from ..models.device import ConnectionType


class ProtocolType(Enum):
    """Protocol types"""
    USB = "usb"
    BLUETOOTH = "bluetooth"
    WIFI = "wifi"
    NFC = "nfc"


class ProtocolStatus(Enum):
    """Protocol status"""
    AVAILABLE = "available"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    DISCONNECTED = "disconnected"


class ProtocolManager:
    """Manages different synchronization protocols"""
    
    def __init__(self, config):
        self.config = config
        self.protocols: Dict[ProtocolType, Dict] = {}
        self.active_protocol: Optional[ProtocolType] = None
        
        self._initialize_protocols()
    
    def _initialize_protocols(self):
        """Initialize available protocols"""
        self.protocols = {
            ProtocolType.USB: {
                "status": ProtocolStatus.AVAILABLE,
                "speed": 480.0,  # Mbps
                "reliability": 0.99,
                "power_consumption": "low",
                "range": "cable",
                "security": "high",
                "compatibility": "universal"
            },
            ProtocolType.BLUETOOTH: {
                "status": ProtocolStatus.AVAILABLE,
                "speed": 24.0,  # Mbps
                "reliability": 0.85,
                "power_consumption": "medium",
                "range": "10m",
                "security": "medium",
                "compatibility": "high"
            },
            ProtocolType.WIFI: {
                "status": ProtocolStatus.AVAILABLE,
                "speed": 100.0,  # Mbps
                "reliability": 0.90,
                "power_consumption": "high",
                "range": "50m",
                "security": "high",
                "compatibility": "high"
            },
            ProtocolType.NFC: {
                "status": ProtocolStatus.AVAILABLE,
                "speed": 0.424,  # Mbps
                "reliability": 0.95,
                "range": "4cm",
                "power_consumption": "very_low",
                "security": "very_high",
                "compatibility": "medium"
            }
        }
    
    def get_available_protocols(self) -> List[ProtocolType]:
        """Get list of available protocols"""
        return [pt for pt, info in self.protocols.items() 
                if info["status"] == ProtocolStatus.AVAILABLE]
    
    def get_protocol_info(self, protocol_type: ProtocolType) -> Dict:
        """Get information about a specific protocol"""
        return self.protocols.get(protocol_type, {})
    
    def connect_protocol(self, protocol_type: ProtocolType) -> bool:
        """Connect using a specific protocol"""
        if protocol_type not in self.protocols:
            return False
        
        protocol_info = self.protocols[protocol_type]
        
        if protocol_info["status"] != ProtocolStatus.AVAILABLE:
            return False
        
        try:
            # Simulate connection process
            protocol_info["status"] = ProtocolStatus.CONNECTING
            
            # Simulate connection delay
            connection_time = self._calculate_connection_time(protocol_type)
            time.sleep(connection_time)
            
            # Simulate connection success/failure
            success_rate = protocol_info["reliability"]
            if random.random() < success_rate:
                protocol_info["status"] = ProtocolStatus.CONNECTED
                self.active_protocol = protocol_type
                return True
            else:
                protocol_info["status"] = ProtocolStatus.ERROR
                return False
                
        except Exception as e:
            protocol_info["status"] = ProtocolStatus.ERROR
            return False
    
    def disconnect_protocol(self, protocol_type: ProtocolType):
        """Disconnect a protocol"""
        if protocol_type in self.protocols:
            self.protocols[protocol_type]["status"] = ProtocolStatus.AVAILABLE
            
            if self.active_protocol == protocol_type:
                self.active_protocol = None
    
    def get_connection_speed(self, protocol_type: ProtocolType) -> float:
        """Get the current connection speed for a protocol"""
        if protocol_type not in self.protocols:
            return 0.0
        
        protocol_info = self.protocols[protocol_type]
        base_speed = protocol_info["speed"]
        
        # Apply realistic variations
        if protocol_info["status"] == ProtocolStatus.CONNECTED:
            # Simulate speed variations based on conditions
            variation = random.uniform(0.7, 1.1)
            return base_speed * variation
        else:
            return 0.0
    
    def get_protocol_recommendation(self, file_size: int, priority: int) -> ProtocolType:
        """Get protocol recommendation based on file size and priority"""
        recommendations = []
        
        for protocol_type, info in self.protocols.items():
            if info["status"] == ProtocolStatus.AVAILABLE:
                score = 0
                
                # Score based on file size
                if file_size < 10 * 1024 * 1024:  # < 10 MB
                    if protocol_type == ProtocolType.USB:
                        score += 10
                    elif protocol_type == ProtocolType.BLUETOOTH:
                        score += 8
                    elif protocol_type == ProtocolType.WIFI:
                        score += 6
                    elif protocol_type == ProtocolType.NFC:
                        score += 4
                
                elif file_size < 100 * 1024 * 1024:  # < 100 MB
                    if protocol_type == ProtocolType.USB:
                        score += 10
                    elif protocol_type == ProtocolType.WIFI:
                        score += 8
                    elif protocol_type == ProtocolType.BLUETOOTH:
                        score += 5
                
                else:  # Large files
                    if protocol_type == ProtocolType.USB:
                        score += 10
                    elif protocol_type == ProtocolType.WIFI:
                        score += 7
                    elif protocol_type == ProtocolType.BLUETOOTH:
                        score += 3
                
                # Score based on priority
                if priority >= 8:  # High priority
                    if protocol_type == ProtocolType.USB:
                        score += 5
                    elif protocol_type == ProtocolType.WIFI:
                        score += 3
                
                # Score based on reliability
                score += int(info["reliability"] * 10)
                
                recommendations.append((protocol_type, score))
        
        # Sort by score and return the best
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[0][0] if recommendations else ProtocolType.USB
    
    def simulate_protocol_issues(self):
        """Simulate realistic protocol issues"""
        for protocol_type, info in self.protocols.items():
            if info["status"] == ProtocolStatus.CONNECTED:
                # Simulate occasional disconnections
                if random.random() < 0.001:  # 0.1% chance
                    info["status"] = ProtocolStatus.ERROR
                    if self.active_protocol == protocol_type:
                        self.active_protocol = None
                
                # Simulate speed fluctuations
                elif random.random() < 0.1:  # 10% chance
                    # Temporary speed reduction
                    pass
    
    def get_protocol_statistics(self) -> Dict:
        """Get protocol usage statistics"""
        stats = {}
        
        for protocol_type, info in self.protocols.items():
            stats[protocol_type.value] = {
                "status": info["status"].value,
                "speed": info["speed"],
                "reliability": info["reliability"],
                "is_active": protocol_type == self.active_protocol
            }
        
        return stats
    
    def _calculate_connection_time(self, protocol_type: ProtocolType) -> float:
        """Calculate realistic connection time for a protocol"""
        base_times = {
            ProtocolType.USB: 0.5,
            ProtocolType.BLUETOOTH: 2.0,
            ProtocolType.WIFI: 1.5,
            ProtocolType.NFC: 0.1
        }
        
        base_time = base_times.get(protocol_type, 1.0)
        
        # Add some randomness
        variation = random.uniform(0.8, 1.5)
        
        return base_time * variation
    
    def reset_all_protocols(self):
        """Reset all protocols to available status"""
        for protocol_info in self.protocols.values():
            protocol_info["status"] = ProtocolStatus.AVAILABLE
        
        self.active_protocol = None