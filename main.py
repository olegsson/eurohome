from flask import Flask, render_template, abort, send_from_directory, request
from datetime import datetime
from os import path

from settings import DIR
from utils import db_execute, jsonify
from api import actions

app = Flask(
    __name__,
    static_url_path=path.join(DIR, 'static')
)

default_response = {
    'message': 'OK'
}

@app.route('/api/<action>', methods=['GET', 'POST'])
def do_stuff(action):
    kwargs = dict(request.args.items())
    try:
        if action in actions:
            assert request.method in actions[action]['methods']
            return jsonify(
                actions[action]['func'](**kwargs) or default_response
            )
        else:
            abort(404)
    except Exception as e:
        print(e)
        abort(403)

@app.route('/static/<path:filepath>')
def send_static(filepath):
    return send_from_directory('static', filepath)

@app.route('/')
def index():
    return render_template(
        'index.html',
        VERSION=VERSION
    )

if __name__ == '__main__':
    app.run()
