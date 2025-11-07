import pytest
from rick.util.loader import load_class
from rick.base import Di


def test_load_class():
    # existing class
    cls = load_class("rick.base.Di")
    assert cls is not None
    assert type(cls) is type(Di)

    # non-existing class
    cls = load_class("rick.base.Dix")
    assert cls is None
