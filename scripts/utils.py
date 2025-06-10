from constants import top_level_domains
from datetime import datetime, timedelta
from commons import BASE_URL
from typing import Iterator
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

def first_not_none[EL](gen: Iterator[EL|None], default=None) -> EL|None:
    return next((el for el in gen if el is not None), default)

approx_time_re = r"\d+ (second|day|hour|minute)s?"
def approx_time(time: timedelta|datetime) -> str:
    if isinstance(time, (float, int)):
        if time > 20*365.25*24*60*60: time = datetime.fromtimestamp(time)
        else: time = timedelta(seconds=time)
    if isinstance(time, datetime): time = datetime.now() - time
    num, word = time.seconds, "second"
    if time.days > 0: num, word = time.days, "day"
    elif time.seconds >= 3600: num, word = time.seconds//3600, "hour"
    elif time.seconds >= 60: num, word = time.seconds//60, "minute"
    if num != 1: word += 's'
    return f"{num} {word}"

def resolve_date(day: int=None, month: int=None, year: int=None) -> datetime|None:
    if day is None: return None
    now = datetime.now()
    if year is None:
        year = now.year
        if month > now.month or (month == now.month and day > now.day): year -= 1
    elif year < 100:
        year += 1900
        if year <= (now.year % 100): year += 100
    return datetime(year, month, day)

russian = "ХЪЖЭБЮ,ё\"№;%:?йцукенгшщзхъфывапролджэячсмитьбю"
english = "{}:\"<>?`@#$%^&qwertyuiop[]asdfghjkl;'zxcvbnm,."
ru_en = {r: e for r, e in zip(russian, english)}
en_ru = {e: r for e, r in zip(english, russian)}
def translit(text: str, d: dict[str, str]) -> str:
    return "".join(d.get(l, l) for l in text.lower())
def same_keys_find(text: str, codes: list[str]) -> str|None:
    text = text.lower().strip()
    for d in [{}, ru_en, en_ru]:
        text = translit(text, d)
        if text in codes: return text
    return False

def prep_query(query: str) -> str:
    query = query.strip()
    if query.endswith("Ё"): return translit(query[:-1], ru_en).strip()
    if query.endswith("~"): return translit(query[:-1], en_ru).strip()
    return query

def normalize_url(url: str) -> str:
    if not is_url(url): return url
    return regex.match(f"^{url_pattern}$", url, regex.IGNORECASE).group("url")

def all_ways(*codes: str) -> list[str]:
    ways = lambda code:[code, translit(code, en_ru), translit(code, ru_en)]
    return [transcode for code in codes for transcode in ways(code.lower())]

def pattern_or(*codes: str, safe: bool=True) -> str:
    return f"({'|'.join(set(map(regex.escape, codes) if safe else codes))})"

def prefix_pattern(word: str) -> str:
    return "(".join(word[:-1])+word[-1]+"?"+")?"*(len(word)-2)

def is_url(query: str) -> bool:
    return regex.search(f"^{BASE_URL}|{url_pattern}$", query, flags=regex.IGNORECASE) is not None

url_pattern = fr"(https?://)?(ww(w|2)\.)?(?P<url>[A-Za-z0-9_.\-~]+?\.{pattern_or(*top_level_domains)}(/.*)?(\?.*)?(#.*)?)"