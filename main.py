from flask import Flask, request, jsonify, redirect, render_template, Response
from user_agent_parser import Parser as UAParser
from currency_converter import CurrencyConverter, RateNotFoundError
from access_limit import AccessLimit
from typing import Callable, TypeVar, Any
from datetime import timedelta, datetime
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations, 
    implicit_multiplication)
from spellchecker import SpellChecker
from googletrans import Translator
from random import randint, random
from urllib.parse import quote
from codes import URLCode, CurrencyCode, is_same_keys, translit, en_ru, ru_en
convert = CurrencyConverter()
from bs4 import BeautifulSoup
from itertools import product
spell_checker = SpellChecker()
translator = Translator()
from pathlib import Path
import regex as re
import requests
import asyncio
import openai
import json
import math
import sys

BASE_FOLDER = Path(__file__).parent
try:
    openai.api_key = (BASE_FOLDER / "openai_key.txt").read_text().strip()
except FileNotFoundError:
    print("OpenAI key file not found")
    AccessLimit.disable["llmask"] = "OpenAI key not found"

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def bad_weather_hours(data: list[int]) -> tuple[int, int]:
    rain_start, rain_end = -1, -1
    tmp = -1
    for i, code in enumerate(data[1:]):
        if code > 50:
            if rain_start == -1:
                rain_start = i
            elif tmp == -1 and rain_end != -1:
                tmp = i
        elif rain_start != -1:
            if rain_end == -1:
                rain_end = i
            if tmp != -1:
                if i-tmp-abs(15-(i+tmp)/2)/12 > rain_end-rain_start-abs(15-(rain_end+rain_start)/2)/12:
                    rain_start = tmp
                    rain_end = i
                tmp = -1
    if rain_start != -1:
        if rain_end == -1:
            rain_end = 0
        if tmp != -1:
            if 24-tmp-abs(3-tmp/2)/12 > rain_end-rain_start-abs(15-(rain_end+rain_start)/2)/12:
                rain_start = tmp
                rain_end = 24
    return rain_start, rain_end

def cool_random(l=None, r=None) -> int|float:
    if l is None: return random()
    if r is None: return randint(1, l)
    return randint(l, r)

def get_current_kgs() -> float:
    url = "https://wise.com/ru/currency-converter/usd-to-kgs-rate?amount=1"
    soup = BeautifulSoup(requests.get(url).text, features="html.parser")
    return float(soup.find(id="target-input")["value"].replace(",", ".", count=1))

with open("./constants/freqs.json", "r") as f:
    freqs = json.loads(f.read())
with open("./constants/bangs.json", "r", encoding="utf-8") as f:
    bangs: dict[str, str] = json.loads(f.read())
def bangs_url(query: str) -> str:
    r = re.search(r"!(\S+)", query)
    a = "!gwoai"
    if r: a = r.group().lower()
    return bangs.get(a[1:], bangs["g"]).format(q=quote(re.sub(r'!\S+\s*', '', query).strip()))
T = TypeVar("T")
def create_variable(file: str, default: T) -> tuple[T, Callable[[], None]]:
    path = f"./variables/{file}.json"
    with open(path, "a") as f: pass
    with open(path, "r", encoding="utf-8") as f: data: dict[str, dict[str, float]] = f.read()
    if not data:
        with open(path, "w", encoding="utf-8") as f: f.write(json.dumps(default))
        data = default
    else: data = json.loads(data)
    def update(d=data):
        with open(path, "w", encoding="utf-8") as f: f.write(json.dumps(d))
    return data, update
groups, update_groups = create_variable("tab_groups", {})
groups: dict[str, dict[str, float]]

history, update_history = create_variable("history", [])
history: list[dict[str, str|float]]

usd_to_kgs, update_usd_to_kgs = create_variable("usd_to_kgs", [])
usd_to_kgs: list[list[float]]
now = datetime.now()
if now.day != datetime.fromtimestamp(usd_to_kgs[-1][0]).day:
    usd_to_kgs.append([now.timestamp(), get_current_kgs()])

places, update_places = create_variable("places", {})
places: dict[str, tuple[float, float]]

