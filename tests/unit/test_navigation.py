"""
Unit tests for NavigationSystem
"""

import pytest
import math
from uav_assistant.navigation import NavigationSystem, Position, Waypoint


class TestNavigationSystem:
    """Test cases for NavigationSystem class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.nav = NavigationSystem()
    
    def test_initialization(self):
        """Test navigation system initialization"""
        assert self.nav.current_position is None
        assert self.nav.home_position is None
        assert len(self.nav.waypoints) == 0
    
    def test_set_home_position(self):
        """Test setting home position"""
        self.nav.set_home_position(47.3977, 8.5456, 408.0)
        assert self.nav.home_position is not None
        assert self.nav.home_position.latitude == 47.3977
        assert self.nav.home_position.longitude == 8.5456
        assert self.nav.home_position.altitude == 408.0
    
    def test_update_position(self):
        """Test updating current position"""
        self.nav.update_position(47.3977, 8.5456, 450.0)
        assert self.nav.current_position is not None
        assert self.nav.current_position.latitude == 47.3977
        assert self.nav.current_position.altitude == 450.0
    
    def test_add_waypoint(self):
        """Test adding waypoint"""
        pos = Position(47.3977, 8.5456, 450.0)
        wp = Waypoint(position=pos, speed=5.0)
        index = self.nav.add_waypoint(wp)
        assert index == 0
        assert len(self.nav.waypoints) == 1
    
    def test_clear_waypoints(self):
        """Test clearing waypoints"""
        pos = Position(47.3977, 8.5456, 450.0)
        wp = Waypoint(position=pos)
        self.nav.add_waypoint(wp)
        self.nav.clear_waypoints()
        assert len(self.nav.waypoints) == 0
    
    def test_distance_calculation(self):
        """Test distance calculation between two positions"""
        pos1 = Position(47.3977, 8.5456, 408.0)
        pos2 = Position(47.3977, 8.5456, 408.0)  # Same position
        distance = self.nav._calculate_distance(pos1, pos2)
        assert distance == pytest.approx(0.0, abs=0.1)
    
    def test_distance_with_altitude_difference(self):
        """Test distance calculation with altitude difference"""
        pos1 = Position(47.3977, 8.5456, 408.0)
        pos2 = Position(47.3977, 8.5456, 508.0)  # 100m higher
        distance = self.nav._calculate_distance(pos1, pos2)
        assert distance == pytest.approx(100.0, abs=0.1)
    
    def test_get_distance_to_waypoint(self):
        """Test getting distance to waypoint"""
        self.nav.update_position(47.3977, 8.5456, 408.0)
        pos = Position(47.3977, 8.5456, 508.0)
        wp = Waypoint(position=pos)
        self.nav.add_waypoint(wp)
        distance = self.nav.get_distance_to_waypoint(0)
        assert distance is not None
        assert distance == pytest.approx(100.0, abs=0.1)
    
    def test_get_distance_to_home(self):
        """Test getting distance to home"""
        self.nav.set_home_position(47.3977, 8.5456, 408.0)
        self.nav.update_position(47.3977, 8.5456, 508.0)
        distance = self.nav.get_distance_to_home()
        assert distance is not None
        assert distance == pytest.approx(100.0, abs=0.1)
    
    def test_bearing_calculation(self):
        """Test bearing calculation"""
        pos1 = Position(47.3977, 8.5456, 408.0)
        pos2 = Position(47.3977, 8.5556, 408.0)  # East
        bearing = self.nav._calculate_bearing(pos1, pos2)
        assert 80 < bearing < 100  # Should be roughly 90 degrees (East)
    
    def test_get_navigation_status(self):
        """Test getting navigation status"""
        status = self.nav.get_navigation_status()
        assert isinstance(status, dict)
        assert "current_position" in status
        assert "home_position" in status
        assert "waypoint_count" in status
        assert "current_waypoint" in status
