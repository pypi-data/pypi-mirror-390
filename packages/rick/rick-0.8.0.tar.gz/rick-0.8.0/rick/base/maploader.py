import functools
import importlib

from threading import Lock

from .di import Di
from ..util.object import full_name


class MapLoader:
    def __init__(self, di: Di, map_: dict = None):
        self._di = di
        self._map = {}
        self._loaded = {}
        self._stack = []
        self._lock = Lock()
        if map_:
            self.append(map_)

    def add(self, name, path):
        """
        Add a single map entry
        :param name: object name
        :param path: object path
        :return: none
        """
        with self._lock:
            self._map[name] = path

    def remove(self, name):
        """
        Remove a cached entry by name
        :param name:
        :return:
        """
        with self._lock:
            if name in self._map.keys():
                del self._map[name]
            if name in self._loaded.keys():
                del self._loaded[name]

    def clear_loaded(self):
        """
        Remove all cached entries
        :return:
        """
        with self._lock:
            self._loaded = {}

    def append(self, map: dict):
        """
        Add multiple map entries from a dict
        :param map: dict with name:path
        :return: none
        """
        with self._lock:
            for k, v in map.items():
                self._map[k] = v

    def contains(self, name):
        """
        Check if a given name exists
        :param name: name to check
        :return: bool
        """
        return name in self._map.keys()

    @functools.lru_cache(maxsize=None)
    def get(self, name: str):
        """
        Retrieve an object from the map
        :param name: name to retrieve
        :return: object
        """
        if name in self._stack:
            raise RuntimeError("get(): circular dependency on object %s" % name)

        with self._lock:
            if name in self._loaded.keys():
                return self._loaded[name]

        if name not in self._map.keys():
            raise ValueError("get(): name '%s' does not exist in map" % name)

        with self._lock:
            self._stack.append(name)
            path = self._map[name]

        module_path, cls_name = path.rsplit(".", 1)
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, cls_name, None)
            if cls is None:
                raise RuntimeError(
                    "get(): cannot find class '%s' in module '%s'"
                    % (cls_name, module_path)
                )

        except ModuleNotFoundError:
            with self._lock:
                self._stack.remove(name)
            raise RuntimeError(
                "get(): mapped module '%s' not found when discovering path %s"
                % (module_path, path)
            )

        obj = self.build(cls)
        with self._lock:
            self._loaded[name] = obj
            self._stack.remove(name)
        return obj

    def build(self, cls) -> object:
        """
        Builds the object
        :param cls: class
        :return: object
        """
        return cls(self._di)

    def register(self, name: str, obj: object):
        """
        Adds an object directly to the internal map
        :param name:
        :param obj:
        :return:
        """
        with self._lock:
            if name in self._map.keys():
                raise ValueError(
                    "register(): name '%s' already exists in the map" % name
                )
            # resolve object name
            self._map[name] = full_name(obj)
            self._loaded[name] = obj
