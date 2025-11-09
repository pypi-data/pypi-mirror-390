"""Data models for the EV-Meter client."""

from dataclasses import dataclass
from enum import Enum


class ChargerState(str, Enum):
    """Enum for charger states based on BLEWIFI protocol."""

    NOT_CONNECTED = "Not Connected"
    WANTS_TO_CHARGE = "Wants to Charge"
    CONNECTED = "Connected"


class EVStatus(str, Enum):
    """EV connection status from working_info."""

    UNKNOWN = "Unknown"
    NOT_CONNECTED = "Not Connected"
    CONNECTED = "Connected"
    WANTS_TO_CHARGE = "Wants to Charge"
    NEED_TO_VENTILATE = "Need to Ventilate"
    ERROR_STATE = "Error State"


class ChargingState(str, Enum):
    """Charging state from working_info."""

    UNKNOWN = "Unknown"
    NOT_CHARGING = "Not Charging"
    CHARGING_1_PHASE = "Charging (1 Phase)"
    CHARGING_3_PHASE = "Charging (3 Phase)"
    WAITING_FOR_EV_AO = "Waiting for EV AO"
    ALWAYS_ON_1_PHASE = "Always On (1 Phase)"
    ALWAYS_ON_3_PHASE = "Always On (3 Phase)"
    WAITING_FOR_EV = "Waiting for EV"


class PhaseType(str, Enum):
    """Phase type from working_info."""

    UNKNOWN = "Unknown"
    PHASE_1 = "Single Phase"
    PHASE_3 = "Three Phase"


class GridType(str, Enum):
    """Grid type from working_info."""

    UNKNOWN = "Unknown"
    TN_S = "TN-S"
    IT = "IT"
    USA_1F_IT = "USA 1F IT"


class MQTTType(str, Enum):
    """MQTT connection status from working_info."""

    UNKNOWN = "Unknown"
    WORKING_PROPERLY = "Working Properly"
    MQTT_NOT_CONFIGURED = "MQTT Not Configured"
    UNABLE_TO_CONNECT_BROKER = "Unable to Connect Broker"
    UNABLE_TO_CONNECT_WIFI = "Unable to Connect WiFi"
    UNABLE_TO_DETECT_WIFI = "Unable to Detect WiFi"
    WIFI_NOT_CONNECTED = "WiFi Not Connected"


@dataclass
class ChargerStatus:
    """Represents the status of an EV charger."""

    charger_id: str
    state: ChargerState
    evse: int
    kubis_version: str
    ev_status: EVStatus
    charging_state: ChargingState
    warnings: int
    errors: int
    phase_type: PhaseType
    grid_type: GridType
    wifi_network: str
    mqtt_type: MQTTType
    firmware_version: int
    set_current: int
    limit: str | int
    start_time: int
    scheduler_version: int
    circuit_breaker: int
    temperature: int


@dataclass
class ChargerMetrics:
    """Represents real-time metrics from an EV charger."""

    charger_id: str
    # Three-phase voltage measurements
    voltage_ph1: float
    voltage_ph2: float
    voltage_ph3: float
    # Three-phase current measurements
    current_ph1: float
    current_ph2: float
    current_ph3: float
    # DLM current measurements
    dlm_current_ph1: float
    dlm_current_ph2: float
    dlm_current_ph3: float
    # Energy measurements
    session_energy_wh: int
    total_energy_wh: int
    # Calculated values
    power_kw: float
    session_energy_kwh: float
    total_energy_kwh: float
    # Average values
    voltage_avg: float
    current_avg: float
    # Other metrics
    temperature: int
    peer_serial_number: int
    avg_ping_latency: int
