from flask import Flask, render_template, send_from_directory, request, Response, redirect, abort
from jinja2.exceptions import TemplateNotFound
from datetime import datetime
from os import path
from glob import iglob

try:
    import ujson
except ImportError:
    import json as ujson # for running on termux

from settings import DIR
from utils import requires_auth, check_auth, jsonify
from api import make_handler, ladder_user

app = Flask(
    __name__,
    static_url_path=path.join(DIR, 'static')
)

@app.route('/api/public/<action>', methods=['GET', 'POST'])
def handler_public(action):
    return make_handler()(action)

@app.route('/api/<action>', methods=['GET', 'POST'])
@requires_auth
def handler_private(action):
    return make_handler(public=False)(action)

@app.route('/static/<path:filepath>')
def send_static(filepath):
    return send_from_directory('static', filepath)

@app.route('/')
def index():
    name = check_auth(request)
    votes = dict(ladder_user(name)) if name else {}
    return render_template(
        'index.html',
        name=name,
        votes=votes,
    )

@app.route('/<page>')
def viewpage(page):
    try:
        return render_template(page+'.html')
    except TemplateNotFound:
        abort(404)

if __name__ == '__main__':
    app.run('0.0.0.0')
