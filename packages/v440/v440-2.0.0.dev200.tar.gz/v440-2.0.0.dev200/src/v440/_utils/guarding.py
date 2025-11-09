from __future__ import annotations

import functools
from typing import *

from v440.core.VersionError import VersionError

__all__ = ["guard"]


def guard(old: Any) -> Any:
    @functools.wraps(old)
    def new(self: Self, value: Any) -> None:
        backup: str
        msg: str
        target: str
        backup = str(self)
        try:
            old(self, value)
        except VersionError:
            self.string = backup
            raise
        except Exception:
            self._string_fset(backup.lower())
            msg = "%r is an invalid value for %r"
            target = type(self).__name__ + "." + old.__name__
            msg %= (value, target)
            raise VersionError(msg)

    return new
