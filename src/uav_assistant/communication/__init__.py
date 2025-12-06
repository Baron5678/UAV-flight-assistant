"""
Communication Module

Handles communication interfaces including:
- Ground station communication
- Telemetry data transmission
- Command reception
- Data logging
"""

from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import json


class MessageType(Enum):
    """Message type enumeration"""
    TELEMETRY = "telemetry"
    COMMAND = "command"
    STATUS = "status"
    ALERT = "alert"
    LOG = "log"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Message:
    """Communication message"""
    type: MessageType
    priority: MessagePriority
    payload: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps({
            "type": self.type.value,
            "priority": self.priority.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat()
        })


class CommunicationInterface:
    """
    Communication interface for UAV data transmission and command reception.
    
    Manages message queues, telemetry streaming, and command handling.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the communication interface.
        
        Args:
            config: Configuration dictionary for communication parameters
        """
        self.config = config or {}
        self.connected = False
        self.message_queue: list = []
        self.command_handlers: Dict[str, Callable] = {}
        self.telemetry_interval = self.config.get("telemetry_interval", 1.0)
        self.logger = logging.getLogger(__name__)
    
    def connect(self, connection_string: str) -> bool:
        """
        Establish connection with ground station.
        
        Args:
            connection_string: Connection string (e.g., "tcp://127.0.0.1:5760")
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        # In a real implementation, this would establish actual connection
        self.connected = True
        self.logger.info(f"Connected to {connection_string}")
        return True
    
    def disconnect(self) -> None:
        """Disconnect from ground station."""
        self.connected = False
        self.logger.info("Disconnected from ground station")
    
    def send_message(self, message: Message) -> bool:
        """
        Send a message to the ground station.
        
        Args:
            message: Message to send
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.connected:
            self.logger.error("Cannot send message: not connected")
            return False
        
        self.message_queue.append(message)
        self.logger.debug(f"Message queued: {message.type.value}")
        return True
    
    def send_telemetry(self, telemetry_data: Dict) -> bool:
        """
        Send telemetry data to ground station.
        
        Args:
            telemetry_data: Dictionary containing telemetry information
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        message = Message(
            type=MessageType.TELEMETRY,
            priority=MessagePriority.NORMAL,
            payload=telemetry_data
        )
        return self.send_message(message)
    
    def send_status(self, status_data: Dict) -> bool:
        """
        Send status update to ground station.
        
        Args:
            status_data: Dictionary containing status information
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        message = Message(
            type=MessageType.STATUS,
            priority=MessagePriority.NORMAL,
            payload=status_data
        )
        return self.send_message(message)
    
    def send_alert(self, alert_message: str, severity: str = "warning") -> bool:
        """
        Send alert to ground station.
        
        Args:
            alert_message: Alert message text
            severity: Severity level (info, warning, error, critical)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        priority_map = {
            "info": MessagePriority.LOW,
            "warning": MessagePriority.NORMAL,
            "error": MessagePriority.HIGH,
            "critical": MessagePriority.CRITICAL
        }
        
        message = Message(
            type=MessageType.ALERT,
            priority=priority_map.get(severity, MessagePriority.NORMAL),
            payload={"message": alert_message, "severity": severity}
        )
        return self.send_message(message)
    
    def register_command_handler(self, command: str, handler: Callable) -> None:
        """
        Register a handler for a specific command.
        
        Args:
            command: Command name
            handler: Function to handle the command
        """
        self.command_handlers[command] = handler
        self.logger.info(f"Handler registered for command: {command}")
    
    def handle_command(self, command: str, parameters: Dict) -> bool:
        """
        Handle an incoming command.
        
        Args:
            command: Command name
            parameters: Command parameters
            
        Returns:
            bool: True if command handled successfully, False otherwise
        """
        handler = self.command_handlers.get(command)
        if handler is None:
            self.logger.warning(f"No handler for command: {command}")
            return False
        
        try:
            handler(parameters)
            self.logger.info(f"Command executed: {command}")
            return True
        except Exception as e:
            self.logger.error(f"Error executing command {command}: {e}")
            return False
    
    def get_message_queue_size(self) -> int:
        """
        Get the current size of the message queue.
        
        Returns:
            int: Number of messages in queue
        """
        return len(self.message_queue)
    
    def clear_message_queue(self) -> None:
        """Clear all messages from the queue."""
        self.message_queue.clear()
        self.logger.info("Message queue cleared")
    
    def is_connected(self) -> bool:
        """
        Check if connected to ground station.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.connected
