"""
Unit tests for SafetyMonitor
"""

import pytest
from uav_assistant.safety import SafetyMonitor, SafetyLevel, SafetyCheck, SafetyAlert


class TestSafetyMonitor:
    """Test cases for SafetyMonitor class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.monitor = SafetyMonitor()
    
    def test_initialization(self):
        """Test safety monitor initialization"""
        assert len(self.monitor.active_alerts) == 0
        assert self.monitor.min_battery_voltage == 10.5
        assert self.monitor.critical_battery_percentage == 20.0
    
    def test_battery_safe(self):
        """Test battery check with safe values"""
        level = self.monitor.check_battery(12.6, 100.0)
        assert level == SafetyLevel.SAFE
        assert len(self.monitor.active_alerts) == 0
    
    def test_battery_warning(self):
        """Test battery check with warning level"""
        level = self.monitor.check_battery(11.5, 25.0)
        assert level == SafetyLevel.WARNING
        assert len(self.monitor.active_alerts) == 1
    
    def test_battery_critical(self):
        """Test battery check with critical level"""
        level = self.monitor.check_battery(10.0, 15.0)
        assert level == SafetyLevel.CRITICAL
        assert len(self.monitor.active_alerts) == 1
        assert self.monitor.active_alerts[0].check_type == SafetyCheck.BATTERY
    
    def test_gps_safe(self):
        """Test GPS check with safe values"""
        level = self.monitor.check_gps(10, 1.5)
        assert level == SafetyLevel.SAFE
    
    def test_gps_insufficient_satellites(self):
        """Test GPS check with insufficient satellites"""
        level = self.monitor.check_gps(4, 2.0)
        assert level == SafetyLevel.WARNING
        assert len(self.monitor.active_alerts) == 1
    
    def test_gps_poor_accuracy(self):
        """Test GPS check with poor accuracy"""
        level = self.monitor.check_gps(8, 6.0)
        assert level == SafetyLevel.WARNING
    
    def test_altitude_safe(self):
        """Test altitude check with safe value"""
        level = self.monitor.check_altitude(50.0)
        assert level == SafetyLevel.SAFE
    
    def test_altitude_exceeded(self):
        """Test altitude check when limit exceeded"""
        level = self.monitor.check_altitude(150.0)
        assert level == SafetyLevel.WARNING
        assert len(self.monitor.active_alerts) == 1
    
    def test_geofence_safe(self):
        """Test geofence check within limits"""
        self.monitor.geofence_enabled = True
        level = self.monitor.check_geofence(500.0)
        assert level == SafetyLevel.SAFE
    
    def test_geofence_breach(self):
        """Test geofence breach"""
        self.monitor.geofence_enabled = True
        level = self.monitor.check_geofence(1500.0)
        assert level == SafetyLevel.CRITICAL
        assert len(self.monitor.active_alerts) == 1
    
    def test_geofence_disabled(self):
        """Test geofence check when disabled"""
        self.monitor.geofence_enabled = False
        level = self.monitor.check_geofence(2000.0)
        assert level == SafetyLevel.SAFE
    
    def test_clear_alert(self):
        """Test clearing specific alert type"""
        self.monitor.check_battery(10.0, 15.0)
        assert len(self.monitor.active_alerts) == 1
        self.monitor.clear_alert(SafetyCheck.BATTERY)
        assert len(self.monitor.active_alerts) == 0
    
    def test_clear_all_alerts(self):
        """Test clearing all alerts"""
        self.monitor.check_battery(10.0, 15.0)
        self.monitor.check_gps(4, 2.0)
        assert len(self.monitor.active_alerts) > 0
        self.monitor.clear_all_alerts()
        assert len(self.monitor.active_alerts) == 0
    
    def test_get_overall_safety_status_safe(self):
        """Test overall status when safe"""
        status = self.monitor.get_overall_safety_status()
        assert status == SafetyLevel.SAFE
    
    def test_get_overall_safety_status_warning(self):
        """Test overall status with warning"""
        self.monitor.check_battery(11.5, 25.0)
        status = self.monitor.get_overall_safety_status()
        assert status == SafetyLevel.WARNING
    
    def test_get_overall_safety_status_critical(self):
        """Test overall status with critical alert"""
        self.monitor.check_battery(10.0, 15.0)
        status = self.monitor.get_overall_safety_status()
        assert status == SafetyLevel.CRITICAL
    
    def test_safety_report(self):
        """Test getting safety report"""
        report = self.monitor.get_safety_report()
        assert isinstance(report, dict)
        assert "overall_status" in report
        assert "active_alerts" in report
        assert "thresholds" in report
    
    def test_alert_callback(self):
        """Test alert callback registration and execution"""
        callback_called = []
        
        def test_callback(alert):
            callback_called.append(alert)
        
        self.monitor.register_alert_callback(test_callback)
        self.monitor.check_battery(10.0, 15.0)
        
        assert len(callback_called) == 1
        assert isinstance(callback_called[0], SafetyAlert)
