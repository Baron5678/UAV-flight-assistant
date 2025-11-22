"""
Unit tests for FlightController
"""

import pytest
from uav_assistant.flight_control import FlightController, FlightMode, FlightStatus


class TestFlightController:
    """Test cases for FlightController class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.controller = FlightController()
    
    def test_initialization(self):
        """Test controller initialization"""
        assert self.controller.mode == FlightMode.MANUAL
        assert self.controller.status == FlightStatus.IDLE
        assert self.controller.altitude == 0.0
        assert self.controller.speed == 0.0
    
    def test_arm_from_idle(self):
        """Test arming UAV from idle state"""
        result = self.controller.arm()
        assert result is True
        assert self.controller.status == FlightStatus.ARMED
    
    def test_arm_when_not_idle(self):
        """Test arming when not in idle state"""
        self.controller.status = FlightStatus.IN_FLIGHT
        result = self.controller.arm()
        assert result is False
    
    def test_disarm_when_armed(self):
        """Test disarming from armed state"""
        self.controller.arm()
        result = self.controller.disarm()
        assert result is True
        assert self.controller.status == FlightStatus.IDLE
    
    def test_disarm_when_in_flight(self):
        """Test disarming when in flight (should fail)"""
        self.controller.status = FlightStatus.IN_FLIGHT
        result = self.controller.disarm()
        assert result is False
    
    def test_takeoff_when_armed(self):
        """Test takeoff from armed state"""
        self.controller.arm()
        result = self.controller.takeoff(10.0)
        assert result is True
        assert self.controller.status == FlightStatus.TAKING_OFF
    
    def test_takeoff_when_not_armed(self):
        """Test takeoff when not armed (should fail)"""
        result = self.controller.takeoff(10.0)
        assert result is False
    
    def test_land_when_in_flight(self):
        """Test landing from in-flight state"""
        self.controller.status = FlightStatus.IN_FLIGHT
        result = self.controller.land()
        assert result is True
        assert self.controller.status == FlightStatus.LANDING
    
    def test_land_when_not_in_flight(self):
        """Test landing when not in flight (should fail)"""
        result = self.controller.land()
        assert result is False
    
    def test_set_mode(self):
        """Test changing flight mode"""
        result = self.controller.set_mode(FlightMode.AUTO)
        assert result is True
        assert self.controller.mode == FlightMode.AUTO
    
    def test_goto_position_when_in_flight(self):
        """Test navigation command when in flight"""
        self.controller.status = FlightStatus.IN_FLIGHT
        result = self.controller.goto_position(47.3977, 8.5456, 50.0)
        assert result is True
    
    def test_goto_position_when_not_in_flight(self):
        """Test navigation command when not in flight (should fail)"""
        result = self.controller.goto_position(47.3977, 8.5456, 50.0)
        assert result is False
    
    def test_get_status(self):
        """Test getting flight status"""
        status = self.controller.get_status()
        assert isinstance(status, dict)
        assert "mode" in status
        assert "status" in status
        assert "altitude" in status
        assert "speed" in status
        assert "heading" in status
