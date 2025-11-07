"""
pycom0com - Python bindings for com0com virtual serial ports
"""

from .core import (
    Com0ComController,
    PortParameters,
    PortPairInfo,
    PortPair,
    CommandResult,
    FriendlyNameInfo,
    Com0ComError,
    Com0ComWarning,
    AdminRequiredError
)

__version__ = "1.0.3"

__all__ = [
    "Com0ComController",
    "PortPair",
    "PortParameters",
    "PortPairInfo",
    "CommandResult",
    "FriendlyNameInfo",
    "Com0ComError",
    "Com0ComWarning",
    "AdminRequiredError"
]