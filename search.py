from flask import Flask, request, jsonify, redirect
from user_agent_parser import Parser as UAParser
from datetime import timedelta, datetime
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations, 
    implicit_multiplication)
from spellchecker import SpellChecker
from urllib.parse import urlencode
from googletrans import Translator
from bs4 import BeautifulSoup
from itertools import product
spell_checker = SpellChecker()
from random import randint
translator = Translator()
from math import *
import requests
import asyncio
import json
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

russian = "ё\"№;%:?йцукенгшщзхъфывапролджэячсмитьбю"
english = "`@#$%^&qwertyuiop[]asdfghjkl;'zxcvbnm,."
ru_en = {r: e for r, e in zip(russian, english)}
en_ru = {e: r for e, r in zip(english, russian)}
def translit(text, d):
    ans = ""
    prev = ""
    for l in text[:-1].lower():
        if l in d and prev != '!':
            ans+=d[l]
        else: ans+=d[l]
        prev = l
    return ans

app = Flask(__name__)
@app.route('/')
def search():
    query = request.args.get("q")
    if query.endswith("Ё"):
        query = translit(query[::-1], ru_en)
    if query.endswith("~"):
        query = translit(query[::-1], en_ru)
    replace = {"y": "youtube", "wa": "walpha", "w": "wiki"}
    qmplus = "https://qmplus.qmul.ac.uk/course/view.php?id="
    codes = {"math": 26196,
              "success": 24587,
              "chem": 24589,
              "phys": 24591,
              "engin": 24595,
              "furth": 24583}
    for old, new in replace.items():
        query = query.replace(f"!{old}", f"!@{new}")
    if query.strip() in qmplus:
        return redirect(qmplus+codes[query.strip()])
    return redirect(f"https://unduck.link?{urlencode({"q": query.replace("!@", "!")})}")
@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")
@app.route("/opensearch.xml")
def opensearch():
    return app.send_static_file("opensearch.xml")
@app.route('/suggest')
def suggest():
    orig = request.args.get("q", "")
    query = orig.strip()
    if query.endswith("Ё"):
        query = translit(query[::-1], ru_en)
    if query.endswith("~"):
        query = translit(query[::-1], en_ru)
    elif query.endswith("."):
        data = []
    elif query.endswith("="): data = evalpy(query[:-1])
    elif query.endswith(" !t"): data = translate(query[:-3])
    elif query.endswith(" !s"): data = spell(query[:-3])
    elif query.endswith(" !d"): data = dictionary(query[:-3])
    elif query.endswith(" !ud"): data = udictionary(query[:-4])
    elif query == "weather": data = weather()
    elif query == "sab": data = ["The key to strategy is not to choose a path to victory", "But to choose so that all paths lead to victory"]
    else: data = autocomplete(query)
    data = data[:page_size(request)+1]
    return jsonify([orig, data])

with open("./freqs.json", "r") as f:
    freqs = json.loads(f.read())

def weather():
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
    for i in range(page_size(request)):
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
    return [f"Temperature : {current} °C"]+[f"Temperature range for {weekdays[current_weekday+i]}: {days_text[i]}" for i in range(len(days_text))]

def cacher(func):
    cache = {}
    def wrapper(query, **kwargs):
        query = query.strip()
        if not query: return [] 
        if query in cache:
            if timedelta(days=1) > (datetime.now() - cache[query]["time"]):
                return cache[query]["response"]
        response = func(query, **kwargs)
        cache[query] = {"response": response, "time": datetime.now()}
        return response
    return wrapper

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

def page_size(request):
    if UAParser(request.headers.get('User-Agent'))()[0] == "Chrome":
        return 2
    else: return 4

def pagify(data, query, page, tail):
    p_size = page_size(request)
    last = len(data) <= (page+1)*p_size+1
    if last: return data[page*p_size:]
    next_page = f"{query}-{'-'*page} {tail}"
    return data[page*p_size:(page+1)*p_size] + [next_page]

def pager(bang):
    def outer(func):
        def inner(query, **kwargs):
            page = len(query) - len(query.rstrip("-"))
            query = query.rstrip("-").strip()
            data = func(query, **kwargs)
            return pagify(data, query, page, kwargs["tail"] if "tail" in kwargs else bang)
        return inner
    return outer
    
@pager("!s")
@cacher
def spell(query, tail="!s"):
    cands = [spell_checker.candidates(word) or [word] for word in query.split()]
    data = sorted(product(*cands), key=lambda sugg:-sum(map(lambda w:freqs.get(w, 0), sugg)))
    return [" ".join(line)+(f" {tail}"*(tail != "!s")) for line in data]

@cacher
def define(term: str):
    data = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}").json()
    if isinstance(data, dict): return None
    res = []
    for word in data:
        for meaning in word["meanings"]:
            res.extend([{"part": meaning["partOfSpeech"], "definition": df["definition"]} for df in meaning["definitions"]])
    return res

@pager("!d")
@cacher
def dictionary(query):
    *words, part = query.split()
    if part in ["noun", "verb", "adj"] and any(words):
        query = " ".join(words)
    else: part = None
    data = define(query)
    if data is None:
        res = spell(query, tail="!d")
        if len(res) == 1 and res[0] == query+" !d":
            return ["no meaning found"]
        return res
    if part is not None: data = [entry for entry in data if entry["part"]==part]
    return [f'{query} — {entry["part"]}, {entry["definition"]}' for entry in data]

@pager("!ud")
@cacher
def udictionary(query):
    soup = BeautifulSoup(requests.get(f"https://www.urbandictionary.com/define.php?term={query}").text, features="html.parser")
    return [df.find("div", class_="meaning").text for df in soup.find_all("div", class_="definition")] or ["no meaning found"]

def evalpy(query):
    from sympy import simplify, cos, sin
    error = False
    try: res = f"{eval(query)}"
    except:
        try:
            res = parse_expr(query, transformations=standard_transformations + (implicit_multiplication,))
        except: res = "not computable"
    return [f"= {res}"]

if __name__ == '__main__':
    app.run(debug=True)
