from scripts.searching import Search
from scripts.utils import page_size
import itertools

def match_history(call: str, query: str=None):
    return [entry["query"] for entry in itertools.islice(Search.match_history(query), page_size()+1)]

from scripts.suggestion import Suggest
match_history = Suggest(r"((?P<query>.+) )?(!h|history)", match_history)

from scripts.testing import Tester
history_tester = Tester(match_history)
history_tester("asdf").claim(None)
history_tester("python !h").claim(True)
history_tester("history").claim(True)