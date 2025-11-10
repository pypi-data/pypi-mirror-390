"""Custom exception hierarchy."""

from neurobus.exceptions.core import (
    BusNotStartedError,
    DispatchError,
    HandlerError,
    NeuroBusError,
    RegistryError,
    SubscriptionError,
)

__all__ = [
    "NeuroBusError",
    "BusNotStartedError",
    "SubscriptionError",
    "DispatchError",
    "HandlerError",
    "RegistryError",
]
