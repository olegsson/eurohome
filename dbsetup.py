import uuid, hashlib

try:
    import ujson
except ImportError:
    import json as ujson # for running on termux

from utils import db_execute

try:
    db_execute('DROP TABLE users')
except:
    pass
try:
    db_execute('DROP TABLE contenders')
except:
    pass
try:
    db_execute('DROP TABLE votes')
except:
    pass
db_execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name text UNIQUE NOT NULL,
        salt text NOT NULL,
        hash text NOT NULL,
        session text DEFAULT NULL
    )
''')
db_execute('''
    CREATE TABLE contenders (
        id INTEGER PRIMARY KEY,
        country text UNIQUE NOT NULL,
        active boolean NOT NULL
    )
''')
db_execute('''
    CREATE TABLE votes (
        id INTEGER PRIMARY KEY,
        user_id int NOT NULL,
        contender_id int NOT NULL,
        magnitude int NOT NULL,
        FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE,
        FOREIGN KEY (contender_id)
            REFERENCES contenders(id)
            ON DELETE CASCADE,
        UNIQUE(user_id, contender_id)
    )
''')

with open('contenders.json', 'r') as f:
    sqlvalues = ','.join(map(
        lambda x: '("%s",1)'%x.lower(),
        ujson.load(f)
        )
    )
db_execute('''
    INSERT INTO contenders (country, active)
    VALUES %s
'''%sqlvalues)
