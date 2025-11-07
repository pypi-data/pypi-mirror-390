import pytest
from rick.form import Form, Field
from rick.mixin import Translator


class SampleForm_Simple(Form):
    def init(self):
        self.field(
            "text", "name", "Full Name", validators="required|minlen:4|maxlen:8"
        ).field(
            "text", "age", "Age", validators="required|numeric|between:9,125"
        ).field(
            "text", "phone", "Phone", validators="numeric|minlen:8|maxlen:16"
        )

        self.control("submit", "save", "Save").control("reset", "clear", "Clear Form")
        return self

    def validator_name(self, data, t: Translator):
        # this validator is only run if standard form validation is successful
        if data["name"] == "dave":
            self.add_error("name", "Dave is not here, man")
            return False
        return True


class SampleForm_Fieldset_a(Form):
    def init(self):
        fs = self.fieldset("fs1", "fs1_label")
        fs.field(
            "text", "name", "Full Name", validators="required|minlen:4|maxlen:8"
        ).field("text", "age", "Age", validators="required|numeric|between:9,125")

        fs = self.fieldset("fs2", "fs2_label")
        fs.field(
            "text", "other_name", "Full Name", validators="required|minlen:4|maxlen:8"
        ).field("text", "other_age", "Age", validators="required|numeric|between:9,125")

        return self

    def validator_name(self, data, t: Translator):
        if data["name"] == "dave":
            self.add_error("name", "Dave is not here, man")
            return False
        return True


class UgaBugaTranslator(Translator):
    MESSAGE = "ugabuga"

    def t(self, message: str):
        return self.MESSAGE


sampleform_simple_payload = {
    "no_error": {"name": "john", "age": 32},
    "no_error_2": {"name": "john", "age": "32"},
    "no_error_3": {"name": "sarah", "age": "14", "phone": "900400300"},
    "custom_validator": {"name": "dave", "age": "17", "phone": "900320400"},
    "missing_field": {"name": "john"},
    "minlen_error": {"name": "j", "age": 32},
    "maxlen_error": {"name": "john_connor", "age": 32},
    "no_numeric_error": {"name": "john", "age": "abc"},
}
sampleform_simple_errors = {
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

sampleform_fieldset_a_payload = {
    "no_error": {"name": "john", "age": 29, "other_name": "john2", "other_age": 14},
    "no_error_2": {
        "name": "john",
        "age": "24",
        "other_name": "john2",
        "other_age": "17",
    },
    "missing_field": {"name": "john"},
    "minlen_error": {"name": "j", "age": 32, "other_name": "j"},
    "maxlen_error": {
        "name": "john_connor",
        "age": 17,
        "other_name": "john",
        "other_age": 14,
    },
    "no_numeric_error": {"name": "john", "age": "abc"},
}
sampleform_fieldset_a_errors = {
    "no_error": {},
    "no_error_2": {},
    "missing_field": {
        "age": {"required": "value required"},
        "other_age": {"required": "value required"},
        "other_name": {"required": "value required"},
    },
    "minlen_error": {
        "name": {"minlen": "minimum allowed length is 4"},
        "other_age": {"required": "value required"},
        "other_name": {"minlen": "minimum allowed length is 4"},
    },
    "maxlen_error": {"name": {"maxlen": "maximum allowed length is 8"}},
    "no_numeric_error": {
        "age": {
            "between": "must be between 9 and 125",
            "numeric": "only digits allowed",
        },
        "other_age": {"required": "value required"},
        "other_name": {"required": "value required"},
    },
}


def run_form(frm: Form, form_data, errors):
    for id, data in form_data.items():
        expected_errors = errors[id]
        assert frm.is_valid(data) == (len(expected_errors) == 0)
        assert frm.get_errors() == expected_errors


@pytest.mark.parametrize(
    "fixture", [(sampleform_simple_payload, sampleform_simple_errors)]
)
def test_form_simpleform(fixture):
    payload = fixture[0]
    errors = fixture[1]
    frm = SampleForm_Simple().init()
    run_form(frm, payload, errors)


@pytest.mark.parametrize(
    "fixture", [(sampleform_fieldset_a_payload, sampleform_fieldset_a_errors)]
)
def test_form_fieldset_a(fixture):
    payload = fixture[0]
    errors = fixture[1]
    frm = SampleForm_Fieldset_a().init()
    run_form(frm, payload, errors)


def test_form_translator():
    tr = UgaBugaTranslator()
    frm = SampleForm_Simple(tr).init()

    for _, field in frm.fields.items():
        assert field.label == UgaBugaTranslator.MESSAGE

    fs = frm.fieldset("fs1", "fieldset label")
    assert fs.label == UgaBugaTranslator.MESSAGE

    # error messages
    frm.is_valid({})
    for field, errors in frm.get_errors().items():
        for _, msg in errors.items():
            assert msg == UgaBugaTranslator.MESSAGE
