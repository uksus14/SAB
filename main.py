from flask import Flask, request, jsonify, redirect, render_template
from user_agent_parser import Parser as UAParser
from datetime import timedelta, datetime
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations, 
    implicit_multiplication)
from spellchecker import SpellChecker
from urllib.parse import urljoin, quote
from googletrans import Translator
from random import randint, random
from bs4 import BeautifulSoup
from itertools import product
spell_checker = SpellChecker()
translator = Translator()
import requests
import asyncio
import json
import math
import re

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def bad_weather_hours(data):
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

with open("./freqs.json", "r") as f:
    freqs = json.loads(f.read())
with open("./bangs.json", "r", encoding="utf-8") as f:
    bangs: dict[str, str] = json.loads(f.read())
def bangs_url(query):
    r = re.search(r"!(\S+)", query)
    a = "!g"
    if r: a = r.group().lower()
    return bangs.get(a[1:], bangs["g"]).format(q=quote(re.sub(r'!\S+\s*', '', query).strip()))
def create_if(path, default):    
    with open(path, "a") as f: pass
    with open(path, "r") as f: data: dict[str, dict[str, float]] = f.read()
    if not data:
        with open(path, "w") as f: f.write(json.dumps(default))
        data = default
    else: data = json.loads(data)
    return data
groups: dict[str, dict[str, float]] = create_if("./tab_groups.json", {})
def update_groups():
    with open("./tab_groups.json", "w") as f: f.write(json.dumps(groups))

history: list[dict[str, str|float]] = sorted(create_if("./history.json", []), key=lambda q:q["time"])
def update_history():
    with open("./history.json", "w") as f: f.write(json.dumps(history))

caches: dict[str, dict[str, dict[str, list|dict|int]]] = create_if("./caches.json", {})
def update_caches(cache, time: float):
    for query in cache:
        if time < (datetime.now().timestamp() - cache[query]["time"]):
            cache.pop(query)
    with open("./caches.json", "w") as f: f.write(json.dumps(caches))

with open("./benchmarks.json", "w") as f: f.write(json.dumps([]))
benchmarks: list[list[str|float]] = []
def update_benchmarks():
    with open("./benchmarks.json", "w") as f: f.write(json.dumps(benchmarks))


russian = "ё\"№;%:?йцукенгшщзхъфывапролджэячсмитьбю"
english = "`@#$%^&qwertyuiop[]asdfghjkl;'zxcvbnm,."
ru_en = {r: e for r, e in zip(russian, english)}
en_ru = {e: r for e, r in zip(english, russian)}
def translit(text, d):
    ans = ""
    prev = ""
    for l in text.lower():
        if l in d and prev != '!':
            ans+=d[l]
        else: ans+=l
        prev = l
    return ans


def cacher(func_or_time: timedelta):
    def outer(func):
        caches[func.__name__] = {}
        cache = caches[func.__name__]
        def inner(query, *args, **kwargs):
            query = query.strip()
            if not query: return [] 
            now = datetime.now().timestamp()
            if query in cache:
                if time > (now - cache[query]["time"]):
                    return cache[query]["response"]
            response = func(query, *args, **kwargs)
            cache[query] = {"response": response, "time": now}
            update_caches(cache, time)
            return response
        return inner
    time = timedelta(days=1)
    if isinstance(func_or_time, timedelta):
        time = func_or_time
        wrapper = outer
    else:
        wrapper = outer(func_or_time)
    time = time.total_seconds()
    return wrapper

@cacher(timedelta(days=30))
def get_title(url):
    return BeautifulSoup(requests.get("https://"+url).text, features="html.parser").title.string

def format_time(time: float):
    return datetime.fromtimestamp(time).strftime("%d-%m-%Y, %H:%M")

def normalize_url(url):
    if url.startswith("https://"): url = url[8:]
    if url.startswith("www."): url = url[4:]
    return url

def manage_groups(query: str):
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
        return render_template("group.html", redirect=redirect, group=group, pages=[{"time": format_time(time), "title": get_title(url), "url": url} for url, time in groups[group].items()])
    groups[group] = {}
    if url: groups[group][url] = datetime.now().timestamp()
    return message("Group created!")

timer_regex = r"^(?P<timer>timer|таймер)( (?P<title>.+?))?(?P<words>(( (?P<hour>\d+)( ?h| (hours?|час(а|(ов))?)))|( (?P<min>\d+)( ?m| (min(ute)?s?|мин(ута|уты)?)))|( (?P<sec>\d+)( ?s| (sec(ond)?s?|сек(унда|унды)?)))){1,3})$"

def benchmark(func):
    def wrapper():
        # global benchmarks
        # start = datetime.now()
        query = request.args.get("q", "")
        res = func(query)
        # benchmarks.append([func.__name__, query, (datetime.now() - start).total_seconds()])
        # benchmarks = benchmarks[-1000:]
        # update_benchmarks()
        return res
    return wrapper

app = Flask(__name__)

@benchmark
def _search(query):
    query = query.strip()
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
        return render_template("timer.html", chrome=chrome(), **m.groupdict())
    codes = {"math": 26196,
              "success": 24587,
              "chem": 24589,
              "phys": 24591,
              "engin": 24595,
              "furth": 24583}
    qmplus = lambda code: f"https://qmplus.qmul.ac.uk/course/view.php?id={code}"
    if query in codes: return redirect(qmplus(codes[query.strip()]))
    if translit(query, ru_en) in codes: return redirect(qmplus(codes[translit(query, ru_en)]))
    if translit(query, en_ru) in codes: return redirect(qmplus(codes[translit(query, en_ru)]))
    history.append({"query": query, "time": datetime.now().timestamp()})
    update_history()
    return redirect(bangs_url(query))
