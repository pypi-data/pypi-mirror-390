from __future__ import annotations

import string as string_
from typing import *

import setdoc

from v440._utils.SlotStringer import SlotStringer
from v440.core.Base import Base
from v440.core.Qual import Qual

__all__ = ["Public"]


class Public(SlotStringer):

    __slots__ = ("_base", "_qual")

    string: str
    packaging: str
    base: Base
    qual: Qual

    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._base = Base()
        self._qual = Qual()
        self.string = string

    def _cmp(self: Self) -> tuple:
        return self.base, self.qual

    @classmethod
    def _deformat(cls: type, info: dict[str, Self]) -> str:
        bases: set
        quals: set
        x: str
        y: str
        bases = set()
        quals = set()
        for x, y in map(cls._split, info.keys()):
            bases.add(x)
            quals.add(y)
        x = Base.deformat(*bases)
        y = Qual.deformat(*quals)
        return x + y

    @classmethod
    def _format_parse(cls: type, spec: str, /) -> dict:
        i: int
        ans: dict
        i = int(spec.lower().startswith("v"))
        while i < len(spec):
            if spec[i] in ("#!."):
                i += 1
            else:
                break
        if i != 0 and spec[i - 1] == "." and i != len(spec) and spec[i] not in "-_":
            i -= 1
        ans = dict(base_f=spec[:i], qual_f=spec[i:])
        return ans

    def _format_parsed(self: Self, *, base_f: str, qual_f: str) -> str:
        return format(self.base, base_f) + format(self.qual, qual_f)

    @classmethod
    def _split(cls: type, value: str) -> tuple[str, str]:
        i: int
        i = int(value.lower().startswith("v"))
        while i < len(value):
            if value[i] in (string_.digits + "!."):
                i += 1
            else:
                break
        if i and (value[i - 1] == "."):
            i -= 1
        return value[:i], value[i:]

    def _string_fset(self: Self, value: str) -> None:
        self.base.string, self.qual.string = self._split(value)

    def _todict(self: Self) -> dict:
        return dict(base=self.base, qual=self.qual)

    @property
    def base(self: Self) -> Base:
        "This property represents the version base."
        return self._base

    @property
    def qual(self: Self) -> Qual:
        "This property represents the qualification."
        return self._qual
