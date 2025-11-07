# Note:
# Regex logic is adapted from django's validators:https://github.com/django/django/blob/master/django/core/validators.py
#
import re
from ipaddress import IPv4Address, IPv6Address

from rick.mixin import Translator
from rick.util.cast import cast_str

from .rule import Rule, registry


@registry.register_cls(name="ipv4")
class IPv4(Rule):
    MSG_ERROR = "invalid IPv4 address"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        if isinstance(value, bool) or not isinstance(value, (str, int, bytes)):
            return False, self.error_message(error_msg, translator)
        try:
            IPv4Address(value)
        except ValueError:
            return False, self.error_message(error_msg, translator)
        return True, ""


@registry.register_cls(name="ipv6")
class IPv6(Rule):
    MSG_ERROR = "invalid IPv6 address"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        if isinstance(value, bool) or not isinstance(value, (str, int, bytes)):
            return False, self.error_message(error_msg, translator)
        try:
            IPv6Address(value)
        except ValueError:
            return False, self.error_message(error_msg, translator)
        return True, ""


@registry.register_cls(name="ip")
class IP(Rule):
    MSG_ERROR = "invalid IPv4 or IPv6 address"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        if isinstance(value, bool) or not isinstance(value, (str, int, bytes)):
            return False, self.error_message(error_msg, translator)
        try:
            IPv6Address(value)
            return True, ""
        except ValueError:
            pass
        try:
            IPv4Address(value)
        except ValueError:
            return False, self.error_message(error_msg, translator)
        return True, ""


@registry.register_cls(name="fqdn")
class Fqdn(Rule):
    MSG_ERROR = "invalid domain name"
    WHITELIST = [
        "localhost",
    ]
    REGEX = re.compile(
        # max length for domain name labels is 63 characters per RFC 1034
        r"((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)" r"(?:[A-Z0-9-]{2,63}(?<!-))\Z",
        re.IGNORECASE,
    )

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is None:
            return False, self.error_message(error_msg, translator)
        value = value.lower()
        if value in Fqdn.WHITELIST or self.REGEX.match(value):
            return True, ""
        try:
            idn_value = value.encode("idna").decode("ascii")
            if self.REGEX.match(idn_value):
                return True, ""
        except UnicodeError:
            pass
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="email")
class Email(Rule):
    MSG_ERROR = "invalid email address"
    REGEX = re.compile(
        # dot-atom
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"
        # quoted-string
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013'
        r'\014\016-\177])*"\Z)',
        re.IGNORECASE,
    )

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is None:
            return False, self.error_message(error_msg, translator)
        toks = value.rsplit("@", 1)
        if len(toks) != 2:
            return False, self.error_message(error_msg, translator)
        user, domain = toks

        # username
        if not self.REGEX.match(user):
            return False, self.error_message(error_msg, translator)

        # domain
        valid, _ = Fqdn().validate(domain)
        if valid:
            return True, ""

        # is it a valid ip addr?
        valid, _ = IP().validate(domain)
        if valid:
            return True, ""
        return False, self.error_message(error_msg, translator)


@registry.register_cls(name="mac")
class Mac(Rule):
    MSG_ERROR = "invalid mac address"
    REGEX = re.compile(r"^(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$")

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        value = cast_str(value)
        if value is not None and self.REGEX.match(value):
            return True, ""
        return False, self.error_message(error_msg, translator)
