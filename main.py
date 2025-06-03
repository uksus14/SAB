from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication
from scripts.utils import page_size, translit, en_ru, ru_en, approx_time
from flask import Flask, request, jsonify, render_template, Response
from scripts.search.menu import URLCode
from scripts.suggest import Suggest
from scripts.actions import Action
from scripts.search import Search
from commons import BASE_FOLDER
from variables import Variable
from typing import Any
import random
import openai
import json
import math

try: openai.api_key = (BASE_FOLDER / "openai_key.txt").read_text().strip()
except FileNotFoundError:
    print("OpenAI key file not found")
    Action.disable["llmask"] = "OpenAI key not found"
        
def cool_choice(*choices):
    for sep in [", ", ",", " "]:
        if len(choices) != 1: break
        choices = choices[0].split(", ")
    return random.choice(choices)
def cool_random(l=None, r=None) -> int|float:
    if l is None: return random.random()
    if r is None: return random.randint(1, l)
    return random.randint(l, r)

class DimentionsNumber(float):
    def __new__(cls, num: float|str, dim: str=None):
        if not dim:
            num, _, dim = num.partition(" ")
        ins = super().__new__(cls, num)
        ins.__init__(num, dim)
        return ins
    def __init__(self, num: float, dim: str):
        self.num = num
        self.dim = dim.replace("**", "^")
        
    def __str__(self):
        return f"{self.num} {self.dim}"

path = f"./variables/variables.json"
with open(path, "a") as f: pass
with open(path, "r", encoding="utf-8") as f: variables_str: dict[str, dict[str, float]] = f.read()
if not variables_str:
    with open(path, "w", encoding="utf-8") as f: f.write(json.dumps([]))
    variables_str = []
else: variables_str = json.loads(variables_str)
variables_str: list[tuple[str, str]] = [tuple(pair) for pair in variables_str]
variables: dict[str, Any] = {}
def evalpy_normalize(script: str) -> str:
    return script.replace("^", "**")
def eval_context():
    return {"globals": math.__dict__|random.__dict__|{"random": cool_random, "choice": cool_choice, "physics": DimentionsNumber},
            "locals": variables}
def add_variable(name: str, script: str) -> bool:
    script = evalpy_normalize(script)
    if (name, script) in variables_str:
        return False
    try: res = eval(script, **eval_context())
    except: return True
    variables[name] = res
    prev = dict(variables_str).get(name, None)
    if prev: variables_str.remove((name, prev))
    variables_str.append((name, script))
    with open("./variables/variables.json", "w", encoding="utf-8") as f: f.write(json.dumps(variables_str))
    return False
for name, script in variables_str:
    script = evalpy_normalize(script)
    try: res = eval(script, **eval_context())
    except: raise Exception(f"There is a problem with variables! check {script}")
    variables[name] = res
with open("./variables/variables.json", "w", encoding="utf-8") as f: f.write(json.dumps(variables_str))

app = Flask(__name__)

@app.route('/')
def search() -> Response:
    query = request.args.get("q", "").strip()
    if query.endswith("Ё"): query = translit(query[:-1], ru_en)
    if query.endswith("~"): query = translit(query[:-1], en_ru)
    return Search.resolve(query)


@app.route(f"/opensearch.xml")
def opensearch() -> Response: return app.send_static_file("opensearch.xml")
@app.route("/menu")
def menu() -> Response:
    return render_template('menu.html', pages=URLCode.menu_data())


@app.route('/suggest')
def suggest() -> Response:
    Variable.do_updates()
    orig: str = request.args.get("q", "")
    query = orig.strip()
    if query.endswith("Ё"): query = translit(query[:-1], ru_en).strip()
    if query.endswith("~"): query = translit(query[:-1], en_ru).strip()
    data = None
    if query.endswith("==="): data = assign(query[:-3])
    elif query.endswith("=="): data = symppy(query[:-2])
    elif query.endswith("="): data = evalpy(query[:-1])
    else: data = Suggest.resolve(orig)
    return jsonify([orig, data[:page_size()+1]])

def assign(query: str) -> list[str]:
    query = query.strip()
    if "=" not in query[1:]: return ["Assignment structure not recognised!"]
    eq, var = query.split("=")
    eq = f"({eq})"
    var, *dims = var.split()
    if dims: eq = f"physics({eq}, '{' '.join(dims)}')"
    if add_variable(var, eq): return ["Something went wrong!"]
    return ["Variable saved"]

def symppy(query: str) -> list[str]:
    query = evalpy_normalize(query)
    try: res = f"== {parse_expr(query, transformations=standard_transformations + (implicit_multiplication,))}"
    except: res = "not computable"
    return [res]

def evalpy(query: str) -> list[str]:
    query = evalpy_normalize(query)
    try: res = f"= {eval(query, **eval_context())}"
    except: return symppy(query)
    return [res]

if __name__ == '__main__':
    app.run(debug=True)