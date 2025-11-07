import decimal
import iso8601
from rick.base import Registry
from typing import Any
from rick.util.cast import cast_str, cast_int, cast_float


class Filter:
    def transform(self, src: Any) -> Any:
        return src


# Filter registry
registry = Registry(Filter)


@registry.register_cls(name="int")
class Int(Filter):
    def transform(self, src: Any) -> Any:
        return cast_int(src)


@registry.register_cls(name="decimal")
class Decimal(Filter):
    def transform(self, src: Any) -> Any:
        try:
            return decimal.Decimal(src)
        except decimal.DecimalException:
            return None


@registry.register_cls(name="float")
class Float(Filter):
    def transform(self, src: Any) -> Any:
        return cast_float(src)


@registry.register_cls(name="datetime")
class Datetime(Filter):
    def transform(self, src: Any) -> Any:
        try:
            return iso8601.parse_date(src)
        except Exception:
            return None


@registry.register_cls(name="bool")
class Bool(Filter):
    IS_TRUE = ["1", "y", "t", "true"]

    def transform(self, src: Any) -> Any:
        src = cast_str(src)
        if not src:
            return False
        return src.lower() in self.IS_TRUE
