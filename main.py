from flask import Flask, request, jsonify, render_template
from scripts.search.menu import URLCode
from scripts.utils import prep_query
from scripts.suggest import Suggest
from scripts.search import Search
from variables import Variable 

app = Flask(__name__)

from scripts.testing import Tester
@app.route("/test")
def test():
    verbose = not (request.args.get("verbose", "").lower().strip() in ["false", "0", "no"])
    log = Tester.test_all(verbose=verbose)
    if not verbose: return render_template("message.html", message="Tests done successfully!")
    return render_template("test.html", testers=log, success=all(line["success"] for line in log))

@app.route('/')
def search():
    return Search.resolve(prep_query(request.args.get("q", "")))
@app.route('/suggest')
def suggest():
    Variable.do_updates()
    orig: str = request.args.get("q", "")
    return jsonify([orig, Suggest.resolve(prep_query(orig))])

@app.route("/opensearch.xml")
def opensearch(): return app.send_static_file("opensearch.xml")
@app.route("/menu")
def menu(): return render_template('menu.html', pages=URLCode.menu_data())

if __name__ == '__main__':
    app.run(debug=False)