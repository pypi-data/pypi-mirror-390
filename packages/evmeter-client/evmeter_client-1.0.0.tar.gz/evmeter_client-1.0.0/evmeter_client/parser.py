"""Binary payload parser for EV-Meter MQTT messages."""

import logging
from itertools import islice
from typing import Iterator

_LOGGER = logging.getLogger(__name__)


def read_integer(iterator: Iterator[int], n: int) -> int:
    """Read n bytes as a little-endian integer from an iterator."""
    return int.from_bytes(bytes(islice(iterator, n)), "little")


def read_string(iterator: Iterator[int], n: int) -> str:
    """Read n bytes as an ASCII string from an iterator."""
    return bytes(islice(iterator, n)).decode("ascii", errors="replace")


def parse_data(iterator: Iterator[int]) -> str:
    """Read a length-prefixed string from the iterator."""
    length = read_integer(iterator, 2)
    data = bytes(islice(iterator, length))
    return data.decode("ascii", errors="replace")


def parse_blewifi_payload(payload_hex: str) -> dict:
    """
    Parse the binary payload from a /BLEWIFI/users response.

    Args:
        payload_hex: Hexadecimal string representation of the payload

    Returns:
        Dictionary containing parsed data fields

    The payload structure (based on sample/parse.py):
    - First 2 bytes: payload length (little-endian)
    - Next N bytes: actual payload data
    - Bytes 18-47: UUID (ASCII)
    - Type byte at offset 0 in payload
    - Status byte at offset 1 in payload
    - If type == 0x03: WorkingInfo structure follows
    """
    try:
        payload_bytes = bytes.fromhex(payload_hex)

        # Extract payload length and actual payload
        n = int.from_bytes(payload_bytes[:2], "little")
        payload = payload_bytes[2 : n + 2]

        # Extract UUID (bytes 18-47 in original message)
        uuid = payload_bytes[18:47].decode("ascii", errors="replace")

        # Parse payload content
        iterator = iter(payload)
        msg_type = read_integer(iterator, 1)
        status = read_integer(iterator, 1)

        result = {
            "uuid": uuid,
            "type": msg_type,
            "status": status,
            "raw_payload": payload.hex(),
        }

        # Type 0x03 indicates WorkingInfo
        if msg_type == 0x03:
            result["working_info"] = parse_working_info(iterator)

        return result

    except (ValueError, IndexError, StopIteration) as e:
        _LOGGER.error("Failed to parse BLEWIFI payload: %s", e)
        return {"error": str(e), "raw_payload": payload_hex}