class DimentionsNumber(float):
    def __new__(cls, num: float|str, dim: str=None):
        if not dim:
            num, _, dim = num.partition(" ")
        ins = super().__new__(cls, num)
        ins.__init__(num, dim)
        return ins
    def __init__(self, num: float, dim: str):
        self.num = num
        self.dim = dim.replace("**", "^")
        
    def __str__(self):
        return f"{self.num} {self.dim}"

variables_str, _ = create_variable("variables", [])
variables_str: list[tuple[str, str]] = [tuple(pair) for pair in variables_str]
variables: dict[str, Any] = {}
def evalpy_normalize(script: str) -> str:
    script = script.replace("^", "**")
    return script
def eval_context():
    return {"globals": math.__dict__|{"random": cool_random, "randint": randint, "physics": DimentionsNumber},
            "locals": variables}
def add_variable(name: str, script: str) -> bool:
    script = evalpy_normalize(script)
    if (name, script) in variables_str:
        return False
    try: res = eval(script, **eval_context())
    except: return True
    variables[name] = res
    prev = dict(variables_str).get(name, None)
    if prev: variables_str.remove((name, prev))
    variables_str.append((name, script))
    with open("./variables/variables.json", "w", encoding="utf-8") as f: f.write(json.dumps(variables_str))
    return False
for name, script in variables_str:
    script = evalpy_normalize(script)
    try: res = eval(script, **eval_context())
    except: raise Exception(f"There is a problem with variables! check {script}")
    variables[name] = res
with open("./variables/variables.json", "w", encoding="utf-8") as f: f.write(json.dumps(variables_str))
    

benchmarks, update_benchmarks = create_variable("benchmarks", [])
benchmarks: list[list[str|float]]

R = TypeVar("R")
caches: dict[str, dict[str, dict[str, list|int]]] = {}
def cacher(func_or_time: timedelta) -> Callable[[Callable[[str], R]], Callable[[str], R]]:
    def outer(func: Callable[[str], R]) -> Callable[[str], R]:
        cache = caches[func.__name__] = {}
        def inner(query: str, *args, **kwargs) -> R:
            query = query.strip()
            now = datetime.now().timestamp()
            if query in cache and time > (now - cache[query]["time"]):
                return cache[query]["response"]
            response = func(query, *args, **kwargs)
            cache[query] = {"response": response, "time": now}
            for query in list(cache.keys()):
                if time < (now - cache[query]["time"]): cache.pop(query)
            return response
        inner.__name__ = func.__name__
        return inner
    time = timedelta(days=1)
    wrapper = outer
    if isinstance(func_or_time, timedelta): time = func_or_time
    else: wrapper = outer(func_or_time)
    time = time.total_seconds()
    return wrapper

@cacher(timedelta(days=30))
def get_title(url: str) -> str:
    return BeautifulSoup(requests.get("https://"+url).text, features="html.parser").title.string

def format_time(time: float) -> str:
    return datetime.fromtimestamp(time).strftime("%d-%m-%Y, %H:%M")

def normalize_url(url: str) -> str:
    if url.startswith("https://"): url = url[8:]
    if url.startswith("www."): url = url[4:]
    return url

def manage_groups(query: str) -> Response:
    if not query.strip():
        return render_template("groups.html", group_sign=grouper(), groups=groups)
    message = lambda m:render_template("message.html", message=m)
    group, *url = query.split()
    url = normalize_url(" ".join(url).strip())
    redirect = True
    if group.endswith("?"):
        group = group[:-1]
        redirect = False
    if group.endswith("-#force"):
        groups.pop(group[:-7])
        return ""
    if group.endswith("-"):
        group = group[:-1]
        if group not in groups:
            return message("No such group exists!")
        if url in groups[group]:
            groups[group].pop(url)
            return message("Url removed from the group!")
        if url:
            return message("Url not found in the group!")
        return render_template("button.html", url="?q="+grouper(f"{group}-%23force"), succ_message=f"group {group} deleted")
    if group in groups:
        if url:
            if url not in groups[group]:
                groups[group][url] = datetime.now().timestamp()
                return message("Url added!")
            return message("Url already in the group!")
        if not groups[group]:
            return message("No urls to open!")
        pages = [{"time": format_time(time), "title": get_title(url), "url": url} for url, time in groups[group].items()]
        return render_template("group.html", redirect=redirect, group=group, pages=pages)
    groups[group] = {}
    if url: groups[group][url] = datetime.now().timestamp()
    return message("Group created!")

