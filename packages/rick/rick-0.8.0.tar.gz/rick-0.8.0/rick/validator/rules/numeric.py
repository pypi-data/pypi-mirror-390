import decimal
import typing

from rick.mixin import Translator
from rick.util.cast import cast_str, cast_float, cast_int

from .rule import Rule, registry


@registry.register_cls(name="between")
class Between(Rule):
    MSG_ERROR = "must be between {0} and {1}"
    DEFAULT_MIN = 0
    DEFAULT_MAX = 255

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_float(value)
        if value is not None and float(options[1]) >= value >= float(options[0]):
            return True, ""
        return False, self.error_message(error_msg, translator, *options)

    def parse_options(self, options):
        if not options:
            return [self.DEFAULT_MIN, self.DEFAULT_MAX]
        if isinstance(options, typing.List):
            if len(options) == 2:
                return options
        raise ValueError("Between.validate(): invalid options parameter length")


@registry.register_cls(name="numeric")
class Numeric(Rule):
    MSG_ERROR = "only digits allowed"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is not None:
            if value.isnumeric():
                return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="decimal")
class Decimal(Rule):
    MSG_ERROR = "invalid decimal"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        if error_msg is None:
            error_msg = self.MSG_ERROR
        try:
            decimal.Decimal(value)
            return True, ""
        except TypeError:
            return False, self.error_message(error_msg, translator)
        except decimal.DecimalException:
            return False, self.error_message(error_msg, translator)


@registry.register_cls(name="int")
class IntRule(Rule):
    MSG_ERROR = "only integer values are allowed"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        if type(value) is int:
            return True, ""

        if type(cast_int(value)) is int:
            return True, ""

        return False, self.error_message(error_msg, translator)
