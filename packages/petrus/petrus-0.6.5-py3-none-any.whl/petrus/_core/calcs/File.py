import os
from typing import *

from petrus._core import utils
from petrus._core.calcs.Calc import Calc


class File(Calc):
    def _calc_core(self: Self):
        n = self.prog.project.name
        return os.path.join("src", n, "core", "__init__.py")

    def _calc_gitignore(self: Self) -> str:
        return ".gitignore"

    def _calc_license(self: Self):
        ans = self.prog.pp.get("project", "license", "file")
        if type(ans) is str:
            return ans
        return self._find("LICENSE.txt")

    def _calc_main(self: Self):
        n = self.prog.project.name
        return os.path.join("src", n, "__main__.py")

    def _calc_init(self: Self):
        n = self.prog.project.name
        return os.path.join("src", n, "__init__.py")

    def _calc_manifest(self: Self):
        return "MANIFEST.in"

    def _calc_pp(self: Self):
        return "pyproject.toml"

    def _calc_readme(self: Self):
        ans = self.prog.pp.get("project", "readme")
        if type(ans) is str and os.path.exists(ans):
            return ans
        return self._find("README.rst")

    def _calc_setup(self: Self) -> str:
        return "setup.cfg"

    def exists(self: Self, name: Any) -> bool:
        f = getattr(self, name)
        return os.path.exists(f)

    @staticmethod
    def _find(file: Any):
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
