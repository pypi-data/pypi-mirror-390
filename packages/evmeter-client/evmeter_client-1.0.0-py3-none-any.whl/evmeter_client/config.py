"""Configuration for the EV-Meter client."""

from dataclasses import dataclass


@dataclass
class EVMeterConfig:
    """Configuration for the EV-Meter client."""

    # Hardcoded MQTT broker settings (as per PRD)
    mqtt_host: str = "iot.nayax.com"
    mqtt_port: int = 1883
    mqtt_username: str = "deviceEV"
    mqtt_password: str = "ng4GycjMmuvpSJU6"

    # User ID for receiving responses (must be configured per installation)
    user_id: str = ""

    # MQTT topic templates following the /BLEWIFI protocol
    command_topic_template: str = "/BLEWIFI/Chargers/{charger_id}"
    response_topic_template: str = "/BLEWIFI/users/{user_id}"
    qos: int = 1
    response_timeout: int = 10
