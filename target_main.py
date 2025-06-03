from scripts.utils import page_size, translit, en_ru, ru_en
from flask import Flask, request, jsonify, render_template, Response
from scripts.search.menu import URLCode
from scripts.suggest import Suggest
from scripts.actions import Action
from scripts.search import Search
from commons import BASE_FOLDER
from variables import Variable
from datetime import datetime
import openai

try: openai.api_key = (BASE_FOLDER / "openai_key.txt").read_text().strip()
except FileNotFoundError:
    print("OpenAI key file not found")
    Action.disable["llmask"] = "OpenAI key not found"


history = Variable[list[dict[str, str|datetime]]].create("history", [])

app = Flask(__name__)

@app.route('/')
def search() -> Response:
    global history
    query = request.args.get("q", "").strip()
    if query.endswith("Ё"): query = translit(query[:-1], ru_en)
    if query.endswith("~"): query = translit(query[:-1], en_ru)
    if query.endswith(" !h") or query == "!h":
        return render_template("history.html", history=match_history(query[:-3]), query=query[:-3], isquery=len(query)>3)
    history.data += [{"query": query, "time": datetime.now()}]
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
    data = Suggest.resolve(orig)
    data = data[:page_size()+1]
    return jsonify([orig, data])

if __name__ == '__main__':
    app.run(debug=True)