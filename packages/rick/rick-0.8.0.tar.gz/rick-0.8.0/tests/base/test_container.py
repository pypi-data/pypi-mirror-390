import pytest

from rick.base.container import (
    ContainerBase,
    Container,
    ShallowContainer,
    MutableContainer,
)

containerbase_data = [
    {
        "key1": "value1",
        "key2": "value2",
        "key3": {
            "subkey1": "subvalue1",
        },
    }
]


@pytest.mark.parametrize("data", containerbase_data)
def test_containerbase(data):
    container = ContainerBase(data)

    # has()
    for key in data.keys():
        assert container.has(key)
        assert container.has(key + "_") is False

    # asdict()
    assert container.asdict() == data

    # get()
    # existing keys - they should all raise RuntimeError
    for k in ["key1", "key2"]:
        with pytest.raises(RuntimeError):
            assert container.get(k) == data[k]

    # non-existing keys
    assert container.get("key_x") is None
    assert container.get("key_x", "no_value") == "no_value"

    # keys()
    key_list = container.keys()
    assert len(key_list) == len(data)
    for k in data.keys():
        assert k in key_list

    # values()
    # should raise RuntimeError
    with pytest.raises(RuntimeError):
        _ = container.values()

    # len()
    assert len(container) == len(data)

    # __getitem__()
    with pytest.raises(RuntimeError):
        _ = container["key1"]

    # contains()
    for k in data.keys():
        assert container.__contains__(k) is True
    assert container.__contains__("keyX") is False

    # test shallow operation
    data["newkey"] = "newvalue"
    assert container.has("newkey") is True


container_data = [
    {
        "key1": "value1",
        "key2": "value2",
        "key3": {
            "subkey1": "subvalue1",
        },
    }
]


@pytest.mark.parametrize("data", container_data)
def test_container(data):
    container = Container(data)

    # get()
    for k in ["key1", "key2"]:
        assert container.get(k) == data[k]
    val_key3 = container.get("key3")
    assert isinstance(val_key3, Container)
    assert val_key3.asdict() == data["key3"]

    # non-existing keys
    assert container.get("key_x") is None
    assert container.get("key_x", "no_value") == "no_value"

    # copy()
    other_c = container.copy()
    assert other_c.asdict() == data
    assert container.asdict() == other_c.asdict()

    # values()
    values = container.values()
    assert len(values) == len(data)
    last_value = values.pop()
    assert isinstance(last_value, Container)

    # __getitem__()
    v = container["key1"]
    assert v == data["key1"]
    assert isinstance(container.__getitem__("key3"), Container)

    # contains()
    for k in data.keys():
        assert container.__contains__(k) is True
    assert container.__contains__("keyX") is False

    # test non-shallow immutability
    data.clear()
    assert container.get("key1") is not None


shallowcontainer_data = [
    {
        "key1": "value1",
        "key2": "value2",
        "key3": {
            "subkey1": "subvalue1",
        },
    }
]


@pytest.mark.parametrize("data", shallowcontainer_data)
def test_shallow_container(data):
    container = ShallowContainer(data)

    # copy()
    other_c = container.copy()
    assert other_c.asdict() == data
    assert container.asdict() == other_c.asdict()

    # test class cast
    val_key3 = container.get("key3")
    assert isinstance(val_key3, ShallowContainer)
    assert val_key3.asdict() == data["key3"]
    assert isinstance(container.__getitem__("key3"), ShallowContainer)

    # test shallow operation
    data["newkey"] = "newvalue"
    assert container.get("newkey") == "newvalue"


mutablecontainer_data = [
    {
        "key1": "value1",
        "key2": "value2",
        "key3": {
            "subkey1": "subvalue1",
        },
    }
]


@pytest.mark.parametrize("data", mutablecontainer_data)
def test_mutable_container(data):
    container = MutableContainer(data)

    # copy()
    other_c = container.copy()
    assert other_c.asdict() == data
    assert container.asdict() == other_c.asdict()

    # A MutableContainer is *not* shallow
    data["newkey"] = "newvalue"
    assert container.get("newkey") is None

    # test class cast
    val_key3 = container.get("key3")
    assert isinstance(val_key3, MutableContainer)
    assert val_key3.asdict() == data["key3"]
    assert isinstance(container.__getitem__("key3"), MutableContainer)

    # clear()
    clone = container.copy()
    container.clear()
    assert container.get("key1") is None
    assert len(container.keys()) == 0
    container = clone

    # update()
    # add
    container.update("newkey", "newvalue")
    assert container.get("newkey") == "newvalue"
    # replace
    container.update("newkey", "replacevalue")
    assert container.get("newkey") == "replacevalue"

    # __setitem__()
    # add
    container["key9"] = "value9"
    assert container.has("key9") is True
    assert container.get("key9") == "value9"
    # replace
    container["key9"] = "other_value9"
    assert container.has("key9") is True
    assert container.get("key9") == "other_value9"

    # __delitem__()

    # remove()
    container.remove("key9")
    assert container.has("key9") is False
