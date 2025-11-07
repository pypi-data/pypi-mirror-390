import pytest
from rick.validator import Validator

FIELD_NAME = "field1"

list_values = {
    "v1": {FIELD_NAME: None},
    "v2": {FIELD_NAME: "String"},
    "v3": {FIELD_NAME: 3},
    "v4": {},
    "v5": {FIELD_NAME: [1]},
    "v6": {FIELD_NAME: [1, 2, 3, 4, 5, 6]},
    "v7": {FIELD_NAME: [-1, 2, 3, 4, 5, 6]},
    "v8": {FIELD_NAME: [1, 2, "90", 4, 5, 6]},
    "v9": {FIELD_NAME: [1, 2, "90", 4, "50a", 6]},
}

list_rules_results = {
    "idlist": {
        "v1": {},  # field not required, None is fine
        "v2": {FIELD_NAME: {"idlist": "value is not a list of ids"}},
        "v3": {FIELD_NAME: {"idlist": "value is not a list of ids"}},
        "v4": {},
        "v5": {},
        "v6": {},
        "v7": {FIELD_NAME: {"idlist": "value is not a list of ids"}},
        "v8": {},
        "v9": {FIELD_NAME: {"idlist": "value is not a list of ids"}},
    },
    "required|idlist": {
        "v1": {FIELD_NAME: {"required": "value required"}},
        "v2": {FIELD_NAME: {"idlist": "value is not a list of ids"}},
        "v3": {FIELD_NAME: {"idlist": "value is not a list of ids"}},
        "v4": {FIELD_NAME: {"required": "value required"}},
        "v5": {},
        "v6": {},
        "v7": {FIELD_NAME: {"idlist": "value is not a list of ids"}},
        "v8": {},
        "v9": {FIELD_NAME: {"idlist": "value is not a list of ids"}},
    },
}


@pytest.mark.parametrize("data", [(list_rules_results, list_values)])
def test_validator_idlist(data):
    for rule, results in data[0].items():
        for tag, result in results.items():
            v = Validator()
            v.add_field(FIELD_NAME, rule)

            valid = v.is_valid(data[1][tag])
            assert v.get_errors() == result
            assert valid == (len(result) == 0)
