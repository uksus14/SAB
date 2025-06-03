from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication
from scripts.utils import eval_normalize

def simplify(call: str, query: str) -> list[str]:
    query = eval_normalize(query.strip())
    try: res = f"== {parse_expr(query, transformations=standard_transformations + (implicit_multiplication,))}"
    except: res = "not computable"
    return res

from scripts.suggestion import Suggest
from datetime import timedelta
# Suggestion(r"={0,2}(?P<query>.+)==", simplify, cache=timedelta(minutes=1))