from scripts.utils import page_size
from typing import Callable

def pagify(data: list[str], call: str, page: int) -> list[str]:
    p_size = page_size()
    if len(data) <= (page+1)*p_size+1: return data[page*p_size:]
    return data[page*p_size:(page+1)*p_size] + [f"{call}-{'-'*page}"]

class Pager:
    def __init__(self, func: Callable[[str], list[str]]) -> Callable[[str], list[str]]:
        self.func = func
    def __call__(self, call: str, **kwargs) -> list[str]:
        call = call.strip()
        stripped = call.rstrip("-")
        page = len(call) - len(stripped)
        call = stripped.strip()
        data = self.func(call, **kwargs)
        if not isinstance(data, list): return data
        return pagify(data, call, page)