timer_regex = r"^(?P<timer>timer|таймер)( (?P<title>.+?))??(?P<words>" + \
    r"( (?P<hour>\d+)( ?h| ?ч| hours?| час(а|ов)?))?" + \
    r"( (?P<min>\d+)( ?m| ?м| min(ute)?s?| мин(ут|ута|уты)?))?" + \
    r"( (?P<sec>\d+)( ?s| ?с| sec(ond)?s?| сек(унд|унда|унды)?))?)$"

# timer_regex = r"^(?P<timer>timer|таймер)( (?P<title>.+?))?(?P<words>(( (?P<hour>\d+)( ?h| ?ч| hours?| час(а|ов)?))|( (?P<min>\d+)( ?m| ?м| min(ute)?s?| мин(ут|ута|уты)?))|( (?P<sec>\d+)( ?s| ?с| sec(ond)?s?| сек(унд|унда|унды)?))){1,3})$"

def benchmark(func: Callable[[], Response]) -> Callable[[], Response]:
    def wrapper() -> Response:
        global benchmarks
        start = datetime.now()
        res = func()
        benchmarks.append([func.__name__, request.args.get("q", ""), (datetime.now() - start).total_seconds()])
        benchmarks = benchmarks[-1000:]
        update_benchmarks()
        return res
    return wrapper

app = Flask(__name__)
bang_keys = sorted(bangs.keys())
add_variable("bang_to_check", f"({variables.get('bang_to_check', -1) - variables.get("deleted", 0)})")
add_variable("deleted", "(0)")

