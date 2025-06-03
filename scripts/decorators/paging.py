from scripts.utils import page_size
from typing import Callable
from functools import wraps

def pagify(data: list[str], call: str, page: int) -> list[str]:
    p_size = page_size()
    if len(data) <= (page+1)*p_size+1: return data[page*p_size:]
    return data[page*p_size:(page+1)*p_size] + [f"{call}-{'-'*page}"]

class Pager:
    def __new__(cls, func: Callable[[str], list]) -> Callable[[str], list]:
        @wraps(func)
        def inner(call: str, **kwargs) -> list[str]:
            call = call.strip()
            stripped = call.rstrip("-")
            page = len(call) - len(stripped)
            call = stripped.strip()
            data = func(call, **kwargs)
            if not isinstance(data, list): return data
            return pagify(data, call, page)
        return inner