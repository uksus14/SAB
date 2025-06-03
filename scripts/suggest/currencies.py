from currency_converter import CurrencyConverter, RateNotFoundError
from bisect import bisect_left, bisect_right
from scripts.codes import Code
from variables import Variable
from datetime import datetime
from bs4 import BeautifulSoup
import requests
convert = CurrencyConverter()

class CurrencyCode(Code):
    _list = []
    DEFAULT_CURRENCY = "usd"
    @classmethod
    def resolve(cls, call: str|None) -> str:
        if call is None: return cls.DEFAULT_CURRENCY
        return super().resolve(call) or call

def get_current_kgs() -> float:
    url = "https://wise.com/ru/currency-converter/usd-to-kgs-rate?amount=1"
    soup = BeautifulSoup(requests.get(url).text, features="html.parser")
    return float(soup.find(id="target-input")["value"].replace(",", ".", count=1))

def update_kgs(usd_to_kgs: Variable[list[dict[str, float|datetime]]]):
    now = datetime.now()
    if (now - usd_to_kgs.data[-1]["time"]).days:
        usd_to_kgs.data += [{"time": now, "rate": get_current_kgs()}]

usd_to_kgs = Variable[list[dict[str, float|datetime]]].create(
    "usd_to_kgs", [{"time": datetime.now(), "rate": get_current_kgs()}], update_kgs)
def closest_kgs_date(date: datetime|None) -> float:
    if date is None: return usd_to_kgs.data[-1]["rate"]
    l = max(bisect_left([entry["time"] for entry in usd_to_kgs.data], (date, 0)), len(usd_to_kgs.data)-1)
    r = max(bisect_right([entry["time"] for entry in usd_to_kgs.data], (date, 0)), len(usd_to_kgs.data)-1) 
    if r-l <= 1: return usd_to_kgs.data[l]["rate"]
    if usd_to_kgs.data[l]["time"]+(usd_to_kgs.data[r]["time"]-usd_to_kgs.data[l]["time"])/2 > date: return usd_to_kgs.data[r]["rate"]
    return usd_to_kgs.data[l]["rate"]

def convert_currencies(call: str, amount: float, fro: str, to: str=None, day: int=None, month: int=None, year: int=None):
    now = datetime.now()
    fro = CurrencyCode.resolve(fro)
    to = CurrencyCode.resolve(to)
    if (len(fro), len(to)) != (3, 3): return None
    date = None
    if day is not None:
        if year is not None:
            year = int(year)
            if year < 100:
                year += 1900
                if year <= (now.year % 100): year += 100
        else:
            year = now.year
            if month > now.month or (month == now.month and day > now.day): year -= 1
        date = datetime(year, month, day)
    tto = to
    if to == "kgs":
        to = "usd"
        amount *= closest_kgs_date(date)
    if fro == "kgs":
        fro = "usd"
        amount /= closest_kgs_date(date)
    try: res = convert.convert(amount, fro.upper(), to.upper(), date)
    except RateNotFoundError:
        try: res = convert.convert(amount, fro.upper(), to.upper())
        except: return None
    return [f"= {res:.2f} {tto}"]

from scripts.suggestion import Suggest
Suggest(r"(?P<amount>\d+\.?\d*) (?P<fro>\p{L}+)( (to|к|в) (?P<to>\p{L}+)(( at)? (?P<day>\d{1,2})(-|/|\.)(?P<month>\d{1,2})((-|/|\.)(?P<year>(\d{2}){1,2}))?)?)?", convert_currencies, cache=True)

CurrencyCode("usd", "us", "dollar", "dol", "d", "доллар", "долларов", "доллара", "доллару", "долларах", "дол", "д")
CurrencyCode("rub", "ru", "ruble", "r", "рубль", "рублей", "рублях", "рублям", "рубля", "рублю", "руб", "р")
CurrencyCode("kgs", "kg", "som", "k", "s", "сом", "сомам", "сомах", "сома", "сомов", "с")
CurrencyCode("gbp", "gb", "pound", "pnd", "p", "фунт", "фунтам", "фунтах", "фунта", "фунтов", "ф")
CurrencyCode("eur", "er", "euro", "eu", "e", "евро", "е")
CurrencyCode("krw", "kor", "korean", "won", "w", "вон", "корейский")