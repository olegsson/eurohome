from sqlalchemy import create_engine
from sqlalchemy.sql import text
import hashlib, ujson
from flask import make_response

from settings import DB

db = create_engine(
    'sqlite:///{db}'.format(**DB),
    pool_recycle=280,
)

def db_execute(sql, **kwargs):
    sql = text(sql)
    with db.begin() as con:
        query = con.execute(sql, **kwargs)
        try:
            data = query.fetchall()
        except Exception as e:
            print(e)
            return None
    return data

def jsonify(data):
    resp = make_response(
        ujson.dumps(
            (dict(row) for row in data)
        ), '200'
    )
    resp.headers['Content-Type'] = 'application/json'
    return resp

def hash_password(salt, password):
    return hashlib.sha512((salt+password).encode('utf-8')).hexdigest()
