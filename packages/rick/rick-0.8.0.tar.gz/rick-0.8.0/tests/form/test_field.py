from rick.form import Field


def test_field_class():
    # simple field test
    f = Field(type="abc", label="def", value=123)
    assert f.type == "abc"
    assert f.label == "def"
    assert f.value == 123

    # test readonly
    assert f.readonly is False
    f = Field(options={"readonly": True})
    assert f.readonly is True
    f = Field(readonly=True)
    assert f.readonly is True

    # test required
    f = Field(required=True)
    assert f.validators == {"required": None}
    f = Field(required=True, validators="minlen:3|maxlen:45")
    assert f.validators == "required|minlen:3|maxlen:45"

    # test required with dict validators
    f = Field(required=True)
    assert f.validators == {"required": None}
    f = Field(required=True, validators={"minlen": [3], "maxlen": [45]})
    assert f.validators == {"required": None, "minlen": [3], "maxlen": [45]}
