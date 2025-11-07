import pytest
from rick.form import RequestRecord, Field, field, record, recordset
from rick.mixin import Translator


class UserRequest(RequestRecord):
    fields = {
        "name": field(validators="required|minlen:4|maxlen:8"),
        "age": field(validators="required|numeric|between:21,90"),
        "phone": field(validators="numeric|minlen:8|maxlen:16"),
    }


class RequestCustomError(RequestRecord):
    fields = {
        "name": field(validators="required|minlen:4|maxlen:8", error="invalid name"),
        "age": field(validators="required|numeric|between:21,90"),
        "phone": field(validators="numeric|minlen:8|maxlen:16", error="invalid phone"),
    }


class RequestCustomValidator(UserRequest):
    def validator_name(self, data, t: Translator):
        # this validator is only run if standard form validation is successful
        if data["name"] == "dave":
            self.add_error("name", "Dave is not here, man")
            return False
        return True


fixture1_data = [
    # -----------------------------------------------------------------------------------------------------------------
    # simple case, valid
    [
        # class
        UserRequest,
        # data
        {"name": "john", "age": 22, "phone": "212212212"},
        # result
        {},
    ],
    # simple case, invalid
    [
        # class
        UserRequest,
        # data
        {"name": "sue", "age": 17, "phone": "212212212"},
        # errors
        {
            "name": {"minlen": "minimum allowed length is 4"},
            "age": {"between": "must be between 21 and 90"},
        },
    ],
    # -----------------------------------------------------------------------------------------------------------------
    # custom error message, valid
    [
        # class
        RequestCustomError,
        # data
        {"name": "john", "age": 22, "phone": "212212212"},
        # result
        {},
    ],
    # custom error message, invalid
    [
        # class
        RequestCustomError,
        # data
        {"name": "sue", "age": 21, "phone": "2a"},
        # errors
        {
            "name": {"*": "invalid name"},
            "phone": {  # phone fails 2 validators, but messages are overriden by custom message
                "*": "invalid phone"
            },
        },
    ],
    # -----------------------------------------------------------------------------------------------------------------
    # custom validator message, valid
    [
        # class
        RequestCustomValidator,
        # data
        {"name": "john", "age": 22, "phone": "212212212"},
        # result
        {},
    ],
    # custom validator message, invalid, fails on phone validators (no custom validator code is reached)
    [
        # class
        RequestCustomValidator,
        # data
        {"name": "dave", "age": 21, "phone": "2a"},
        # errors
        {
            "phone": {
                "minlen": "minimum allowed length is 8",
                "numeric": "only digits allowed",
            }
        },
    ],
    # custom validator message, invalid, fails on name, using custom validator code
    [
        # class
        RequestCustomValidator,
        # data
        {"name": "dave", "age": 21, "phone": "21212121"},
        # errors
        {
            "name": {
                "*": "Dave is not here, man",
            }
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
    assert is_valid == req.is_valid(data)
    assert req.get_errors() == result


def test_requesrecord_filter():
    pass
