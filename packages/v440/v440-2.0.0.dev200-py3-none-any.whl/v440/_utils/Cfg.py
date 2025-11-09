import enum
import functools
import re
import tomllib
from importlib import resources
from typing import *

__all__ = ["Cfg"]


class Cfg(enum.Enum):
    cfg = None

    @functools.cached_property
    def data(self: Self) -> dict:
        "This cached property holds the cfg data."
        text: str = resources.read_text("v440._utils", "cfg.toml")
        ans: dict = tomllib.loads(text)
        return ans

    @classmethod
    def fullmatches(cls: type, key: str, value: str) -> dict[str, str]:
        ans: dict = cls.cfg.patterns[key].fullmatch(value).groupdict()
        x: str
        for x in ans.keys():
            if ans[x] is None:
                ans[x] = ""
        return ans

    @functools.cached_property
    def patterns(self: Self) -> dict[str, re.Pattern]:
        ans: dict = dict()
        parts: dict = dict()
        x: str
        y: str
        z: str
        for x, y in self.data["patterns"].items():
            z = y.format(**parts)
            parts[x] = f"(?P<{x}>{z})"
            ans[x] = re.compile(z, re.IGNORECASE | re.VERBOSE)
        return ans
