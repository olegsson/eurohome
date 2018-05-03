from utils import db_execute, hash_password, jsonify
from flask import request
import uuid

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
        SELECT country, IFNULL(t.score, 0)
        FROM contenders LEFT JOIN t ON id = contender_id
        ORDER BY t.score DESC, country
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
    'vote': {
        'func': vote,
        'methods': ['POST'],
    },
    'users': {
        'func': users,
        'methods': ['GET'],
    },
    'ladder-global': {
        'func': ladder_global,
        'methods': ['GET'],
    },
    'ladder-user': {
        'func': ladder_user,
        'methods': ['GET'],
    },
}

actions_public = {
    'register': {
        'func': register,
        'methods': ['POST'],
    },
}

def make_handler(public=True):
    actions = actions_public if public else actions_private
    def do_stuff(action):
        kwargs = dict(request.args.items())
        # try:
        if action in actions:
            assert request.method in actions[action]['methods']
            data = actions[action]['func'](**kwargs) or default_response
            print(data)
            return jsonify(data or default_response)
        else:
            abort(404)
        # except Exception as e:
        #     print(e)
        #     abort(403)
    return do_stuff
