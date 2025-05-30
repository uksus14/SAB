from scripts.utils import first_not_none
from datetime import datetime, timedelta
from scripts.commons import MessageList
from typing import Callable, TypeVar

R = TypeVar("R")
class Cacher:
    GENERIC_DEFAULT_TIME = timedelta(days=1)
    exempt_messages = [MessageList.all()]
    def __init__(self, time: timedelta=None):
        self.time = time if time else self.GENERIC_DEFAULT_TIME
        self.cache = {}
    @classmethod
    def isexempt(cls, response) -> bool:
        if not isinstance(response, str): False
        return bool(first_not_none(messagelist.match(response) for messagelist in cls.exempt_messages))
    def __call__(self, func: Callable[[str], R]) -> Callable[[str], R]:
        def wrapper(call: str, *args, **kwargs) -> R:
            call = call.strip()
            now = datetime.now()
            
            if call in self.cache and self.time > (now - self.cache[call]["time"]):
                return self.cache[call]["response"]
            
            response = func(call, *args, **kwargs)
            if not self.isexempt(response):
                self.cache[call] = {"response": response, "time": now}
            
            for call in list(self.cache.keys()):
                if self.time < (now - self.cache[call]["time"]): self.cache.pop(call)
            return response
        return wrapper