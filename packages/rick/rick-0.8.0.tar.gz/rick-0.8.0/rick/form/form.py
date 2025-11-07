from rick.mixin import Translator
from .requestrecord import RequestRecord
from .field import Field


class Control:
    type = ""
    label = ""
    value = None
    attributes = {}
    options = {}

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class FieldSet:
    def __init__(self, parent: RequestRecord, id: str, label: str):
        self.id = id
        self.label = label
        self.form = parent
        self.translator = parent.get_translator()
        self.fields = {}

    def field(self, field_type: str, field_id: str, label: str, **kwargs):
        """
        Adds a field

        Optional kwargs:
        value=None: Field value
        required=True: If field is required
        validators=[list] |  validators="string": Validator list
        messages={}: Custom validation messages
        select={}: dict of values:labels for select
        attributes={}: optional visualization attributes
        options={}: optional field-specific options

        :param field_type:
        :param field_id:
        :param label:
        :return: self
        """

        if field_id in self.fields.keys():
            raise RuntimeError("duplicated field id '%s'" % (id,))

        kwargs["type"] = field_type
        kwargs["label"] = self.translator.t(label)
        field = Field(**kwargs)
        self.fields[field_id] = field
        self.form.add_field(field_id, field)
        return self


class Form(RequestRecord):
    DEFAULT_FIELDSET = "__default__"
    METHOD_POST = "POST"
    METHOD_PUT = "PUT"
    METHOD_PATCH = "PATCH"
    METHOD_SEARCH = "SEARCH"

    def __init__(self, translator: Translator = None):
        super().__init__(translator)
        self._fieldsets = {}
        self.controls = {}
        self.method = self.METHOD_POST
        self.action = ""
        self.fieldset(self.DEFAULT_FIELDSET, "")

    def set_action(self, url: str):
        """
        Define action URL
        :param url: action url
        :return: self
        """
        self.action = url
        return self

    def get_action(self) -> str:
        """
        Get action url value
        :return: str
        """
        return self.action

    def set_method(self, method: str):
        """
        Set HTTP method
        :param method:
        :return: self
        """
        self.method = method
        return self

    def get_method(self) -> str:
        """
        Get HTTP Method
        :return: str
        """
        return self.method

    def clear(self):
        """
        Removes all defined items
        :return:
        """
        super().clear()
        self._fieldsets = {}
        self.controls = {}
        self.method = self.METHOD_POST
        self.action = ""

    def fieldset(self, id: str, label: str) -> FieldSet:
        """
        Adds/retrieves a fieldset to the form
        If fieldset doesn't exist, it is created
        If a fieldset exists, its label is updated **unless** label is empty

        :param id: fieldset id
        :param label: fieldset legend
        :return: FieldSet
        """
        if len(label) > 0:
            label = self._translator.t(label)
        # if its existing, update label and return

        if id in self._fieldsets.keys():
            # only update label if label is not none
            if len(label) > 0:
                self._fieldsets[id].label = label
            return self._fieldsets[id]

        fs = FieldSet(self, id, label)
        self._fieldsets[id] = fs
        return fs

    def field(self, field_type: str, field_id: str, label: str, **kwargs):
        """
        Adds a field to the form

        Alias for FieldSet:field(), and will use the internal DEFAULT_FIELDSET

        :param field_type:
        :param field_id:
        :param label:
        :param kwargs:
        :return: FieldSet
        """
        return self.fieldset(self.DEFAULT_FIELDSET, "").field(
            field_type, field_id, self._translator.t(label), **kwargs
        )

    def control(self, control_type: str, control_id: str, label: str, **kwargs):
        """
        Adds a control element to the form
        :param control_type:
        :param control_id:
        :param label:
        :param kwargs:
        :return: self
        """
        kwargs["type"] = control_type
        kwargs["label"] = self._translator.t(label)
        control = Control(**kwargs)
        self.controls[control_id] = control
        return self

    def add_field(self, id: str, field: Field):
        """
        Add a field object to the internal collection
        :param id: field id
        :param field: field object
        :return: self
        """
        self.fields[id] = field
        if len(field.validators) > 0:
            self.validator.add_field(id, field.validators, field.error_message)
        return self

    def add_error(self, id: str, error_message: str):
        """
        Adds or overrides a validation error to a field
        if field already have errors, they are removed and replaced by a wildcard error
        :param id field id
        :param error_message error message
        :return self
        """
        if id not in self.fields.keys():
            raise ValueError("invalid field id %s" % (id,))
        if self._translator is not None:
            error_message = self._translator.t(error_message)
        self.errors[id] = {"*": error_message}
        return self

    def get_fieldsets(self) -> dict:
        """
        Get internal fieldset dict
        :return: dict
        """
        return self._fieldsets
