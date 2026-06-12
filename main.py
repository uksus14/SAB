from flask import Flask, request, jsonify, render_template, redirect
from flask.typing import ResponseReturnValue
from scripts.suggest.eval import cool_eval
from scripts.search.menu import URLCode
from scripts.utils import prep_query
from scripts.suggest import Suggest
from commons import PORT, BASE_URL
from scripts.search import Search
from variables import Variable

app = Flask(__name__)

from scripts.testing import Tester
@app.route("/test")
def test() -> ResponseReturnValue:
    verbose = not (request.args.get("verbose", "").lower().strip() in ["false", "0", "no"])
    if not verbose:
        Tester.test_all(verbose=False)
        return render_template("message.html", message="Tests done successfully!")
    log = Tester.test_all(verbose=True)
    return render_template("test.html", testers=log, success=all(line["success"] for line in log))

@app.route('/')
def search() -> ResponseReturnValue:
    query = request.args.get("q", None)
    if query is None: return redirect('/menu')
    res = Search.resolve(prep_query(query))
    if res is None: return render_template("message.html", message="Failed to receive an answer")
    return res
@app.route('/suggest')
def suggest() -> ResponseReturnValue:
    Variable.do_updates()
    orig: str = request.args.get("q", "")
    return jsonify([orig, Suggest.resolve(prep_query(orig))])

@app.route("/opensearch.xml")
def opensearch(): return app.send_static_file("opensearch.xml")
@app.route("/menu")
def menu(): return render_template('menu.html', pages=URLCode.menu_data())
@app.route("/change-port/<int:port>")
def change_port(port: int): return redirect(f"{BASE_URL.rpartition(':')[0]}:{port}/", 301)
clipboard = None
@app.route("/api/vscode", methods=['GET', 'POST'])
def vscode():
    global clipboard
    if request.method == 'POST':
        clipboard = request.data.decode()
        return jsonify({"status": "201", "result": Suggest.resolve(clipboard)})
    else:
        return redirect(f"{request.host_url}?q={clipboard}")
@app.route("/api/eval", methods=['POST'])
def pyeval():
    query = request.data.decode().strip('=')+'='
    return jsonify({"status": "201", "result": str(cool_eval(query)).strip('= ')})

if __name__ == '__main__':
    app.run(debug=False, port=PORT)