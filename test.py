from api import *

try:
    register('luka', 'asdf')
    register('hana', 'asdf')
except:
    pass

vote('luka', 'croatia', 1)
vote('luka', 'serbia', 10)
vote('luka', 'ALBANIA', 3)
vote('hana', 'croatia', 1)
vote('hana', 'serbia', 10)
vote('hana', 'uNITED Kingdom', 7)

ladder_global()
ladder_user('hana')
