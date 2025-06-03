from scripts.utils import approx_time, approx_time_re
from scripts.message import MessageList
from datetime import datetime, timedelta
from variables import AccessVar
from functools import wraps
from typing import Callable
from bisect import bisect

class AccessLimiter:
    var_name = "access_{}"
    
    messages = MessageList(empty_query="Please provide a query",
                           reset="Access reset",
                           access=fr"(?P<num>\d+) requests made in last (?P<period>{approx_time_re}), (?P<all>\d+) since the beginning",
                           too_fast=fr"Please wait (?P<wait>{approx_time_re}) before making another request",
                           reached_limit=fr"You have reached the limit of (?P<max_count>\d+) requests per (?P<period>{approx_time_re})\. first request was (?P<first_req>{approx_time_re}) ago\. Wait or type 'reset\?'")
    full_access = []
    def __init__(self, max_count: int=None, period: timedelta=None, min_time: timedelta|None = timedelta(seconds=2)):
        self.max_count = max_count
        self.period = period
        self.min_time = min_time
    def add_access(self, call: str):
        self._slice.append(datetime.now())
        self.access.data += [{"time": self.slice[-1], "call": call}]
    @property
    def slice(self) -> list[datetime]:
        if self.period: self._slice = self._slice[bisect(self._slice, datetime.now() - self.period):]
        return self._slice
    def setfunc(self, funcname: str):
        self.funcname = funcname
        self.access = AccessVar.create(self.var_name.format(funcname), [])
        slice = [entry["time"] for entry in self.access.data]
        self._slice = []
        if self.period: self._slice = slice[bisect(slice, datetime.now()-self.period):]
    def __call__(self, func: Callable[[str], list[str]], funcname: str) -> Callable[[str], list[str]]:
        self.setfunc(funcname)
        @wraps(func)
        def wrapper(call: str, query: str, *args, **kwargs) -> list[str]|str:
            if self.funcname in AccessLimiter.full_access:
                self.add_access(call)
                return func(call, query=query, *args, **kwargs)
            err = None
            if not query: err = self.messages.empty_query.format()
            elif query.lower() == "reset":
                self._slice.clear()
                err = self.messages.reset.format()
            elif query.lower() == "access" and self.period:
                err = self.messages.access.format(num=len(self.slice), period=approx_time(self.period), all=len(self.access.data))
            elif self.slice and self.min_time and datetime.now() - self.slice[-1] < self.min_time:
                err = self.messages.too_fast.format(wait=approx_time(self.min_time))
            elif self.max_count and len(self.slice) >= self.max_count:
                err = self.messages.reached_limit.format(max_count=self.max_count, period=approx_time(self.period), first_req=approx_time(self.slice[0]))
            if err: return err
            self.add_access(call)
            return func(call, query=query, *args, **kwargs)
        if self.funcname in AccessLimiter.full_access: return func
        return wrapper