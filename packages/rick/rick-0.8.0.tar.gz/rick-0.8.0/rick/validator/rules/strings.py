# Note:
# Regex logic is adapted from django's validators:https://github.com/django/django/blob/master/django/core/validators.py
#

import re
import typing

from rick.mixin import Translator
from rick.util.cast import cast_str

from .rule import Rule, registry


@registry.register_cls(name="alpha")
class Alpha(Rule):
    MSG_ERROR = "only alphabetic characters allowed"
    RE_ALPHA = re.compile(r"^[a-zA-Z]+$")

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is not None:
            if re.match(self.RE_ALPHA, value):
                return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="alphanum")
class AlphaNum(Rule):
    MSG_ERROR = "only alphanumeric characters allowed"
    RE_ALPHANUM = re.compile(r"^[a-zA-Z0-9]+$")

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is not None:
            if re.match(self.RE_ALPHANUM, value):
                return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="slug")
class Slug(Rule):
    MSG_ERROR = "only alphabetic characters or dash (-,_) allowed"
    RE_SLUG = re.compile(r"^[-a-zA-Z0-9_]+$")

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is not None:
            if re.match(self.RE_SLUG, value):
                return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="len")
class Len(Rule):
    MSG_ERROR = "length must be between [{0}, {1}]"
    DEFAULT_LEN_MIN = 0
    DEFAULT_LEN_MAX = 255

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        options = self.parse_options(options)

        if isinstance(value, int):
            value = cast_str(value)
        if hasattr(value, "__len__") and (
            int(options[1]) >= len(value) >= int(options[0])
        ):
            return True, ""
        return False, self.error_message(error_msg, translator, *options)

    def parse_options(self, options):
        if not options:
            return [self.DEFAULT_LEN_MIN, self.DEFAULT_LEN_MAX]
        if isinstance(options, typing.List):
            if len(options) == 2:
                return options
        raise ValueError("Len.validate(): invalid options parameter length")


@registry.register_cls(name="minlen")
class MinLen(Rule):
    MSG_ERROR = "minimum allowed length is {0}"
    DEFAULT_LEN = 0

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        options = self.parse_options(options)

        if isinstance(value, int):
            value = cast_str(value)

        if hasattr(value, "__len__") and (len(value) >= options[0]):
            return True, ""

        return False, self.error_message(error_msg, translator, *options)

    def parse_options(self, options):
        if isinstance(options, typing.List):
            if len(options) > 0:
                return [int(options[0])]
        return [self.DEFAULT_LEN]


@registry.register_cls(name="maxlen")
class MaxLen(MinLen):
    MSG_ERROR = "maximum allowed length is {0}"
    DEFAULT_LEN = 255

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        options = self.parse_options(options)

        if isinstance(value, int):
            value = cast_str(value)

        if hasattr(value, "__len__") and (len(value) <= options[0]):
            return True, ""
        return False, self.error_message(error_msg, translator, *options)
