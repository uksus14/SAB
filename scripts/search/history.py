from scripts.searching import Search
from flask import render_template
from bs4 import BeautifulSoup

def match_history(call: str, query: str=None):
    return render_template("history.html", history=list(Search.match_history(query)), query=query)

match_history = Search(r"((?P<query>.+) )?!h", match_history)

def history_nonempty(html: str):
    """Checking if is history and history is nonempty"""
    soap = BeautifulSoup(html, features="html")
    title = soap.find(id="title").text.lower().strip()
    return "history" in title and len(soap.find("ul").find_all("li")) > 0
        
from scripts.testing import Tester
timer_tester = Tester(match_history)
timer_tester("!h").claim(history_nonempty)
timer_tester("timer !h").claim(history_nonempty)