from inspect import isclass
from typing import Any, Union, List
from rick.mixin import Translator
from rick.util.object import get_attribute_names
from rick.validator import Validator
from deprecated import deprecated
from .field import Field, TYPE_FIELD, TYPE_RECORD, TYPE_RECORDSET


class RequestRecord:
    def __init__(self, translator: Translator = None):
        """
        Constructor
        :param translator: optional translator object
        """
        if not translator:
            translator = Translator()

        self.validator = Validator()
        self.errors = {}
        self._translator = translator

        # Fields can be defined as class attribute items, as a spec to be used to assemble the final runtime objects:
        # class MyRequest(RequestRecord):
        #     fields = {
        #       'field_name': field(validators="..."), # field is declared as a spec
        #     }
        #     (...)
        # These specs are a dict with the parameters to build the appropriate object (usually Field instances), as well
        # as the actual class to be used in this build process. Specs can easily be declared by
        # using the field() function
        #
        # When the RequestRecord is initialized, these specs (if any) are automatically converted to fields, and
        # the fields dict is replaced by an instance attribute with the same name, and the proper object list
        #
        # Records and Recordsets are handled both as fields and as separate structures; The basic field definition is
        # kept as a field (mostly for validation purposes), but the actual objects are handled in separate collections
        self.records = {}
        self.recordsets = {}

        fields = {}
        if hasattr(self, "fields"):
            field_spec = getattr(self, "fields")
            if isinstance(field_spec, dict):
                # create objects from existing spec
                for name, spec in field_spec.items():
                    args = spec.copy()
                    field_type = args.pop("_type")
                    if field_type == TYPE_FIELD:
                        obj = args.pop("cls")(**args)

                    elif field_type in [TYPE_RECORD, TYPE_RECORDSET]:
                        cls = args.pop("cls")
                        # create dummy field with validators
                        obj = Field(**args)
                        # create record
                        if field_type == TYPE_RECORD:
                            self.records[name] = cls(self._translator)
                        else:
                            self.recordsets[name] = cls(self._translator)

                    # add field to the collection
                    fields[name] = obj

                    # add validation rules if exist
                    if len(obj.validators) > 0:
                        self.validator.add_field(
                            name, obj.validators, obj.error_message
                        )
            else:
                raise ValueError("RequestRecord(): invalid  field spec format")
        self.fields = fields

    def clear(self):
        """
        Removes all fields and errors
        :return: self
        """
        self.fields = {}
        self.errors = {}
        self.records = {}
        self.recordsets = {}
        return self

    def field(self, field_id: str, **kwargs):
        """
        Adds a field to the form

        :param field_id:
        :param kwargs:
        :return: self
        """
        if field_id in self.fields.keys():
            raise RuntimeError("duplicated field id '%s'" % (id,))

        field = Field(**kwargs)
        self.add_field(field_id, field)
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

    def is_valid(self, data: dict) -> bool:
        """
        Validate fields

        magic validation methods are run only if the fields pass regular validation - the rationale is to avoid
        having basic validation (such as required, numeric, etc) repeated within the custom validator code

        :param data: dict of values to validate
        :return: True if dict is valid, False otherwise
        """
        self.clear_errors()
        valid_fields = self.validator.is_valid(data, self._translator)

        # validate records
        valid_records = True

        # dict-like records
        for record_name, record in self.records.items():
            # record may or may not be required
            if record_name in data.keys():
                record_data = data[record_name]
                if record.is_valid(record_data):
                    # copy potentially filtered data to the field
                    self.fields[record_name].value = record.get_data()
                else:
                    valid_records = False
                    self._add_record_error(record_name, record.get_errors())

        # record sets (lists)
        for record_name, record in self.recordsets.items():
            # record may or may not be required
            if record_name in data.keys():
                record_errors = {}
                record_values = []
                i = 0
                for record_data in data[record_name]:
                    if record.is_valid(record_data):
                        record_values.append(record.get_data())
                    else:
                        record_errors[i] = record.get_errors()
                    i += 1

                if len(record_errors) > 0:
                    valid_records = False
                    self._add_record_error(record_name, record_errors)
                else:
                    self.fields[record_name].value = record_values

        if valid_fields and valid_records:
            # set values for fields
            for field_name, field in self.fields.items():
                # attempt to find a method called validator_<field_id>() in the current object
                method_name = "_".join(["validator", field_name.replace("-", "_")])
                custom_validator = getattr(self, method_name, None)
                # if exists and is method
                if custom_validator and callable(custom_validator):
                    # execute custom validator method
                    if not custom_validator(data, self._translator):
                        # note: errors are added inside the custom validator method; at this point,
                        # there are no other errors, as valid_fields and valid_records is true
                        return False

                if field_name in data.keys():
                    if field.filter is None:
                        field.value = data[field_name]
                    else:
                        field.value = field.filter.transform(data[field_name])
                else:
                    field.value = None
            return True

        # concat validation errors with record errors
        self.errors = {**self.errors, **self.validator.get_errors()}
        return False

    @deprecated("replaced by function get_errors()")
    def error_messages(self) -> dict:
        """
        Get validation error messages
        :return: dict
        """
        return self.errors

    def get_errors(self) -> dict:
        """
        Alias for self.error_messages()
        :return:
        """
        return self.errors

    def clear_errors(self):
        """
        Clean the error collection
        :return: none
        """
        self.errors = {}

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

    def get(self, id: str) -> Any:
        """
        Retrieve field value by id
        :param id: field id
        :return: Any
        """
        if id in self.fields.keys():
            return self.fields[id].value
        return None

    def get_data(self) -> dict:
        """
        Retrieve all data as a dict
        :return: dict
        """
        result = {}
        for id, f in self.fields.items():
            result[id] = f.value
        return result

    def bind(self, cls_obj) -> Any:
        """
        Retrieve all data as a cls_obj object

        Notes:
            - only non-None values are binded!!! (this is required to prevent eg. primary keys becoming null on insert)
            - if cls_obj is a class, a new instance is created and used as target object
            - attribute name can be specified via bind=name parameter in the Field class; if bind name is specified,
            it is used instead of id for binding purposes
            - attributes are copied by name; if the attribute doesn't exist in the target object, it is ignored
            - This method can be used to easily convert form data into RickDB Records

        :param cls_obj: class or object
        :return: cls_obj object instance
        """
        if isclass(cls_obj):
            cls_obj = cls_obj()

        # create field map based on optional bind fields
        bind_fields = {}
        for name, field in self.fields.items():
            if field.value is not None:
                if field.bind is None:
                    bind_fields[name] = field
                else:
                    bind_fields[field.bind] = field

        for name in get_attribute_names(cls_obj):
            if name in bind_fields.keys():
                setattr(cls_obj, name, bind_fields[name].value)
        return cls_obj

    def bindx(self, cls_obj) -> Any:
        """
        Retrieve all data as a cls_obj object, and all non-mapped attributes as a dict

        Notes:
            - only non-None values are binded!!! (this is required to prevent eg. primary keys becoming null on insert)
            - if cls_obj is a class, a new instance is created and used as target object
            - attribute name can be specified via bind=name parameter in the Field class; if bind name is specified,
            it is used instead of id for binding purposes
            - attributes are copied by name; if the attribute doesn't exist in the target object, it is returned as
            unmapped value
            - This method can be used to easily convert form data into RickDB Records

        :param cls_obj: class or object
        :return: (cls_obj object instance, dict of unmapped values)
        """
        if isclass(cls_obj):
            cls_obj = cls_obj()

        result = {}
        # create field map based on optional bind fields
        bind_fields = {}
        for name, field in self.fields.items():
            if field.value is not None:
                if field.bind is None:
                    bind_fields[name] = field
                else:
                    bind_fields[field.bind] = field

        obj_attrs = get_attribute_names(cls_obj)
        for name, field in bind_fields.items():
            if name in obj_attrs:
                setattr(cls_obj, name, bind_fields[name].value)
            else:
                result[name] = bind_fields[name].value
        return cls_obj, result

    def set(self, id: str, value: Any):
        """
        Set field value
        :param id: field id
        :param value: value
        :return: self
        """
        if id in self.fields.keys():
            self.fields[id].value = value
        return self

    def get_translator(self) -> Translator:
        return self._translator

    def _add_record_error(self, id: str, errors: Union[List, dict]):
        """
        Adds or overrides record validation errors
        if the record field already has errors, they are removed and replaced by  the specified ones
        :param id: field id
        :param errors: record errors
        :return self
        """
        if id not in self.fields.keys():
            raise ValueError("invalid field id %s" % (id,))
        self.errors[id] = {"_": errors}
        return self
