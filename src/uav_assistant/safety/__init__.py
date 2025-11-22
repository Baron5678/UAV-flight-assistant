"""
Safety Module

Handles safety monitoring and emergency procedures including:
- Battery level monitoring
- GPS signal quality
- Geofence boundaries
- Emergency landing procedures
- Collision avoidance
"""

from typing import Dict, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import logging


class SafetyLevel(Enum):
    """Safety alert level enumeration"""
    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class SafetyCheck(Enum):
    """Safety check types"""
    BATTERY = "battery"
    GPS = "gps"
    ALTITUDE = "altitude"
    GEOFENCE = "geofence"
    CONNECTION = "connection"
    SENSORS = "sensors"


@dataclass
class SafetyAlert:
    """Safety alert information"""
    check_type: SafetyCheck
    level: SafetyLevel
    message: str
    details: Dict = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class SafetyMonitor:
    """
    Safety monitoring system for UAV operations.
    
    Continuously monitors critical parameters and triggers alerts or
    emergency procedures when necessary.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the safety monitor.
        
        Args:
            config: Configuration dictionary for safety parameters
        """
        self.config = config or {}
        self.active_alerts: List[SafetyAlert] = []
        self.alert_callbacks: List[Callable] = []
        self.logger = logging.getLogger(__name__)
        
        # Safety thresholds
        self.min_battery_voltage = self.config.get("min_battery_voltage", 10.5)
        self.critical_battery_percentage = self.config.get("critical_battery", 20.0)
        self.warning_battery_percentage = self.config.get("warning_battery", 30.0)
        self.max_altitude = self.config.get("max_altitude", 120.0)  # meters
        self.min_gps_satellites = self.config.get("min_gps_satellites", 6)
        self.geofence_enabled = self.config.get("geofence_enabled", False)
        self.geofence_radius = self.config.get("geofence_radius", 1000.0)  # meters
    
    def check_battery(self, voltage: float, percentage: float) -> SafetyLevel:
        """
        Check battery safety status.
        
        Args:
            voltage: Battery voltage
            percentage: Battery percentage
            
        Returns:
            SafetyLevel: Current safety level for battery
        """
        if voltage < self.min_battery_voltage or percentage < self.critical_battery_percentage:
            alert = SafetyAlert(
                check_type=SafetyCheck.BATTERY,
                level=SafetyLevel.CRITICAL,
                message=f"Critical battery level: {percentage:.1f}%",
                details={"voltage": voltage, "percentage": percentage}
            )
            self._trigger_alert(alert)
            return SafetyLevel.CRITICAL
        
        elif percentage < self.warning_battery_percentage:
            alert = SafetyAlert(
                check_type=SafetyCheck.BATTERY,
                level=SafetyLevel.WARNING,
                message=f"Low battery warning: {percentage:.1f}%",
                details={"voltage": voltage, "percentage": percentage}
            )
            self._trigger_alert(alert)
            return SafetyLevel.WARNING
        
        return SafetyLevel.SAFE
    
    def check_gps(self, satellites: int, hdop: float) -> SafetyLevel:
        """
        Check GPS signal quality.
        
        Args:
            satellites: Number of satellites
            hdop: Horizontal dilution of precision
            
        Returns:
            SafetyLevel: Current safety level for GPS
        """
        if satellites < self.min_gps_satellites:
            alert = SafetyAlert(
                check_type=SafetyCheck.GPS,
                level=SafetyLevel.WARNING,
                message=f"Insufficient GPS satellites: {satellites}",
                details={"satellites": satellites, "hdop": hdop}
            )
            self._trigger_alert(alert)
            return SafetyLevel.WARNING
        
        if hdop > 5.0:
            alert = SafetyAlert(
                check_type=SafetyCheck.GPS,
                level=SafetyLevel.WARNING,
                message=f"Poor GPS accuracy: HDOP {hdop:.2f}",
                details={"satellites": satellites, "hdop": hdop}
            )
            self._trigger_alert(alert)
            return SafetyLevel.WARNING
        
        return SafetyLevel.SAFE
    
    def check_altitude(self, current_altitude: float) -> SafetyLevel:
        """
        Check if altitude is within safe limits.
        
        Args:
            current_altitude: Current altitude in meters
            
        Returns:
            SafetyLevel: Current safety level for altitude
        """
        if current_altitude > self.max_altitude:
            alert = SafetyAlert(
                check_type=SafetyCheck.ALTITUDE,
                level=SafetyLevel.WARNING,
                message=f"Maximum altitude exceeded: {current_altitude:.1f}m",
                details={"altitude": current_altitude, "limit": self.max_altitude}
            )
            self._trigger_alert(alert)
            return SafetyLevel.WARNING
        
        return SafetyLevel.SAFE
    
    def check_geofence(self, distance_from_home: float) -> SafetyLevel:
        """
        Check if UAV is within geofence boundaries.
        
        Args:
            distance_from_home: Distance from home position in meters
            
        Returns:
            SafetyLevel: Current safety level for geofence
        """
        if not self.geofence_enabled:
            return SafetyLevel.SAFE
        
        if distance_from_home > self.geofence_radius:
            alert = SafetyAlert(
                check_type=SafetyCheck.GEOFENCE,
                level=SafetyLevel.CRITICAL,
                message=f"Geofence breach: {distance_from_home:.1f}m from home",
                details={"distance": distance_from_home, "limit": self.geofence_radius}
            )
            self._trigger_alert(alert)
            return SafetyLevel.CRITICAL
        
        return SafetyLevel.SAFE
    
    def register_alert_callback(self, callback: Callable) -> None:
        """
        Register a callback function for safety alerts.
        
        Args:
            callback: Function to call when alert is triggered
        """
        self.alert_callbacks.append(callback)
        self.logger.info("Alert callback registered")
    
    def _trigger_alert(self, alert: SafetyAlert) -> None:
        """
        Trigger a safety alert.
        
        Args:
            alert: Safety alert to trigger
        """
        # Check if this alert is already active
        for active_alert in self.active_alerts:
            if (active_alert.check_type == alert.check_type and
                active_alert.level == alert.level):
                return  # Don't duplicate alerts
        
        self.active_alerts.append(alert)
        self.logger.warning(f"Safety alert: {alert.message}")
        
        # Call registered callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
    
    def clear_alert(self, check_type: SafetyCheck) -> None:
        """
        Clear alerts for a specific check type.
        
        Args:
            check_type: Type of safety check to clear
        """
        self.active_alerts = [
            alert for alert in self.active_alerts
            if alert.check_type != check_type
        ]
        self.logger.info(f"Cleared alerts for {check_type.value}")
    
    def clear_all_alerts(self) -> None:
        """Clear all active alerts."""
        self.active_alerts.clear()
        self.logger.info("All alerts cleared")
    
    def get_active_alerts(self) -> List[SafetyAlert]:
        """
        Get list of active safety alerts.
        
        Returns:
            List[SafetyAlert]: List of active alerts
        """
        return self.active_alerts.copy()
    
    def get_overall_safety_status(self) -> SafetyLevel:
        """
        Get overall safety status based on active alerts.
        
        Returns:
            SafetyLevel: Overall safety level
        """
        if not self.active_alerts:
            return SafetyLevel.SAFE
        
        # Return the highest severity level among active alerts
        levels = [alert.level for alert in self.active_alerts]
        if SafetyLevel.EMERGENCY in levels:
            return SafetyLevel.EMERGENCY
        elif SafetyLevel.CRITICAL in levels:
            return SafetyLevel.CRITICAL
        elif SafetyLevel.WARNING in levels:
            return SafetyLevel.WARNING
        
        return SafetyLevel.SAFE
    
    def get_safety_report(self) -> Dict:
        """
        Get comprehensive safety report.
        
        Returns:
            Dict: Safety status report
        """
        return {
            "overall_status": self.get_overall_safety_status().value,
            "active_alerts": [
                {
                    "type": alert.check_type.value,
                    "level": alert.level.value,
                    "message": alert.message,
                    "details": alert.details
                }
                for alert in self.active_alerts
            ],
            "thresholds": {
                "min_battery_voltage": self.min_battery_voltage,
                "critical_battery_percentage": self.critical_battery_percentage,
                "max_altitude": self.max_altitude,
                "min_gps_satellites": self.min_gps_satellites,
                "geofence_enabled": self.geofence_enabled,
                "geofence_radius": self.geofence_radius
            }
        }