def parse_working_info(iterator: Iterator[int]) -> dict:
    """
    Parse WorkingInfo structure from the payload iterator.

    Based on sample/working_info.py, the payload structure after type and status bytes:
    - Bytes 0-3: EVSE Status (4 bytes)
    - Variable: Kubis Version (length-prefixed string)
    - Byte: EV Status enum
    - Byte: Charging State enum
    - Byte: Warnings
    - Byte: Errors
    - 2 bytes each: Voltage Phase 1-3 (divide by 4.0 for volts)
    - 2 bytes each: Current Phase 1-3 (divide by 10.0 for amps)
    - 4 bytes: Session Energy (Wh)
    - 4 bytes: Total Energy (Wh)
    - Byte: Phase Type
    - Byte: Set Current
    - 2 bytes: Firmware Version
    - 4 bytes: Limit
    - Variable: WiFi Network (length-prefixed string)
    - Byte: Grid Type
    - Byte: MQTT Type
    - 8 bytes: Charger ID
    - 8 bytes: Start Time
    - 4 bytes: Scheduler Version
    - 4 bytes: Circuit Breaker
    - 2 bytes each: DLM Current Phase 1-3 (divide by 10.0)
    - Byte: Temperature
    - 4 bytes: Peer Serial Number
    - 4 bytes: Avg Ping Latency
    """
    working_info = {}

    try:
        # Bytes 0-3: EVSE Status (4 bytes, not 2!)
        evse_status = read_integer(iterator, 4)
        working_info["evse"] = evse_status

        # Variable length: Kubis Version (length-prefixed string)
        kubis_version = parse_data(iterator)
        working_info["kubisVersion"] = kubis_version

        # Byte: EV Status
        ev_status = read_integer(iterator, 1)
        ev_status_map = {
            0x00: "UNKNOWN",
            0x01: "NOT_CONNECTED",
            0x02: "CONNECTED",
            0x03: "WANTS_TO_CHARGE",
            0x04: "NEED_TO_VENTILATE",
            0x05: "ERROR_STATE",
        }
        working_info["evStatus"] = ev_status_map.get(ev_status, "UNKNOWN")

        # Byte: Charging State
        charging_state = read_integer(iterator, 1)
        charging_state_map = {
            0x00: "UNKNOWN",
            0x01: "NOT_CHARGING",
            0x02: "CHARGING_1_PHASE",
            0x03: "CHARGING_3_PHASE",
            0x04: "WAITING_FOR_EV_AO",
            0x05: "ALWAYS_ON_1_PHASE",
            0x06: "ALWAYS_ON_3_PHASE",
            0x07: "WAITING_FOR_EV",
        }
        working_info["chargingState"] = charging_state_map.get(
            charging_state, "UNKNOWN"
        )

        # Byte: Warnings (1 byte, not 2!)
        warnings = read_integer(iterator, 1)
        working_info["warnings"] = warnings

        # Byte: Errors (1 byte, not 2!)
        errors = read_integer(iterator, 1)
        working_info["errors"] = errors

        # Bytes: Voltage Phase 1-3 (divide by 4.0, not 10.0!)
        voltage_ph1 = read_integer(iterator, 2) / 4.0
        working_info["voltagePh1"] = voltage_ph1

        voltage_ph2 = read_integer(iterator, 2) / 4.0
        working_info["voltagePh2"] = voltage_ph2

        voltage_ph3 = read_integer(iterator, 2) / 4.0
        working_info["voltagePh3"] = voltage_ph3

        # Bytes: Current Phase 1-3 (divide by 10.0)
        current_ph1 = read_integer(iterator, 2) / 10.0
        working_info["currentPh1"] = current_ph1

        current_ph2 = read_integer(iterator, 2) / 10.0
        working_info["currentPh2"] = current_ph2

        current_ph3 = read_integer(iterator, 2) / 10.0
        working_info["currentPh3"] = current_ph3

        # 4 bytes: Session Energy (Wh)
        session_energy = read_integer(iterator, 4)
        working_info["session"] = session_energy

        # 4 bytes: Total Energy (Wh)
        total_energy = read_integer(iterator, 4)
        working_info["total"] = total_energy

        # Byte: Phase Type (0x01=PHASE_1, 0x02=PHASE_3, not 0x03!)
        phase_type = read_integer(iterator, 1)
        phase_type_map = {0x00: "UNKNOWN", 0x01: "PHASE_1", 0x02: "PHASE_3"}
        working_info["phase_type"] = phase_type_map.get(
            phase_type, f"UNKNOWN_{phase_type}"
        )

        # Byte: Set Current
        set_current = read_integer(iterator, 1)
        working_info["setCurrent"] = set_current

        # 2 bytes: Firmware Version (not 1 byte!)
        firmware_version = read_integer(iterator, 2)
        working_info["firmwareVersion"] = firmware_version

        # 4 bytes: Limit
        limit_value = read_integer(iterator, 4)
        if limit_value == 0xFFFFFFFF or limit_value >= 0xFFFFFFFF:
            working_info["limit"] = "UNLIMITED"
        else:
            working_info["limit"] = limit_value

        # Variable length: WiFi Network (length-prefixed string, not fixed 5 bytes!)
        wifi = parse_data(iterator)
        working_info["wifi"] = wifi

        # Byte: Grid Type
        grid_type = read_integer(iterator, 1)
        grid_type_map = {
            0x00: "UNKNOWN",
            0x01: "TN_S",
            0x02: "IT",
            0x03: "USA_1F_IT",
        }
        working_info["grid_type"] = grid_type_map.get(grid_type, f"UNKNOWN_{grid_type}")

        # Byte: MQTT Type
        mqtt_type = read_integer(iterator, 1)
        mqtt_type_map = {
            0x00: "UNKNOWN",
            0x01: "WORKING_PROPERLY",
            0x02: "MQTT_NOT_CONFIGURED",
            0x03: "UNABLE_TO_CONNECT_BROKER",
            0x04: "UNABLE_TO_CONNECT_WIFI",
            0x05: "UNABLE_TO_DETECT_WIFI",
            0x06: "WIFI_NOT_CONNECTED",
        }
        working_info["mqtt_type"] = mqtt_type_map.get(mqtt_type, f"UNKNOWN_{mqtt_type}")

        # 8 bytes: Charger ID (not 6 bytes!)
        charger_id = read_integer(iterator, 8)
        working_info["id"] = charger_id

        # 8 bytes: Start Time
        start_time = read_integer(iterator, 8)
        working_info["startTime"] = start_time

        # 4 bytes: Scheduler Version (not 1 byte!)
        scheduler_version = read_integer(iterator, 4)
        working_info["schedulerVersion"] = scheduler_version

        # 4 bytes: Circuit Breaker (not 1 byte!)
        circuit_break = read_integer(iterator, 4)
        working_info["circuitBreak"] = circuit_break

        # 2 bytes each: DLM Current Ph1-3 (divide by 10.0)
        dlm_current_ph1 = read_integer(iterator, 2) / 10.0
        working_info["dlmCurrentPh1"] = dlm_current_ph1

        dlm_current_ph2 = read_integer(iterator, 2) / 10.0
        working_info["dlmCurrentPh2"] = dlm_current_ph2

        dlm_current_ph3 = read_integer(iterator, 2) / 10.0
        working_info["dlmCurrentPh3"] = dlm_current_ph3

        # 1 byte: Temperature (not 2 bytes!)
        temperature = read_integer(iterator, 1)
        working_info["temperature"] = temperature

        # 4 bytes: Peer Serial Number (not 6 bytes!)
        peer_serial = read_integer(iterator, 4)
        working_info["peerSerialNumber"] = peer_serial

        # 4 bytes: Avg Ping Latency (not 1 byte!)
        avg_ping = read_integer(iterator, 4)
        working_info["avgPingLatency"] = avg_ping

    except (StopIteration, ValueError) as e:
        _LOGGER.warning("Incomplete WorkingInfo data: %s", e)

    return working_info
