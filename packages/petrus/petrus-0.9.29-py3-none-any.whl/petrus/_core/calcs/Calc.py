from typing import *

from .BaseCalc import BaseCalc


class Calc(BaseCalc):

    def __getattr__(self: Self, name: Any) -> Any:
        ans: Any
        name_: str
        name_ = str(name)
        if hasattr(type(self), name_):
            return object.__getattribute__(self, name_)
        if name_.startswith("_"):
            raise AttributeError(name_)
        if not hasattr(self, "_lock"):
            self._lock = set()
        if name_ in self._lock:
            raise Exception
        self._lock.add(name_)
        try:
            ans = self._calc(name_)
            object.__setattr__(self, name_, ans)
        finally:
            self._lock.remove(name_)
        return ans

    def _calc(self: Self, name: Any) -> Any:
        return getattr(self, f"_calc_{name}")()
