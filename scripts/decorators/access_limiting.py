from scripts.utils import approx_time, approx_time_re
from scripts.commons import MessageList
from datetime import datetime, timedelta
from typing import Callable
import json

def disabled(limiter: 'AccessLimiter') -> Callable[..., str]:
    def wrapper(*args, **kwargs) -> str:
        return limiter.messages.disabled.template.format(funcname=limiter.funcname, reason=AccessLimiter.disable.get(limiter.funcname, ""))
    return wrapper
class AccessLimiter:
    path = "./variables/access_{}.json"
    
    messages = MessageList(empty_query="Please provide a query",
                           reset="Access reset",
                           access=fr"(?P<num>\d+) requests made in last (?P<period>{approx_time_re})",
                           too_fast=fr"Please wait (?P<wait>{approx_time_re}) before making another request",
                           reached_limit=fr"You have reached the limit of (?P<max_count>\d+) requests per (?P<period>{approx_time_re})\. first request was (?P<first_req>{approx_time_re}) ago\. Wait or type 'reset\?'")
    full_access = []
    def __init__(self, max_count: int, period: timedelta, min_time: timedelta = timedelta(seconds=2)):
        self.max_count = max_count
        self.period = period
        self.min_time = min_time
        self._accesses = []
    @property
    def accesses(self) -> list[datetime]:
        now = datetime.now()
        if self._accesses and now - self._accesses[0] < self.period:
            self._accesses = list(filter(lambda access: now - access < self.period, self._accesses))
        if not self._accesses: return [now - self.period]
        return self._accesses
    def setfunc(self, funcname: str):
        self.funcname = funcname
        with open(self.path.format(self.funcname), "a") as f: pass
        with open(self.path.format(self.funcname), "r") as f: data = f.read()
        if data: self._accesses = [datetime.fromtimestamp(access) for access in json.loads(data)]
        self.update()
    def update(self):
        with open(self.path.format(self.funcname), "w") as f: f.write(json.dumps([access.timestamp() for access in self.accesses]))
    def __call__(self, func: Callable[[str], list[str]], funcname: str) -> Callable[[str], list[str]]:
        self.setfunc(funcname)
        def wrapper(call: str, query: str=None, *args, **kwargs) -> list[str]|str:
            if self.funcname in AccessLimiter.full_access: return func(call, query=query, *args, **kwargs)
            if query is None: query = call
            query = query.strip()
            now = datetime.now()
            err = None
            if not query: err = self.messages.empty_query.template
            elif query.lower() == "reset":
                self._accesses.clear()
                err = self.messages.reset.template
            elif query.lower() == "access":
                err = self.messages.access.template.format(num=len(self.accesses), period=approx_time(self.period))
            elif now - self.accesses[-1] < self.min_time:
                err = self.messages.too_fast.template.format(wait=approx_time(self.min_time))
            elif len(self.accesses) >= self.max_count:
                err = self.messages.reached_limit.template.format(max_count=self.max_count, period=approx_time(self.period), first_req=approx_time(self.accesses[0]))
            self.update()
            if err: return err
            self._accesses.append(datetime.now())
            return func(call, query=query, *args, **kwargs)
        if self.funcname in AccessLimiter.full_access: return func
        return wrapper