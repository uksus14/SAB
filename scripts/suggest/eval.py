from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication
from scripts.serializing import Serializers
from variables import EvalStrVar

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
"""

eval_strs = EvalStrVar.create("eval", default_eval.split("\n"), ext="py", serializer=Serializers.line_splitter())

def globs():
    import variables.eval
    return variables.eval.__dict__

def refresh_eval(call: str) -> str:
    prev = eval_strs.data
    eval_strs.refresh()
    if cool_eval("None=").startswith("= "): return "Variables refreshed!"
    eval_strs._data = prev
    return "There was a problem with Variables!"

def cool_eval(call: str, query: str, assignment: str=None) -> str:
    query = query.replace("^", "**")
    func = exec if assignment else eval
    try: return f"= {func(query, globals=globs())}"
    except: return symppy_eval(call+"=")

def symppy_eval(call: str, query: str) -> str:
    query = query.replace("^", "**")
    try: return f"== {parse_expr(query, transformations=standard_transformations + (implicit_multiplication,))}"
    except: return "not computable"

def add_line(call: str, query: str, var: str=None, val: str=None):
    query = query.replace("^", "**")
    if not cool_eval(call.replace("===", "=")).startswith("= "): return "Adding line failed!"
    eval_strs.data += [query]
    return "Line saved!"

from scripts.suggestion import Suggest
refresh_eval = Suggest(r"==r", refresh_eval)
cool_eval = Suggest(r"(==? )?(?P<query>(?P<assignment>.*[^!=><]=[^=].*)|.+)=", cool_eval)
symppy_eval = Suggest(r"(==? )?(?P<query>.+)==", symppy_eval)
add_line = Suggest(r"(==? )?(?P<query>.+)===", add_line)