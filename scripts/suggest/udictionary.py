from bs4 import BeautifulSoup, Tag
import requests

udict_exception = Exception("There was a problem with udictionary scraping")
def udictionary_inner(call: str, query: str) -> list[str]|str:
    soup = BeautifulSoup(requests.get(f"https://www.urbandictionary.com/define.php?term={query}").text, features="html.parser")
    res: list[str] = []
    for defin in soup.find_all("div", class_="definition"):
        if not isinstance(defin, Tag): raise udict_exception
        mean = defin.find("div", class_="meaning")
        if mean is None: raise udict_exception
        res.append(mean.text)
    return res or "No meaning found"

from scripts.suggestion import Suggest
udictionary = Suggest(r"(?P<query>.+) !?(ud|urban|meaning)", udictionary_inner, cache=True, page=True)

from scripts.testing import Tester
udict_tester = Tester(udictionary)
udict_tester("moron ud").claim(True)
udict_tester("rizz !urban").claim(True)