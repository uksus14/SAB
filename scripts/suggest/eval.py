from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication
from scripts.serializing import Serializers
from variables import EvalStrVar
import regex

default_eval = """#Eval variables and functions here
from math import *
import random as rand_mod
from random import *
def choice(*choices):
    for _ in [", ", ",", " "]:
        if len(choices) != 1: break
        choices = choices[0].split(", ")
    return rand_mod.choice(choices)
def random(l=None, r=None) -> int|float:
    if l is None: return rand_mod.random()
    if r is None: return rand_mod.randint(1, l)
    return rand_mod.randint(l, r)
def count(*args):
    ans = {}
    for arg in args:
        if arg in ans: ans[arg] += 1
        else: ans[arg] = 1
    return ans
"""

eval_strs = EvalStrVar.create("eval", default_eval.split("\n"), ext="py", serializer=Serializers.line_splitter())

def globs():
    import variables.eval
    return variables.eval.__dict__

def normalize_eval(query: str) -> str:
    return query.replace("^", "**").replace("->", ":")

def refresh_eval(call: str) -> str:
    prev = eval_strs.data
    eval_strs.refresh()
    if cool_eval("None=").startswith("= "): return "Variables refreshed!"
    eval_strs._data = prev
    return "There was a problem with Variables!"

def search_eval(call: str, query: str) -> list[str]:
    ans = []
    if not regex.match(r"^\/.*\/$", query): mm = lambda match: query in match
    else: mm = lambda match:regex.search(query[1:-1], match)
    for line in eval_strs.data[eval_strs.data.index("#constants"):]:
        match = regex.match(assignment_re, line, flags=regex.IGNORECASE)
        if not match: continue
        match = match.group("variable")
        if mm(match): ans.append(f"= {match}")
    return ans or "No variables found!"

def cool_eval(call: str, query: str, variable: str=None, value: str=None, normalize=True) -> str:
    query = normalize_eval(query)
    if value:
        value = normalize_eval(value)
        try: return f"= {eval(value, globals=globs())}"
        except: pass
    try: return f"= {eval(query, globals=globs())}"
    except: pass
    normalized = symppy_eval(call+"=")
    if not normalize or normalized == "not computable": return normalized
    return f"= {eval(normalized[3:], globals=globs())}"
def symppy_eval(call: str, query: str) -> str:
    query = normalize_eval(query)
    try: exp = parse_expr(query, transformations=standard_transformations + (implicit_multiplication,))
    except: return "not computable"
    return f"== {exp}"

def add_line(call: str, query: str, variable: str=None, value: str=None) -> str:
    query = normalize_eval(query)
    if not cool_eval(call.replace("===", "=")).startswith("= "): return "Adding line failed!"
    def persist(line: str) -> bool:
        match = regex.match(f"^{assignment_re}$", line) or regex.match(r"^(?P<variable>\w+)[.[].+$", line)
        return match is None or match.group("variable") != variable
    if variable is None: persist = lambda l: True
    var_line = eval_strs.data.index("#variables")
    eval_strs.data = eval_strs.data[:var_line]+list(filter(persist, eval_strs.data[var_line:]))+[query]
    return "Line saved!"

assignment_re = r"(?P<variable>.*?[^!=><])=(?P<value>[^=].*)"
from scripts.suggestion import Suggest
refresh_eval = Suggest(r"==r", refresh_eval)
search_eval = Suggest(r"(?P<query>.+)=\?", search_eval, page=True)
cool_eval = Suggest(fr"(==? )?(?P<query>({assignment_re})|.+)=", cool_eval)
symppy_eval = Suggest(r"(==? )?(?P<query>.+)==", symppy_eval)
add_line = Suggest(fr"(==? )?(?P<query>({assignment_re})|.+)===", add_line)

from scripts.testing import Tester
refresh_tester = Tester(refresh_eval)
refresh_tester("asdf").claim(None)
refresh_tester("==r").claim("Variables refreshed!")
def not_novarfound(ans):
    """checking if the answer is not 'No variables found!'"""
    return ans and ans != "No variables found!"
search_tester = Tester(search_eval)
search_tester("el=?").claim(not_novarfound)
search_tester("/^el.+$/=?").claim(not_novarfound)
search_tester("qwertyu=?").claim("No variables found!")
eval_tester = Tester(cool_eval)
eval_tester("= 34+1=").claim("= 35")
eval_tester("= qwer+dfgh=").claim("== dfgh + qwer")
eval_tester("== random()=").claim(True)
eval_tester("random(3)=").claim(True)
symppy_tester = Tester(symppy_eval)
symppy_tester("x-q+3r-2r==").claim("== -q + r + x")
add_tester = Tester(add_line)
add_tester("z=3===").claim("Line saved!")
add_tester("z=[]===").claim("Line saved!")
add_tester("z.append(3)===").claim("Line saved!")