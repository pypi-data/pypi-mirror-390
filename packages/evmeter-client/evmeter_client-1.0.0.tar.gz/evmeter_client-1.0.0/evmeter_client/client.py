"""Async MQTT client for EV-Meter chargers."""

import asyncio
import logging
from typing import Any

import aiomqtt

from .config import EVMeterConfig
from .exceptions import EVMeterError, EVMeterProtocolError, EVMeterTimeoutError
from .models import (
    ChargerMetrics,
    ChargerState,
    ChargerStatus,
    ChargingState,
    EVStatus,
    GridType,
    MQTTType,
    PhaseType,
)
from .parser import parse_blewifi_payload

_LOGGER = logging.getLogger(__name__)


class EVMeterClient:
    """Asynchronous client to interact with the EV-Meter MQTT backend."""

    def __init__(self, config: EVMeterConfig):
        self.config = config
        self._client: aiomqtt.Client | None = None
        self._response_futures: dict[str, asyncio.Future] = {}

    async def connect(self) -> None:
        """Connect to the MQTT broker."""
        if self._client:
            _LOGGER.warning("Already connected.")
            return

        self._client = aiomqtt.Client(
            hostname=self.config.mqtt_host,
            port=self.config.mqtt_port,
            username=self.config.mqtt_username,
            password=self.config.mqtt_password,
        )
        await self._client.__aenter__()
        # Subscribe to the user's response topic
        response_topic = self.config.response_topic_template.format(
            user_id=self.config.user_id
        )
        await self._client.subscribe(response_topic, qos=self.config.qos)
        asyncio.create_task(self._message_handler())

    async def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None

    async def _message_handler(self) -> None:
        """Handle incoming MQTT messages."""
        if not self._client:
            return
        async for message in self._client.messages:
            topic = str(message.topic)
            payload_hex = message.payload.hex()
            _LOGGER.info(f"Received message on topic: {topic}")
            _LOGGER.info(f"Payload length: {len(message.payload)} bytes")
            _LOGGER.info(f"Payload (hex): {payload_hex[:100]}...")

            # Parse the payload to see what we got
            try:
                from .parser import parse_blewifi_payload

                parsed = parse_blewifi_payload(payload_hex)
                _LOGGER.info(f"Parsed message type: {parsed.get('type')}")
                _LOGGER.info(f"Parsed status: {parsed.get('status')}")
                if "working_info" in parsed:
                    wi = parsed["working_info"]
                    _LOGGER.info(f"  EVSE: {wi.get('evse')}")
                    _LOGGER.info(f"  Voltage Ph1: {wi.get('voltagePh1')} V")
                    _LOGGER.info(f"  Current Ph1: {wi.get('currentPh1')} A")
                    _LOGGER.info(f"  Session: {wi.get('session')} Wh")
            except Exception as e:
                _LOGGER.warning(f"Error parsing message for logging: {e}")

            # All responses come to the user topic, so we need to correlate
            # based on pending requests
            # TODO: Implement proper correlation ID when protocol supports it
            try:
                # For now, complete any pending request with this response
                # In production, we'd need better correlation logic
                if self._response_futures:
                    # Get the first pending future
                    charger_id = next(iter(self._response_futures))
                    future = self._response_futures.pop(charger_id)
                    future.set_result(message.payload)
            except Exception as e:
                _LOGGER.warning("Error handling message: %s", e)

    async def _send_command(
        self, charger_id: str, command_payload: bytes
    ) -> dict[str, Any]:
        """Send a command and wait for a response."""
        if not self._client:
            raise EVMeterError("Not connected to MQTT broker")

        command_topic = self.config.command_topic_template.format(charger_id=charger_id)

        # Create future for response correlation
        # TODO: Use correlation ID from protocol for better request/response matching
        future = asyncio.get_running_loop().create_future()
        self._response_futures[charger_id] = future

        print(f"Sending command to topic: {command_topic}")
        # This is test/debug code - use _create_command_payload in production
        command_payload = bytes.fromhex(
            "61000000000000000724EXAMPLE_USER_ID_HEX_STRING_GOES_HERE...truncated for security"
        )
        print(f"Command Payload (hex): {command_payload.hex()}")
        # Publish the binary command payload
        await self._client.publish(
            command_topic, payload=command_payload, qos=self.config.qos
        )

        try:
            response_payload = await asyncio.wait_for(
                future, timeout=self.config.response_timeout
            )
            # Parse the binary response
            return parse_blewifi_payload(response_payload.hex())
        except asyncio.TimeoutError as e:
            self._response_futures.pop(charger_id, None)
            raise EVMeterTimeoutError(
                f"Timeout waiting for response for charger {charger_id}"
            ) from e

    def _create_command_payload(self, charger_id: str) -> bytes:
        """
        Create a command payload to request data from a charger.

        Based on the sample/pub script, the payload structure is:
        - Bytes 0-1: Length (little-endian)
        - Bytes 2-7: Six zero bytes
        - Bytes 8-9: Command marker (0x07 0x24)
        - Byte 10: Separator (0x00)
        - Bytes 11-47: User UUID (37 bytes, space-padded ASCII)
        - Bytes 48-49: (0x30 0x00)
        - Bytes 50+: Additional data (appears to be a token/signature)
        """
        # Start with zeros
        command_data = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        # Add command marker
        command_data += bytes([0x07, 0x24])

        # Add separator
        command_data += bytes([0x00])

        # Add user UUID as ASCII text (space + UUID, total 37 bytes)
        # The user_id is already in hex format like "65336132363961312D..."
        # We need to convert it to the actual ASCII UUID format
        # Convert hex string to ASCII
        try:
            uuid_bytes = bytes.fromhex(self.config.user_id)
            uuid_str = uuid_bytes.decode("ascii")
        except Exception:
            # If conversion fails, use the string as-is
            uuid_str = self.config.user_id

        user_uuid_str = " " + uuid_str
        user_uuid_bytes = user_uuid_str.encode("ascii")[:37].ljust(37, b"\x00")
        command_data += user_uuid_bytes

        # Add the 0x30 0x00 bytes
        command_data += bytes([0x30, 0x00])

        # Add the additional data from sample (this appears to be some kind of token)
        # Using the exact bytes from sample/pub for now
        # TODO: Determine if this is a static token or needs to be generated
        additional_data = bytes.fromhex(
            "1709043bb89880139705bed04d4ea2d5dd1bed824fb9478e24ebff3080cb4e3ea6b785f1011f11572ff096324d876a270000"
        )
        command_data += additional_data

        # Prepend length
        length = len(command_data)
        payload = length.to_bytes(2, "little") + command_data

        return payload

    async def get_charger_status(self, charger_id: str) -> ChargerStatus:
        """Get the current status of the charger."""
        command_payload = self._create_command_payload(charger_id)
        response = await self._send_command(charger_id, command_payload)

        try:
            _LOGGER.debug(f"Full response for status: {response}")

            # Extract status from parsed response
            status_code = response.get("status", 0)
            working_info = response.get("working_info", {})

            # Map status codes to ChargerState based on PROTOCOL.md
            # 0 = NOT_CONNECTED, 1 = WANTS_TO_CHARGE, 2 = CONNECTED
            state_map = {
                0: ChargerState.NOT_CONNECTED,
                1: ChargerState.WANTS_TO_CHARGE,
                2: ChargerState.CONNECTED,
            }
            state = state_map.get(status_code, ChargerState.NOT_CONNECTED)

            # Map working_info enums to our models
            ev_status_map = {
                "UNKNOWN": EVStatus.UNKNOWN,
                "NOT_CONNECTED": EVStatus.NOT_CONNECTED,
                "CONNECTED": EVStatus.CONNECTED,
                "WANTS_TO_CHARGE": EVStatus.WANTS_TO_CHARGE,
                "NEED_TO_VENTILATE": EVStatus.NEED_TO_VENTILATE,
                "ERROR_STATE": EVStatus.ERROR_STATE,
            }

            charging_state_map = {
                "UNKNOWN": ChargingState.UNKNOWN,
                "NOT_CHARGING": ChargingState.NOT_CHARGING,
                "CHARGING_1_PHASE": ChargingState.CHARGING_1_PHASE,
                "CHARGING_3_PHASE": ChargingState.CHARGING_3_PHASE,
                "WAITING_FOR_EV_AO": ChargingState.WAITING_FOR_EV_AO,
                "ALWAYS_ON_1_PHASE": ChargingState.ALWAYS_ON_1_PHASE,
                "ALWAYS_ON_3_PHASE": ChargingState.ALWAYS_ON_3_PHASE,
                "WAITING_FOR_EV": ChargingState.WAITING_FOR_EV,
            }

            phase_type_map = {
                "UNKNOWN": PhaseType.UNKNOWN,
                "PHASE_1": PhaseType.PHASE_1,
                "PHASE_3": PhaseType.PHASE_3,
            }

            grid_type_map = {
                "UNKNOWN": GridType.UNKNOWN,
                "TN_S": GridType.TN_S,
                "IT": GridType.IT,
                "USA_1F_IT": GridType.USA_1F_IT,
            }

            mqtt_type_map = {
                "UNKNOWN": MQTTType.UNKNOWN,
                "WORKING_PROPERLY": MQTTType.WORKING_PROPERLY,
                "MQTT_NOT_CONFIGURED": MQTTType.MQTT_NOT_CONFIGURED,
                "UNABLE_TO_CONNECT_BROKER": MQTTType.UNABLE_TO_CONNECT_BROKER,
                "UNABLE_TO_CONNECT_WIFI": MQTTType.UNABLE_TO_CONNECT_WIFI,
                "UNABLE_TO_DETECT_WIFI": MQTTType.UNABLE_TO_DETECT_WIFI,
                "WIFI_NOT_CONNECTED": MQTTType.WIFI_NOT_CONNECTED,
            }

            return ChargerStatus(
                charger_id=charger_id,
                state=state,
                evse=working_info.get("evse", 0),
                kubis_version=working_info.get("kubisVersion", ""),
                ev_status=ev_status_map.get(
                    working_info.get("evStatus", "UNKNOWN"), EVStatus.UNKNOWN
                ),
                charging_state=charging_state_map.get(
                    working_info.get("chargingState", "UNKNOWN"), ChargingState.UNKNOWN
                ),
                warnings=working_info.get("warnings", 0),
                errors=working_info.get("errors", 0),
                phase_type=phase_type_map.get(
                    working_info.get("phase_type", "UNKNOWN"), PhaseType.UNKNOWN
                ),
                grid_type=grid_type_map.get(
                    working_info.get("grid_type", "UNKNOWN"), GridType.UNKNOWN
                ),
                wifi_network=working_info.get("wifi", ""),
                mqtt_type=mqtt_type_map.get(
                    working_info.get("mqtt_type", "UNKNOWN"), MQTTType.UNKNOWN
                ),
                firmware_version=working_info.get("firmwareVersion", 0),
                set_current=working_info.get("setCurrent", 0),
                limit=working_info.get("limit", 0),
                start_time=working_info.get("startTime", 0),
                scheduler_version=working_info.get("schedulerVersion", 0),
                circuit_breaker=working_info.get("circuitBreak", 0),
                temperature=working_info.get("temperature", 0),
            )
        except (KeyError, TypeError) as e:
            raise EVMeterProtocolError(
                f"Invalid status response payload: {response}"
            ) from e

    async def get_charger_metrics(self, charger_id: str) -> ChargerMetrics:
        """Get real-time metrics from the charger."""
        command_payload = self._create_command_payload(charger_id)
        response = await self._send_command(charger_id, command_payload)

        try:
            _LOGGER.debug(f"Full response: {response}")
            working_info = response.get("working_info", {})
            _LOGGER.debug(f"Working info: {working_info}")

            # Three-phase voltage measurements
            voltage_ph1 = working_info.get("voltagePh1", 0.0)
            voltage_ph2 = working_info.get("voltagePh2", 0.0)
            voltage_ph3 = working_info.get("voltagePh3", 0.0)

            # Three-phase current measurements
            current_ph1 = working_info.get("currentPh1", 0.0)
            current_ph2 = working_info.get("currentPh2", 0.0)
            current_ph3 = working_info.get("currentPh3", 0.0)

            # DLM current measurements
            dlm_current_ph1 = working_info.get("dlmCurrentPh1", 0.0)
            dlm_current_ph2 = working_info.get("dlmCurrentPh2", 0.0)
            dlm_current_ph3 = working_info.get("dlmCurrentPh3", 0.0)

            # Energy measurements
            session_energy_wh = working_info.get("session", 0)
            total_energy_wh = working_info.get("total", 0)

            # Calculate total power from all 3 phases (V * I), convert to kW
            power_kw = (
                voltage_ph1 * current_ph1
                + voltage_ph2 * current_ph2
                + voltage_ph3 * current_ph3
            ) / 1000.0

            # Convert energy to kWh
            session_energy_kwh = session_energy_wh / 1000.0
            total_energy_kwh = total_energy_wh / 1000.0

            # Calculate averages
            voltage_avg = (voltage_ph1 + voltage_ph2 + voltage_ph3) / 3.0
            current_avg = (current_ph1 + current_ph2 + current_ph3) / 3.0

            return ChargerMetrics(
                charger_id=charger_id,
                voltage_ph1=voltage_ph1,
                voltage_ph2=voltage_ph2,
                voltage_ph3=voltage_ph3,
                current_ph1=current_ph1,
                current_ph2=current_ph2,
                current_ph3=current_ph3,
                dlm_current_ph1=dlm_current_ph1,
                dlm_current_ph2=dlm_current_ph2,
                dlm_current_ph3=dlm_current_ph3,
                session_energy_wh=session_energy_wh,
                total_energy_wh=total_energy_wh,
                power_kw=power_kw,
                session_energy_kwh=session_energy_kwh,
                total_energy_kwh=total_energy_kwh,
                voltage_avg=voltage_avg,
                current_avg=current_avg,
                temperature=working_info.get("temperature", 0),
                peer_serial_number=working_info.get("peerSerialNumber", 0),
                avg_ping_latency=working_info.get("avgPingLatency", 0),
            )
        except (KeyError, TypeError) as e:
            raise EVMeterProtocolError(
                f"Invalid metrics response payload: {response}"
            ) from e
