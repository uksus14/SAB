from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication
from contextlib import suppress 

def normalize_eval(query: str) -> str:
    return query.replace("^", "**").replace("->", ":")

def globs():
    import variables.eval
    return variables.eval.__dict__

globs = globs()

def parse(query: str):
    transformations = standard_transformations + (implicit_multiplication,)
    return str(parse_expr(query, transformations=transformations))

def cool_eval(query: str):
    if not query: return ""
    query = normalize_eval(query)
    with suppress(Exception): return eval(query, globals=globs)
    with suppress(Exception): return eval(parse(query), globals=globs)
    return "Error"

test = """

14000+2(14750+20425)
"""


test = test.splitlines()
if not test[-1].strip(): test = test[:-1]
if not test[0]: test = test[1:]
[print(f"{line:<40} | {cool_eval(line)}") for line in test]