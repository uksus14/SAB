from bs4 import BeautifulSoup
import requests

def get_title(url: str) -> str:
    return BeautifulSoup(requests.get("https://"+url).text, features="html.parser").title.string

from scripts.actions import Action
from datetime import timedelta
get_title = Action(get_title, cache=timedelta(days=30))

# def groups(call: str, query: str) -> list[str]:
#     query = query.strip()
#     if query:
#         url = normalize_url(query[1:])
#         appear = [f"Url appears in {group}" for group, urls in groups.items() if url in urls]
#         if appear: return appear
#         group, *url = query.split()
#         url = normalize_url(" ".join(url).strip())
#         if group in groups:
#             return [f"{call} {url}" for url in groups[group].keys()]
#     return [grouper(group) for group in groups.keys()]

# from scripts.suggest.suggestion import Suggestion
# Suggestion(r"\\", groups, page=True)
# Suggestion(r"/", groups, page=True)