# EV-Meter Client

A Python client library for EV-Meter electric vehicle chargers that communicate via MQTT using the BLEWIFI protocol.

[![PyPI version](https://badge.fury.io/py/evmeter-client.svg)](https://badge.fury.io/py/evmeter-client)
[![Python versions](https://img.shields.io/pypi/pyversions/evmeter-client.svg)](https://pypi.org/project/evmeter-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Async MQTT client** for EV-Meter chargers
- **Binary protocol parsing** for BLEWIFI messages
- **Comprehensive data models** with 25+ fields
- **Real-time monitoring** of charging sessions
- **3-phase electrical measurements** (voltage, current, power)
- **Energy tracking** (session and lifetime totals)
- **Diagnostic information** (warnings, errors, WiFi status)

## Installation

```bash
pip install evmeter-client
```

## Quick Start

```python
import asyncio
from evmeter_client import EVMeterClient, EVMeterConfig

async def main():
    # Configure with your charger details
    config = EVMeterConfig(
        user_id="your-user-id-hex-string"
    )
    
    # Create client and connect
    client = EVMeterClient(config)
    await client.connect()
    
    try:
        # Get charger status
        status = await client.get_charger_status("YOUR_CHARGER_ID")
        print(f"Charger Status: {status.charger_state}")
        print(f"EV Status: {status.ev_status}")
        print(f"Power: {status.power_kw} kW")
        
        # Get detailed metrics
        metrics = await client.get_charger_metrics("YOUR_CHARGER_ID")
        print(f"Session Energy: {metrics.session_energy_kwh} kWh")
        print(f"Voltage L1: {metrics.voltage_l1} V")
        print(f"Current L1: {metrics.current_l1} A")
        
    finally:
        await client.disconnect()

# Run the example
asyncio.run(main())
```

## Configuration

The library connects to the EV-Meter MQTT broker with hardcoded settings:

```python
config = EVMeterConfig(
    user_id="your-hex-user-id",  # Required: Your unique user ID
    mqtt_host="mqtt.evmeter.com",  # Fixed
    mqtt_port=1883,  # Fixed
    mqtt_username="deviceEV",  # Fixed
    mqtt_password="ng4GycjMmuvpSJU6"  # Fixed
)
```

Only the `user_id` needs to be configured - get this from your EV-Meter app or MQTT logs.

## Data Models

### ChargerStatus
- `charger_state`: Current charger state (IDLE, CHARGING, ERROR, etc.)
- `ev_status`: EV connection status (NOT_CONNECTED, CONNECTED, WANTS_TO_CHARGE, etc.)
- `charging_state`: Detailed charging state (1_PHASE, 3_PHASE, WAITING, etc.)
- `power_kw`: Real-time power consumption
- `session_energy_kwh`: Current session energy
- `total_energy_kwh`: Lifetime energy total
- `warnings`: Warning count
- `errors`: Error count

### ChargerMetrics
- **3-Phase Electrical**: Individual and average voltage/current for all phases
- **Energy**: Session and total energy with precise measurements
- **Configuration**: Set current limit, circuit breaker rating
- **System**: Temperature, WiFi RSSI, firmware versions
- **Diagnostics**: EVSE status, ping latency, peer serial number

## Protocol

The library implements the BLEWIFI protocol used by EV-Meter chargers:

- **Command Topic**: `/BLEWIFI/Chargers/{charger_id}`
- **Response Topic**: `/BLEWIFI/users/{user_id}`
- **Binary Payloads**: Custom binary format with comprehensive working info

## MQTT Monitoring Utility

The package includes a command-line utility for monitoring all MQTT traffic on the EV-Meter broker:

```bash
# After installing the package
evmeter-monitor
```

This utility will:
- Connect to the EV-Meter MQTT broker
- Subscribe to all topics (`#` wildcard)  
- Display all messages with timestamps
- Attempt to parse payloads and show both raw and parsed data
- Show parsing failures for non-BLEWIFI messages

Example output:
```
[2025-11-08 13:06:29.608] Topic: /device/state/0000000000208348
Raw payload: Text: left
✗ Parsing failed: fromhex() argument must be str, not bytes
------------------------------------------------------------

[2025-11-08 13:06:30.123] Topic: /BLEWIFI/users/1234567890abcdef
Raw payload: Hex: aa 55 17 00 01 02 03 04 05 06 07 08 09 0a 0b 0c (24 bytes)
✓ Parsing succeeded!
Parsed data:
{
  "charger_state": "CHARGING",
  "ev_status": "CONNECTED",
  "power_kw": 7.2,
  "session_energy_kwh": 12.5
}
------------------------------------------------------------
```

You can also run the standalone script:
```bash
python mqtt_monitor.py
```

## Error Handling

```python
from evmeter_client.exceptions import EVMeterError, EVMeterTimeoutError

try:
    status = await client.get_charger_status("CHARGER_ID")
except EVMeterTimeoutError:
    print("Charger didn't respond in time")
except EVMeterError as e:
    print(f"EV-Meter error: {e}")
```

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/evmeter-client.git
cd evmeter-client

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
ruff check .
```

## Home Assistant Integration

This library is used by the [EV-Meter Home Assistant integration](https://github.com/yourusername/evmeter-hacs) to provide comprehensive monitoring of EV-Meter chargers in Home Assistant.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### v1.0.0
- Initial release
- Full BLEWIFI protocol support
- Comprehensive data models
- Async MQTT client
- Real-time monitoring capabilities