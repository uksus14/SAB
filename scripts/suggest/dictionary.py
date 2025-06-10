from scripts.utils import pattern_or, prefix_pattern
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

def define_test(definition: str):
    def claim(ans: list[dict[str, str]]):
        return any(definition in entry["definition"] for entry in ans)
    claim.__doc__ = f"""checking if answer has '{definition}'"""
    return claim

from scripts.testing import Tester
define_tester = Tester(define, define_test)
define_tester("small !d", "small").claim("Any part of something that is smaller")
define_tester("small adverb !d", "small", "adverb").claim("In a small fashion")
define_tester("asdf !d", "asdf").claim(None)
define_tester("subservient verb !d", "subservient", "verb").claim(True)

parts = ["noun", "verb", "adjective", "adverb"]
def dictionary(call: str, query: str, part_slice: str=None) -> list[str]:
    part = part_slice and next((part for part in parts if part.startswith(part_slice)))
    define_call = query
    if part is not None: define_call = f"{query} {part}"
    data = define(define_call, term=query, part=part)
    if data is None: return None
    return [f'{query} — {entry["part"]}, {entry["definition"]}' for entry in data] or "No definition found!"
 
from scripts.suggestion import Suggest
dictionary = Suggest(fr"(?P<query>.+?)( (?P<part_slice>{pattern_or(*[prefix_pattern(part) for part in parts], safe=False)}))? {pattern_or('!d', 'meaning', 'means', 'значение', 'это', 'значит', 'определение')}", dictionary, cache=timedelta(days=30), page=True)

dictionary_tester = Tester(dictionary, contains_expect=True)
dictionary_tester("small !d").claim(["small — noun, Any part of something that is smaller or slimmer than the rest, now usually with anatomical reference to the back.", "small !d-"])
dictionary_tester("small adv !d").claim("small — adverb, In a small fashion.")
dictionary_tester("asdf !d").claim(None)
dictionary_tester("subservient ve !d").claim("No definition found!")