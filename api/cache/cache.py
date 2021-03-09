from rejson import Client, Path
import redis

rj = Client(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def is_connected():
    try:
        rj.ping()
        return True
    except redis.ConnectionError:
        return False

def set_result(key, data):
    rj.jsonset(key, Path.rootPath(), data)

def get_result(key):
    return rj.jsonget(key, no_escape=True)

def delete_result(key):
    rj.jsondel(key, Path.rootPath())

def get_keys_by_match(match='*'):
    return r.scan_iter(match=match)

def delete_keys_by_match(match='*'):
    keys = list(get_keys_by_match(match))
    for k in keys:
        r.delete(k)

def delete_cache():
    return r.flushall()
