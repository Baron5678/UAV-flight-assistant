"""
UAV Flight Assistant - A comprehensive system for UAV flight management and control.

This package provides modules for:
- Flight control and planning
- Navigation and positioning
- Sensor data processing
- Communication interfaces
- Safety monitoring and management
"""

__version__ = "0.1.0"
__author__ = "Baron5678"

from .flight_control import FlightController
from .navigation import NavigationSystem
from .sensors import SensorManager
from .communication import CommunicationInterface
from .safety import SafetyMonitor

__all__ = [
    "FlightController",
    "NavigationSystem",
    "SensorManager",
    "CommunicationInterface",
    "SafetyMonitor",
]
