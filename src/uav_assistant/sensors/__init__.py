"""
Sensor Management Module

Handles sensor data collection and processing including:
- IMU (Inertial Measurement Unit) data
- GPS data
- Barometer readings
- Battery monitoring
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging


# Constants
GPS_NO_FIX_HDOP = 99.99  # HDOP value indicating no GPS fix available


class SensorType(Enum):
    """Sensor type enumeration"""
    IMU = "imu"
    GPS = "gps"
    BAROMETER = "barometer"
    BATTERY = "battery"
    COMPASS = "compass"
    ULTRASONIC = "ultrasonic"


@dataclass
class IMUData:
    """IMU sensor data"""
    acceleration_x: float  # m/s^2
    acceleration_y: float
    acceleration_z: float
    gyro_x: float  # rad/s
    gyro_y: float
    gyro_z: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class GPSData:
    """GPS sensor data"""
    latitude: float
    longitude: float
    altitude: float  # meters
    speed: float  # m/s
    satellites: int
    hdop: float  # Horizontal dilution of precision
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class BarometerData:
    """Barometer sensor data"""
    pressure: float  # hPa
    temperature: float  # Celsius
    altitude: float  # meters (calculated from pressure)
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class BatteryData:
    """Battery sensor data"""
    voltage: float  # Volts
    current: float  # Amperes
    remaining: float  # Percentage (0-100)
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class SensorManager:
    """
    Manages all sensors and their data collection.
    
    Provides interfaces for reading sensor data and monitoring sensor health.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the sensor manager.
        
        Args:
            config: Configuration dictionary for sensor parameters
        """
        self.config = config or {}
        self.sensors: Dict[SensorType, bool] = {}
        self.last_imu_data: Optional[IMUData] = None
        self.last_gps_data: Optional[GPSData] = None
        self.last_barometer_data: Optional[BarometerData] = None
        self.last_battery_data: Optional[BatteryData] = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize sensor availability
        self._initialize_sensors()
    
    def _initialize_sensors(self) -> None:
        """Initialize and detect available sensors."""
        # In a real implementation, this would detect actual hardware
        self.sensors = {
            SensorType.IMU: True,
            SensorType.GPS: True,
            SensorType.BAROMETER: True,
            SensorType.BATTERY: True,
            SensorType.COMPASS: True,
            SensorType.ULTRASONIC: False
        }
        self.logger.info("Sensors initialized")
    
    def is_sensor_available(self, sensor_type: SensorType) -> bool:
        """
        Check if a sensor is available.
        
        Args:
            sensor_type: Type of sensor to check
            
        Returns:
            bool: True if sensor is available, False otherwise
        """
        return self.sensors.get(sensor_type, False)
    
    def read_imu(self) -> Optional[IMUData]:
        """
        Read IMU sensor data.
        
        Returns:
            IMUData: Current IMU readings, or None if unavailable
        """
        if not self.is_sensor_available(SensorType.IMU):
            return None
        
        # In a real implementation, this would read from actual hardware
        # For now, return simulated data
        data = IMUData(
            acceleration_x=0.0,
            acceleration_y=0.0,
            acceleration_z=9.81,
            gyro_x=0.0,
            gyro_y=0.0,
            gyro_z=0.0
        )
        self.last_imu_data = data
        return data
    
    def read_gps(self) -> Optional[GPSData]:
        """
        Read GPS sensor data.
        
        Returns:
            GPSData: Current GPS readings, or None if unavailable
        """
        if not self.is_sensor_available(SensorType.GPS):
            return None
        
        # In a real implementation, this would read from actual hardware
        data = GPSData(
            latitude=0.0,
            longitude=0.0,
            altitude=0.0,
            speed=0.0,
            satellites=0,
            hdop=GPS_NO_FIX_HDOP  # Indicates no GPS fix
        )
        self.last_gps_data = data
        return data
    
    def read_barometer(self) -> Optional[BarometerData]:
        """
        Read barometer sensor data.
        
        Returns:
            BarometerData: Current barometer readings, or None if unavailable
        """
        if not self.is_sensor_available(SensorType.BAROMETER):
            return None
        
        # In a real implementation, this would read from actual hardware
        data = BarometerData(
            pressure=1013.25,
            temperature=20.0,
            altitude=0.0
        )
        self.last_barometer_data = data
        return data
    
    def read_battery(self) -> Optional[BatteryData]:
        """
        Read battery sensor data.
        
        Returns:
            BatteryData: Current battery readings, or None if unavailable
        """
        if not self.is_sensor_available(SensorType.BATTERY):
            return None
        
        # In a real implementation, this would read from actual hardware
        data = BatteryData(
            voltage=12.6,
            current=0.0,
            remaining=100.0
        )
        self.last_battery_data = data
        return data
    
    def get_all_sensor_data(self) -> Dict:
        """
        Get data from all available sensors.
        
        Returns:
            Dict: Dictionary containing all sensor readings
        """
        return {
            "imu": self.read_imu(),
            "gps": self.read_gps(),
            "barometer": self.read_barometer(),
            "battery": self.read_battery()
        }
    
    def get_sensor_health(self) -> Dict:
        """
        Get health status of all sensors.
        
        Returns:
            Dict: Dictionary containing sensor health information
        """
        health = {}
        for sensor_type, available in self.sensors.items():
            health[sensor_type.value] = {
                "available": available,
                "status": "OK" if available else "UNAVAILABLE"
            }
        return health
