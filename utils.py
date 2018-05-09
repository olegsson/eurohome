from sqlalchemy import create_engine
from sqlalchemy.sql import text
import hashlib, ujson
from flask import make_response, request, Response, abort
from functools import wraps

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
    resp = make_response(ujson.dumps(resdata), '200')
    resp.headers['Content-Type'] = 'application/json'
    return resp

def hash_password(salt, password):
    return hashlib.sha512((salt+password).encode('utf-8')).hexdigest()

def check_auth(request):
    auth = request.authorization
    if not auth:
        return False
    try:
        salt, hash = db_execute('''
            SELECT salt, hash
            FROM users
            WHERE name = :name
        ''', name=auth.username)[0]
    except IndexError as e:
        return False
    return hash == hash_password(salt, auth.password)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if check_auth(request):
            return f(*args, **kwargs)
        return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        )
    return decorated
