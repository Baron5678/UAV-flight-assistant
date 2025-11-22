"""
Navigation Module

Handles UAV navigation and positioning including:
- GPS processing
- Waypoint management
- Path planning
- Position estimation
"""

from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import math
import logging


# Constants
EARTH_RADIUS_METERS = 6371000  # Earth's radius in meters


@dataclass
class Position:
    """Represents a geographic position"""
    latitude: float
    longitude: float
    altitude: float
    
    def __str__(self):
        return f"({self.latitude:.6f}, {self.longitude:.6f}, {self.altitude:.1f}m)"


@dataclass
class Waypoint:
    """Represents a waypoint in a flight path"""
    position: Position
    speed: float = 5.0  # m/s
    hold_time: float = 0.0  # seconds
    action: Optional[str] = None
    
    def __str__(self):
        return f"Waypoint at {self.position}"


class NavigationSystem:
    """
    Navigation system for UAV path planning and position tracking.
    
    Manages waypoints, calculates distances, and handles path planning.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the navigation system.
        
        Args:
            config: Configuration dictionary for navigation parameters
        """
        self.config = config or {}
        self.current_position: Optional[Position] = None
        self.home_position: Optional[Position] = None
        self.waypoints: List[Waypoint] = []
        self.current_waypoint_index = 0
        self.logger = logging.getLogger(__name__)
    
    def set_home_position(self, latitude: float, longitude: float, 
                          altitude: float = 0.0) -> None:
        """
        Set the home position for the UAV.
        
        Args:
            latitude: Home latitude
            longitude: Home longitude
            altitude: Home altitude in meters
        """
        self.home_position = Position(latitude, longitude, altitude)
        self.logger.info(f"Home position set to {self.home_position}")
    
    def update_position(self, latitude: float, longitude: float, 
                        altitude: float) -> None:
        """
        Update current UAV position.
        
        Args:
            latitude: Current latitude
            longitude: Current longitude
            altitude: Current altitude in meters
        """
        self.current_position = Position(latitude, longitude, altitude)
        self.logger.debug(f"Position updated to {self.current_position}")
    
    def add_waypoint(self, waypoint: Waypoint) -> int:
        """
        Add a waypoint to the flight path.
        
        Args:
            waypoint: Waypoint to add
            
        Returns:
            int: Index of the added waypoint
        """
        self.waypoints.append(waypoint)
        self.logger.info(f"Waypoint added: {waypoint}")
        return len(self.waypoints) - 1
    
    def clear_waypoints(self) -> None:
        """Clear all waypoints from the flight path."""
        self.waypoints.clear()
        self.current_waypoint_index = 0
        self.logger.info("All waypoints cleared")
    
    def get_distance_to_waypoint(self, waypoint_index: int) -> Optional[float]:
        """
        Calculate distance to a specific waypoint.
        
        Args:
            waypoint_index: Index of the waypoint
            
        Returns:
            float: Distance in meters, or None if calculation not possible
        """
        if not self.current_position or waypoint_index >= len(self.waypoints):
            return None
        
        waypoint = self.waypoints[waypoint_index]
        return self._calculate_distance(
            self.current_position, 
            waypoint.position
        )
    
    def get_distance_to_home(self) -> Optional[float]:
        """
        Calculate distance to home position.
        
        Returns:
            float: Distance in meters, or None if calculation not possible
        """
        if not self.current_position or not self.home_position:
            return None
        
        return self._calculate_distance(
            self.current_position,
            self.home_position
        )
    
    def _calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """
        Calculate distance between two positions using Haversine formula.
        
        Args:
            pos1: First position
            pos2: Second position
            
        Returns:
            float: Distance in meters
        """
        # Convert to radians
        lat1 = math.radians(pos1.latitude)
        lat2 = math.radians(pos2.latitude)
        dlat = math.radians(pos2.latitude - pos1.latitude)
        dlon = math.radians(pos2.longitude - pos1.longitude)
        
        # Haversine formula
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        # Horizontal distance
        horizontal_distance = EARTH_RADIUS_METERS * c
        
        # Include altitude difference
        altitude_diff = pos2.altitude - pos1.altitude
        
        # Total 3D distance
        return math.sqrt(horizontal_distance ** 2 + altitude_diff ** 2)
    
    def get_bearing_to_waypoint(self, waypoint_index: int) -> Optional[float]:
        """
        Calculate bearing to a specific waypoint.
        
        Args:
            waypoint_index: Index of the waypoint
            
        Returns:
            float: Bearing in degrees (0-360), or None if calculation not possible
        """
        if not self.current_position or waypoint_index >= len(self.waypoints):
            return None
        
        waypoint = self.waypoints[waypoint_index]
        return self._calculate_bearing(
            self.current_position,
            waypoint.position
        )
    
    def _calculate_bearing(self, pos1: Position, pos2: Position) -> float:
        """
        Calculate bearing from pos1 to pos2.
        
        Args:
            pos1: Starting position
            pos2: Target position
            
        Returns:
            float: Bearing in degrees (0-360)
        """
        lat1 = math.radians(pos1.latitude)
        lat2 = math.radians(pos2.latitude)
        dlon = math.radians(pos2.longitude - pos1.longitude)
        
        y = math.sin(dlon) * math.cos(lat2)
        x = (math.cos(lat1) * math.sin(lat2) -
             math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
        
        bearing = math.atan2(y, x)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360
        
        return bearing
    
    def get_navigation_status(self) -> Dict:
        """
        Get current navigation status.
        
        Returns:
            Dict: Current navigation information
        """
        return {
            "current_position": str(self.current_position) if self.current_position else None,
            "home_position": str(self.home_position) if self.home_position else None,
            "waypoint_count": len(self.waypoints),
            "current_waypoint": self.current_waypoint_index,
            "distance_to_home": self.get_distance_to_home()
        }
