"""Exceptions for the EV-Meter client."""


class EVMeterError(Exception):
    """Base exception for the EV-Meter client."""


class EVMeterTimeoutError(EVMeterError):
    """Raised when a response from the charger times out."""


class EVMeterProtocolError(EVMeterError):
    """Raised when there is an error in the EV-Meter protocol."""
