import datetime
import decimal
import io
import uuid
from dataclasses import dataclass

import pytest

from rick.serializer.msgpack import pack, packb, unpack, unpackb


# Test fixtures and helper classes


@dataclass
class SimpleDataclass:
    """Simple dataclass for testing."""

    name: str
    value: int


@dataclass
class NestedDataclass:
    """Dataclass with nested dataclass."""

    title: str
    data: SimpleDataclass


@dataclass
class DataclassWithCustomTypes:
    """Dataclass with custom types."""

    id: uuid.UUID
    created: datetime.datetime
    amount: decimal.Decimal


class SimpleObject:
    """Simple object for testing."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (
            isinstance(other, SimpleObject) and self.x == other.x and self.y == other.y
        )


class ObjectWithMethods:
    """Object with methods."""

    def __init__(self, value):
        self.value = value

    def double(self):
        return self.value * 2

    def __eq__(self, other):
        return isinstance(other, ObjectWithMethods) and self.value == other.value


class NestedObject:
    """Object with nested object."""

    def __init__(self, name, child):
        self.name = name
        self.child = child

    def __eq__(self, other):
        return (
            isinstance(other, NestedObject)
            and self.name == other.name
            and self.child == other.child
        )


# Basic Type Tests


class TestDatetime:
    """Tests for datetime.date and datetime.datetime serialization."""

    def test_date_serialization(self):
        """Test datetime.date round-trip."""
        original = datetime.date(2025, 11, 6)
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert isinstance(unpacked, datetime.date)
        assert type(unpacked) == datetime.date

    def test_datetime_serialization(self):
        """Test datetime.datetime round-trip."""
        original = datetime.datetime(2025, 11, 6, 14, 30, 45, 123456)
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert isinstance(unpacked, datetime.datetime)
        assert unpacked.microsecond == 123456

    def test_datetime_now(self):
        """Test datetime.now() serialization."""
        original = datetime.datetime.now()
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert unpacked.tzinfo == original.tzinfo


class TestDecimal:
    """Tests for decimal.Decimal serialization."""

    def test_decimal_serialization(self):
        """Test basic Decimal round-trip."""
        original = decimal.Decimal("123.456")
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert isinstance(unpacked, decimal.Decimal)

    def test_decimal_high_precision(self):
        """Test high-precision Decimal."""
        original = decimal.Decimal("123.456789012345678901234567890")
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert str(unpacked) == str(original)

    def test_decimal_negative(self):
        """Test negative Decimal."""
        original = decimal.Decimal("-999.99")
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original

    def test_decimal_zero(self):
        """Test zero Decimal."""
        original = decimal.Decimal("0")
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original


class TestUUID:
    """Tests for uuid.UUID serialization."""

    def test_uuid_serialization(self):
        """Test UUID round-trip."""
        original = uuid.uuid4()
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert isinstance(unpacked, uuid.UUID)

    def test_uuid_deterministic(self):
        """Test specific UUID value."""
        original = uuid.UUID("12345678-1234-5678-1234-567812345678")
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert str(unpacked) == "12345678-1234-5678-1234-567812345678"


class TestMemoryview:
    """Tests for memoryview serialization."""

    def test_memoryview_serialization(self):
        """Test memoryview round-trip."""
        original = memoryview(b"Hello, World!")
        packed = packb(original)
        unpacked = unpackb(packed)

        # Note: memoryview is deserialized as bytes
        assert unpacked == original.tobytes()
        assert isinstance(unpacked, bytes)

    def test_memoryview_empty(self):
        """Test empty memoryview."""
        original = memoryview(b"")
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == b""


# Dataclass Tests


class TestDataclasses:
    """Tests for dataclass serialization."""

    def test_simple_dataclass(self):
        """Test simple dataclass round-trip."""
        original = SimpleDataclass(name="test", value=42)
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert isinstance(unpacked, SimpleDataclass)
        assert unpacked.name == "test"
        assert unpacked.value == 42

    def test_nested_dataclass(self):
        """Test nested dataclass."""
        original = NestedDataclass(
            title="parent", data=SimpleDataclass(name="child", value=100)
        )
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert isinstance(unpacked, NestedDataclass)
        assert isinstance(unpacked.data, SimpleDataclass)

    def test_dataclass_with_custom_types(self):
        """Test dataclass with custom types."""
        original = DataclassWithCustomTypes(
            id=uuid.uuid4(),
            created=datetime.datetime.now(),
            amount=decimal.Decimal("999.99"),
        )
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert isinstance(unpacked, DataclassWithCustomTypes)
        assert isinstance(unpacked.id, uuid.UUID)
        assert isinstance(unpacked.created, datetime.datetime)
        assert isinstance(unpacked.amount, decimal.Decimal)


# Object Tests


class TestObjects:
    """Tests for general Python object serialization."""

    def test_simple_object(self):
        """Test simple object round-trip."""
        original = SimpleObject(10, 20)
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert isinstance(unpacked, SimpleObject)
        assert unpacked.x == 10
        assert unpacked.y == 20

    def test_object_with_methods(self):
        """Test object with methods."""
        original = ObjectWithMethods(21)
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert isinstance(unpacked, ObjectWithMethods)
        assert unpacked.double() == 42

    def test_nested_object(self):
        """Test nested objects."""
        original = NestedObject(name="parent", child=SimpleObject(5, 10))
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert isinstance(unpacked, NestedObject)
        assert isinstance(unpacked.child, SimpleObject)


# Container Tests


class TestContainers:
    """Tests for containers with custom types."""

    def test_list_of_dates(self):
        """Test list of datetime.date."""
        original = [
            datetime.date(2025, 1, 1),
            datetime.date(2025, 6, 15),
            datetime.date(2025, 12, 31),
        ]
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert all(isinstance(d, datetime.date) for d in unpacked)

    def test_dict_with_custom_types(self):
        """Test dict with custom types as values."""
        original = {
            "date": datetime.date.today(),
            "uuid": uuid.uuid4(),
            "decimal": decimal.Decimal("123.45"),
        }
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert isinstance(unpacked["date"], datetime.date)
        assert isinstance(unpacked["uuid"], uuid.UUID)
        assert isinstance(unpacked["decimal"], decimal.Decimal)

    def test_list_of_objects(self):
        """Test list of objects."""
        original = [SimpleObject(1, 2), SimpleObject(3, 4), SimpleObject(5, 6)]
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert all(isinstance(obj, SimpleObject) for obj in unpacked)

    def test_list_of_dataclasses(self):
        """Test list of dataclasses."""
        original = [
            SimpleDataclass(name="a", value=1),
            SimpleDataclass(name="b", value=2),
            SimpleDataclass(name="c", value=3),
        ]
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert all(isinstance(dc, SimpleDataclass) for dc in unpacked)


# File I/O Tests


class TestFileIO:
    """Tests for file stream operations."""

    def test_pack_unpack_file(self):
        """Test pack/unpack with file streams."""
        original = {
            "date": datetime.date.today(),
            "uuid": uuid.uuid4(),
            "decimal": decimal.Decimal("999.99"),
        }

        # Write to bytes buffer
        buffer = io.BytesIO()
        pack(original, buffer)

        # Read from buffer
        buffer.seek(0)
        unpacked = unpack(buffer)

        assert unpacked == original

    def test_packb_unpackb(self):
        """Test packb/unpackb functions."""
        original = SimpleDataclass(name="test", value=42)
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert isinstance(packed, bytes)


# Edge Cases and Error Tests


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_none_value(self):
        """Test None serialization."""
        original = {"value": None}
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original
        assert unpacked["value"] is None

    def test_empty_dict(self):
        """Test empty dict."""
        original = {}
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original

    def test_empty_list(self):
        """Test empty list."""
        original = []
        packed = packb(original)
        unpacked = unpackb(packed)

        assert unpacked == original

    def test_mixed_types_list(self):
        """Test list with mixed types."""
        original = [
            1,
            "string",
            datetime.date.today(),
            uuid.uuid4(),
            SimpleObject(1, 2),
            SimpleDataclass(name="test", value=42),
        ]
        packed = packb(original)
        unpacked = unpackb(packed)

        assert len(unpacked) == len(original)
        assert unpacked[0] == 1
        assert unpacked[1] == "string"
        assert isinstance(unpacked[2], datetime.date)
        assert isinstance(unpacked[3], uuid.UUID)
        assert isinstance(unpacked[4], SimpleObject)
        assert isinstance(unpacked[5], SimpleDataclass)

    def test_nested_containers(self):
        """Test deeply nested containers."""
        original = {
            "level1": {"level2": {"level3": [SimpleDataclass(name="deep", value=999)]}}
        }
        packed = packb(original)
        unpacked = unpackb(packed)

        assert isinstance(unpacked["level1"]["level2"]["level3"][0], SimpleDataclass)
        assert unpacked["level1"]["level2"]["level3"][0].name == "deep"


# Complex Integration Tests


class TestComplexScenarios:
    """Tests for complex real-world scenarios."""

    def test_mixed_objects_and_dataclasses(self):
        """Test mixing objects and dataclasses."""
        obj = SimpleObject(1, 2)
        dc = SimpleDataclass(name="test", value=42)

        original = {
            "object": obj,
            "dataclass": dc,
            "nested": {"more_objects": [obj, dc]},
        }

        packed = packb(original)
        unpacked = unpackb(packed)

        assert isinstance(unpacked["object"], SimpleObject)
        assert isinstance(unpacked["dataclass"], SimpleDataclass)
        assert isinstance(unpacked["nested"]["more_objects"][0], SimpleObject)
        assert isinstance(unpacked["nested"]["more_objects"][1], SimpleDataclass)

    def test_object_with_all_custom_types(self):
        """Test object containing all custom types (using dict container)."""
        # Note: Use dict instead of locally-defined class to avoid reconstruction issues
        original = {
            "date": datetime.date.today(),
            "datetime": datetime.datetime.now(),
            "decimal": decimal.Decimal("123.45"),
            "uuid": uuid.uuid4(),
            "memview": memoryview(b"data"),
            "dataclass": SimpleDataclass(name="nested", value=100),
            "object": SimpleObject(1, 2),
        }

        packed = packb(original)
        unpacked = unpackb(packed)

        assert isinstance(unpacked["date"], datetime.date)
        assert isinstance(unpacked["datetime"], datetime.datetime)
        assert isinstance(unpacked["decimal"], decimal.Decimal)
        assert isinstance(unpacked["uuid"], uuid.UUID)
        assert isinstance(unpacked["memview"], bytes)
        assert isinstance(unpacked["dataclass"], SimpleDataclass)
        assert isinstance(unpacked["object"], SimpleObject)
