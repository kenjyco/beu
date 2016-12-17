import gzip
import pickle
import ujson
import beu


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
            attr: self._make_key(self._base_key, attr)
            for attr in index_fields
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
        for field in self._json_fields:
            val = data.get(field)
            if val is not None:
                data[field] = gzip.compress(bytes(ujson.dumps(val), 'utf-8'))
        for field in self._pickle_fields:
            val = data.get(field)
            if val is not None:
                data[field] = gzip.compress(pickle.dumps(val))
        pipe = beu.REDIS.pipeline()
        pipe.zadd(self._make_key(self._base_key, 'id'), now, key)
        pipe.hmset(key, data)
        for attr, base in self._index_base_keys.items():
            key_name = self._make_key(base, data.get(attr, ''))
            pipe.zadd(key_name, now, key)
            pipe.zincrby(base, str(data.get(attr, '')), 1)
        pipe.execute()
        return key

    def show_keyspace(self):
        return [
            (key, beu.REDIS.type(key))
            for key in beu.REDIS.scan_iter('{}*'.format(self._base_key))
        ]

    def index_field_info(self, index_field, n=25):
        """Return a list of redis keys and counts for top values of index_field"""
        results = []
        base_key = self._index_base_keys.get(index_field)
        if base_key:
            results = [
                (self._make_key(base_key, beu.decode(name)), count)
                for name, count in beu.zshow(base_key, end=n-1)
            ]
        return results

    def newest_top_indexed(self, index_field, n=25, recent_count=5):
        """Return a list of dicts with info about the top... """
        return [
            {
                'count': count,
                'index': index,
                'newest': beu.zshow(index, end=recent_count-1)
            }
            for index, count in self.index_field_info(index_field, n)
        ]
