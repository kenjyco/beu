import pickle
import ujson
import beu
from redis import ResponseError


class UniqueRedThing(beu.RedKeyMaker):
    def __init__(self, namespace, unique_field, json_fields='', pickle_fields=''):
        """Pass in namespace and the unique field

        - json_fields: string of fields that should be serialized as JSON
        - pickle_fields: string of fields with complex/arbitrary structure

        Separate fields in strings by any of , ; |
        """
        self._unique_field = unique_field
        self._json_fields = beu.string_to_set(json_fields)
        self._pickle_fields = beu.string_to_set(pickle_fields)

        u = set([unique_field])
        invalid = (
            u.intersection(self._json_fields)
            .union(u.intersection(self._pickle_fields))
            .union(self._json_fields.intersection(self._pickle_fields))
        )
        assert invalid == set(), 'field(s) used in too many places: {}'.format(invalid)

        self._base_key = self._make_key(namespace, unique_field)
        self._next_id_string_key = self._make_key(self._base_key, '_next_id')
        self._id_zset_key = self._make_key(self._base_key, '_id')
        self._ts_zset_key = self._make_key(self._base_key, '_ts')

        _parts = [
            '({}, {}'.format(repr(namespace), repr(unique_field)),
            'json_fields={}'.format(repr(json_fields)) if json_fields else '',
            'pickle_fields={}'.format(repr(pickle_fields)) if pickle_fields else '',
        ]
        self._init_args = ''.join([
            self.__class__.__name__,
            ', '.join([p for p in _parts if p is not '']),
            ')'
        ])
        beu.REDIS.hincrby(self.__class__.__name__, self._init_args, 1)

    def __repr__(self):
        return self._init_args

    @property
    def size(self):
        return beu.REDIS.zcard(self._id_zset_key)

    def add(self, **data):
        unique_val = data.get(self._unique_field)
        assert unique_val is not None, (
            '{} field is not in data'.format(repr(self._unique_field))
        )
        score = beu.REDIS.zscore(self._id_zset_key, unique_val)
        assert score is None, (
            '{}={} already exists'.format(self._unique_field, repr(unique_val))
        )

        now = beu.utc_now_float_string()
        key = self._get_next_key(self._next_id_string_key, self._base_key)
        id_num = int(key.split(':')[-1])
        for field in self._json_fields:
            val = data.get(field)
            if val is not None:
                data[field] = ujson.dumps(val)
        for field in self._pickle_fields:
            val = data.get(field)
            if val is not None:
                data[field] = pickle.dumps(val)
        pipe = beu.REDIS.pipeline()
        pipe.zadd(self._id_zset_key, id_num, unique_val)
        pipe.zadd(self._ts_zset_key, now, key)
        pipe.hmset(key, data)
        pipe.execute()
        return key

    def get_hash_id(self, unique_val):
        score = beu.REDIS.zscore(self._id_zset_key, unique_val)
        if score:
            return self._make_key(self._base_key, int(score))

    def get_by_hash_id(self, hash_id, fields='', include_meta=False,
                       timestamp_formatter=beu.identity, ts_fmt=None, ts_tz=None,
                       admin_fmt=False, item_format=''):
        """Wrapper to beu.REDIS.hget/hmget/hgetall

        - fields: string of field names to get separated by any of , ; |
        - include_meta: if True include attributes _id and _ts
        - timestamp_formatter: a callable to apply to the _ts timestamp
        - ts_fmt: strftime format for the returned timestamps (_ts field)
        - ts_tz: a timezone to convert the timestamp to before formatting
        - admin_fmt: if True, use format and timezone defined in settings file
        - item_format: format string for each item (return a string instead of
          a dict)
        """
        fields = beu.string_to_set(fields)
        num_fields = len(fields)
        if timestamp_formatter == beu.identity and include_meta:
            if ts_fmt or ts_tz or admin_fmt:
                timestamp_formatter = beu.get_timestamp_formatter_from_args(
                    ts_fmt=ts_fmt,
                    ts_tz=ts_tz,
                    admin_fmt=admin_fmt
                )
        try:
            if num_fields == 1:
                field = fields.pop()
                data = {field: beu.REDIS.hget(hash_id, field)}
            elif num_fields > 1:
                data = dict(zip(fields, beu.REDIS.hmget(hash_id, *fields)))
            else:
                _data = beu.REDIS.hgetall(hash_id)
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
                val = beu.decode(data[field])
                data[field] = beu.from_string(val) if val is not None else None
        if include_meta:
            data['_id'] = beu.decode(hash_id)
            data['_ts'] = timestamp_formatter(
                beu.REDIS.zscore(self._ts_zset_key, hash_id)
            )
        if item_format:
            return item_format.format(**data)
        return data

    def get_by_value(self, unique_val, fields='', include_meta=False,
                     timestamp_formatter=beu.identity, ts_fmt=None, ts_tz=None,
                     admin_fmt=False, item_format=''):
        """Wrapper to self.get_by_hash_id

        - fields: string of field names to get separated by any of , ; |
        - include_meta: if True include attributes _id and _ts
        - timestamp_formatter: a callable to apply to the _ts timestamp
        - ts_fmt: strftime format for the returned timestamps (_ts field)
        - ts_tz: a timezone to convert the timestamp to before formatting
        - admin_fmt: if True, use format and timezone defined in settings file
        - item_format: format string for each item (return a string instead of
          a dict)
        """
        hash_id = self.get_hash_id(unique_val)
        data = {}
        if hash_id:
            data = self.get_by_hash_id(
                hash_id,
                fields=fields,
                include_meta=include_meta,
                timestamp_formatter=timestamp_formatter,
                ts_fmt=ts_fmt,
                ts_tz=ts_tz,
                admin_fmt=admin_fmt,
                item_format=item_format
            )
        return data


    def recent_ids(self, limit=10, ts_fmt=None, ts_tz=None, admin_fmt=False):
        """Return list of 2-item tuples (hash_id, utc_float/formatted)

        - ts_fmt: strftime format for the returned timestamp
        - ts_tz: a timezone to convert the timestamp to before formatting
        - admin_fmt: if True, use format and timezone defined in settings file
        """
        format_timestamp = beu.get_timestamp_formatter_from_args(
            ts_fmt=ts_fmt,
            ts_tz=ts_tz,
            admin_fmt=admin_fmt
        )
        return [
            (beu.decode(hash_id), format_timestamp(utc_float))
            for hash_id, utc_float in beu.zshow(self._ts_zset_key, end=limit-1)
        ]

    def recent_values(self, limit=10, show_repr=False):
        """Return list of limit most recent unique values

        - show_repr: if True show the object's string representation instead of
          the value of the unique_field
        """
        return [
            beu.decode(val)
            for val in beu.REDIS.zrevrange(self._id_zset_key, start=0, end=limit-1)
        ]
