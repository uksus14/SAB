from datetime import datetime, timedelta
import json
from typing import Callable
from utils import approx_time

class AccessLimit:
    path = "./variables/access_{}.json"
    disable = []
    full_access = []
    def __init__(self, max_count: int, period: timedelta, min_time: timedelta = timedelta(seconds=2)):
        self.max_count = max_count
        self.period = period
        self.min_time = min_time
        self._accesses = []
    @property
    def accesses(self) -> list[datetime]:
        now = datetime.now()
        self._accesses = [access for access in self._accesses if now - access < self.period]
        if not self._accesses: return [now - self.period]
        return self._accesses
    def access(self): self._accesses.append(datetime.now())
    def setfunc(self, funcname: str):
        self.funcname = funcname
        with open(self.path.format(self.funcname), "a") as f: pass
        with open(self.path.format(self.funcname), "r") as f: data = f.read()
        if data: self._accesses = [datetime.fromtimestamp(access) for access in json.loads(data)]
        self.update()
    def update(self):
        with open(self.path.format(self.funcname), "w") as f: f.write(json.dumps([access.timestamp() for access in self.accesses]))
    def __call__(self, func: Callable[[str], list[str]]) -> Callable[[str], list[str]]:
        self.setfunc(func.__name__)
        def wrapper(query: str) -> list[str]:
            now = datetime.now()
            err = None
            if not query.strip(): err = "Please provide a query"
            elif query.lower() == "reset":
                self._accesses.clear()
                err = "Access reset"
            elif query.lower() == "access":
                err = f"{len(self.accesses)} requests made in last {approx_time(self.period)}"
            elif now - self.accesses[-1] < self.min_time:
                err = f"Please wait {approx_time(self.min_time)} before making another request"
            elif len(self.accesses) >= self.max_count:
                err = f"You have reached the limit of {self.max_count} requests per {approx_time(self.period)}. first request was {approx_time(self.accesses[0])}. Wait or type 'reset?'"
            self.update()
            if err: return [err]
            self.access()
            return func(query)
        if self.funcname in AccessLimit.full_access: return func
        if self.funcname in AccessLimit.disable: return lambda query: [f"{self.funcname} is disabled. {AccessLimit.disable[self.funcname]}"]
        return wrapper