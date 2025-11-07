from rick.filter import registry as filter_registry, Filter
import inspect

TYPE_FIELD = 1
TYPE_RECORD = 2
TYPE_RECORDSET = 3


def field(**kwargs):
    """
    Spec wrapper for Field

    :param type: str field type
    :param label: str field label
    :param value: optional predefined value
    :param required: bool required
    :param readonly: bool readonly
    :param validators: string|dict validators
    :param error: optional custom error message
    :param select: optional select value list
    :param filter: optional filter
    :param attributes: dict optional attributes
    :param options: dict extra options
    :return: dict
    """
    kwargs["cls"] = Field
    kwargs["_type"] = TYPE_FIELD
    return kwargs


def record(cls, required=False, error=None):
    """
    Spec wrapper for a record
    :param cls: record class
    :param required: if the field is mandatory
    :return: dict
    """
    return {
        "_type": TYPE_RECORD,
        "cls": cls,
        "validators": "required|dict" if required else "dict",
        "error": error,
    }


def recordset(cls, required=False, error=None):
    """
    Spec wrapper for a list of records
    :param cls: record class
    :param required: if the field is mandatory
    :return: dict
    """
    return {
        "_type": TYPE_RECORDSET,
        "cls": cls,
        "validators": "required|list" if required else "list",
        "error": error,
    }


class Field:
    def __init__(
        self,
        type="",
        label="",
        value=None,
        required=False,
        readonly=False,
        validators="",
        error=None,
        select: list = None,
        filter=None,
        attributes: dict = None,
        options: dict = None,
        bind: str = None,
    ):
        """
        Field Constructor
        :param type: str field type
        :param label: str field label
        :param value: optional predefined value
        :param required: bool required
        :param readonly: bool readonly
        :param validators: string|dict validators
        :param error: optional custom error message
        :param select: optional select value list
        :param filter: optional filter
        :param attributes: dict optional attributes
        :param options: dict extra options
        :param bind: optional bind name for data elements
        """
        if select is None:
            select = []

        if attributes is None:
            attributes = {}

        if options is None:
            options = {}

        # Field attributes
        self.type = type
        self.label = label
        self.value = value
        self.required = required
        self.readonly = readonly
        self.validators = validators
        self.error_message = error
        self.select = select
        self.filter = filter
        self.attributes = attributes
        self.options = options
        self.bind = bind

        # pass direct read-only mapping to options
        if self.readonly:
            self.options["readonly"] = True

        # pass direct options read-only to main scope
        if "readonly" in self.options.keys():
            self.readonly = self.options["readonly"]

        # fetch/build filter object if any
        if self.filter is not None:
            if isinstance(self.filter, str):
                # self.filter has a filter name, use it to fetch the object
                if not filter_registry.has(self.filter):
                    raise ValueError("Invalid filter name '{}'".format(self.filter))
                self.filter = filter_registry.get(self.filter)
            elif inspect.isclass(self.filter):
                # build object
                self.filter = self.filter()
                if not isinstance(self.filter, Filter):
                    raise ValueError("Field filter must be either a string or a class")

        if self.required:
            # add required validator
            if len(self.validators) == 0:
                self.validators = {"required": None}
            else:
                if isinstance(self.validators, str):
                    self.validators = "required|" + self.validators
                elif isinstance(self.validators, dict):
                    self.validators["required"] = None