@app.route('/')
def search() -> Response:
    query = request.args.get("q", "").strip()
    if query.startswith("refine"):
        if query.startswith("refine replace "):
            bangs[bang_keys[variables["bang_to_check"]]] = query[15:].strip()
            with open("./constants/bangs.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(bangs))
        else:
            add_variable("bang_to_check", f"({variables['bang_to_check']+1})")
            if query.endswith('<'):
                add_variable("bang_to_check", f"({variables['bang_to_check']-1-(not variables["deleted"])})")
            if query.endswith('-'):
                add_variable("deleted", f"({variables["deleted"]+1})")
                bangs.pop(bang_keys[variables["bang_to_check"]-1])
                with open("./constants/bangs.json", "w", encoding="utf-8") as f:
                    f.write(json.dumps(bangs))
        print(f"{100*variables["bang_to_check"]/len(bang_keys):.2f}%, {bang_keys[variables['bang_to_check']]}", flush=True)
        return redirect(bangs[bang_keys[variables["bang_to_check"]]].format(q=bang_keys[variables["bang_to_check"]]))
    if query.startswith("https://") or query.startswith("www."):
        return redirect(query)
    if query.startswith("/" if chrome() else "\\"):
        res = manage_groups(query[1:])
        update_groups()
        return res
    if query.endswith("Ё"):
        query = translit(query[:-1], ru_en)
    if query.endswith("~"):
        query = translit(query[:-1], en_ru)
    if query.endswith(" !h") or query == "!h":
        return render_template("history.html", history=match_history(query[:-3]), query=query[:-3], isquery=len(query)>3)
    m = re.match(timer_regex, query)
    if m is not None:
        m = m.groupdict()
        total_secs = (xifNone(m["hour"])*60+xifNone(m["min"]))*60+xifNone(m["sec"])
        return render_template("timer.html", chrome=chrome(), total_secs=total_secs, **m)
    history.append({"query": query, "time": datetime.now().timestamp()})
    update_history()
    url = URLCode.resolve(query)
    if url: return redirect(url)
    return redirect(bangs_url(query))


@app.route(f"/opensearch.xml")
def opensearch() -> Response: return app.send_static_file("opensearch.xml")
@app.route("/menu")
def menu() -> Response:
    return render_template('menu.html', pages=URLCode.menu_data())

def pager(context: Callable[[str], str]) -> Callable[[Callable[[str], list[str]]], Callable[[str], list[str]]]:
    def outer(func: Callable[[str], list[str]]) -> Callable[[str], list[str]]:
        def inner(query: str, **kwargs) -> list[str]:
            page = len(query) - len(query.rstrip("-"))
            query = query.rstrip("-").strip()
            data = func(query, **kwargs)
            return pagify(data, query, page, kwargs.get("context", context) or context)
        return inner
    return outer

def chrome() -> bool: return UAParser(request.headers.get('User-Agent'))()[0] == "Chrome"

def grouper(t: str="") -> str: return ("/" if chrome() else "\\")+str(t)

@pager(grouper)
def suggest_groups(query: str) -> list[str]:
    query = query.strip()
    if query:
        url = normalize_url(query[1:])
        appear = [f"Url appears in {group}" for group, urls in groups.items() if url in urls]
        if appear: return appear
        group, *url = query.split()
        url = normalize_url(" ".join(url).strip())
        if group in groups:
            return [grouper(f"{query} {url}") for url in groups[group].keys()]
    return [grouper(group) for group in groups.keys()]

def updates():
    now = datetime.now()
    if now.day != datetime.fromtimestamp(usd_to_kgs[-1][0]).day:
        usd_to_kgs.append((now.timestamp(), get_current_kgs()))
    update_usd_to_kgs()

def closest_kgs_date(date: datetime|None) -> float:
    if date is None: return usd_to_kgs[-1][1]
    comp = (date.timestamp(), 0)
    l, r = None, None
    for course in [tuple(pair) for pair in usd_to_kgs]:
        if comp < course:
            r = course
            break
        l = course
    if not l: return r[1]
    if not r: return l[1]
    if r[0]+l[0] > 2*comp[0]:
        return l[1]
    return r[1]

@cacher
def currency(query: str, data: dict[str, str]):
    now = datetime.now()
    number = float(data["number"])
    fro = data["from"].lower()
    fro = CurrencyCode.resolve(fro) or fro
    to = data["to"]
    if to is None: to = variables["default_currency"]
    print(to, flush=True)
    to = CurrencyCode.resolve(to.lower()) or to.lower()
    date = None
    day = data["day"]
    month = data["month"]
    year = data["year"]
    if day is not None:
        day, month = int(day), int(month)
        if year:
            year = int(year)
            if year < 100:
                if year > (now.year % 100):
                    year += 1900
                else: year += 2000
        elif month < now.month or (month == now.month and day <= now.day): year = now.year
        else: year = now.year-1
        date = datetime(year, month, day)
    tto = to
    if to == "kgs":
        to = "usd"
        number *= closest_kgs_date(date)
    if fro == "kgs":
        fro = "usd"
        number /= closest_kgs_date(date)
    try: res = convert.convert(number, fro.upper(), to.upper(), date)
    except RateNotFoundError: res = convert.convert(number, fro.upper(), to.upper())
    return [f"= {res:.2f} {tto}"]
def xifNone(d: Any|None, x: Any=0)->Any:
    a = d if d is not None else x
    return int(a) if isinstance(a, str) and a.isdigit() else a
@cacher(timedelta(days=30))
def to_feet(query: str, data: dict[str, str]):
    inches = xifNone(data["inches"])+xifNone(data["inches_only"])
    mod, to = 30.48, xifNone(data["to"], "cm")
    if to == "m": mod /= 100
    return [f"= {(xifNone(data["feet"])+inches/12) * mod:.2f} {to}"]
@cacher(timedelta(days=30))
def to_cm(query: str, data: dict[str, str]):
    if data["fro"] == "cm": cm = float(data["cm_or_m"])
    elif data["fro"] == "m": cm = float(data["cm_or_m"])*100
    inches = cm/2.54
    foot = "foot" if inches//12 == 1 else "feet"
    return ["= " + bool(inches//12) * f"{int(inches//12)} {foot} " + (inches%12 > .5) * f"{inches%12:.2f} inches"]

rs = [(r"^((?P<feet>\d+) f(oo|ee)t( (?P<inches>\d+)( inch(es)?)?)?|(?P<inches_only>\d+) inch(es)?)( to (?P<to>m|cm))?$", to_feet),
      (r"^(?P<cm_or_m>\d+\.?(\d+)?) (?P<fro>cm|m) to feet$", to_cm),
      (r"^(?P<number>\d+\.?(\d+)?) (?P<from>\p{L}+) (to|к|в) (?P<to>\p{L}+)(( at)? (?P<day>\d{1,2})(-|/|\.)(?P<month>\d{1,2})((-|/|\.)(?P<year>(\d{2}){1,2}))?)?$", currency),
]
rs: list[tuple[str, Callable[[str, dict[str, str]], list[str]]]]

def ends_with(query, *ends: str) -> bool: return any(query.endswith(end) for end in ends)
@app.route('/suggest')
def suggest() -> Response:
    updates()
    orig: str = request.args.get("q", "")
    query = orig.strip()
    if query.startswith("/" if chrome() else "\\"):
        return jsonify([orig, suggest_groups(query[1:])])
    if query.endswith("Ё"):
        query = translit(query[:-1], ru_en).strip()
    if query.endswith("~"):
        query = translit(query[:-1], en_ru).strip()
    data = None
    if ends_with(query, "."): data = []
    elif ends_with(query, "==="): data = assign(query[:-3])
    elif ends_with(query, "=="): data = symppy(query[:-2])
    elif ends_with(query, "="): data = evalpy(query[:-1])
    elif ends_with(query, " !h", "!h"): data = [q["query"] for q in match_history(query[:-3])]
    elif ends_with(query, " !t", " перевод"): data = translate(query[:-3])
    elif ends_with(query, " !s"): data = spell(query[:-3])
    elif ends_with(query, " !ud"): data = udictionary(query[:-4])
    elif ends_with(query, " !d", " meaning"): data = dictionary(" ".join(query.split()[:-1]))
    elif ends_with(query, " !abbr", " abbr", " abbreviation"): data = abbreviate(" ".join(query.split()[:-1]))
    elif ends_with(query, "!!?"): data = llmask(query[:-3])
    elif is_same_keys(query, ["weather"]+[f"weather {place}" for place in places]): data = weather(query[8:])
    elif query == "sab": data = ["The key to strategy is not to choose a path to victory", "But to choose so that all paths lead to victory"]
    else:
        for r, sugg in rs:
            match = re.match(r, query)
            if match: break
        if match: data = sugg(query, match.groupdict())
    if data is None: data = autocomplete(query)
    data = data[:page_size()+1]
    return jsonify([orig, data])

@AccessLimit(max_count=50, period=timedelta(days=1), min_time=timedelta(seconds=3))
@cacher
def llmask(query: str) -> list[str]:
    prep = "You are a helpful assistant. Respond with a very short factual answer, ideally one phrase or a few words"
    query = query.strip()+"?"
    response = openai.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prep}, {"role": "user", "content": query}],
        temperature=0.1,
        max_tokens=100,
    )
    return [response.choices[0].message.content.strip()]

