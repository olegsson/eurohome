from flask import abort, request, redirect, Response
from werkzeug import wrappers
import uuid

from utils import db_execute, salt_hash, jsonify, default_response, check_auth

def vote(country, magnitude):
    name = request.name
    magnitude = int(magnitude)
    assert 0 < magnitude <= 12 and magnitude != 11
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
        SELECT country, IFNULL(t.score, 0) AS score
        FROM contenders LEFT JOIN t ON id = contender_id
        ORDER BY t.score DESC, country
    """, name=name)

def users():
    return db_execute("""
        SELECT name FROM users
        ORDER BY name
    """)

def login(name, password):
    resp = redirect('/')
    try:
        salt, hash = db_execute('''
            SELECT salt, hash
            FROM users
            WHERE name = :name
        ''', name=name)[0]
        if hash == salt_hash(salt, password):
            token = salt_hash(uuid.uuid4().hex, name)
            db_execute('''
                UPDATE users
                SET session = :token
                WHERE name = :name
            ''', token=token, name=name)
            resp.set_cookie('token', token)
            return resp
    except IndexError as e:
        pass
    resp.set_cookie('token', '', expires=0)
    return resp

def register(name, password):
    if '' in (name, password):
        return redirect('/')
    salt = uuid.uuid4().hex
    hash = salt_hash(salt, password)
    db_execute("""
        INSERT INTO users (name, salt, hash)
        VALUES (:name, :salt, :hash)
    """, name=name, salt=salt, hash=hash)
    return login(name, password)

def logout():
    token = request.cookies.get('token')
    if token is not None:
        db_execute('''
            UPDATE users
            SET session = NULL
            WHERE session = :token
        ''', token=token)
    resp = redirect('/')
    resp.set_cookie('token', '', expires=0)
    return resp

actions_private = {
    'logout': {
        'func': logout,
        'methods': ['GET'],
    },
    'vote': {
        'func': vote,
        'methods': ['POST'],
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
        'methods': ['POST'],
    },
    'login': {
        'func': login,
        'methods': ['POST'],
    },
}

def make_handler(public=True):
    actions = actions_public if public else actions_private
    def do_stuff(action):
        kwargs = dict(request.args.items()) or dict(request.form.items())
        try:
            if action in actions:
                assert request.method in actions[action]['methods']
                data = actions[action]['func'](**kwargs) or default_response
                if isinstance(data, wrappers.Response):
                    return data
                return jsonify(data)
            else:
                abort(404)
        except Exception as e:
            print(e)
            abort(403)
    return do_stuff
