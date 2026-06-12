from scripts.searching import Search
from flask import render_template
from bs4 import BeautifulSoup, Tag

def match_history_inner(call: str, query: str|None=None):
    return render_template("history.html", history=list(Search.match_history(query)), query=query)

match_history = Search(r"((?P<query>.+) )?!h", match_history_inner)

def history_nonempty(html: str) -> bool:
    """Checking if is history and history is nonempty"""
    soap = BeautifulSoup(html, features="html.parser")
    titleEl = soap.find(id="title")
    if titleEl is None: return False
    title: str = titleEl.text.lower().strip()
    results = soap.find("ul")
    if not isinstance(results, Tag): return False
    return "history" in title and len(results.find_all("li")) > 0

from scripts.testing import Tester
timer_tester = Tester(match_history)
timer_tester("!h").claim(history_nonempty)
timer_tester("timer !h").claim(history_nonempty)