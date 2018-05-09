from flask import abort, request, redirect, Response
from werkzeug import wrappers
import uuid

from utils import db_execute, hash_password, jsonify, default_response, check_auth

def register(name, password):
    salt = uuid.uuid4().hex
    hash = hash_password(salt, password)
    db_execute("""
        INSERT INTO users (name, salt, hash)
        VALUES (:name, :salt, :hash)
    """, name=name, salt=salt, hash=hash)

def vote(country, magnitude):
    name = request.authorization.username
    magnitude = int(magnitude)
    assert 0 < magnitude <= 10
    db_execute("""
        INSERT OR REPLACE INTO votes(user_id, contender_id, magnitude)
        VALUES (
            (SELECT id FROM users WHERE name = :name),
            (SELECT id FROM contenders WHERE country = :country),
            :magnitude
        )
    """, name=name, country=country.lower(), magnitude=magnitude)

def ladder_global():
    return db_execute("""
        WITH t AS (
            SELECT contender_id, SUM(magnitude) AS score FROM votes
            GROUP BY contender_id
        )
        SELECT country, IFNULL(t.score, 0) AS score
        FROM contenders LEFT JOIN t ON id = contender_id
        ORDER BY score DESC, country
    """)

def ladder_user(name=None):
    name = name or request.authorization.username
    return db_execute("""
        WITH t AS (
            SELECT contender_id, SUM(magnitude) AS score
            FROM votes
            WHERE user_id = (SELECT id FROM users WHERE name = :name)
            GROUP BY contender_id
        )
        SELECT country, IFNULL(t.score, 0)
        FROM contenders LEFT JOIN t ON id = contender_id
        ORDER BY t.score DESC, country
    """, name=name)

def users():
    return db_execute("""
        SELECT name FROM users
        ORDER BY name
    """)

actions_private = {
    'login': {
        'func': lambda: Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        ),
        'methods': ['GET', 'POST'],
    },
    'vote': {
        'func': vote,
        'methods': ['GET', 'POST'],
    },
    'users': {
        'func': users,
        'methods': ['GET'],
    },
    'ladder-user': {
        'func': ladder_user,
        'methods': ['GET'],
    },
}

actions_public = {
    'ladder-global': {
        'func': ladder_global,
        'methods': ['GET'],
    },
    'register': {
        'func': register,
        'methods': ['GET', 'POST'],
    },
    'logged_in': {
        'func': lambda: check_auth(request),
        'methods': ['GET', 'POST'],
    }
}

def make_handler(public=True):
    actions = actions_public if public else actions_private
    def do_stuff(action):
        kwargs = dict(request.args.items())
        # try:
        if action in actions:
            assert request.method in actions[action]['methods']
            data = actions[action]['func'](**kwargs) or default_response
            if isinstance(data, wrappers.Response):
                return data
            return jsonify(data)
        else:
            abort(404)
        # except Exception as e:
        #     print(e)
        #     abort(403)
    return do_stuff
