import copy
import importlib
from threading import Lock
from inspect import isclass

from rick.base import Di
from rick.event.handler import EventHandler


class EventState:
    """
    Wrapper for EventManager sleep() configuration
    This class should be treated as read-only, as EventManager will reference EventState.data on wakeup(), instead
    of copying the attribute
    """

    def __init__(self, src: dict):
        self.data = copy.deepcopy(src)


class EventManager:
    def __init__(self):
        #
        self._handlers = {}
        self._stack = []
        self._stack_lock = Lock()
        self._handler_lock = Lock()

    def sleep(self) -> EventState:
        """
        Serialize EventManager config
        This can be used with self.wakeup() to save/restore internal state for the manager,
        for fast instantiation
        :return EventState
        """
        with self._handler_lock:
            return EventState(self._handlers)

    def wakeup(self, src: EventState):
        """
        Unserialize EventManager config
        :param src: EventState object
        :return:
        """
        with self._handler_lock:
            with self._stack_lock:
                self._handlers = src.data

    def load_handlers(self, src: dict):
        """
        Load event handlers from a configuration dict
        Config dict format:
            {
            'event_name': {
                10: [event handler, ...],
                11: [event handler, ..]
            }
        :param src: configuration dict
        :return:
        """
        for event_name, priorities in src.items():
            if not isinstance(priorities, dict):
                raise RuntimeError(
                    "load_handlers(): priority list for '%s' must be of dict type"
                    % (event_name,)
                )
            for pri, handlers in priorities.items():
                if not isinstance(handlers, (list, tuple)):
                    raise RuntimeError(
                        "load_handlers(): handler list for '%s':%s must be of list type"
                        % (event_name, pri)
                    )

                for h in handlers:
                    self.add_handler(event_name, h, pri)

    def add_handler(self, event_name: str, handler: str, priority: int = 100):
        """
        Register an event handler
        Internally, event handlers are stored as follows:
        self._handlers = {
            'event_name': {
                handlers: [event handler, event handler, ...]
                10: [event handler, ...],
                11: [event handler, ..]
            }
        }

        :param event_name: event name
        :param handler: fully qualified name for handler class or function
        :param priority: lower number handlers get executed first
        :return:
        """
        if type(handler) is not str:
            raise RuntimeError("add_handler(): empty or invalid event handler")

        if type(priority) is not int:
            raise RuntimeError("add_handler(): invalid priority")

        with self._handler_lock:
            if event_name in self._handlers.keys():
                evt = self._handlers[event_name]
                existing_handlers = evt["handlers"]
                if handler in existing_handlers:
                    raise RuntimeError(
                        "add_handler(): duplicated handler {} for event {}".format(
                            handler, event_name
                        )
                    )
                existing_handlers.append(handler)

                if priority in evt.keys():
                    evt[priority].append(handler)
                else:
                    evt[priority] = [handler]
            else:
                self._handlers[event_name] = {
                    "handlers": [handler],
                    priority: [handler],
                }

    def remove_handler(self, event_name: str, handler: str) -> bool:
        """
        Removes any
        :param event_name:
        :param handler:
        :return:
        """
        with self._handler_lock:
            if event_name not in self._handlers.keys():
                # event not found
                return False

            evt = self._handlers[event_name]
            if handler not in evt["handlers"]:
                # handler not found
                return False

            cleanup = []
            # remove from handler list
            evt["handlers"].remove(handler)
            # remove from runqueues
            for priority, handlers in evt.items():
                if handler in handlers:
                    handlers.remove(handler)
                    if len(handlers) == 0:
                        cleanup.append(priority)

            # remove empty priority list
            for priority in cleanup:
                del self._handlers[event_name][priority]

            return True

    def purge(self):
        """
        Clear all events and handlers
        :param self:
        :return:
        """
        with self._handler_lock:
            with self._stack_lock:
                self._handlers = {}
                self._stack = []

    def get_events(self):
        with self._handler_lock:
            return list(self._handlers.keys())

    def dispatch(self, di: Di, event_name: str, **kwargs):
        """
        Dispatches an Event by name
        Returns True if dispatched, False if not
        :param di: Di instance
        :param event_name: event name to dispatch
        :param kwargs:
        :return: bool
        """
        if event_name not in self._handlers.keys():
            return False

        if event_name in self._stack:
            raise RuntimeError(
                "dispatch(): circular event dependency when performing '{}'".format(
                    event_name
                )
            )
        self._stack.append(event_name)

        with self._handler_lock:
            evt = self._handlers[event_name]
            priorities = list(evt.keys())
            priorities.remove("handlers")
            priorities.sort()
            for p in priorities:
                for handler in evt[p]:
                    module_path, cls_name = handler.rsplit(".", 1)
                    try:
                        # try to locate function or class
                        module = importlib.import_module(module_path)
                        cls = getattr(module, cls_name, None)
                        if cls is None:
                            self._stack_remove(event_name)
                            raise RuntimeError(
                                "dispatch(): cannot find class or function '%s' in module '%s'"
                                % (cls_name, module_path)
                            )

                    except ModuleNotFoundError:
                        self._stack_remove(event_name)
                        raise RuntimeError(
                            "dispatch(): mapped module '%s' not found when discovering path '%s'"
                            % (module_path, handler)
                        )

                    if isclass(cls) and issubclass(cls, EventHandler):
                        # build object from class
                        obj = cls(di)

                        # check if event method handler exists
                        obj_handler = getattr(obj, event_name, None)
                        if obj_handler is None:
                            raise RuntimeError(
                                "dispatch(): event handler for '%s' not found in '%s'"
                                % (event_name, handler)
                            )
                        obj_handler(**kwargs)

                    elif callable(cls) and not isclass(cls):
                        # cls is a function
                        kwargs["event_name"] = event_name
                        cls(**kwargs)

                    else:
                        raise RuntimeError(
                            "dispatch(): handler '%s' for event '%s' invalid or incompatible"
                            % (handler, event_name)
                        )

        self._stack_remove(event_name)
        return True

    def _stack_remove(self, event_name):
        """
        Removes event name from the running stack
        :param event_name:
        :return:
        """
        with self._stack_lock:
            # Note: list.remove() is not thread safe
            self._stack.remove(event_name)
