from abc import abstractmethod
from typing import *

import setdoc
from datahold import OkayList
from datarepr import datarepr

from v440._utils.BaseStringer import BaseStringer
from v440._utils.guarding import guard

__all__ = ["ListStringer"]


class ListStringer(BaseStringer, OkayList):

    __slots__ = ()
    string: str
    packaging: Any
    data: tuple

    @setdoc.basic
    def __add__(self: Self, other: Any) -> Self:
        alt: tuple
        ans: Self
        try:
            alt = tuple(other)
        except Exception:
            return NotImplemented
        ans = type(self)()
        ans.data = self.data + alt
        return ans

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return bool(self.data)

    @setdoc.basic
    def __mul__(self: Self, other: Any) -> Self:
        ans: Self
        ans = type(self)()
        ans.data = self.data * other
        return ans

    @setdoc.basic
    def __radd__(self: Self, other: Any) -> Self:
        alt: tuple
        ans: Self
        try:
            alt = tuple(other)
        except Exception:
            return NotImplemented
        ans = type(self)()
        ans.data = alt + self.data
        return ans

    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(type(self).__name__, list(self))

    def _cmp(self: Self) -> tuple:
        return tuple(map(self._sort, self.data))

    @classmethod
    @abstractmethod
    def _data_parse(cls: type, value: list) -> Iterable: ...

    @classmethod
    @abstractmethod
    def _sort(cls: type, value: Any): ...

    @property
    @setdoc.basic
    def data(self: Self) -> tuple:
        return self._data

    @data.setter
    @guard
    def data(self: Self, value: Iterable) -> None:
        self._data = tuple(self._data_parse(list(value)))

    def sort(self: Self, *, key: Any = None, reverse: Any = False) -> None:
        "This method sorts the data."
        data: list
        k: Any
        r: bool
        data = list(self.data)
        k = self._sort if key is None else key
        r = bool(reverse)
        data.sort(key=k, reverse=r)
        self.data = data
