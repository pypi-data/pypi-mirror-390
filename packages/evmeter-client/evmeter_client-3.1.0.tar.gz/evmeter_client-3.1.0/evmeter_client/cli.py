"""
Command Line Interface for EV-Meter Client

This module provides CLI utilities for EV-Meter operations.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Optional

import aiomqtt
from .parser import parse_blewifi_payload

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# EV-Meter MQTT broker configuration
MQTT_HOST = "iot.nayax.com"
MQTT_PORT = 1883
MQTT_USERNAME = "deviceEV"
MQTT_PASSWORD = "ng4GycjMmuvpSJU6"


def format_raw_payload(payload: bytes) -> str:
    """Format raw payload for display."""
    try:
        # Try to decode as UTF-8 text
        text = payload.decode('utf-8')
        return f"Text: {text}"
    except UnicodeDecodeError:
        # Display as hex if it's binary data
        hex_data = payload.hex()
        # Format hex in groups of 2 for readability
        formatted_hex = ' '.join(hex_data[i:i+2] for i in range(0, len(hex_data), 2))
        return f"Hex: {formatted_hex} ({len(payload)} bytes)"


def format_parsed_data(parsed_data: dict) -> str:
    """Format parsed data for display."""
    return json.dumps(parsed_data, indent=2, default=str)


async def mqtt_monitor():
    """Main MQTT monitoring function."""
    logger.info(f"Connecting to MQTT broker: {MQTT_HOST}:{MQTT_PORT}")
    logger.info(f"Username: {MQTT_USERNAME}")
    logger.info("Subscribing to all topics (#)")
    logger.info("Press Ctrl+C to stop\n")

    try:
        async with aiomqtt.Client(
            hostname=MQTT_HOST,
            port=MQTT_PORT,
            username=MQTT_USERNAME,
            password=MQTT_PASSWORD,
        ) as client:
            # Subscribe to all topics
            await client.subscribe("#")
            logger.info("✓ Connected and subscribed to all topics")
            logger.info("=" * 80)

            async for message in client.messages:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                topic = message.topic.value
                payload = message.payload

                print(f"\n[{timestamp}] Topic: {topic}")
                print(f"Raw payload: {format_raw_payload(payload)}")

                # Try to parse the payload
                try:
                    parsed_data = parse_blewifi_payload(payload)
                    print("✓ Parsing succeeded!")
                    print(f"Parsed data:\n{format_parsed_data(parsed_data)}")
                except Exception as e:
                    print(f"✗ Parsing failed: {e}")

                print("-" * 60)

    except KeyboardInterrupt:
        logger.info("\n\nMonitoring stopped by user")
    except Exception as e:
        logger.error(f"MQTT connection error: {e}")
        raise


def main():
    """Main CLI entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("EV-Meter Client CLI")
        print("Usage: evmeter-monitor")
        print("       Monitor all MQTT traffic on EV-Meter broker")
        return 0
    
    print("EV-Meter MQTT Monitor")
    print("=" * 40)
    print("This utility monitors all MQTT traffic on the EV-Meter broker")
    print("and attempts to parse payloads using the evmeter-client parser.\n")

    try:
        return asyncio.run(mqtt_monitor())
    except KeyboardInterrupt:
        print("\nShutting down...")
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())