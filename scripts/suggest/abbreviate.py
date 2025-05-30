from bs4 import BeautifulSoup
import requests

def abbreviate(call: str, query: str="") -> list[str]:
    query = query.strip()
    if not query: return ["Please provide a word to abbreviate"]
    soup = BeautifulSoup(requests.get(f"https://www.acronymfinder.com/{query}.html").text, "html.parser")
    results = soup.find("table", class_="result-list")
    if not results:
        return ["No results found."]
    results = results.find("tbody").find_all("td", class_="result-list__body__meaning")
    return [result.text for result in results]

from scripts.suggest.suggestion import Suggest
abbreviate = Suggest(r"(?P<query>.+) (!abbr|abbr|abbreviation|stands for|акроним|расшифровывается)", abbreviate, cache=True, page=True)