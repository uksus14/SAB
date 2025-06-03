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
def detect_redirect(call: str) -> str: return call
def bang_url(call: str, query: str, bang: str=None) -> str:
    if isinstance(bang, str): bang = bang.lower().strip()
    if bang not in bangs:
        query = call
        bang = default_bang
    return bangs[bang].format(q=quote(query.strip()))
detect_redirect = Search(url_pattern, detect_redirect)
bang_url = Search(r"(?P<query>.+?)( !(?P<bang>\p{L}+))?", bang_url)