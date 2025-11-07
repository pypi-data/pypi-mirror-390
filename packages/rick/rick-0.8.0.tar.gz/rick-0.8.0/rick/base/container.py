import collections
import copy


class ContainerBase:
    def __init__(self, data):
        self._data = data

    def has(self, key):
        return key in self._data.keys()

    def asdict(self):
        return self._data

    def get(self, key, default=None):
        if key in self._data:
            return self.__getitem__(key)
        return default

    def copy(self):
        raise RuntimeError("ContainerBase.copy(): abstract method")

    def keys(self):
        return self._data.keys()

    def values(self):
        """
        Retrieve raw value list
        :return: list of values
        """
        result = []
        for k in self._data.keys():
            result.append(self.__getitem__(k))
        return result

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        raise RuntimeError("ContainerBase.__getitem__(): abstract method")

    def __contains__(self, item):
        return item in self._data.keys()


class Container(ContainerBase):
    """
    Immutable(read-only) container that copies initial data

    Operations on the initial data dict passed on __init__ dont affect container contents
    """

    def __init__(self, data: dict):
        """
        Constructor
        :param data: dict with data to be made available
        """
        if not isinstance(data, collections.abc.Mapping):
            raise ValueError(
                "expected dict/Mapping, %s found instead" % str(type(data))
            )
        super(Container, self).__init__(copy.deepcopy(data))

    def __getitem__(self, key):
        v = self._data[key]
        if isinstance(v, collections.abc.Mapping):
            return Container(v)
        return v

    def copy(self):
        return Container(self._data)


class MutableContainer(ContainerBase):
    """
    Mutable(updatable) container

    """

    def __init__(self, data: dict = None):
        if data is None:
            super(MutableContainer, self).__init__({})
        else:
            if not isinstance(data, collections.abc.MutableMapping):
                raise ValueError(
                    "expected dict/MutableMapping, %s found instead" % str(type(data))
                )
            super(MutableContainer, self).__init__(copy.deepcopy(data))

    def __getitem__(self, key):
        v = self._data[key]
        if isinstance(v, collections.abc.MutableMapping):
            return MutableContainer(v)
        return v

    def copy(self):
        return MutableContainer(self._data)

    def clear(self):
        self._data.clear()

    def update(self, key, value):
        self._data.__setitem__(key, value)

    def __setitem__(self, key, item):
        self._data.__setitem__(key, item)

    def __delitem__(self, key):
        self._data.__delitem__(key)

    def remove(self, key):
        self._data.__delitem__(key)


class ShallowContainer(ContainerBase):
    """
    Immutable (read-only) container that does not copy initial data

    Note: if the underlying original dict passed on the constructor is changed, container contents *will* change
    """

    def __init__(self, data: dict):
        """
        Constructor
        :param data: dict with data to be made available
        """
        if not isinstance(data, collections.abc.Mapping):
            raise ValueError(
                "expected dict/Mapping, %s found instead" % str(type(data))
            )
        super(ShallowContainer, self).__init__(data)

    def copy(self):
        return ShallowContainer(self._data)

    def __getitem__(self, key):
        v = self._data[key]
        if isinstance(v, collections.abc.Mapping):
            return ShallowContainer(v)
        return v
