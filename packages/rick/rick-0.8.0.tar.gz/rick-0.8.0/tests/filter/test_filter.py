import decimal
import iso8601
import pytest
from rick.filter import registry as filter_registry


def test_filter_registry():
    assert "int" in filter_registry.names()


def test_filter_registry_int():
    assert "int" in filter_registry.names()

    filter = filter_registry.get("int")
    assert filter.transform("100") == int(100)
    # invalid values should return None
    assert filter.transform("abc") is None


def test_filter_registry_decimal():
    assert "decimal" in filter_registry.names()

    filter = filter_registry.get("decimal")
    assert filter.transform("3.14159265") == decimal.Decimal("3.14159265")
    assert filter.transform("-2.00000000009") == decimal.Decimal("-2.00000000009")
    assert filter.transform("") is None
    assert filter.transform("a2b") is None


def test_filter_registry_float():
    assert "float" in filter_registry.names()

    filter = filter_registry.get("float")
    v = 3.14159265
    assert filter.transform("3.14159265") == v
    v = -2.00000000009
    assert filter.transform("-2.00000000009") == v
    assert filter.transform("") is None
    assert filter.transform("a2b") is None


def test_filter_registry_datetime():
    assert "datetime" in filter_registry.names()

    filter = filter_registry.get("datetime")
    assert filter.transform("2022-05-31T15:11Z") == iso8601.parse_date(
        "2022-05-31T15:11Z"
    )
    assert filter.transform("20-20-2020") is None
    assert filter.transform("3500-14-15") is None


def test_filter_registry_bool():
    assert "bool" in filter_registry.names()

    filter = filter_registry.get("bool")
    assert filter.transform("true") is True
    assert filter.transform("true_") is False
    assert filter.transform("1") is True
    assert filter.transform("y") is True
    assert filter.transform("N") is False
    assert filter.transform("abcdef") is False
