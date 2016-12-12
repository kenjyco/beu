import beu


class RedThing(object):
    def __init__(self, namespace, name, *attrs):
        """Pass in namespace, name, and attributes to index on"""
        self._base_key = self._make_key(namespace, name)
        self._index_keys = {
            attr: self._make_key(self._base_key, attr)
            for attr in attrs
        }

    def _make_key(self, *parts):
        return ':'.join([str(part) for part in parts])

    def _get_next_key(self):
        pipe = beu.REDIS.pipeline()
        key = self._make_key(self._base_key, 'next_id')
        pipe.setnx(key, 1)
        pipe.get(key)
        pipe.incr(key)
        result = pipe.execute()
        return self._make_key(self._base_key, int(result[1]))

    def add(self, **data):
        key = self._get_next_key()
        now = beu.utc_now_float_string()
        pipe = beu.REDIS.pipeline()
        pipe.zadd(self._make_key(self._base_key, 'id'), now, key)
        pipe.hmset(key, data)
        for attr, base in self._index_keys.items():
            key_name = self._make_key(base, data.get(attr, ''))
            pipe.zadd(key_name, now, key)
            pipe.zincrby(base, str(data.get(attr, '')), 1)
        result = pipe.execute()
        return key
