"""
Example usage of UAV Flight Assistant

This example demonstrates basic usage of the UAV flight assistant system,
including initialization, flight planning, and monitoring.
"""

import logging
from uav_assistant.flight_control import FlightController, FlightMode
from uav_assistant.navigation import NavigationSystem, Position, Waypoint
from uav_assistant.sensors import SensorManager
from uav_assistant.communication import CommunicationInterface
from uav_assistant.safety import SafetyMonitor


def setup_logging():
    """Configure logging for the example"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main example function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Initializing UAV Flight Assistant")
    
    # Initialize all systems
    flight_controller = FlightController()
    navigation = NavigationSystem()
    sensors = SensorManager()
    communication = CommunicationInterface()
    safety_monitor = SafetyMonitor()
    
    # Set up home position
    logger.info("Setting home position")
    home_lat, home_lon = 47.3977, 8.5456
    navigation.set_home_position(home_lat, home_lon, 408.0)
    
    # Create a simple flight plan with waypoints
    logger.info("Creating flight plan")
    waypoints = [
        Waypoint(Position(47.3980, 8.5460, 450.0), speed=5.0),
        Waypoint(Position(47.3985, 8.5465, 450.0), speed=5.0),
        Waypoint(Position(47.3990, 8.5470, 450.0), speed=5.0),
    ]
    
    for wp in waypoints:
        navigation.add_waypoint(wp)
    
    logger.info(f"Added {len(waypoints)} waypoints to flight plan")
    
    # Check sensor health
    logger.info("Checking sensor health")
    sensor_health = sensors.get_sensor_health()
    for sensor, status in sensor_health.items():
        logger.info(f"  {sensor}: {status['status']}")
    
    # Simulate pre-flight checks
    logger.info("Performing pre-flight checks")
    
    # Check battery
    battery_data = sensors.read_battery()
    if battery_data:
        safety_level = safety_monitor.check_battery(
            battery_data.voltage,
            battery_data.remaining
        )
        logger.info(f"Battery check: {safety_level.value}")
    
    # Check GPS
    gps_data = sensors.read_gps()
    if gps_data:
        safety_level = safety_monitor.check_gps(
            gps_data.satellites,
            gps_data.hdop
        )
        logger.info(f"GPS check: {safety_level.value}")
    
    # Connect to ground station (simulated)
    logger.info("Connecting to ground station")
    communication.connect("tcp://127.0.0.1:5760")
    
    # Send initial status
    status = flight_controller.get_status()
    communication.send_status(status)
    
    # Arm the vehicle
    logger.info("Arming vehicle")
    if flight_controller.arm():
        logger.info("Vehicle armed successfully")
        communication.send_status(flight_controller.get_status())
    else:
        logger.error("Failed to arm vehicle")
        return
    
    # Set flight mode
    logger.info("Setting flight mode to AUTO")
    flight_controller.set_mode(FlightMode.AUTO)
    
    # Simulate takeoff
    logger.info("Initiating takeoff")
    target_altitude = 450.0 - 408.0  # 42 meters AGL
    if flight_controller.takeoff(target_altitude):
        logger.info(f"Takeoff initiated to {target_altitude}m AGL")
        communication.send_alert("Takeoff initiated", "info")
    
    # Get navigation status
    nav_status = navigation.get_navigation_status()
    logger.info(f"Navigation status: {nav_status}")
    
    # Get safety report
    safety_report = safety_monitor.get_safety_report()
    logger.info(f"Safety status: {safety_report['overall_status']}")
    
    # Simulate mission execution would happen here
    logger.info("Mission execution would proceed here...")
    logger.info("(In a real system, this would involve continuous monitoring and control)")
    
    # Cleanup
    logger.info("Mission complete")
    communication.disconnect()
    logger.info("UAV Flight Assistant example completed")


if __name__ == "__main__":
    main()
