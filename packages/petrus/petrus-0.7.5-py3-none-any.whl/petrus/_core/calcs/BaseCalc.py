from typing import *


class BaseCalc:
    _CORE = "prog"

    def __delattr__(self: Self, name):
        self.__check(name)
        object.__delattr__(self, name)

    def __init__(self: Self, core, /) -> None:
        object.__setattr__(self, type(self)._CORE, core)
        getattr(self, "__post_init__", int)()

    def __setattr__(self: Self, name, value):
        self.__check(name)
        object.__setattr__(self, name, value)

    def __check(self: Self, name):
        if name.startswith("_"):
            return
        if not hasattr(super(), name):
            return
        raise AttributeError("readonly")
