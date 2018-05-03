from flask import Flask, render_template, abort, send_from_directory, request, Response
from datetime import datetime
from os import path

from settings import DIR
from utils import requires_auth
from api import make_handler

app = Flask(
    __name__,
    static_url_path=path.join(DIR, 'static')
)

default_response = [{
    'message': 'OK'
}]

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
@requires_auth
def index():
    return render_template(
        'index.html',
    )

if __name__ == '__main__':
    app.run()
