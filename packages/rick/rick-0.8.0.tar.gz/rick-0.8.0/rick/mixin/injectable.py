from rick.base import Di


class Injectable:
    def __init__(self, di: Di):
        self._di = di

    def set_di(self, di: Di):
        self._di = di

    def get_di(self) -> Di:
        return self._di
