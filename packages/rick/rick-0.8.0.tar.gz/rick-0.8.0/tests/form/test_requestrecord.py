import pytest
from rick.form import RequestRecord, Field, field
from rick.mixin import Translator


class RequestRecord_A(RequestRecord):
    def init(self):
        self.field("name", validators="required|minlen:4|maxlen:8").field(
            "age", validators="required|numeric|between:9,125"
        ).field("phone", validators="numeric|minlen:8|maxlen:16")
        return self

    def validator_name(self, data, t: Translator):
        # this validator is only run if standard form validation is successful
        if data["name"] == "dave":
            self.add_error("name", "Dave is not here, man")
            return False
        return True


class RequestRecord_B(RequestRecord):
    fields = {
        "name": field(validators="required|minlen:4|maxlen:8"),
        "age": field(validators="required|numeric|between:9,125"),
        "phone": field(validators="numeric|minlen:8|maxlen:16"),
    }

    def validator_name(self, data, t: Translator):
        # this validator is only run if standard form validation is successful
        if data["name"] == "dave":
            self.add_error("name", "Dave is not here, man")
            return False
        return True


# RequestRecord variant with bind names
# bind names are used instead of the field name, for object mapping purposes
class RequestRecord_C(RequestRecord_B):
    fields = {
        "my_name": field(validators="required|minlen:4|maxlen:8", bind="name"),
        "age": field(validators="required|numeric|between:9,125"),
        "my_phone": field(validators="numeric|minlen:8|maxlen:16", bind="phone"),
    }


# RequestRecord variant with bindx names
# bindx is a bind() variant that also returns unmapped values
class RequestRecord_D(RequestRecord_B):
    fields = {
        "my_name": field(validators="required|minlen:4|maxlen:8", bind="name"),
        "age": field(validators="required|numeric|between:9,125"),
        "my_phone": field(validators="numeric|minlen:8|maxlen:16", bind="phone"),
        "unmapped_1": field(validators="maxlen:16"),
        "unmapped_2": field(validators="maxlen:16"),
        "unmapped_3": field(validators="maxlen:16"),
    }


class ObjectRecord:
    name = None
    age = None
    phone = None

    def asdict(self) -> dict:
        return {"name": self.name, "age": self.age, "phone": self.phone}


requestrecord_simple_fixture = {
    "no_error": {"name": "john", "age": 32},
    "no_error_2": {"name": "john", "age": "32"},
    "no_error_3": {"name": "sarah", "age": "14", "phone": "900400300"},
    "custom_validator": {"name": "dave", "age": "17", "phone": "900320400"},
    "missing_field": {"name": "john"},
    "minlen_error": {"name": "j", "age": 32},
    "maxlen_error": {"name": "john_connor", "age": 32},
    "no_numeric_error": {"name": "john", "age": "abc"},
}
requestrecord_simple_result = {
    "no_error": {},
    "no_error_2": {},
    "no_error_3": {},
    "custom_validator": {"name": {"*": "Dave is not here, man"}},
    "missing_field": {"age": {"required": "value required"}},
    "minlen_error": {"name": {"minlen": "minimum allowed length is 4"}},
    "maxlen_error": {"name": {"maxlen": "maximum allowed length is 8"}},
    "no_numeric_error": {
        "age": {
            "between": "must be between 9 and 125",
            "numeric": "only digits allowed",
        }
    },
}

rr_to_obj_input = [
    {"name": "john", "age": 32},
    {"name": "gary", "age": 60, "phone": "91000000"},
    {"name": "anthony", "age": 60, "phone": "92000000"},
]
rr_to_obj_output = [
    {"name": "john", "age": 32, "phone": None},
    {"name": "gary", "age": 60, "phone": "91000000"},
    {"name": "anthony", "age": 60, "phone": "92000000"},
]

bind_input = [
    {"my_name": "john", "age": 32},
    {"my_name": "gary", "age": 60, "my_phone": "91000000"},
    {"my_name": "anthony", "age": 60, "my_phone": "92000000"},
]
bind_output = [
    {"name": "john", "age": 32, "phone": None},
    {"name": "gary", "age": 60, "phone": "91000000"},
    {"name": "anthony", "age": 60, "phone": "92000000"},
]

bindx_input = [
    {"my_name": "john", "age": 32},
    {"my_name": "gary", "age": 60, "my_phone": "91000000", "unmapped_1": "field1"},
    {
        "my_name": "anthony",
        "age": 60,
        "my_phone": "92000000",
        "unmapped_1": "field1",
        "unmapped_2": "field2",
    },
]
bindx_output = [
    [{"name": "john", "age": 32, "phone": None}, {}],
    [{"name": "gary", "age": 60, "phone": "91000000"}, {"unmapped_1": "field1"}],
    [
        {"name": "anthony", "age": 60, "phone": "92000000"},
        {"unmapped_1": "field1", "unmapped_2": "field2"},
    ],
]


@pytest.mark.parametrize(
    "form_data, result", [(requestrecord_simple_fixture, requestrecord_simple_result)]
)
def test_requestrecord_a_validator(form_data, result):
    for id, data in form_data.items():
        frm = RequestRecord_A().init()

        assert frm.is_valid(data) == (len(result[id]) == 0)
        assert frm.get_errors() == result[id]


@pytest.mark.parametrize(
    "form_data, result", [(requestrecord_simple_fixture, requestrecord_simple_result)]
)
def test_requestrecord_b_validator(form_data, result):
    for id, data in form_data.items():
        # RequestRecord_B() has no custom init()
        frm = RequestRecord_B()

        assert frm.is_valid(data) == (len(result[id]) == 0)
        assert frm.get_errors() == result[id]


@pytest.mark.parametrize("form_data, result", [(rr_to_obj_input, rr_to_obj_output)])
def test_requestrecord_to_object(form_data, result):
    i = 0
    for data in form_data:
        frm = RequestRecord_B()
        assert frm.is_valid(data)
        # transform to ObjectRecord
        obj = frm.bind(ObjectRecord)
        assert obj is not None
        assert isinstance(obj, ObjectRecord)
        assert obj.asdict() == result[i]
        i += 1


@pytest.mark.parametrize("form_data, result", [(bind_input, bind_output)])
def test_requestrecord_to_object_bind(form_data, result):
    i = 0
    for data in form_data:
        frm = RequestRecord_C()
        assert frm.is_valid(data)
        # transform to ObjectRecord
        obj = frm.bind(ObjectRecord)
        assert obj is not None
        assert isinstance(obj, ObjectRecord)
        assert obj.asdict() == result[i]
        i += 1


@pytest.mark.parametrize("form_data, result", [(bindx_input, bindx_output)])
def test_requestrecord_to_object_bindx(form_data, result):
    i = 0
    for data in form_data:
        frm = RequestRecord_D()
        assert frm.is_valid(data)
        # transform to ObjectRecord
        obj, data = frm.bindx(ObjectRecord)
        assert obj is not None
        assert isinstance(obj, ObjectRecord)
        assert obj.asdict() == result[i][0]
        assert data == result[i][1]
        i += 1


def test_requestrecord():
    frm = RequestRecord_A().init()
    assert len(frm.fields) > 0
    frm.clear()
    assert len(frm.fields) == 0
    assert len(frm.errors) == 0

    # set value for existing field
    frm = RequestRecord_A().init()
    frm.set("name", "abc")
    assert frm.get_data()["name"] == "abc"

    # set value for non-existing field (should ignore)
    frm = RequestRecord_A()
    frm.set("address", "abc")
    assert "address" not in frm.fields.keys()
    assert "address" not in frm.get_data().keys()
