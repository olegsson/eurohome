from sqlalchemy import create_engine
from sqlalchemy.sql import text
import hashlib
from flask import make_response, request, Response, abort
from functools import wraps

try:
    import ujson
except ImportError:
    import json as ujson # for running on termux

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
            # print(e)
            return None
    return data

default_response = [{'message': 'OK'}]

def jsonify(data):
    try:
        resdata = (dict(row) for row in data)
    except TypeError:
        resdata = data
    try:
        resdata = ujson.dumps(resdata)
    except TypeError:
        resdata = ujson.dumps(list(resdata))
    resp = make_response(resdata, '200')
    resp.headers['Content-Type'] = 'application/json'
    return resp

def salt_hash(salt, string):
    return hashlib.sha512((salt+string).encode('utf-8')).hexdigest()

def check_auth(request):
    token = request.cookies.get('token')
    if token is not None:
        try:
            name = db_execute('''
                SELECT name
                FROM users
                WHERE session = :token
            ''', token=token)[0][0]
            request.name = name
            return name
        except IndexError as e:
            pass
    return False

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if check_auth(request):
            return f(*args, **kwargs)
        abort(401)
    return decorated
