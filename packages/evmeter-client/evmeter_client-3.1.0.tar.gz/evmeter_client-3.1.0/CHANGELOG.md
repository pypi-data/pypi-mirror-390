# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2025-11-10

### Minor
- Version minor release
- TODO: Add specific changes for this release
## [2.0.0] - 2025-11-08

### Major
- Version major release
- TODO: Add specific changes for this release
## [1.3.0] - 2025-11-08

### Minor
- Version minor release
- TODO: Add specific changes for this release
## [1.2.1] - 2025-11-08

### Patch
- Version patch release
- TODO: Add specific changes for this release
## [1.2.0] - 2025-11-08

### Minor
- Version minor release
- TODO: Add specific changes for this release
## [1.1.1] - 2025-11-08

### Fixed
- **CRITICAL**: Fixed hardcoded placeholder text in command payload that caused ValueError during charger validation
- Replaced placeholder with proper `_create_command_payload()` method call in `_send_command()`

## [1.1.0] - 2025-11-08

### Added
- MQTT monitoring utility (`evmeter-monitor` CLI command)
- Standalone MQTT monitor script (`mqtt_monitor.py`)
- Command-line interface module (`evmeter_client.cli`)
- Comprehensive examples script (`examples.py`)
- Real-time MQTT traffic monitoring with parsing attempts
- Formatted display of raw and parsed message data

### Changed
- Updated README with monitoring utility documentation
- Added CLI entry point in pyproject.toml
- Enhanced examples with monitoring use cases

## [1.0.0] - 2025-11-08

### Added
- Initial release of evmeter-client
- Full BLEWIFI protocol implementation for EV-Meter chargers
- Async MQTT client with aiomqtt backend
- Binary payload parsing for working info responses
- Comprehensive data models with 25+ fields:
  - ChargerStatus with state, power, energy tracking
  - ChargerMetrics with 3-phase electrical measurements
  - Complete enum support for all status fields
- Real-time monitoring capabilities
- Error handling and timeout management
- Type hints and async/await support
- Comprehensive test suite
- Professional packaging for PyPI distribution

### Features
- **MQTT Communication**: Async client for EV-Meter's MQTT broker
- **Protocol Support**: Complete BLEWIFI binary protocol implementation
- **Data Models**: Rich Python models for all charger data
- **3-Phase Monitoring**: Individual and average voltage/current/power
- **Energy Tracking**: Session and lifetime energy measurements
- **System Diagnostics**: Temperature, WiFi, firmware, error monitoring
- **Home Assistant Ready**: Designed for HA integration usage

### Dependencies
- aiomqtt >= 1.2.0, < 3.0.0
- Python >= 3.8

### Documentation
- Complete README with examples
- Type hints throughout codebase
- Inline documentation for all public APIs