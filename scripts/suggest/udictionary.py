from bs4 import BeautifulSoup
import requests

def udictionary(call: str, query: str) -> list[str]:
    soup = BeautifulSoup(requests.get(f"https://www.urbandictionary.com/define.php?term={query}").text, features="html.parser")
    return [df.find("div", class_="meaning").text for df in soup.find_all("div", class_="definition")] or "No meaning found"

from scripts.suggestion import Suggest
udictionary = Suggest(r"(?P<query>.+) !?(ud|urban)", udictionary, cache=True, page=True)