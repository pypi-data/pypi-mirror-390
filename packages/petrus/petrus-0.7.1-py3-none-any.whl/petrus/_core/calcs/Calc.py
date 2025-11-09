from typing import *

from .BaseCalc import BaseCalc


class Calc(BaseCalc):
    _CORE = "prog"

    def __getattr__(self: Self, name: Any) -> Any:
        name_: str
        name_ = str(name)
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

    def _calc(self: Self, name):
        return getattr(self, f"_calc_{name}")()
