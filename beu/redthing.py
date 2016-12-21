import pickle
import ujson
import beu
from redis import ResponseError


class RedThing(object):
    """

    Possible uses:

    - store events and meta-data with ability to query on indexed attributes
    """
    def __init__(self, namespace, name, index_fields=[], json_fields=[],
                 pickle_fields=[]):
        """Pass in namespace, name, and list of fields to index on

        - index_fields: list of fields that should be indexed
        - json_fields: list of fields that should be serialized as JSON
        - pickle_fields: list of fields with complex/arbitrary structure
        """
        index_fields = set(index_fields)
        self._json_fields = set(json_fields)
        self._pickle_fields = set(pickle_fields)

        invalid = (
            index_fields.intersection(self._json_fields)
            .union(index_fields.intersection(self._pickle_fields))
            .union(self._json_fields.intersection(self._pickle_fields))
        )
        if invalid != set():
            msg = 'The following field(s) used in too many places: {}'
            raise Exception(msg.format(invalid))

        self._base_key = self._make_key(namespace, name)
        self._index_base_keys = {
            index_field: self._make_key(self._base_key, index_field)
            for index_field in index_fields
        }
        self._next_id_string_key = self._make_key(self._base_key, '_next_id')
        self._id_zset_key = self._make_key(self._base_key, '_id')

    def _make_key(self, *parts):
        return ':'.join([str(part) for part in parts])

    def _get_next_key(self, next_id_string_key=None, base_key=None):
        if next_id_string_key is None:
            next_id_string_key = self._next_id_string_key
            base_key = self._base_key
        if base_key is None:
            base_key = ':'.join(next_id_string_key.split(':')[:-1])
        pipe = beu.REDIS.pipeline()
        pipe.setnx(next_id_string_key, 1)
        pipe.get(next_id_string_key)
        pipe.incr(next_id_string_key)
        result = pipe.execute()
        return self._make_key(base_key, int(result[1]))

    def size(self):
        return beu.REDIS.zcard(self._id_zset_key)

    def recent_keys(self, n=5):
        return beu.zshow(self._id_zset_key, end=n)

    def add(self, **data):
        key = self._get_next_key()
        now = beu.utc_now_float_string()
        for field in self._json_fields:
            val = data.get(field)
            if val is not None:
                data[field] = ujson.dumps(val)
        for field in self._pickle_fields:
            val = data.get(field)
            if val is not None:
                data[field] = pickle.dumps(val)
        pipe = beu.REDIS.pipeline()
        pipe.zadd(self._id_zset_key, now, key)
        pipe.hmset(key, data)
        for index_field, base_key in self._index_base_keys.items():
            key_name = self._make_key(base_key, data.get(index_field, ''))
            pipe.sadd(key_name, key)
            pipe.zincrby(base_key, str(data.get(index_field, '')), 1)
        pipe.execute()
        return key

    def get(self, hash_key, *fields):
        """Wrapper to beu.REDIS.hget/hmget/hgetall"""
        num_fields = len(fields)
        try:
            if num_fields == 1:
                data = {fields[0]: beu.REDIS.hget(hash_key, fields[0])}
            elif num_fields > 1:
                data = dict(zip(fields, beu.REDIS.hmget(hash_key, *fields)))
            else:
                _data = beu.REDIS.hgetall(hash_key)
                data = {
                    beu.decode(k): v
                    for k, v in _data.items()
                }
        except ResponseError:
            data = {}

        for field in data.keys():
            if field in self._json_fields:
                data[field] = ujson.loads(data[field])
            elif field in self._pickle_fields:
                data[field] = pickle.loads(data[field])
            else:
                data[field] = beu.from_string(beu.decode(data[field]))
        return data

    def show_keyspace(self):
        if self.size() <= 50:
            return [
                (beu.decode(key), beu.decode(beu.REDIS.type(key)))
                for key in beu.REDIS.scan_iter('{}*'.format(self._base_key))
            ]
        else:
            print('Keyspace is too large')

    def clear_keyspace(self):
        for key in beu.REDIS.scan_iter('{}*'.format(self._base_key)):
            beu.REDIS.delete(key)

    def index_field_info(self, n=10):
        """Return list of 2-item tuples (index_field:value, count)

        - n: include top n per index type
        """
        results = []
        for index_field, base_key in sorted(self._index_base_keys.items()):
            results.extend([
                (':'.join([index_field, beu.decode(name)]), int(count))
                for name, count in beu.zshow(base_key, end=n-1)
            ])
        return results
