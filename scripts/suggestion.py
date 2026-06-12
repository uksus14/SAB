from scripts.decorators import Pager, AccessLimiter
from scripts.utils import approx_time, page_size
from typing import Callable, Tuple
from scripts.actions import Action
from datetime import timedelta
import requests

class Suggest(Action[list[str]|str|None]):
    order = ...
    _list = []
    DEFAULT_CACHE_TIME = timedelta(days=1)
    def __init__(self, pattern: str, action: Callable[..., list[str]|str|None], *, cache: bool|timedelta=False, page: bool=False, limit: bool|Callable[[Callable, str], AccessLimiter]=False):
        super().__init__(action, pattern=pattern, cache=cache, limit=limit)
        self.page = page
        if self.page:
            self.pattern = f"^{pattern}-*$"
            self.action = Pager(self.action)
    @classmethod
    def resolve(cls, call) -> list[str]:
        try: res = super().resolve(call)
        except requests.ConnectionError:
            res = "No internet connection"
        if not isinstance(res, list): res = [str(res)]
        return res[:page_size()+1]
    def __call__(self, call, *args, **kwargs):
        return super().__call__(call, *args, **kwargs)
    def __repr__(self) -> str:
        cache = self.cache
        cache = cache if isinstance(cache, bool) else approx_time(cache)
        return f"Suggest(r\"{self.pattern}\", {self.funcname}, cache={cache}, page={self.page})"