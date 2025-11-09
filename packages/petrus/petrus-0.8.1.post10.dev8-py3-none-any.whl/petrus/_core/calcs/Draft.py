import importlib.resources
from typing import *

from petrus._core.calcs.Calc import Calc


class Draft(Calc):
    def _calc(self: Self, name: Any) -> str:
        return importlib.resources.read_text("petrus.drafts", "%s.txt" % name)
