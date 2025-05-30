from urllib.parse import quote
import requests

def autocomplete(call: str) -> list[str]:
    url = f"https://suggestqueries.google.com/complete/search?client=chrome&q={quote(call)}"
    return requests.get(url).json()[1]

from scripts.suggest.suggestion import Suggest
autocomplete = Suggest(r".+", autocomplete, cache=True)