@pager(lambda t: f"{t} !abbr")
@cacher
def abbreviate(query: str) -> list[str]:
    query = query.strip()
    if not query: return ["Please provide a word to abbreviate"]
    soup = BeautifulSoup(requests.get(f"https://www.acronymfinder.com/{query}.html").text, "html.parser")
    results = soup.find("table", class_="result-list")
    if not results:
        return ["No results found."]
    results = results.find("tbody").find_all("td", class_="result-list__body__meaning")
    return [result.text for result in results]

def match_history(query: str) -> list[dict[str, str]]:
    return [{"time": format_time(q["time"]), "query": q["query"]} for q in history if query in q["query"]]

def get_current_coords():
    response = requests.get("https://ipinfo.io/json")
    data = response.json()
    lat, lon = data["loc"].split(",")
    return float(lat), float(lon)

with open("./constants/weather_codes.json", "r") as f:
    decode_weather = {int(code): desc for code, desc in json.loads(f.read()).items()}
@cacher(timedelta(minutes=5))
def weather(query: str) -> list[str]:
    place = is_same_keys(query, places.keys())
    if place: lat, lon = places[place]
    elif query: return [f"Place {query} not found"]
    else: lat, lon = get_current_coords()
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "weather_code",
        "daily": "apparent_temperature_max,apparent_temperature_min,precipitation_probability_mean,weather_code",
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    data = response.json()
    current = data['current_weather']['temperature']
    days_text = []
    for i in range(page_size()):
        sys.stdout.flush()
        day_max = data['daily']['apparent_temperature_max'][i]
        day_min = data['daily']['apparent_temperature_min'][i]
        day = f"{day_min} °C - {day_max} °C"
        day_weather = data['daily']['weather_code'][i]
        if day_weather > 50:
            rain_start, rain_end = bad_weather_hours(data["hourly"]["weather_code"][i*24:(i+1)*24])
            day_rain_chance = data['daily']['precipitation_probability_mean'][i]
            day += f", {decode_weather[day_weather]}, rain chance: {day_rain_chance}% from hours {rain_start} to {rain_end}"
        days_text.append(day)
    current_weekday = datetime.now().weekday()
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return [f"Temperature : {current} °C"]+[f"Temperature range for {weekdays[(current_weekday+i)%7]}: {days_text[i]}" for i in range(len(days_text))]

