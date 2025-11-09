from __future__ import annotations

import operator
import string as string_
from functools import reduce
from typing import *

from v440._utils.Cfg import Cfg
from v440._utils.Clue import Clue
from v440._utils.guarding import guard
from v440._utils.QualStringer import QualStringer

__all__ = ["Dev"]


class Dev(QualStringer):

    __slots__ = ()
    string: str
    packaging: str
    lit: str
    num: int

    def _cmp(self: Self) -> tuple:
        if self.lit:
            return 0, self.num
        else:
            return (1,)

    @classmethod
    def _deformat(cls: type, info: dict[str, Self], /) -> str:
        clues: Iterable[Clue]
        clues = map(Clue.by_example, info.keys())
        return reduce(operator.and_, clues, Clue()).solo(".dev")

    @classmethod
    def _format_parse(cls: type, spec: str, /) -> dict:
        m: dict
        e: Clue
        m = Cfg.fullmatches("dev_f", spec)
        e = Clue(
            head=m["dev_head_f"],
            sep=m["dev_sep_f"],
            mag=len(m["dev_num_f"]),
        )
        return dict(clue=e)

    def _format_parsed(self: Self, *, clue: Clue) -> str:
        if not self:
            return ""
        if "" == clue.head:
            return ".dev" + str(self.num)
        if 0 == clue.mag and 0 == self.num:
            return clue.head
        return clue.head + clue.sep + format(self.num, f"0{clue.mag}d")

    @classmethod
    def _lit_parse(cls: type, value: str) -> str:
        if value == "dev":
            return "dev"
        else:
            raise ValueError

    @property
    def packaging(self: Self) -> Optional[int]:
        if self:
            return self.num
        else:
            return

    @packaging.setter
    @guard
    def packaging(self: Self, value: Optional[SupportsIndex]) -> None:
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.lit = "dev"
            self.num = operator.index(value)
