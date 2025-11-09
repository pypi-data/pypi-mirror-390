from abc import ABCMeta, abstractmethod
from typing import *

import setdoc
import unhash
from datarepr import oxford

from v440._utils.Cfg import Cfg
from v440._utils.guarding import guard
from v440.core.VersionError import VersionError

__all__ = ["BaseStringer"]


class BaseStringer(metaclass=ABCMeta):
    __slots__ = ()

    string: str
    packaging: Any

    @abstractmethod
    @setdoc.basic
    def __bool__(self: Self) -> bool: ...

    @setdoc.basic
    def __eq__(self: Self, other: Any) -> bool:
        if type(self) is type(other):
            return self._cmp() == other._cmp()
        else:
            return False

    @setdoc.basic
    def __format__(self: Self, format_spec: Any) -> str:
        parsed: dict
        ans: str
        msg: str
        try:
            parsed = self._format_parse(str(format_spec))
        except Exception:
            msg = Cfg.cfg.data["consts"]["errors"]["format"]
            msg %= (format_spec, type(self).__name__)
            raise VersionError(msg)  # from None
        ans = str(self._format_parsed(**parsed))
        return ans

    @setdoc.basic
    def __ge__(self: Self, other: Any) -> bool:
        if type(self) is type(other):
            return self._cmp() >= other._cmp()
        else:
            return NotImplemented

    @setdoc.basic
    def __gt__(self: Self, other: Any) -> bool:
        if type(self) is type(other):
            return self._cmp() > other._cmp()
        else:
            return NotImplemented

    __hash__ = unhash

    @abstractmethod
    @setdoc.basic
    def __init__(self: Self, string: Any) -> None: ...

    @setdoc.basic
    def __le__(self: Self, other: Any) -> bool:
        if type(self) is type(other):
            return self._cmp() <= other._cmp()
        else:
            return NotImplemented

    @setdoc.basic
    def __lt__(self: Self, other: Any) -> bool:
        if type(self) is type(other):
            return self._cmp() < other._cmp()
        else:
            return NotImplemented

    @setdoc.basic
    def __ne__(self: Self, other: Any) -> bool:
        return not (self == other)

    @abstractmethod
    @setdoc.basic
    def __repr__(self: Self) -> str: ...

    @classmethod
    def __subclasshook__(cls: type, other: type, /) -> bool:
        "This magic classmethod can be overwritten for a custom subclass check."
        return NotImplemented

    @setdoc.basic
    def __str__(self: Self) -> str:
        return format(self, "")

    @abstractmethod
    def _cmp(self: Self) -> Any: ...

    @classmethod
    @abstractmethod
    def _deformat(cls: type, info: dict[str, Self], /) -> Any: ...

    @classmethod
    @abstractmethod
    def _format_parse(self: Self, spec: str, /) -> dict: ...

    @abstractmethod
    def _format_parsed(self: Self, **kwargs: Any) -> Any: ...

    @abstractmethod
    def _string_fset(self: Self, value: str) -> None: ...

    @setdoc.basic
    def copy(self: Self) -> Self:
        return type(self)(self)

    @classmethod
    def deformat(cls: type, *strings: Any) -> str:
        keys: tuple = tuple(map(str, strings))
        values: tuple = tuple(map(cls, keys))
        info: dict = dict(zip(keys, values))
        try:
            ans: str = cls._deformat(info)
        except Exception:
            msg: str = Cfg.cfg.data["consts"]["errors"]["deformat"]
            msg %= oxford(*strings)
            raise TypeError(msg)
        return ans

    @property
    @abstractmethod
    def packaging(self: Self) -> Any: ...

    @property
    def string(self: Self) -> str:
        "This property represents self as str."
        return format(self, "")

    @string.setter
    @guard
    def string(self: Self, value: Any) -> None:
        self._string_fset(str(value).lower())
