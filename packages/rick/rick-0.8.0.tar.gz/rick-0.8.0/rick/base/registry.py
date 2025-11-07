from threading import Lock


class BaseRegistry:
    def __init__(self, cls):
        self._prototype = cls
        self._registry = {}
        self._lock = Lock()

    def get(self, name: str):
        """
        Get an object from registry
        :param name: entry name
        :return: object
        """
        with self._lock:
            if name in self._registry.keys():
                return self._registry[name]
            raise ValueError("Registry.get(): name '%s' not found in registry" % name)

    def has(self, name: str):
        """
        Check if a name is registered
        :param name: name to check
        :return: bool
        """
        with self._lock:
            return name in self._registry.keys()

    def names(self):
        """
        Get list of available names
        :return: list
        """
        with self._lock:
            return list(self._registry.keys())

    def remove(self, name: str):
        """
        Remove a specific entry
        :param name: entry to remove
        :return:
        """
        with self._lock:
            if name in self._registry.keys():
                del self._registry[name]

    def __getitem__(self, key):
        with self._lock:
            return self._registry[key]

    def __setitem__(self, key, value):
        raise RuntimeError(
            "Repository.__setitem__(): implicit write operation forbidden"
        )

    def __delitem__(self, key):
        with self._lock:
            del self._registry[key]

    def __contains__(self, key):
        with self._lock:
            return key in self._registry.keys()

    def __len__(self):
        with self._lock:
            return len(self._registry)

    def __repr__(self):
        return repr(self._registry)


class Registry(BaseRegistry):
    def register_cls(self, name: str = None, override: bool = False):
        """
        Class registration decorator
        The object is created and added to the registry dict
        :param name: entry name
        :param override: True to override existing entries
        :return: class
        """
        if not name:
            raise ValueError("Registry.register(): missing name parameter")

        def _register(cls):
            self.register_obj(name, cls(), override)
            return cls

        return _register

    def register_obj(self, name: str, obj, override: bool = False):
        if not isinstance(obj, self._prototype):
            raise TypeError(
                "Registry.register_obj(): object or class does not extend the required interface"
            )

        with self._lock:
            if name in self._registry.keys() and not override:
                raise ValueError("Registry.register_obj(): name already exists")
            self._registry[name] = obj


class ClassRegistry(BaseRegistry):
    def register(self, name: str = None, override: bool = False):
        """
        Class registration decorator
        The object is created and added to the registry dict
        :param name: entry name
        :param override: True to override existing entries
        :return: class
        """
        if not name:
            raise ValueError("Registry.register(): missing name parameter")

        def _register(cls):
            self.register_cls(name, cls, override)
            return cls

        return _register

    def register_cls(self, name: str, cls, override: bool = False):
        if not issubclass(cls, self._prototype):
            raise TypeError(
                "Registry.register_cls(): object or class does not extend the required interface"
            )

        with self._lock:
            if name in self._registry.keys() and not override:
                raise ValueError("Registry.register_cls(): name already exists")
            self._registry[name] = cls
