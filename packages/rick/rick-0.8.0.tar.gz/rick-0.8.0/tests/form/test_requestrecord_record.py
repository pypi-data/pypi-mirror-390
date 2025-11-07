import pytest
from rick.form import RequestRecord, Field, field, record, recordset
from rick.mixin import Translator


class UserRequest(RequestRecord):
    fields = {
        "name": field(validators="required|minlen:4|maxlen:8"),
        "age": field(validators="required|numeric|between:21,90"),
        "phone": field(validators="numeric|minlen:8|maxlen:16"),
    }


class TeamRecord(RequestRecord):
    fields = {
        "team_name": field(validators="required|minlen:4|maxlen:128"),
        "members": recordset(UserRequest, required=True),
    }


class TeamLeaderRecord(RequestRecord):
    fields = {
        "team_name": field(validators="required|minlen:4|maxlen:128"),
        "leader": record(UserRequest, required=True),
    }


fixture1_data = [
    # -----------------------------------------------------------------------------------------------------------------
    # recordlist, valid
    [
        # class
        TeamRecord,
        # data
        {
            "team_name": "some_name",
            "members": [
                {"name": "john", "age": 22, "phone": 212212212},
                {"name": "gary", "age": 21, "phone": 12345678},
            ],
        },
        # result
        {},
    ],
    # recordlist, errors
    [
        # class
        TeamRecord,
        # data
        {
            "team_name": 1,
            "members": [
                {"name": "john", "age": 22, "phone": "a"},
                {"name": "gary", "age": 16, "phone": 12345678},
            ],
        },
        # result
        {
            "members": {
                "_": {
                    0: {
                        "phone": {
                            "numeric": "only digits allowed",
                            "minlen": "minimum allowed length is 8",
                        }
                    },
                    1: {"age": {"between": "must be between 21 and 90"}},
                }
            },
            "team_name": {"minlen": "minimum allowed length is 4"},
        },
    ],
    # -----------------------------------------------------------------------------------------------------------------
    # record, valid
    [
        # class
        TeamLeaderRecord,
        # data
        {
            "team_name": "some_name",
            "leader": {"name": "john", "age": 22, "phone": 212212212},
        },
        # result
        {},
    ],
    # record, errors
    [
        # class
        TeamLeaderRecord,
        # data
        {"team_name": 1, "leader": {"name": "gary", "age": 16, "phone": 12345678}},
        # result
        {
            "leader": {"_": {"age": {"between": "must be between 21 and 90"}}},
            "team_name": {"minlen": "minimum allowed length is 4"},
        },
    ],
]


@pytest.mark.parametrize("cls, data, result", fixture1_data)
def test_requestrecord(cls, data, result):
    is_valid = len(result) == 0
    req = cls()

    # confirm fields are defined on the object
    for name, _ in data.items():
        assert name in req.fields.keys()

    # confirm validation
    req.is_valid(data)

    assert is_valid == req.is_valid(data)
    assert req.get_errors() == result


def test_requesrecord_filter():
    pass