@app.route('/')
def search():
    return _search()

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")
@app.route("/opensearch.xml")
def opensearch():
    return app.send_static_file("opensearch.xml")

variables = {}

def pager(context):
    def outer(func):
        def inner(query, **kwargs):
            page = len(query) - len(query.rstrip("-"))
            query = query.rstrip("-").strip()
            data = func(query, **kwargs)
            return pagify(data, query, page, kwargs.get("context", context) or context)
        return inner
    return outer

def chrome(): return UAParser(request.headers.get('User-Agent'))()[0] == "Chrome"

def grouper(t=""): return ("/" if chrome() else "\\")+str(t)

@pager(grouper)
def suggest_groups(query):
    query = query.strip()
    print(query)
    if query:
        url = normalize_url(query[1:])
        appear = [f"Url appears in {group}" for group, urls in groups.items() if url in urls]
        if appear: return appear
        group, *url = query.split()
        url = normalize_url(" ".join(url).strip())
        if group in groups:
            return [grouper(f"{query} {url}") for url in groups[group].keys()]
    print([grouper(group) for group in groups.keys()])
    return [grouper(group) for group in groups.keys()]


@benchmark
def _suggest(orig: str):
    query = orig.strip()
    if query.startswith("/" if chrome() else "\\"):
        return jsonify([orig, suggest_groups(query[1:])])
    if query.endswith("Ё"):
        query = translit(query[:-1], ru_en).strip()
    if query.endswith("~"):
        query = translit(query[:-1], en_ru).strip()
    if query.endswith("."):
        data = []
    elif query.endswith("==="): data = assign(query[:-3])
    elif query.endswith("=="): data = symppy(query[:-2])
    elif query.endswith("="): data = evalpy(query[:-1])
    elif query.endswith(" !h") or query == "!h": data = [q["query"] for q in match_history(query[:-3])]
    elif query.endswith(" !t"): data = translate(query[:-3])
    elif query.endswith(" !s"): data = spell(query[:-3])
    elif query.endswith(" !d"): data = dictionary(query[:-3])
    elif query.endswith(" !ud"): data = udictionary(query[:-4])
    elif "weather" in [query, translit(query, en_ru), translit(query, ru_en)]: data = weather(query)
    elif query == "sab": data = ["The key to strategy is not to choose a path to victory", "But to choose so that all paths lead to victory"]
    else: data = autocomplete(query)
    data = data[:page_size()+1]
    return jsonify([orig, data])
@app.route('/suggest')
def suggest():
    return _suggest()

def match_history(query):
    return [{"time": format_time(q["time"]), "query": q["query"]} for q in history if query in q["query"]]

@cacher(timedelta(minutes=5))
def weather(query):
    decode_weather = {51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle", 56: "Light freezing Drizzle", 57: "Dense freezing drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain", 66: "Light freezing rain", 67: "Heavy freezing Rain", 71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall", 77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers"}
    response = requests.get("https://ipinfo.io/json")
    data = response.json()
    lat, lon = data["loc"].split(",")
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": float(lat),
        "longitude": float(lon),
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
def autocomplete(query):
    url = f"https://suggestqueries.google.com/complete/search?client=chrome&q={query}"
    return requests.get(url).json()[1]

@cacher
def translate(query):
    query = query.rstrip("-").strip()
    langs = ['en', 'ru']
    ru = query[0] in russian
    return [loop.run_until_complete(translator.translate(query, src=langs[ru], dest=langs[not ru])).text]

def page_size():
    if chrome():
        return 2
    else: return 4

def pagify(data, query, page, context):
    p_size = page_size()
    last = len(data) <= (page+1)*p_size+1
    if last: return data[page*p_size:]
    next_page = context(f"{query}-{'-'*page}")
    return data[page*p_size:(page+1)*p_size] + [next_page]

def bang(code): return lambda t:f"{t} !{code}"

@pager(bang("s"))
@cacher
def spell(query, context=None):
    cands = [spell_checker.candidates(word) or [word] for word in query.split()]
    data = sorted(product(*cands), key=lambda sugg:-sum(map(lambda w:freqs.get(w, 0), sugg)))
    if context is None: context = lambda t:t
    return [context(" ".join(line)) for line in data]

@cacher(timedelta(days=30))
def define(term: str):
    data = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}").json()
    if isinstance(data, dict): return None
    res = []
    for word in data:
        for meaning in word["meanings"]:
            res.extend([{"part": meaning["partOfSpeech"], "definition": df["definition"]} for df in meaning["definitions"]])
    return res

@pager(bang("d"))
@cacher
def dictionary(query):
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
def udictionary(query):
    soup = BeautifulSoup(requests.get(f"https://www.urbandictionary.com/define.php?term={query}").text, features="html.parser")
    return [df.find("div", class_="meaning").text for df in soup.find_all("div", class_="definition")] or ["no meaning found"]

def assign(query):
    eq, var = query.split("=")
    variables[var] = float(evalpy(eq)[0][2:])
    return ["Variable saved"]

def symppy(query):
    query = query.replace("^", "**")
    try: res = f"== {parse_expr(query, transformations=standard_transformations + (implicit_multiplication,))}"
    except: res = "not computable"
    return [res]

def cool_random(l=None, r=None):
    if l is None: return random()
    if r is None: return randint(1, l)
    return randint(l, r)

def evalpy(query):
    query = query.replace("^", "**")
    try: res = f"= {eval(query, math.__dict__|{"random": cool_random}, variables)}"
    except:
        return symppy(query)
    return [res]

if __name__ == '__main__':
    app.run(debug=False)
