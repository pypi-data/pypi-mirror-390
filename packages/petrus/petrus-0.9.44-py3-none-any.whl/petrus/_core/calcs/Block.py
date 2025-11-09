from functools import cached_property
from typing import *

from petrus._core.calcs.BaseCalc import BaseCalc
from petrus._core.consts.Const import Const


class Block(BaseCalc):
    @cached_property
    def text(self: Self) -> str:
        ans: str
        blocks: list
        blocks = []
        for k in Const.const.data["CONST"]["BLOCKKEYS"]:
            b = getattr(self, k)
            if b is None:
                continue
            b = b.strip("\n")
            blocks.append(b)
        ans = "\n\n".join(blocks)
        while "\n\n\n" in ans:
            ans = ans.replace("\n\n\n", "\n\n")
        return ans

    @cached_property
    def heading(self: Self) -> str:
        n: Any
        l: str
        ans: str
        n = self.prog.project.name
        l = "=" * len(n)
        ans = "%s\n%s\n%s" % (l, n, l)
        return ans

    @cached_property
    def overview(self: Self) -> str:
        d: str
        lines: str
        d = str(self.prog.project.description)
        if not d:
            return None
        lines = self.ftitle("Overview")
        lines += str(d)
        return lines

    @cached_property
    def installation(self: Self) -> Any:
        name: Any
        ans: Any
        name = self.prog.project.name
        ans = self.prog.draft.installation.format(name=name)
        return ans

    @cached_property
    def license(self: Self) -> str:
        classifiers: Any
        lines: str
        classifiers = self.prog.project.classifiers
        if type(classifiers) is not list:
            return None
        if Const.const.data["CONST"]["MIT"] not in classifiers:
            return None
        lines = self.ftitle("License")
        lines += "This project is licensed under the MIT License."
        return lines

    @cached_property
    def links(self: Self) -> str:
        urls: Any
        lines: str
        urls = self.prog.project.urls
        if type(urls) is not dict:
            return None
        if len(urls) == 0:
            return None
        lines = self.ftitle("Links")
        for i in urls.items():
            lines += "* `%s <%s>`_\n" % i
        return lines

    @cached_property
    def credits(self: Self) -> str:
        n: Any
        e: Any
        lines: str
        pn: Any
        n, e = self.prog.author
        lines = self.ftitle("Credits")
        if n:
            lines += "* Author: %s\n" % n
        if e:
            lines += "* Email: `%s <mailto:%s>`_\n" % (e, e)
        while not lines.endswith("\n\n"):
            lines += "\n"
        pn = self.prog.project.name
        lines += "Thank you for using ``%s``!" % pn
        return lines

    @staticmethod
    def ftitle(value: Any, /, lining: Any = "-") -> str:
        v: str
        l: str
        ans: str
        v = str(value)
        l = str(lining)
        l *= len(v)
        ans = "%s\n%s\n\n" % (v, l)
        return ans
