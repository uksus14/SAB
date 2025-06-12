from flask import Response, render_template, redirect
from scripts.utils import approx_time, is_url
from typing import Callable, Tuple, Generator
from scripts.decorators import AccessLimiter
from datetime import datetime, timedelta
from scripts.actions import Action
from variables import HistoryVar

class Search(Action[str|None]):
    history = HistoryVar.create("history", [])
    order = None
    _list = []
    DEFAULT_CACHE_TIME = timedelta(days=1)
    def __init__(self, pattern: str, action: Callable[[str, *Tuple[str, ...]], str|None], *, cache: bool|timedelta=False, limit: bool|Callable[[Callable], AccessLimiter]=False):
        super().__init__(action, pattern=pattern, cache=cache, limit=limit)
    @classmethod
    def resolve(cls, call: str) -> Response:
        res = super().resolve(call)
        cls.history.append({"query": call, "time": datetime.now()})
        if not isinstance(res, str) or res.startswith("<!DOCTYPE html>"): return res
        return redirect(res) if is_url(res) else render_template("message.html", message=res)
    @classmethod
    def match_history(cls, query: str=None) -> Generator[dict[str, str|datetime]]:
        if query is None: return reversed(Search.history.data)
        return (entry for entry in reversed(Search.history.data) if query in entry["query"])
    def __repr__(self) -> str:
        return f"Search(r\"{self.pattern}\", {self.funcname}, cache={self.cache and approx_time(self.cache)})"