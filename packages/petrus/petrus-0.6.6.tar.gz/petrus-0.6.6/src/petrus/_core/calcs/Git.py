import os
import subprocess
from typing import *

from petrus._core.calcs.Calc import Calc


class Git(Calc):
    def __call__(self: Self, *args: Any, force: Any = False) -> Any:
        a: Any
        args_: list[str]
        for a in args:
            if type(a) is not str:
                raise TypeError(a)
        if not (force or self.is_repo()):
            return
        args_ = ["git"] + list(args)
        return subprocess.run(args_)

    def _calc_author(self: Self) -> Any:
        a: Any
        e: Any
        a = self.prog.kwargs["author"]
        e = self.prog.kwargs["email"]
        if {a, e} == {None}:
            return None
        if a is None:
            return e
        if e is None:
            return a
        return f"{a} <{e}>"

    def init(self: Self) -> None:
        if self.is_repo():
            return
        self("init", os.getcwd(), force=True)
        self.commit("Initial Commit")

    def commit_version(self: Self) -> None:
        m: Any
        m = "Version %s" % self.prog.project.version
        self.commit(m)

    def commit(self: Self, message: Any) -> None:
        if message is None:
            message = "a"
        else:
            message = str(message)
        try:
            self("add", "-A").check_returncode()
        except:
            return
        args = ["commit", "--allow-empty", "-m", message]
        if self.author is not None:
            args += ["--author", self.author]
        self(*args)

    def push(self: Self) -> None:
        pass  # self("push").returncode and self("push", "-u")

    def is_repo(self: Self) -> Any:
        called = self("rev-parse", force=True)
        if called is None:
            return False
        return not called.returncode

    def move(self: Self, a: Any, b: Any, /) -> None:
        try:
            self("mv", a, b).check_returncode()
        except:
            pass
        else:
            return
        os.rename(a, b)
