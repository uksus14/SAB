from datetime import datetime, timedelta
from typing import Iterator, TypeVar
from urllib.parse import quote
from constants import bangs
import user_agent_parser
import flask
import regex

def ischrome() -> bool:
    return user_agent_parser.Parser(flask.request.headers.get('User-Agent'))()[0] == "Chrome"

def page_size() -> int:
    if ischrome():
        return 2
    else: return 4

def eval_normalize(script: str) -> str:
    return script.replace("^", "**").replace("\\**", "^")

def bangs_url(query: str) -> str:
    r = regex.search(r"!(\S+)", query)
    a = "!gwoai"
    if r: a = r.group().lower()
    return bangs.get(a[1:], bangs["gwoai"]).format(q=quote(regex.sub(r'!\S+\s*', '', query).strip()))

EL = TypeVar("EL")
def first_not_none(gen: Iterator[EL|None], default=None) -> EL|None:
    return next((el for el in gen if el is not None), default)

approx_time_re = r"\d+ (second|day|hour|minute)s?"
def approx_time(time: timedelta|datetime) -> str:
    if isinstance(time, datetime): time = datetime.now() - time
    num, word = time.seconds, "second"
    if time.days > 0: num, word = time.days, "day"
    if time.seconds >= 3600: num, word = time.seconds//3600, "hour"
    if time.seconds >= 60: num, word = time.seconds//60, "minute"
    if num != 1: word += 's'
    return f"{num} {word}"