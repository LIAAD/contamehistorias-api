from rejson import Client, Path
from redis import ConnectionError

rj = Client(host='localhost', port=6379, decode_responses=True)
jp = rj.pipeline()

def is_connected():
    try:
        rj.ping()
        return True
    except ConnectionError:
        return False

def set_result(key, data):
    rj.jsonset(key, Path.rootPath(), data)

def get_result(key):
    return rj.jsonget(key, no_escape=True)

def delete_result(key):
    rj.jsondel(key, Path.rootPath())

def delete_cache():
    jp.flushall()
    jp.execute()
