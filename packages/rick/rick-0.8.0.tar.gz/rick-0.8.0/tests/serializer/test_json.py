import json
from rick.serializer.json.json import CamelCaseJsonEncoder, ExtendedJsonEncoder


class SomeRecord:
    def asdict(self) -> dict:
        return {
            "first_name": "first_name",
            "last_name": "last_name",
        }


def test_json_encoder_memoryview():
    record = {
        "key1": b"some binary string",
        "key2": memoryview(b"other binary string"),
        "key3": b'special "',
    }
    serialized = json.dumps(record, cls=ExtendedJsonEncoder)
    assert (
        serialized
        == '{"key1": "some binary string", "key2": "other binary string", "key3": "special \\""}'
    )
    result = json.loads(serialized)
    assert result["key1"] == "some binary string"
    assert result["key2"] == "other binary string"
    assert result["key3"] == 'special "'


def test_camelcase_json_encoder():
    record = SomeRecord()
    serialized = json.dumps(record, cls=CamelCaseJsonEncoder)
    result = json.loads(serialized)
    assert len(result) == 2
    assert result["firstName"] == "first_name"
    assert result["lastName"] == "last_name"
