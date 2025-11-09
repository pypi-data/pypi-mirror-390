from __future__ import annotations

import operator
import string as string_
from typing import *

import keyalias
import setdoc

from v440._utils.ListStringer import ListStringer
from v440._utils.releaseparse import deleting, getting, setting

__all__ = ["Release"]


@keyalias.getdecorator(major=0, minor=1, micro=2, patch=2)
class Release(ListStringer):
    __slots__ = ()

    string: str
    packaging: tuple
    data: tuple
    major: int
    minor: int
    micro: int
    patch: int

    @setdoc.basic
    def __delitem__(self: Self, key: Any) -> None:
        self._data = deleting.delitem(self.data, key)

    @setdoc.basic
    def __getitem__(self: Self, key: Any) -> int | list:
        return getting.getitem(self.data, key)

    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._data = ()
        self.string = string

    @setdoc.basic
    def __setitem__(self: Self, key: Any, value: Any) -> None:
        self._data = setting.setitem(self.data, key, value)

    @classmethod
    def _data_parse(cls: type, value: list) -> Iterable:
        v: list = list(map(cls._item_parse, value))
        while v and v[-1] == 0:
            v.pop()
        return v

    @classmethod
    def _deformat(cls: type, info: dict[str, Self], /) -> str:
        i: int
        j: int
        k: int
        s: str
        t: str
        table: list[int]
        if len(info) == 0:
            return ""
        i = 0
        j = 0
        for s in info.keys():
            k = s.count(".")
            i = max(i, k + 1)
            t = s.rstrip("0")
            if t.endswith(".") or t == "":
                j = max(j, k)
        if j == 0:
            j = -1
        table = [0] * i
        for s in info.keys():
            if s == "":
                continue
            for i, t in enumerate(s.split(".")):
                k = cls._deformat_force(t)
                table[i] = cls._deformat_comb(table[i], k)
        s = ""
        for i, k in enumerate(table):
            if k > 1:
                s += "#" * k
            elif i == j:
                s += "#"
            s += "."
        s = s.rstrip(".")
        return s

    @classmethod
    def _deformat_force(cls: type, part: str) -> int:
        if part == "0":
            return -1
        if part.startswith("0"):
            return len(part)
        return -len(part)

    @classmethod
    def _deformat_comb(cls: type, x: int, y: int) -> int:
        if 0 > x * y:
            if x + y <= 0:
                return max(x, y)
            raise ValueError
        elif 0 < x * y:
            if x < 0:
                return max(x, y)
            if x == y:
                return x
            raise ValueError
        else:
            return x + y

    @classmethod
    def _format_parse(cls: type, spec: str, /) -> str:
        if spec.strip("#."):
            raise ValueError
        return dict(mags=tuple(map(len, spec.rstrip(".").split("."))))

    def _format_parsed(self: Self, *, mags: tuple) -> str:
        m: int
        data: list[int]
        parts: list[int]
        data = list(self)
        data += [0] * max(0, len(mags) - len(self))
        parts = [f"0{m}d" for m in mags]
        parts += [""] * max(0, len(self) - len(mags))
        return ".".join(map(format, data, parts))

    @classmethod
    def _item_parse(cls: type, value: SupportsIndex) -> int:
        ans: int
        ans = operator.index(value)
        if ans < 0:
            raise ValueError
        return ans

    @classmethod
    def _sort(cls: type, value: int) -> int:
        return value

    def _string_fset(self: Self, value: str) -> None:
        if value.strip(string_.digits + "."):
            raise ValueError
        self.data = map(int, value.split("."))

    def bump(self: Self, index: SupportsIndex = -1, amount: SupportsIndex = 1) -> None:
        i: int = operator.index(index)
        a: int = operator.index(amount)
        x: int = getting.getitem_int(self.data, i) + a
        self._data = setting.setitem_int(self.data, i, x)
        if i != -1:
            self.data = self.data[: i + 1]

    packaging = ListStringer.data
