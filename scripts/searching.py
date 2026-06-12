from scripts.utils import approx_time, match_url
from variables import HistoryVar, HistoryEntry
from typing import Callable, Tuple, Iterator
from scripts.decorators import AccessLimiter
from flask.typing import ResponseReturnValue
from flask import render_template, redirect
from datetime import datetime, timedelta
from scripts.actions import Action
from commons import BASE_URL

class Search(Action[ResponseReturnValue|None]):
    history = HistoryVar.create("history")
    order = ...
    _list = []
    DEFAULT_CACHE_TIME = timedelta(days=1)
    def __init__(self, pattern: str, action: Callable[..., ResponseReturnValue|None], *, cache: bool|timedelta=False, limit: bool|Callable[[Callable, str], AccessLimiter]=False):
        super().__init__(action, pattern=pattern, cache=cache, limit=limit)
    @classmethod
    def resolve(cls, call: str) -> ResponseReturnValue|None:
        res = super().resolve(call)
        cls.history.append({"query": call, "time": datetime.now()})
        if isinstance(res, str) and not res.startswith("<!DOCTYPE html>"):
            if match_url(res) or res.startswith(BASE_URL):
                return redirect(res)
            return render_template("message.html", message=res)
        return res
    @classmethod
    def match_history(cls, query: str|None=None) -> Iterator[HistoryEntry]:
        if query is None: return reversed(Search.history.data)
        return (entry for entry in reversed(Search.history.data) if query in entry["query"])
    def __repr__(self) -> str:
        cache = self.cache
        cache = cache if isinstance(cache, bool) else approx_time(cache)
        return f"Search(r\"{self.pattern}\", {self.funcname}, cache={cache})"