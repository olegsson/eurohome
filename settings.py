from os import path
from urllib.parse import quote as urlquote

DIR = path.dirname(path.realpath(__file__))

DB = {
    'db': urlquote(path.join(DIR, 'eurohome.db')),
}

VERSION = '0.0.1'
