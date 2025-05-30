from spellchecker import SpellChecker
import requests
spell_checker = SpellChecker()


def define(call: str, term: str, part: str=None) -> list[dict[str, str]]:
    data = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}").json()
    if isinstance(data, dict): return None
    res = []
    for word in data:
        for meaning in word["meanings"]:
            meanings = [{"part": meaning["partOfSpeech"], "definition": df["definition"]} for df in meaning["definitions"]]
            if part is not None: meanings = [entry for entry in meanings if entry["part"]==part]
            res.extend(meanings)
    return res

from scripts.actions import Action
from datetime import timedelta
define = Action(define, cache=timedelta(days=30))

def dictionary(call: str, query: str) -> list[str]:
    *words, part_maybe = query.split()
    part = next((part for part in ["noun", "verb", "adjective", "adverb"] if part.startswith(part_maybe)), None)
    if part is not None:
        query = " ".join(words)
        call = f"{query} {part}"
    data = define(call, term=query, part=part)
    if data is None: return None
    return [f'{query} — {entry["part"]}, {entry["definition"]}' for entry in data]

from scripts.suggest.suggestion import Suggest
dictionary = Suggest(r"(?P<query>.+) (!d|meaning|значение|это|значит|определение)", dictionary, cache=timedelta(days=30), page=True)
