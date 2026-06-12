from scripts.utils import url_pattern
from scripts.searching import Search
from urllib.parse import quote
from constants import bangs
from pathlib import Path
import importlib

for path in Path(__file__).parent.glob("*.py"):
    if path.name == "__init__.py": continue
    importlib.import_module(f"{__name__}.{path.stem}")

default_bang = "gwoai"
def detect_redirect_inner(call: str, url: str) -> str: return f"https://{url}"
def bang_url_inner(call: str, query: str, bang: str|None=None) -> str:
    if isinstance(bang, str): bang = bang.lower().strip()
    if bang not in bangs:
        query = call
        bang = default_bang
    return bangs[bang].format(q=quote(query.strip()))

detect_redirect = Search(url_pattern, detect_redirect_inner)
bang_url = Search(r"(?P<query>.+?)( !(?P<bang>\p{L}+))?", bang_url_inner)