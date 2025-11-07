"""
Custom MessagePack serializer/deserializer supporting extended Python types.

Supports:
- datetime.date
- datetime.datetime
- decimal.Decimal
- uuid.UUID
- dataclasses
- memoryview
- general Python objects
"""

import datetime
import decimal
import importlib
import uuid
from dataclasses import asdict, fields, is_dataclass
from typing import Any

import msgpack


# Custom type codes for msgpack extension types
EXT_TYPE_DATE = 1
EXT_TYPE_DATETIME = 2
EXT_TYPE_DECIMAL = 3
EXT_TYPE_UUID = 4
EXT_TYPE_DATACLASS = 5
EXT_TYPE_MEMORYVIEW = 6
EXT_TYPE_OBJECT = 7


def default(obj: Any) -> msgpack.ExtType:
    """
    Default encoder for custom types.

    Args:
        obj: Object to encode

    Returns:
        msgpack.ExtType with encoded data

    Raises:
        TypeError: If object type is not supported
    """
    if isinstance(obj, datetime.datetime):
        # Encode datetime as ISO format string
        data = obj.isoformat().encode("utf-8")
        return msgpack.ExtType(EXT_TYPE_DATETIME, data)

    elif isinstance(obj, datetime.date):
        # Encode date as ISO format string
        data = obj.isoformat().encode("utf-8")
        return msgpack.ExtType(EXT_TYPE_DATE, data)

    elif isinstance(obj, decimal.Decimal):
        # Encode Decimal as string to preserve precision
        data = str(obj).encode("utf-8")
        return msgpack.ExtType(EXT_TYPE_DECIMAL, data)

    elif isinstance(obj, uuid.UUID):
        # Encode UUID as bytes (16 bytes)
        data = obj.bytes
        return msgpack.ExtType(EXT_TYPE_UUID, data)

    elif isinstance(obj, memoryview):
        # Encode memoryview as bytes
        data = obj.tobytes()
        return msgpack.ExtType(EXT_TYPE_MEMORYVIEW, data)

    elif is_dataclass(obj):
        # Encode dataclass as dict with class name
        class_name = f"{obj.__class__.__module__}.{obj.__class__.__qualname__}"

        # Create field dict without converting nested dataclasses to dicts
        field_dict = {}
        for field in fields(obj):
            field_dict[field.name] = getattr(obj, field.name)

        data_dict = {"__class__": class_name, "__data__": field_dict}
        # Pack the dict and wrap in ExtType
        # Nested dataclasses will be handled by recursive default() calls
        packed = msgpack.packb(data_dict, default=default, use_bin_type=True)
        return msgpack.ExtType(EXT_TYPE_DATACLASS, packed)

    elif hasattr(obj, "__dict__") and not isinstance(obj, type):
        # Encode general Python objects
        class_name = f"{obj.__class__.__module__}.{obj.__class__.__qualname__}"

        # Get object's instance variables
        obj_dict = obj.__dict__.copy()

        data_dict = {"__class__": class_name, "__data__": obj_dict}
        # Pack the dict and wrap in ExtType
        packed = msgpack.packb(data_dict, default=default, use_bin_type=True)
        return msgpack.ExtType(EXT_TYPE_OBJECT, packed)

    raise TypeError(f"Unknown type: {type(obj)}")


def ext_hook(code: int, data: bytes) -> Any:
    """
    Extension hook for decoding custom types.

    Args:
        code: Extension type code
        data: Encoded data

    Returns:
        Decoded Python object

    Raises:
        ValueError: If extension type code is unknown
    """
    if code == EXT_TYPE_DATETIME:
        # Decode datetime from ISO format string
        iso_string = data.decode("utf-8")
        return datetime.datetime.fromisoformat(iso_string)

    elif code == EXT_TYPE_DATE:
        # Decode date from ISO format string
        iso_string = data.decode("utf-8")
        return datetime.date.fromisoformat(iso_string)

    elif code == EXT_TYPE_DECIMAL:
        # Decode Decimal from string
        decimal_string = data.decode("utf-8")
        return decimal.Decimal(decimal_string)

    elif code == EXT_TYPE_UUID:
        # Decode UUID from bytes
        return uuid.UUID(bytes=data)

    elif code == EXT_TYPE_MEMORYVIEW:
        # Decode memoryview from bytes
        return memoryview(data)

    elif code == EXT_TYPE_DATACLASS:
        # Decode dataclass from packed dict
        data_dict = msgpack.unpackb(data, ext_hook=ext_hook, raw=False)
        class_name = data_dict["__class__"]
        class_data = data_dict["__data__"]

        # Dynamically import and reconstruct the dataclass
        try:
            # Split module and class name
            module_name, cls_name = class_name.rsplit(".", 1)

            # Import the module
            module = importlib.import_module(module_name)

            # Get the class
            cls = getattr(module, cls_name)

            # Verify it's a dataclass
            if not is_dataclass(cls):
                raise TypeError(f"{class_name} is not a dataclass")

            # Reconstruct the dataclass instance
            return cls(**class_data)
        except (ImportError, AttributeError, TypeError) as e:
            # If reconstruction fails, return dict representation with error info
            return {
                "__dataclass__": class_name,
                "__reconstruction_error__": str(e),
                **class_data,
            }

    elif code == EXT_TYPE_OBJECT:
        # Decode general Python object from packed dict
        data_dict = msgpack.unpackb(data, ext_hook=ext_hook, raw=False)
        class_name = data_dict["__class__"]
        class_data = data_dict["__data__"]

        # Dynamically import and reconstruct the object
        try:
            # Split module and class name
            module_name, cls_name = class_name.rsplit(".", 1)

            # Import the module
            module = importlib.import_module(module_name)

            # Get the class
            cls = getattr(module, cls_name)

            # Create instance without calling __init__ (like pickle does)
            obj = cls.__new__(cls)

            # Set instance variables
            for key, value in class_data.items():
                setattr(obj, key, value)

            return obj
        except (ImportError, AttributeError, TypeError) as e:
            # If reconstruction fails, return dict representation with error info
            return {
                "__object__": class_name,
                "__reconstruction_error__": str(e),
                **class_data,
            }

    raise ValueError(f"Unknown extension type code: {code}")


def packb(obj: Any, **kwargs) -> bytes:
    """
    Serialize object to msgpack bytes with custom type support.

    Args:
        obj: Object to serialize
        **kwargs: Additional arguments passed to msgpack.packb

    Returns:
        Serialized bytes
    """
    return msgpack.packb(obj, default=default, use_bin_type=True, **kwargs)


def unpackb(packed: bytes, **kwargs) -> Any:
    """
    Deserialize msgpack bytes to Python object with custom type support.

    Args:
        packed: Serialized bytes
        **kwargs: Additional arguments passed to msgpack.unpackb

    Returns:
        Deserialized Python object
    """
    return msgpack.unpackb(packed, ext_hook=ext_hook, raw=False, **kwargs)


def pack(obj: Any, stream, **kwargs) -> None:
    """
    Serialize object to msgpack and write to stream with custom type support.

    Args:
        obj: Object to serialize
        stream: File-like object to write to
        **kwargs: Additional arguments passed to msgpack.pack
    """
    msgpack.pack(obj, stream, default=default, use_bin_type=True, **kwargs)


def unpack(stream, **kwargs) -> Any:
    """
    Deserialize msgpack from stream to Python object with custom type support.

    Args:
        stream: File-like object to read from
        **kwargs: Additional arguments passed to msgpack.unpack

    Returns:
        Deserialized Python object
    """
    return msgpack.unpack(stream, ext_hook=ext_hook, raw=False, **kwargs)
