from spellchecker import SpellChecker
from itertools import product
from constants import freqs
spell_checker = SpellChecker()

def spell(call: str, query: str=None) -> list[str]:
    if query is None: return None
    cands = [spell_checker.candidates(word) or [word] for word in query.split()]
    data = sorted(product(*cands), key=lambda sugg:sum(map(lambda w:freqs.get(w, 0), sugg)), reverse=True)
    if len(data) == 1: return "words not recognized"
    return [call.replace(query, " ".join(line)) for line in data]

from scripts.suggest.suggestion import Suggest
from datetime import timedelta
spell = Suggest(r"(?P<query>.+) !(s|d)", spell, cache=timedelta(minutes=10))