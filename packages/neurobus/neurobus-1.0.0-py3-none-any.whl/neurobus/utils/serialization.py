"""Serialization utilities using msgpack."""

from datetime import datetime
from typing import Any
from uuid import UUID

import msgpack


def serialize(data: Any) -> bytes:
    """
    Serialize data to msgpack format.

    Handles special types: UUID, datetime

    Args:
        data: Data to serialize

    Returns:
        Serialized bytes

    Raises:
        TypeError: If data contains non-serializable types
    """
    return msgpack.packb(data, default=_encode_special_types, use_bin_type=True)


def deserialize(data: bytes) -> Any:
    """
    Deserialize data from msgpack format.

    Args:
        data: Serialized bytes

    Returns:
        Deserialized data

    Raises:
        ValueError: If data is invalid msgpack
    """
    return msgpack.unpackb(data, raw=False, object_hook=_decode_special_types)


def _encode_special_types(obj: Any) -> Any:
    """
    Encode special types for msgpack serialization.

    Args:
        obj: Object to encode

    Returns:
        Encoded representation

    Raises:
        TypeError: If object type is not supported
    """
    if isinstance(obj, UUID):
        return {"__uuid__": str(obj)}
    elif isinstance(obj, datetime):
        return {"__datetime__": obj.isoformat()}
    elif hasattr(obj, "__dict__"):
        # Fallback for objects with __dict__
        return {"__object__": obj.__class__.__name__, "data": obj.__dict__}
    else:
        raise TypeError(f"Cannot serialize type: {type(obj)}")


def _decode_special_types(obj: Any) -> Any:
    """
    Decode special types from msgpack deserialization.

    Args:
        obj: Object to decode

    Returns:
        Decoded object
    """
    if isinstance(obj, dict):
        if "__uuid__" in obj:
            return UUID(obj["__uuid__"])
        elif "__datetime__" in obj:
            return datetime.fromisoformat(obj["__datetime__"])
    return obj


def event_to_bytes(event: Any) -> bytes:
    """
    Serialize Event to bytes.

    Args:
        event: Event instance

    Returns:
        Serialized bytes
    """
    return serialize(event.to_dict())


def bytes_to_event(data: bytes) -> dict[str, Any]:
    """
    Deserialize bytes to event dictionary.

    Args:
        data: Serialized bytes

    Returns:
        Event dictionary (use Event.from_dict() to reconstruct)
    """
    return deserialize(data)
