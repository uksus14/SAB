from spellchecker import SpellChecker
import requests
spell_checker = SpellChecker()


def define(call: str, term: str=None) -> list[dict[str, str]]:
    if term is None: return None
    data = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}").json()
    if isinstance(data, dict): return None
    res = []
    for word in data:
        for meaning in word["meanings"]:
            res.extend([{"part": meaning["partOfSpeech"], "definition": df["definition"]} for df in meaning["definitions"]])
    return res

from scripts.actions import Action
from datetime import timedelta
define = Action(define, cache=timedelta(days=30))

def dictionary(call: str, query: str=None) -> list[str]:
    if query is None: return None
    *words, part = query.split()
    if part in ["noun", "verb", "adj", "adv"] and any(words):
        if part == "adj": part = "adjective"
        if part == "adv": part = "adverb"
        query = " ".join(words)
    else: part = None
    data = define(call, term=query)
    if data is None: return None
    if part is not None: data = [entry for entry in data if entry["part"]==part]
    return [f'{query} — {entry["part"]}, {entry["definition"]}' for entry in data]

from scripts.suggest.suggestion import Suggest
dictionary = Suggest(r"(?P<query>.+) (!d|meaning|значение|это|значит|определение)", dictionary, cache=timedelta(days=30), page=True)
