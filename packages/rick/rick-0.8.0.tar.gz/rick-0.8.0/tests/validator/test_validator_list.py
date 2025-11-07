import pytest
from rick.validator import Validator

FIELD_NAME = "list"

list_values = {
    "v1": {FIELD_NAME: None},
    "v2": {FIELD_NAME: "String"},
    "v3": {FIELD_NAME: 3},
    "v4": {},
    "v5": {FIELD_NAME: [1]},
    "v6": {FIELD_NAME: [1, 2, 3, 4, 5, 6]},
}

list_rules_results = {
    "list": {
        "v1": {},  # field not required, None is fine
        "v2": {FIELD_NAME: {"list": "value is not a list"}},
        "v3": {FIELD_NAME: {"list": "value is not a list"}},
        "v4": {},
        "v5": {},
        "v6": {},
    },
    "required|list": {
        "v1": {FIELD_NAME: {"required": "value required"}},
        "v2": {FIELD_NAME: {"list": "value is not a list"}},
        "v3": {FIELD_NAME: {"list": "value is not a list"}},
        "v4": {FIELD_NAME: {"required": "value required"}},
        "v5": {},
        "v6": {},
    },
    "required|list|listlen:2": {
        "v1": {FIELD_NAME: {"required": "value required"}},
        "v2": {
            FIELD_NAME: {
                "list": "value is not a list",
                "listlen": "item count must be between 2 and ∞",
            }
        },
        "v3": {
            FIELD_NAME: {
                "list": "value is not a list",
                "listlen": "item count must be between 2 and ∞",
            }
        },
        "v4": {FIELD_NAME: {"required": "value required"}},
        "v5": {FIELD_NAME: {"listlen": "item count must be between 2 and ∞"}},
        "v6": {},
    },
    "required|list|listlen:2,4": {
        "v1": {FIELD_NAME: {"required": "value required"}},
        "v2": {
            FIELD_NAME: {
                "list": "value is not a list",
                "listlen": "item count must be between 2 and 4",
            }
        },
        "v3": {
            FIELD_NAME: {
                "list": "value is not a list",
                "listlen": "item count must be between 2 and 4",
            }
        },
        "v4": {FIELD_NAME: {"required": "value required"}},
        "v5": {FIELD_NAME: {"listlen": "item count must be between 2 and 4"}},
        "v6": {FIELD_NAME: {"listlen": "item count must be between 2 and 4"}},
    },
    "required|list|listlen:2,5": {
        "v1": {FIELD_NAME: {"required": "value required"}},
        "v2": {
            FIELD_NAME: {
                "list": "value is not a list",
                "listlen": "item count must be between 2 and 5",
            }
        },
        "v3": {
            FIELD_NAME: {
                "list": "value is not a list",
                "listlen": "item count must be between 2 and 5",
            }
        },
        "v4": {FIELD_NAME: {"required": "value required"}},
        "v5": {FIELD_NAME: {"listlen": "item count must be between 2 and 5"}},
        "v6": {FIELD_NAME: {"listlen": "item count must be between 2 and 5"}},
    },
}


@pytest.mark.parametrize("data", [(list_rules_results, list_values)])
def test_validator_list(data):
    for rule, results in data[0].items():
        for tag, result in results.items():
            v = Validator()
            v.add_field(FIELD_NAME, rule)

            valid = v.is_valid(data[1][tag])
            assert v.get_errors() == result
            assert valid == (len(result) == 0)
