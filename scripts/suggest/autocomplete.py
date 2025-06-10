from urllib.parse import quote
import requests

def autocomplete(call: str) -> list[str]:
    url = f"https://suggestqueries.google.com/complete/search?client=chrome&q={quote(call)}"
    return requests.get(url).json()[1]

from scripts.suggestion import Suggest
autocomplete = Suggest(r".+", autocomplete, cache=True)

def autocomplete_claim(ans):
    """checking if autocomplete is a list of strings"""
    return isinstance(ans, list) and isinstance(ans[0], str)

from scripts.testing import Tester
complete_tester = Tester(autocomplete)
complete_tester("test").claim(autocomplete_claim)