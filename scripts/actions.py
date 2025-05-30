from __future__ import annotations
from scripts.utils import approx_time, first_not_none
from scripts.decorators import Cacher, AccessLimiter
from typing import Callable, Tuple, TypeVar, Any
from scripts.commons import MessageList
from datetime import timedelta

AR = TypeVar("AR")

class ActionList:
    _instance = None
    actions: list[Action] = []
    def __new__(cls):
        if cls._instance is None: cls._instance = super().__new__(cls)
        return cls._instance
    def add(self, action: Action): self.actions.append(action)
    def __call__(self, *args, **kwargs) -> None|AR|str:
        return first_not_none(action(*args, **kwargs) for action in self.actions)
    def exec(self, *args, **kwargs) -> None|AR:
        return first_not_none(action.exec(*args, **kwargs) for action in self.actions)
    def __repr__(self) -> str:
        return f"{type(self).__name__}(\n" + ",\n".join(map(str, self.actions))+")"
    def __getattribute__(self, name) -> Any|Action:
        actions: list[Action] = super().__getattribute__('actions')
        action = next((action for action in actions if action.funcname == name), None)
        return super().__getattribute__(name) if action is None else action

class Action:
    DEFAULT_CACHE_TIME = timedelta(days=1)
    DEFAULT_ACCESS_LIMIT = AccessLimiter(50, timedelta(days=1), timedelta(seconds=3))
    _list = ActionList()
    messages = MessageList(disabled=r"(?P<funcname>[a-zA-Z]+) is disabled. (?P<reason>.+)")
    disable: dict[str, str] = {}
    def __init__(self, action: Callable[[str, *Tuple[str, ...]], AR], *, cache: bool|timedelta=False, limit: bool|AccessLimiter=False):
        self.funcname = action.__name__
        self._list.add(self)
        self.inner = action
        self.action = self.inner
        if limit:
            if limit is True: limit = self.DEFAULT_ACCESS_LIMIT
            self.action = limit(self.action, self.funcname)
        self.limit = limit
        if cache:
            if cache is True: cache = self.DEFAULT_CACHE_TIME
            self.action = Cacher(cache)(self.action)
        self.cache = cache
    
    def __call__(self, call: str, *args, **kwargs) -> None|AR|str:
        print(call, self.funcname, self.disable)
        if self.funcname in self.disable:
            return self.messages.disabled.format(funcname=self.funcname, reason=self.disable[self.funcname])
        return self.exec(call, *args, **kwargs)
    def exec(self, call: str, *args, **kwargs) -> None|AR:
        return self.action(call.strip(), *args, **kwargs)

    def __repr__(self) -> str:
        return f"Action({self.funcname}, cache={approx_time(self.cache)})"