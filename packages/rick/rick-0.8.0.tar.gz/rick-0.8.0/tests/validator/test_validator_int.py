import pytest
from rick.validator import Validator

int_spec = {
    "field1": {
        "required": None,
        "int": None,
    },
}

int_fixture = [
    [
        int_spec,
        {"field1": "1"},
        {},
    ],
    [
        int_spec,
        {"field1": "-1"},
        {},
    ],
    [
        int_spec,
        {"field1": "909999999"},
        {},
    ],
    [
        int_spec,
        {"field1": "-32435343451"},
        {},
    ],
    [
        int_spec,
        {"field1": "1a"},
        {"field1": {"int": "only integer values are allowed"}},
    ],
    [
        int_spec,
        {"field1": ""},
        {"field1": {"int": "only integer values are allowed"}},
    ],
]


@pytest.mark.parametrize("validators,values,result", int_fixture)
def test_int_validator(validators, values, result):
    v = Validator(validators)

    for field, opts in validators.items():
        r = v.field_rules(field)
        if isinstance(opts, dict):
            assert len(r) == len(opts)

    with pytest.raises(ValueError):
        v.field_rules("non-existing-field")

    valid = v.is_valid(values)
    assert valid == (len(result) == 0)
    assert v.get_errors() == result
