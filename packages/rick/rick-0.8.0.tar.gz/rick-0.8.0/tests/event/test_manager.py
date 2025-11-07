import pytest

from rick.base import Di
from rick.event import EventHandler, EventManager


class Handler_0:
    def event_one(self, **kwargs):
        if "out" in kwargs.keys():
            kwargs["out"].append(1)

    def event_two(self, **kwargs):
        if "out" in kwargs.keys():
            kwargs["out"].append(-1)


class Handler_1(Handler_0, EventHandler):
    pass


class Handler_2(EventHandler):
    def event_one(self, **kwargs):
        if "out" in kwargs.keys():
            kwargs["out"].append(2)

    def event_two(self, **kwargs):
        if "out" in kwargs.keys():
            kwargs["out"].append(-2)


def handler_3(**kwargs):
    assert "event_name" in kwargs.keys()
    if "out" in kwargs.keys():
        kwargs["out"].append(3)


mgr_cfg = {
    "event_one": {
        1: [
            "tests.event.test_manager.handler_3",
        ],
        2: [
            "tests.event.test_manager.Handler_2",
        ],
        3: [
            "tests.event.test_manager.Handler_1",
        ],
    },
    "event_two": {
        1: ["tests.event.test_manager.handler_3"],
        2: ["tests.event.test_manager.Handler_2"],
        3: ["tests.event.test_manager.Handler_1"],
    },
}

invalid_mgr_cfg = {
    "event_one": {
        1: [
            "tests.event.test_manager.handler_3",
        ],
        2: [
            "tests.event.test_manager.Handler_0",
        ],
        3: [
            "tests.event.test_manager.Handler_1",
        ],
    },
}


def test_manager():
    di = Di()
    mgr = EventManager()
    mgr.load_handlers(mgr_cfg)

    # test dispatching event 1
    out_list = []
    # dispatch an event, each event changes the out list
    mgr.dispatch(di, "event_one", out=out_list)
    assert out_list == [3, 2, 1]

    # test dispatching event 2
    out_list = []
    # dispatch an event, each event changes the out list
    assert mgr.dispatch(di, "event_two", out=out_list) is True
    assert out_list == [3, -2, -1]


def test_manager_invalid():
    di = Di()
    mgr = EventManager()
    mgr.load_handlers(invalid_mgr_cfg)

    with pytest.raises(RuntimeError):
        # test dispatching event 1
        out_list = []
        # dispatch event 1, should fail because Handler_0 is not descendant of
        # EventHandler
        mgr.dispatch(di, "event_one", out=out_list)
        assert out_list == [3, 2, 1]


def test_manager_noevent():
    di = Di()
    mgr = EventManager()
    mgr.load_handlers(invalid_mgr_cfg)

    # event doesn't exist, it should return False
    out_list = []
    assert mgr.dispatch(di, "event_two", out=out_list) is False


def test_manager_sleep():
    di = Di()
    mgr = EventManager()
    mgr.load_handlers(mgr_cfg)

    # save mgr state, create new object & reload config
    state = mgr.sleep()
    mgr = EventManager()
    mgr.wakeup(state)

    # test dispatching event 1
    out_list = []
    # dispatch an event, each event changes the out list
    mgr.dispatch(di, "event_one", out=out_list)
    assert out_list == [3, 2, 1]

    # test dispatching event 2
    out_list = []
    # dispatch an event, each event changes the out list
    mgr.dispatch(di, "event_two", out=out_list)
    assert out_list == [3, -2, -1]
