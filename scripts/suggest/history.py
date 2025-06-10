from scripts.searching import Search
from scripts.utils import page_size
import itertools

def match_history(call: str, query: str=None):
    return [entry["query"] for entry in itertools.islice(Search.match_history(query), page_size()+1)]

from scripts.suggestion import Suggest
match_history = Suggest(r"((?P<query>.+) )?!h", match_history)