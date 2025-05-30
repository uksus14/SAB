from scripts.utils import approx_time, first_not_none
from scripts.decorators import Pager, AccessLimiter
from scripts.actions import ActionList, Action
from typing import Callable, Tuple
from datetime import timedelta
from pathlib import Path
import bisect
import regex


order_path = Path(__file__).parent / "order.txt"

with open(order_path, "r") as f:
    order = f.read().split()
class SuggestionList(ActionList):
    _instance = None
    actions: list['Suggest'] = []
    def exec(self, call: str) -> list[str]|None:
        return super().exec(call)
    def add(self, action: Action):
        if action.funcname not in order: order.insert(0, action.funcname)
        bisect.insort(self.actions, action, key=lambda ac:order.index(ac.funcname))
        with open(order_path, "w") as f:
            f.write("\n".join(order))

class Suggest(Action):
    _list = SuggestionList()
    DEFAULT_CACHE_TIME = timedelta(days=1)
    def __init__(self, pattern: str, action: Callable[[str, *Tuple[str, ...]], list[str]], *, cache: bool|timedelta=False, page: bool=False, limit: bool|AccessLimiter=False):
        self.pattern = f"^{pattern}$"
        super().__init__(action, cache=cache, limit=limit)
        self.page = page
        if self.page:
            self.pattern = f"^{pattern}-*$"
            self.action = Pager(self.action)
    def match(self, call: str) -> None|dict[str, str]:
        match = regex.match(self.pattern, call.strip())
        if match: return match.groupdict()
        return None
    def __call__(self, call, **kwargs):
        groups = self.match(call)
        if groups is None: return None
        res = super().__call__(call, **groups, **kwargs)
        if res is not None and not isinstance(res, list): res = [str(res)]
        return res
    def exec(self, call: str, **kwargs) -> None|list[str]:
        res = super().exec(call, **kwargs)
        if res is not None and not isinstance(res, list): res = [str(res)]
        return res
    def __repr__(self) -> str:
        return f"Suggest(r\"{self.pattern}\", {self.funcname}, cache={self.cache and approx_time(self.cache)}, page={self.page})"