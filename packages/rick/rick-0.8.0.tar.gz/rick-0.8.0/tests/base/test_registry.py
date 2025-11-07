import pytest
from rick.base import Registry


class SomeClass:
    pass


class OtherClass:
    pass


class TestRegistry:
    def test_init(self):
        registry = Registry(SomeClass)
        registry.register_obj("name", SomeClass())
        assert registry.has("name") is True
        with pytest.raises(TypeError):
            registry.register_obj("foo", OtherClass())

    def test_register_obj(self):
        registry = Registry(SomeClass)
        obj1 = SomeClass()
        obj2 = SomeClass()
        obj1_name = str(type(obj1))
        assert registry.has(obj1_name) is False

        # register 1 object
        registry.register_obj(obj1_name, obj1)
        assert registry.has(obj1_name) is True
        assert registry.get(obj1_name) == obj1
        assert registry.get(obj1_name) != obj2

        # replace object
        registry.register_obj(obj1_name, obj2, True)
        assert registry.get(obj1_name) == obj2
        assert registry.get(obj1_name) != obj1

    def test_names_remove(self):
        registry = Registry(SomeClass)
        obj1 = SomeClass()
        obj2 = SomeClass()
        obj1_name = str(type(obj1)) + "1"
        obj2_name = str(type(obj2)) + "2"

        names = registry.names()
        assert len(names) == 0

        registry.register_obj(obj1_name, obj1)
        registry.register_obj(obj2_name, obj2)

        names = registry.names()
        assert len(names) == 2
        for n in names:
            assert n in [obj1_name, obj2_name]

        registry.remove(obj1_name)
        names = registry.names()
        assert len(names) == 1
        assert names.pop() == obj2_name
