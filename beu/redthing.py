import pickle
import ujson
import beu
from collections import defaultdict
from functools import partial
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

    @property
    def size(self):
        return beu.REDIS.zcard(self._id_zset_key)

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

    def get(self, hash_key, fields=''):
        """Wrapper to beu.REDIS.hget/hmget/hgetall

        - fields: string of field names to get separated by any of , ; |
        """
        fields = beu.string_to_set(fields)
        num_fields = len(fields)
        try:
            if num_fields == 1:
                field = fields.pop()
                data = {field: beu.REDIS.hget(hash_key, field)}
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
                val = beu.decode(data[field])
                data[field] = beu.from_string(val) if val is not None else None
        return data

    def find(self, terms='', start=0, end=float('inf'), n=20, desc=True,
             get_fields='', all_fields=False, count=False, ts_fmt=None,
             ts_tz=None, admin_fmt=False, since='', until=''):
        """Return a list of dicts that match the search terms

        - terms: string of 'index_field:value' pairs separated by any of , ; |
        - start: utc timestamp float
        - end: utc timestamp float
        - n: max number of results
        - desc: if True, return results in descending order
        - get_fields: string of field names to get for each matching hash_id
          separated by any of , ; |
        - all_fields: if True, return all fields of each matching hash_id
        - count: if True, only return the total number of results
        - ts_fmt: strftime format for the returned timestamps (_ts field)
        - ts_tz: a timezone to convert the timestamp to before formatting
        - admin_fmt: if True, use format and timezone defined in settings file
        - since: a 'num.unit' string (i.e. 15.seconds, 2.weeks, etc)
        - until: a 'num.unit' string (i.e. 15.seconds, 2.weeks, etc)
        """
        base_find_key = self._make_key(self._base_key, '_find')
        next_id_key = self._make_key(base_find_key, '_next_id')
        to_intersect = []
        tmp_keys = []
        d = defaultdict(list)
        get_next_tmp_key = lambda: self._get_next_key(next_id_key, base_find_key)
        terms = beu.string_to_set(terms)
        get_fields = beu.string_to_set(get_fields)
        for term in terms:
            index_field, value = term.split(':')
            d[index_field].append(term)
        for index_field, grouped_terms in d.items():
            if len(grouped_terms) > 1:
                # Compute the union of all index_keys for the same field
                tmp_key = get_next_tmp_key()
                tmp_keys.append(tmp_key)
                beu.REDIS.sunionstore(
                    tmp_key,
                    *[
                        self._make_key(self._base_key, term)
                        for term in grouped_terms
                    ]
                )
                to_intersect.append(tmp_key)
            else:
                to_intersect.append(self._make_key(self._base_key, grouped_terms[0]))

        if to_intersect:
            intersect_key = get_next_tmp_key()
            tmp_keys.append(intersect_key)
            beu.REDIS.sinterstore(intersect_key, *to_intersect)
            last_key = get_next_tmp_key()
            tmp_keys.append(last_key)
            beu.REDIS.zinterstore(last_key, (intersect_key, self._id_zset_key), aggregate='MAX')
            for tmp_key in tmp_keys[:-1]:
                beu.REDIS.delete(tmp_key)
            tmp_keys = [tmp_keys[-1]]
        else:
            last_key = self._id_zset_key

        if since:
            val = beu.utc_ago_float_string(since)
            if val:
                start = float(val)
        if until:
            val = beu.utc_ago_float_string(until)
            if val:
                end = float(val)

        if count:
            if start > 0 or end < float('inf'):
                val = beu.REDIS.zcount(last_key, start, end)
            else:
                val = beu.REDIS.zcard(last_key)
            for tmp_key in tmp_keys:
                beu.REDIS.delete(tmp_key)
            return val

        if desc:
            range_func = partial(beu.REDIS.zrevrangebyscore, last_key, end, start, start=0, num=n)
        else:
            range_func = partial(beu.REDIS.zrangebyscore, last_key, start, end, start=0, num=n)

        if admin_fmt:
            format_timestamp = partial(
                beu.utc_float_to_pretty, fmt=beu.ADMIN_DATE_FMT, timezone=beu.ADMIN_TIMEZONE
            )
        elif ts_tz and ts_fmt:
            format_timestamp = partial(beu.utc_float_to_pretty, fmt=ts_fmt, timezone=ts_tz)
        elif ts_fmt:
            format_timestamp = partial(beu.utc_float_to_pretty, fmt=ts_fmt)
        else:
            format_timestamp = lambda x: x

        i = 0
        results = []
        for hash_id, timestamp in range_func(withscores=True):
            if all_fields:
                d = self.get(hash_id)
            elif get_fields:
                d = self.get(hash_id, ','.join(get_fields))
            else:
                d = {}
            d['_id'] = beu.decode(hash_id)
            d['_ts'] = format_timestamp(timestamp)
            d['_pos'] = i
            results.append(d)
            i += 1

        for tmp_key in tmp_keys:
            beu.REDIS.delete(tmp_key)

        return results

    def delete(self, hash_id, pipe=None):
        """Delete a specific hash_id's data and remove from indexes it is in

        - hash_id: hash_id to remove
        - pipe: if a redis pipeline object is passed in, just add more
          operations to the pipe
        """
        score = beu.REDIS.zscore(self._id_zset_key, hash_id)
        if score is None:
            return
        if pipe is not None:
            execute = False
        else:
            pipe = beu.REDIS.pipeline()
            execute = True

        indexed_data = self.get(hash_id, ','.join(self._index_base_keys.keys()))
        pipe.delete(hash_id)
        for k, v in indexed_data.items():
            old_index_key = self._make_key(self._base_key, k, v)
            pipe.srem(old_index_key, hash_id)
            pipe.zincrby(self._index_base_keys[k], v, -1)

        if execute:
            pipe.zrem(self._id_zset_key, hash_id)
            return pipe.execute()

    def delete_to(self, score):
        """Delete all items with a score (timestamp) between 0 and score"""
        pipe = beu.REDIS.pipeline()
        for hash_id in beu.REDIS.zrangebyscore(self._id_zset_key, 0, score):
            self.delete(hash_id, pipe)
        pipe.zremrangebyscore(self._id_zset_key, 0, score)
        return pipe.execute()[-1]

    def update(self, hash_id, **data):
        """Update data at a particular hash_id"""
        score = beu.REDIS.zscore(self._id_zset_key, hash_id)
        if score is None or data == {}:
            return
        now = beu.utc_now_float_string()
        pipe = beu.REDIS.pipeline()
        indexed_data = self.get(hash_id, ','.join(self._index_base_keys.keys()))
        for k, v in indexed_data.items():
            if k in data and data[k] != v:
                old_index_key = self._make_key(self._base_key, k, v)
                index_key = self._make_key(self._base_key, k, data[k])
                pipe.srem(old_index_key, hash_id)
                pipe.zincrby(self._index_base_keys[k], v, -1)
                pipe.sadd(index_key, hash_id)
                pipe.zincrby(self._index_base_keys[k], data[k], 1)
        pipe.hmset(hash_id, data)
        pipe.zadd(self._id_zset_key, now, hash_id)
        pipe.execute()
        return hash_id

    def show_keyspace(self):
        if self.size <= 500:
            return sorted([
                (beu.decode(key), beu.decode(beu.REDIS.type(key)))
                for key in beu.REDIS.scan_iter('{}*'.format(self._base_key))
            ])
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
