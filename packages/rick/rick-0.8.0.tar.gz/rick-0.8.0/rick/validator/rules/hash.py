import re

from rick.mixin import Translator
from rick.util.cast import cast_str

from .rule import Rule, registry


@registry.register_cls(name="md5")
class MD5(Rule):
    MSG_ERROR = "invalid md5 hash"
    REGEX = re.compile(r"^[0-9a-f]{32}$", re.IGNORECASE)

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is not None and self.REGEX.match(value):
            return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="sha1")
class SHA1(Rule):
    MSG_ERROR = "invalid sha1 hash"
    REGEX = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is not None and self.REGEX.match(value):
            return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="sha256")
class SHA256(Rule):
    MSG_ERROR = "invalid sha256 hash"
    REGEX = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is not None and self.REGEX.match(value):
            return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="sha512")
class SHA512(Rule):
    MSG_ERROR = "invalid sha512 hash"
    REGEX = re.compile(r"^[0-9a-f]{128}$", re.IGNORECASE)

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is not None and self.REGEX.match(value):
            return True, ""
        return False, self.error_message(error_msg, translator)
