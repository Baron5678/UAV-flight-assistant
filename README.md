# UAV Flight Assistant

A comprehensive Python-based system for UAV (Unmanned Aerial Vehicle) flight management and control. This diploma project provides a modular framework for managing UAV operations including flight control, navigation, sensor monitoring, communication, and safety features.

## Features

### 🚁 Flight Control
- Multiple flight modes (Manual, Stabilize, Auto, Guided, Loiter, RTL, Land)
- Takeoff and landing procedures
- Position control and navigation commands
- Real-time status monitoring

### 🗺️ Navigation System
- GPS-based positioning
- Waypoint management and path planning
- Distance and bearing calculations using Haversine formula
- Home position management and return-to-launch capability

### 📡 Sensor Management
- IMU (Inertial Measurement Unit) data processing
- GPS receiver integration
- Barometer altitude estimation
- Battery monitoring
- Sensor health monitoring

### 📢 Communication
- Ground station communication interface
- Telemetry data streaming
- Command reception and handling
- Alert and logging systems
- Prioritized message queuing

### 🛡️ Safety Monitoring
- Battery level monitoring with configurable thresholds
- GPS signal quality checks
- Altitude limit enforcement
- Geofence boundary management
- Emergency alert system with callbacks

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from source

```bash
# Clone the repository
git clone https://github.com/Baron5678/UAV-flight-assistant.git
cd UAV-flight-assistant

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Quick Start

```python
from uav_assistant.flight_control import FlightController, FlightMode
from uav_assistant.navigation import NavigationSystem, Position, Waypoint
from uav_assistant.sensors import SensorManager
from uav_assistant.safety import SafetyMonitor

# Initialize systems
controller = FlightController()
navigation = NavigationSystem()
sensors = SensorManager()
safety = SafetyMonitor()

# Set home position
navigation.set_home_position(47.3977, 8.5456, 408.0)

# Arm and takeoff
controller.arm()
controller.takeoff(target_altitude=50.0)

# Add waypoints
waypoint = Waypoint(Position(47.3980, 8.5460, 450.0), speed=5.0)
navigation.add_waypoint(waypoint)

# Monitor safety
battery = sensors.read_battery()
safety.check_battery(battery.voltage, battery.remaining)
```

See the [examples](examples/) directory for more detailed usage examples.

## Project Structure

```
UAV-flight-assistant/
├── src/
│   └── uav_assistant/
│       ├── flight_control/    # Flight control modules
│       ├── navigation/        # Navigation and positioning
│       ├── sensors/           # Sensor data management
│       ├── communication/     # Communication interfaces
│       └── safety/            # Safety monitoring
├── tests/
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── config/                    # Configuration files
├── examples/                  # Example scripts
├── docs/                      # Documentation
├── pyproject.toml            # Project metadata and dependencies
└── requirements.txt          # Python dependencies
```

## Configuration

The system can be configured using the YAML configuration file located at `config/default_config.yaml`. Key configuration parameters include:

- **Flight Control**: Maximum altitude, speed limits, takeoff/landing parameters
- **Safety**: Battery thresholds, GPS requirements, geofence settings
- **Navigation**: Waypoint acceptance radius, default speeds
- **Communication**: Telemetry intervals, connection settings
- **Sensors**: Sample rates, update intervals

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=uav_assistant --cov-report=html

# Run specific test file
pytest tests/unit/test_flight_control.py
```

### Code Quality

```bash
# Format code with black
black src/ tests/

# Run linter
flake8 src/ tests/

# Type checking
mypy src/
```

## Safety Considerations

⚠️ **Important Safety Notice**

This is an educational diploma project and should not be used for actual flight operations without:
- Proper hardware integration and testing
- Compliance with local aviation regulations
- Safety certification and validation
- Appropriate fail-safe mechanisms
- Professional review and approval

Always follow local laws and regulations regarding UAV operations.

## Contributing

This is a diploma project, but suggestions and feedback are welcome. Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project was developed as part of a diploma thesis on UAV flight management systems.

## Contact

- Author: Baron5678
- Repository: https://github.com/Baron5678/UAV-flight-assistant
- Issues: https://github.com/Baron5678/UAV-flight-assistant/issues

---

**Note**: This is an educational project demonstrating UAV flight management concepts. It is not intended for use in production UAV systems without significant additional development, testing, and safety validation.