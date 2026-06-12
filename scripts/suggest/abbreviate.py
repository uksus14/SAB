from scripts.utils import pattern_or
from bs4 import BeautifulSoup, Tag
import requests

def abbreviate_inner(call: str, query: str) -> list[str]|str:
    query = query.strip()
    soup = BeautifulSoup(requests.get(f"https://www.acronymfinder.com/{query}.html").text, "html.parser")
    results = soup.find("table", class_="result-list")
    if not isinstance(results, Tag): return "No results found."
    results = results.find("tbody")
    if not isinstance(results, Tag): return "There was a problem with scraping abbreviations"
    results = results.find_all("td", class_="result-list__body__meaning")
    return [result.text for result in results]

from scripts.suggestion import Suggest
abbreviate = Suggest(fr"(?P<query>.+) !?{pattern_or("abbr", "abbreviation", "stands for", "акроним", "расшифровывается")}", abbreviate_inner, cache=True, page=True)


from scripts.testing import Tester
abbr_tester = Tester(abbreviate, contains_expect=True)
abbr_tester("ASDFLKJASDF abbr").claim("No results found.")
abbr_tester("NASA stands for").claim(["NASA stands for-", "National Aeronautics and Space Administration (USA)"])
abbr_tester("NASA !акроним-").claim("NASA !акроним--")