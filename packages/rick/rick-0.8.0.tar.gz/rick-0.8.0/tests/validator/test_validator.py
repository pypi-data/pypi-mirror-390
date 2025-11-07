import pytest
from rick.mixin import Translator
from rick.validator import Validator

# field validators in dict format
dict_validators = {
    "field1": {
        "required": None,
        "maxlen": 3,
    },
    "field2": {
        "minlen": 4,
    },
    "field3": {
        "required": None,
        "bail": None,
        "numeric": None,
        "len": [2, 4],
    },
}

# field validators in str format
str_validators = {
    "field1": "required|maxlen:3",
    "field2": "minlen:4",
    "field3": "bail|required|numeric|len:2,4",
}

#
# Fixtures for validator format
fixtures_formats = [
    [
        # ==== dict format - no error
        dict_validators,
        {"field1": "123", "field2": "abcdef", "field3": "123"},
        {},
    ],
    [
        # ==== dict format - error
        dict_validators,
        {"field2": "abcdef", "field3": "13"},
        {"field1": {"required": "value required"}},
    ],
    [
        # ==== dict format - all error
        dict_validators,
        {"field2": "", "field3": "a"},
        {
            "field1": {"required": "value required"},
            "field2": {"minlen": "minimum allowed length is 4"},
            "field3": {"numeric": "only digits allowed"},
        },
    ],
    [
        # ==== string format - no error
        str_validators,
        {"field1": "123", "field2": "abcdef", "field3": "123"},
        {},
    ],
    [
        # ==== str format - error
        str_validators,
        {"field2": "abcdef", "field3": "13"},
        {"field1": {"required": "value required"}},
    ],
    [
        # ==== str format - all error
        str_validators,
        {"field2": "", "field3": "a"},
        {
            "field1": {"required": "value required"},
            "field2": {"minlen": "minimum allowed length is 4"},
            "field3": {"numeric": "only digits allowed"},
        },
    ],
]

messages_case1 = {
    "field2": "custom message for field 2",
    "field3": "custom message for field 3",
}

fixtures = [
    [
        # ==== valid case, no errors
        str_validators,
        {"field1": "123", "field2": "abcdef", "field3": "123"},
        {},
    ],
    [
        # ==== errors in all fields
        str_validators,
        {"field2": "abc", "field3": "1"},
        {
            "field1": {"required": "value required"},
            "field2": {"minlen": "minimum allowed length is 4"},
            "field3": {"len": "length must be between [2, 4]"},
        },
    ],
    [
        # ==== errors, len of numeric
        str_validators,
        {"field1": "abc", "field2": "abcd", "field3": 1},
        {"field3": {"len": "length must be between [2, 4]"}},
    ],
    [
        # ==== errors, bail test
        str_validators,
        {
            "field1": "abc",
            "field2": "abcd",
            "field3": "a",  # fail numeric and length, only numeric is reported due to bail
        },
        {"field3": {"numeric": "only digits allowed"}},
    ],
]

#
# Fixtures for translator test
fixtures_translator = [
    [
        # ==== valid case, no errors
        str_validators,
        {"field1": "123", "field2": "abcdef", "field3": "123"},
        {},
    ],
    [
        # ==== errors in all fields
        str_validators,
        {"field2": "abc", "field3": "1"},
        {
            "field1": {"required": "mana mana"},
            "field2": {"minlen": "mana mana"},
            "field3": {"len": "mana mana"},
        },
    ],
    [
        # ==== errors, len of numeric
        str_validators,
        {"field1": "abc", "field2": "abcd", "field3": 1},
        {"field3": {"len": "mana mana"}},
    ],
    [
        # ==== errors, bail test
        str_validators,
        {
            "field1": "abc",
            "field2": "abcd",
            "field3": "a",  # fail numeric and length, only numeric is reported due to bail
        },
        {"field3": {"numeric": "mana mana"}},
    ],
]


class ManaManaTranslator(Translator):
    def t(self, text: str):
        return "mana mana"


@pytest.mark.parametrize("validators,values,result", fixtures_formats)
def test_validator(validators, values, result):
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


@pytest.mark.parametrize("validators,values,result", fixtures)
def test_fixtures(validators, values, result):
    v = Validator(validators)
    for field, opts in values.items():
        r = v.field_rules(field)
        assert isinstance(r, dict)
        assert len(r) > 0

    valid = v.is_valid(values)
    assert valid == (len(result) == 0)
    assert v.get_errors() == result


@pytest.mark.parametrize("validators,values,result", fixtures_translator)
def test_translator(validators, values, result):
    v = Validator(validators)
    t = ManaManaTranslator()

    for field, opts in values.items():
        r = v.field_rules(field)
        assert isinstance(r, dict)
        assert len(r) > 0

    valid = v.is_valid(values, translator=t)
    assert valid == (len(result) == 0)
    assert v.get_errors() == result
