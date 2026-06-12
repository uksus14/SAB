from __future__ import annotations
from scripts.utils import approx_time, first_not_none
from scripts.decorators import Cacher, AccessLimiter
from flask.typing import ResponseReturnValue
from scripts.decorators import coerce_types
from scripts.message import MessageList
from typing import Callable, Self
from commons import BASE_FOLDER
from types import EllipsisType
from datetime import timedelta
import bisect
import regex


class Action[AR]:
    DEFAULT_CACHE_TIME = timedelta(days=1)
    order: list[str]|None|EllipsisType = None
    _list: list[Self] = []
    __full_list: list[Self] = []
    messages = MessageList(disabled=r"(?P<funcname>[a-zA-Z]+) is disabled. (?P<reason>.+)")
    disable: dict[str, str] = {}
    def __init__(self, action: Callable[..., AR], *, pattern: str|None=None, cache: bool|timedelta=False, limit: bool|Callable[[Callable, str], AccessLimiter]=False):
        self.pattern = pattern
        self.funcname = action.__name__
        if self.order is None: self._list.append(self)
        else: self.add(self)
        self.__full_list.append(self)
        self.inner = action
        self.action = coerce_types(self.inner)
        if limit:
            if limit is True: limit = AccessLimiter[AR].prep(50, timedelta(days=1), timedelta(seconds=3))
            self.action = limit(self.action, self.funcname)
        self.limit = limit
        if cache:
            if cache is True: cache = self.DEFAULT_CACHE_TIME
            self.action = Cacher(self.action, cache)
        self.cache = cache
    @classmethod
    def _order_file(cls, mode: str):
        return open(BASE_FOLDER / "orders" / f"{cls.__name__.lower()}_order.txt", mode, encoding="utf-8")
    @classmethod
    def add(cls, action: Self):
        if cls.order is None or cls.order == ...:
            with cls._order_file("a") as f: pass
            with cls._order_file("r") as f: content: str = f.read()
            cls.order = content.split("\n")
        if action.funcname not in cls.order:
            cls.order.insert(0, action.funcname)
            with cls._order_file("w") as f: f.write("\n".join(cls.order))
        bisect.insort(cls._list, action, key=lambda ac:cls.order.index(ac.funcname)) # type: ignore
    @classmethod
    def resolve(cls, call) -> AR|str|None:
        for action in cls._list:
            res = action(call)
            print(res)
            if res is not None: return res
        return first_not_none(action(call) for action in cls._list)
    @classmethod
    def get(cls, funcname: str) -> Self|None:
        return next((action for action in cls._list if action.funcname == funcname), None)
    @classmethod
    def iter(cls): return iter(cls._list)
    def match(self, call: str) -> None|dict[str, str]:
        if self.pattern is None: return {}
        match = regex.match(f"^{self.pattern}$", call.strip(), regex.IGNORECASE)
        return None if match is None else match.groupdict()
    def __call__(self, call: str, *args, **kwargs) -> AR|str|None:
        groups = self.match(call)
        if groups is None: return None
        if self.funcname not in self.disable: return self.action(call.strip(), *args, **groups, **kwargs)
        return self.messages.disabled.format(funcname=self.funcname, reason=self.disable[self.funcname])
    def __repr__(self) -> str:
        cache = self.cache
        cache = cache if isinstance(cache, bool) else approx_time(cache)
        return f"Action({self.funcname}, cache={cache})"