@cacher
def autocomplete(query) -> list[str]:
    url = f"https://suggestqueries.google.com/complete/search?client=chrome&q={quote(query)}"
    return requests.get(url).json()[1]

@cacher
def translate(query: str) -> list[str]:
    query = query.rstrip("-").strip()
    langs = ['en', 'ru']
    ru = query[0].lower() in "йцукенгшщзхъфывапролджэячсмитьбю"
    return [loop.run_until_complete(translator.translate(query, src=langs[ru], dest=langs[not ru])).text]

def page_size() -> int:
    if chrome():
        return 2
    else: return 4

def pagify(data: list[str], query: str, page: int, context: Callable[[str], str]) -> list[str]:
    p_size = page_size()
    last = len(data) <= (page+1)*p_size+1
    if last: return data[page*p_size:]
    next_page = context(f"{query}-{'-'*page}")
    return data[page*p_size:(page+1)*p_size] + [next_page]

def bang(code): return lambda t:f"{t} !{code}"

@pager(bang("s"))
@cacher
def spell(query: str, context: Callable[[str], str]=lambda t:t) -> list[str]:
    cands = [spell_checker.candidates(word) or [word] for word in query.split()]
    data = sorted(product(*cands), key=lambda sugg:-sum(map(lambda w:freqs.get(w, 0), sugg)))
    return [context(" ".join(line)) for line in data]

@cacher(timedelta(days=30))
def define(term: str) -> list[dict[str, str]]:
    data = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}").json()
    if isinstance(data, dict): return None
    res = []
    for word in data:
        for meaning in word["meanings"]:
            res.extend([{"part": meaning["partOfSpeech"], "definition": df["definition"]} for df in meaning["definitions"]])
    return res

@pager(bang("d"))
@cacher
def dictionary(query: str) -> list[str]:
    *words, part = query.split()
    if part in ["noun", "verb", "adj", "adv"] and any(words):
        if part == "adj": part = "adjective"
        if part == "adv": part = "adverb"
        query = " ".join(words)
    else: part = None
    data = define(query)
    if data is None:
        res = spell(query, context=bang("d"))
        if len(res) == 1 and res[0] == query+" !d":
            return ["no meaning found"]
        return res
    if part is not None: data = [entry for entry in data if entry["part"]==part]
    return [f'{query} — {entry["part"]}, {entry["definition"]}' for entry in data]

@pager(bang("ud"))
@cacher(timedelta(days=7))
def udictionary(query: str) -> list[str]:
    soup = BeautifulSoup(requests.get(f"https://www.urbandictionary.com/define.php?term={query}").text, features="html.parser")
    return [df.find("div", class_="meaning").text for df in soup.find_all("div", class_="definition")] or ["no meaning found"]


def assign(query: str) -> list[str]:
    query = query.strip()
    if query.startswith("weather "):
        places[query[8:].lower()] = get_current_coords()
        update_places()
    elif "=" in query:
        eq, var = query.split("=")
        eq = f"({eq})"
        var, *dims = var.split()
        if dims:
            eq = f"physics({eq}, '{' '.join(dims)}')"
        if add_variable(var, eq): return ["Something went wrong!"]
    else: return ["Assignment structure not recognised!"]
    return ["Variable saved"]

def symppy(query: str) -> list[str]:
    query = evalpy_normalize(query)
    try: res = f"== {parse_expr(query, transformations=standard_transformations + (implicit_multiplication,))}"
    except: res = "not computable"
    return [res]

def evalpy(query: str) -> list[str]:
    query = evalpy_normalize(query)
    try: res = f"= {eval(query, **eval_context())}"
    except:
        return symppy(query)
    return [res]

if __name__ == '__main__':
    app.run(debug=False)
