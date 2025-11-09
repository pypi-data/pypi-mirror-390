import os
from functools import cached_property
from typing import *

from petrus._core import utils
from petrus._core.calcs.BaseCalc import BaseCalc


class File(BaseCalc):

    @cached_property
    def core(self: Self) -> Any:
        n: Any
        n = self.prog.project.name
        return os.path.join("src", n, "core", "__init__.py")

    @cached_property
    def gitignore(self: Self) -> str:
        return ".gitignore"

    @cached_property
    def license(self: Self) -> Any:
        ans: Any
        ans = self.prog.pp.get("project", "license", "file")
        if type(ans) is str:
            return ans
        return self._find("LICENSE.txt")

    @cached_property
    def main(self: Self) -> Any:
        n: Any
        n = self.prog.project.name
        return os.path.join("src", n, "__main__.py")

    @cached_property
    def init(self: Self) -> Any:
        n: Any
        n = self.prog.project.name
        return os.path.join("src", n, "__init__.py")

    @cached_property
    def manifest(self: Self) -> str:
        return "MANIFEST.in"

    @cached_property
    def pp(self: Self) -> str:
        return "pyproject.toml"

    @cached_property
    def readme(self: Self) -> Any:
        ans: Any
        ans = self.prog.pp.get("project", "readme")
        if type(ans) is str and os.path.exists(ans):
            return ans
        return self._find("README.rst")

    @cached_property
    def setup(self: Self) -> str:
        return "setup.cfg"

    def exists(self: Self, name: Any) -> bool:
        f: Any
        f = getattr(self, name)
        return os.path.exists(f)

    @staticmethod
    def _find(file: Any) -> Any:
        t: Any
        l: list[str]
        if utils.isfile(file):
            return file
        t = os.path.splitext(file)[0]
        l = os.listdir()
        l = list(l)
        l.sort(reverse=True)
        for x in l:
            if t == os.path.splitext(x)[0]:
                return x
        return file
