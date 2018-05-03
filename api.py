from utils import db_execute, hash_password, jsonify
import uuid

def adduser(name, password):
    salt = uuid.uuid4().hex
    hash = hash_password(salt, password)
    db_execute("""
        INSERT INTO users (name, salt, hash)
        VALUES (:name, :salt, :hash)
    """, name=name.lower(), salt=salt, hash=hash)

def vote(name, country, magnitude):
    # print(name, country, magnitude)
    magnitude = int(magnitude)
    assert 0 < magnitude <= 10
    db_execute("""
        INSERT OR REPLACE INTO votes(user_id, contender_id, magnitude)
        VALUES (
            (SELECT id FROM users WHERE name = :name),
            (SELECT id FROM contenders WHERE country = :country),
            :magnitude
        )
    """, name=name.lower(), country=country.lower(), magnitude=magnitude)

def ladder_global():
    return db_execute("""
        WITH t AS (
            SELECT contender_id, sum(magnitude) AS score FROM votes
            GROUP BY contender_id
        )
        SELECT country, t.score
        FROM contenders LEFT JOIN t ON id = contender_id
        ORDER BY t.score DESC, country
    """)

def ladder_user(name):
    return db_execute("""
        WITH t AS (
            SELECT contender_id, sum(magnitude) AS score
            FROM votes
            WHERE user_id = (SELECT id FROM users where name = :name)
            GROUP BY contender_id
        )
        SELECT country, t.score
        FROM contenders LEFT JOIN t ON id = contender_id
        ORDER BY t.score DESC, country
    """, name=name)

actions = {
    'vote': {
        'func': vote,
        'methods': ['POST'],
    },
    'adduser': {
        'func': vote,
        'methods': ['POST'],
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
