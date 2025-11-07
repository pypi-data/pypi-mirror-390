# Note:
# Regex logic is adapted from django's validators:https://github.com/django/django/blob/master/django/core/validators.py
#

import re
import iso8601
from collections.abc import Mapping
from rick.mixin import Translator
from rick.util.cast import cast_str, cast_int

from .rule import Rule, registry


@registry.register_cls(name="bail")
class Bail(Rule):
    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        return True, ""


@registry.register_cls(name="id")
class Id(Rule):
    MSG_ERROR = "invalid id"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is not None and value.isnumeric() and int(value) > 0:
            return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="uuid")
class Uuid(Rule):
    MSG_ERROR = "invalid uuid"
    REGEX = re.compile(r"^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$")

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is not None and self.REGEX.match(value):
            return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="required")
class Required(Rule):
    MSG_ERROR = "value required"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        if value is None:
            return False, self.error_message(error_msg, translator)
        return True, ""


@registry.register_cls(name="notempty")
class NotEmpty(Rule):
    MSG_ERROR = "cannot be empty"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is not None and len(value.strip()) > 0:
            return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="in")
class In(Rule):
    MSG_ERROR = "out of bound value"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_int(value)
        if not options:
            options = []

        if value is not None and (value in options):
            return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="notin")
class NotIn(Rule):
    MSG_ERROR = "out of bound value"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_int(value)
        if not options:
            options = []
        if value is not None and (value not in options):
            return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="strin")
class StrIn(Rule):
    MSG_ERROR = "out of bound value"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if not options:
            options = []

        if value is not None and (value in options):
            return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="strnotin")
class StrNotIn(Rule):
    MSG_ERROR = "out of bound value"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if not options:
            options = []

        if value is not None and (value not in options):
            return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="bool")
class Bool(Rule):
    MSG_ERROR = "invalid boolean"
    BOOL_VALUES = ["0", "1", "y", "t", "true", "n", "f", "false"]

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is not None and value.lower() in Bool.BOOL_VALUES:
            return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="iso8601")
class ISO8601(Rule):
    MSG_ERROR = "invalid date"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is None:
            return False, self.error_message(error_msg, translator)
        try:
            iso8601.parse_date(value)
        except iso8601.ParseError:
            return False, self.error_message(error_msg, translator)
        return True, ""


@registry.register_cls(name="list")
class RuleList(Rule):
    MSG_ERROR = "value is not a list"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        if type(value) not in (tuple, list):
            return False, self.error_message(error_msg, translator)
        return True, ""


@registry.register_cls(name="idlist")
class RuleIdList(Rule):
    MSG_ERROR = "value is not a list of ids"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        if type(value) not in (tuple, list):
            return False, self.error_message(error_msg, translator)

        for item in value:
            item = cast_str(item)
            if item is None or not item.isnumeric():
                return False, self.error_message(error_msg, translator)
            if int(item) <= 0:
                return False, self.error_message(error_msg, translator)
        return True, ""


@registry.register_cls(name="dict")
class RuleDict(Rule):
    MSG_ERROR = "value is not dictionary"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        if not isinstance(value, Mapping):
            return False, self.error_message(error_msg, translator)
        return True, ""


@registry.register_cls(name="listlen")
class ListLen(Rule):
    MSG_ERROR = "item count must be between {0} and {1}"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value_len = 0
        if type(value) in (list, tuple):
            value_len = len(value)

        if len(options) >= 2:
            min = int(options[0])
            max = int(options[1])
            if (value_len > max) or (value_len < min):
                return False, self.error_message(error_msg, translator, *options)
        if len(options) == 1:
            min = int(options[0])
            if value_len < min:
                _args = [min, str("∞")]
                return False, self.error_message(error_msg, translator, *_args)
        return True, ""
