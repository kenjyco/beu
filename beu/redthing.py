import pickle
import ujson
import beu
from collections import defaultdict
from functools import partial
from redis import ResponseError


class RedThing(object):
    """

    Possible uses:

    - store events/logs and meta-data with ability to query on indexed attributes
    """
    def __init__(self, namespace, name, unique_field='', index_fields='',
                 json_fields='', pickle_fields=''):
        """Pass in namespace and name

        - unique_field: name of the optional unique field
        - index_fields: string of fields that should be indexed
        - json_fields: string of fields that should be serialized as JSON
        - pickle_fields: string of fields with complex/arbitrary structure

        Separate fields in strings by any of , ; |
        """
        self._unique_field = unique_field
        index_fields_set = beu.string_to_set(index_fields)
        self._json_fields = beu.string_to_set(json_fields)
        self._pickle_fields = beu.string_to_set(pickle_fields)

        u = set([unique_field])
        invalid = (
            index_fields_set.intersection(self._json_fields)
            .union(index_fields_set.intersection(self._pickle_fields))
            .union(index_fields_set.intersection(u))
            .union(self._json_fields.intersection(self._pickle_fields))
            .union(self._json_fields.intersection(u))
            .union(self._pickle_fields.intersection(u))
        )
        assert invalid == set(), 'field(s) used in too many places: {}'.format(invalid)

        self._base_key = self._make_key(namespace, name)
        self._index_base_keys = {
            index_field: self._make_key(self._base_key, index_field)
            for index_field in index_fields_set
        }
        self._next_id_string_key = self._make_key(self._base_key, '_next_id')
        self._ts_zset_key = self._make_key(self._base_key, '_ts')
        self._id_zset_key = self._make_key(self._base_key, '_id')
        self._find_base_key = self._make_key(self._base_key, '_find')
        self._find_next_id_string_key = self._make_key(self._find_base_key, '_next_id')
        self._find_stats_hash_key = self._make_key(self._find_base_key, '_stats')
        self._find_searches_zset_key = self._make_key(self._find_base_key, '_searches')

        _parts = [
            '({}, {}'.format(repr(namespace), repr(name)),
            'unique_field={}'.format(repr(unique_field)) if unique_field else '',
            'index_fields={}'.format(repr(index_fields)) if index_fields else '',
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

    def _make_key(self, *parts):
        """Join the string parts together, separated by colon(:)"""
        return ':'.join([str(part) for part in parts])

    def _get_next_key(self, next_id_string_key, base_key=None):
        """Get the next key to use and increment next_id_string_key"""
        if base_key is None:
            base_key = ':'.join(next_id_string_key.split(':')[:-1])
        pipe = beu.REDIS.pipeline()
        pipe.setnx(next_id_string_key, 1)
        pipe.get(next_id_string_key)
        pipe.incr(next_id_string_key)
        result = pipe.execute()
        return self._make_key(base_key, int(result[1]))

    def _get_next_find_key(self):
        return self._get_next_key(self._find_next_id_string_key, self._find_base_key)

    def add(self, **data):
        """Add all fields and values in data to the collection

        If self._unique_field is a non-empty string, that field must be provided
        in the data and there must not be an item in the collection with the
        same value for that field
        """
        if self._unique_field:
            unique_val = data.get(self._unique_field)
            assert unique_val is not None, (
                'unique field {} is not in data'.format(repr(self._unique_field))
            )
            score = beu.REDIS.zscore(self._id_zset_key, unique_val)
            assert score is None, (
                '{}={} already exists'.format(self._unique_field, repr(unique_val))
            )

        now = self.now_utc_float
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
        if self._unique_field:
            pipe.zadd(self._id_zset_key, id_num, unique_val)
        pipe.zadd(self._ts_zset_key, now, key)
        pipe.hmset(key, data)
        for index_field, base_key in self._index_base_keys.items():
            key_name = self._make_key(base_key, data.get(index_field))
            pipe.sadd(key_name, key)
            pipe.zincrby(base_key, str(data.get(index_field)), 1)
        pipe.execute()
        return key

    def get(self, hash_id, fields='', include_meta=False,
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

    def get_hash_id_for_unique_value(self, unique_val):
        """Return the hash_id of the object that has unique_val in _unique_field"""
        if self._unique_field:
            score = beu.REDIS.zscore(self._id_zset_key, unique_val)
            if score:
                return self._make_key(self._base_key, int(score))

    def get_by_unique_value(self, unique_val, fields='', include_meta=False,
                            timestamp_formatter=beu.identity, ts_fmt=None,
                            ts_tz=None, admin_fmt=False, item_format=''):
        """Wrapper to self.get

        - fields: string of field names to get separated by any of , ; |
        - include_meta: if True include attributes _id and _ts
        - timestamp_formatter: a callable to apply to the _ts timestamp
        - ts_fmt: strftime format for the returned timestamps (_ts field)
        - ts_tz: a timezone to convert the timestamp to before formatting
        - admin_fmt: if True, use format and timezone defined in settings file
        - item_format: format string for each item (return a string instead of
          a dict)
        """
        hash_id = self.get_hash_id_for_unique_value(unique_val)
        data = {}
        if hash_id:
            data = self.get(
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

    def get_by_position(self, pos):
        data = {}
        x = beu.REDIS.zrange(self._ts_zset_key, pos, pos, withscores=True)
        if x:
            hash_id, ts = x[0]
            data = self.get(hash_id)
            data['_id'] = beu.decode(hash_id)
            data['_ts_raw'] = ts
            data['_ts_admin'] = beu.utc_float_to_pretty(
                ts,
                fmt=beu.ADMIN_DATE_FMT,
                timezone=beu.ADMIN_TIMEZONE
            )
        return data

    @property
    def last(self):
        """Return the last item in the collection"""
        return self.get_by_position(-1)

    @property
    def first(self):
        """Return the first item in the collection"""
        return self.get_by_position(0)

    @property
    def size(self):
        """Return cardinality of self._ts_zset_key (number of items in the zset)"""
        return beu.REDIS.zcard(self._ts_zset_key)

    @property
    def now_pretty(self):
        return beu.utc_float_to_pretty()

    @property
    def now_utc_float(self):
        return float(beu.utc_now_float_string())

    @property
    def keyspace(self):
        """Show the Redis keyspace for self._base_key

        If collection size is over 500 items, a message will be returned instead
        """
        if self.size <= 500:
            return sorted([
                (beu.decode(key), beu.decode(beu.REDIS.type(key)))
                for key in beu.REDIS.scan_iter('{}*'.format(self._base_key))
            ])
        else:
            return 'Keyspace is too large'

    def clear_keyspace(self):
        """Delete all Redis keys under self._base_key"""
        for key in beu.REDIS.scan_iter('{}*'.format(self._base_key)):
            beu.REDIS.delete(key)

    def delete(self, hash_id, pipe=None):
        """Delete a specific hash_id's data and remove from indexes it is in

        - hash_id: hash_id to remove
        - pipe: if a redis pipeline object is passed in, just add more
          operations to the pipe
        """
        assert hash_id.startswith(self._base_key), (
            '{} does not start with {}'.format(repr(hash_id), repr(self._base_key))
        )
        score = beu.REDIS.zscore(self._ts_zset_key, hash_id)
        if score is None:
            return
        if pipe is not None:
            execute = False
        else:
            pipe = beu.REDIS.pipeline()
            execute = True

        pipe.delete(hash_id)
        index_fields = ','.join(self._index_base_keys.keys())
        if index_fields:
            for k, v in self.get(hash_id, index_fields).items():
                old_index_key = self._make_key(self._base_key, k, v)
                pipe.srem(old_index_key, hash_id)
                pipe.zincrby(self._index_base_keys[k], v, -1)
        if self._unique_field:
            unique_val = self.get(hash_id, self._unique_field)[self._unique_field]
            pipe.zrem(self._id_zset_key, unique_val)

        if execute:
            pipe.zrem(self._ts_zset_key, hash_id)
            return pipe.execute()

    def delete_to(self, score=None, ts='', tz=None):
        """Delete all items with a score (timestamp) between 0 and score

        - score: a utc_float
        - ts: a timestamp with form between YYYY and YYYY-MM-DD HH:MM:SS.f
          (in the timezone specified in tz or ADMIN_TIMEZONE)
        - tz: a timezone
        """
        if ts:
            tz = tz or beu.ADMIN_TIMEZONE
            score = float(beu.date_string_to_utc_float_string(ts, tz))
        if score is None:
            return
        pipe = beu.REDIS.pipeline()
        for hash_id in beu.REDIS.zrangebyscore(self._ts_zset_key, 0, score):
            self.delete(hash_id, pipe)
        pipe.zremrangebyscore(self._ts_zset_key, 0, score)
        return pipe.execute()[-1]

    def update(self, hash_id, **data):
        """Update data at a particular hash_id

        If a unique_field is being used, it cannot be updated
        """
        assert hash_id.startswith(self._base_key), (
            '{} does not start with {}'.format(repr(hash_id), repr(self._base_key))
        )
        if self._unique_field:
            assert self._unique_field not in data, (
                '{} is the unique field and cannot be updated'.format(repr(self._unique_field))
            )
        score = beu.REDIS.zscore(self._ts_zset_key, hash_id)
        if score is None or data == {}:
            return
        now = self.now_utc_float
        pipe = beu.REDIS.pipeline()
        index_fields = ','.join(self._index_base_keys.keys())
        if index_fields:
            for k, v in self.get(hash_id, index_fields).items():
                if k in data and data[k] != v:
                    old_index_key = self._make_key(self._base_key, k, v)
                    index_key = self._make_key(self._base_key, k, data[k])
                    pipe.srem(old_index_key, hash_id)
                    pipe.zincrby(self._index_base_keys[k], v, -1)
                    pipe.sadd(index_key, hash_id)
                    pipe.zincrby(self._index_base_keys[k], data[k], 1)
        pipe.hmset(hash_id, data)
        pipe.zadd(self._ts_zset_key, now, hash_id)
        pipe.execute()
        return hash_id

    def recent_unique_values(self, limit=10):
        """Return list of limit most recent unique values"""
        return [
            beu.decode(val)
            for val in beu.REDIS.zrevrange(self._id_zset_key, start=0, end=limit-1)
        ]

    def index_field_info(self, limit=10):
        """Return list of 2-item tuples (index_field:value, count)

        - limit: number of top index values per index type
        """
        results = []
        for index_field, base_key in sorted(self._index_base_keys.items()):
            results.extend([
                (':'.join([index_field, beu.decode(name)]), int(count))
                for name, count in beu.zshow(base_key, end=limit-1)
            ])
        return results

    def _redis_zset_from_terms(self, terms=''):
        """Return Redis key containing sorted set and bool denoting if its a temp

        - terms: string of 'index_field:value' pairs separated by any of , ; |

        Also keep track of count, size, and timestamp stats for any intermediate
        temporary sets created
        """
        to_intersect = []
        tmp_keys = []
        d = defaultdict(list)
        stat_base_names = {}
        terms = beu.string_to_set(terms)
        now = self.now_utc_float
        for term in terms:
            index_field, value = term.split(':')
            d[index_field].append(term)
        for index_field, grouped_terms in d.items():
            if len(grouped_terms) > 1:
                # Compute the union of all index_keys for the same field
                tmp_key = self._get_next_find_key()
                stat_base_names[';'.join(sorted(grouped_terms))] = tmp_key
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
                k = self._make_key(self._base_key, grouped_terms[0])
                stat_base_names[grouped_terms[0]] = k
                to_intersect.append(k)

        if len(to_intersect) > 1:
            intersect_key = self._get_next_find_key()
            tmp_keys.append(intersect_key)
            stat_base_names[';'.join(sorted(stat_base_names.keys()))] = intersect_key
            beu.REDIS.sinterstore(intersect_key, *to_intersect)
            last_key = self._get_next_find_key()
            tmp_keys.append(last_key)
            beu.REDIS.zinterstore(last_key, (intersect_key, self._ts_zset_key), aggregate='MAX')
        elif len(to_intersect) == 1:
            last_key = self._get_next_find_key()
            tmp_keys.append(last_key)
            beu.REDIS.zinterstore(last_key, (to_intersect[0], self._ts_zset_key), aggregate='MAX')
        else:
            last_key = self._ts_zset_key

        if stat_base_names:
            pipe = beu.REDIS.pipeline()
            for stat_base, set_name in stat_base_names.items():
                pipe.zadd(self._find_searches_zset_key, now, stat_base)
                pipe.hincrby(self._find_stats_hash_key, stat_base + '--count', 1)
                pipe.hset(
                    self._find_stats_hash_key,
                    stat_base + '--last_size',
                    beu.REDIS.scard(set_name)
                )
            pipe.execute()

        if tmp_keys:
            for tmp_key in tmp_keys[:-1]:
                beu.REDIS.delete(tmp_key)
            tmp_keys = [tmp_keys[-1]]

        return (last_key, tmp_keys != [])

    def find(self, terms='', start=None, end=None, limit=20, desc=None,
             get_fields='', all_fields=False, count=False, ts_fmt=None,
             ts_tz=None, admin_fmt=False, start_ts='', end_ts='', since='',
             until='', include_meta=True, item_format=''):
        """Return a list of dicts (or dict of list of dicts) that match all terms

        Multiple values in (terms, get_fields, start_ts, end_ts, since, until)
        must be separated by any of , ; |

        - terms: string of 'index_field:value' pairs
        - start: utc_float
        - end: utc_float
        - limit: max number of results
        - desc: if True, return results in descending order; if None,
          auto-determine if desc should be True or False
        - get_fields: string of field names to get for each matching hash_id
        - all_fields: if True, return all fields of each matching hash_id
        - count: if True, only return the total number of results (per time range)
        - ts_fmt: strftime format for the returned timestamps (_ts field)
        - ts_tz: a timezone to convert the timestamp to before formatting
        - admin_fmt: if True, use format and timezone defined in settings file
        - start_ts: timestamps with form between YYYY and YYYY-MM-DD HH:MM:SS.f
          (in the timezone specified in ts_tz or ADMIN_TIMEZONE)
        - end_ts: timestamps with form between YYYY and YYYY-MM-DD HH:MM:SS.f
          (in the timezone specified in ts_tz or ADMIN_TIMEZONE)
        - since: 'num:unit' strings (i.e. 15:seconds, 1.5:weeks, etc)
        - until: 'num:unit' strings (i.e. 15:seconds, 1.5:weeks, etc)
        - include_meta: if True (and 'count' is False), include attributes
          _id, _ts, and _pos in the results
        - item_format: format string for each item
        """
        results = {}
        now = self.now_utc_float
        result_key, result_key_is_tmp = self._redis_zset_from_terms(terms)
        time_ranges = beu.get_time_ranges_and_args(
            tz=ts_tz,
            now=now,
            start=start,
            end=end,
            start_ts=start_ts,
            end_ts=end_ts,
            since=since,
            until=until
        )
        timestamp_formatter = beu.get_timestamp_formatter_from_args(
            ts_fmt=ts_fmt,
            ts_tz=ts_tz,
            admin_fmt=admin_fmt
        )

        for name, start_end_tuple in time_ranges.items():
            _start, _end = start_end_tuple
            if count:
                if _start > 0 or _end < float('inf'):
                    func = partial(beu.REDIS.zcount, result_key, _start, _end)
                else:
                    func = partial(beu.REDIS.zcard, result_key)
                results[name] = func()
            else:
                _desc = desc
                if _desc is None:
                    if 'start' in name or 'since' in name:
                        _desc = False
                    else:
                        _desc = True

                if _desc:
                    func = partial(
                        beu.REDIS.zrevrangebyscore, result_key, _end, _start,
                        start=0, num=limit, withscores=True
                    )
                else:
                    func = partial(
                        beu.REDIS.zrangebyscore, result_key, _start, _end,
                        start=0, num=limit, withscores=True
                    )

                i = 0
                _results = []
                for hash_id, timestamp in func():
                    if all_fields:
                        d = self.get(
                            hash_id,
                            include_meta=include_meta,
                            timestamp_formatter=timestamp_formatter,
                            item_format=item_format,
                        )
                        if include_meta and not item_format:
                            d['_pos'] = i
                    elif get_fields:
                        d = self.get(
                            hash_id,
                            get_fields,
                            include_meta=include_meta,
                            timestamp_formatter=timestamp_formatter,
                            item_format=item_format,
                        )
                        if include_meta and not item_format:
                            d['_pos'] = i
                    else:
                        d = {}
                        if include_meta:
                            d['_id'] = beu.decode(hash_id)
                            d['_ts'] = timestamp_formatter(timestamp)
                            d['_pos'] = i
                        if item_format:
                            d = item_format.format(**d)
                    _results.append(d)
                    i += 1
                results[name] = _results

        if result_key_is_tmp:
            beu.REDIS.delete(result_key)

        if len(results) == 1:
            results = list(results.values())[0]
        return results

    def select_and_modify(self, menu_item_format='', action='update',
                          update_fields='', **find_kwargs):
        """Find items matching 'find_kwargs', make selections, then perform action

        - menu_item_format: format string for each menu item
        - action: 'update' or 'delete'
        - update_fields: (required if action is update)... a string containing
          fields to update, separated by any of , ; |
        - find_kwargs: a dict of kwargs for the self.find method
            - note: admin_fmt=True and include_meta=True cannot be over-written

        If the action was 'update', return a list of hash_ids that were modified.
        If the action was 'delete', return a list redis pipe execution results
        per selected item (list of lists)
        """
        assert action in ('update', 'delete'), 'action can only be "update" or "delete"'
        update_fields = beu.string_to_set(update_fields)
        if action == 'update':
            assert update_fields != set(), 'update_fields is required if action is "update"'
            assert self._unique_field not in update_fields, (
                '{} is the unique field and cannot be updated'.format(repr(self._unique_field))
            )
        find_kwargs.update(dict(admin_fmt=True, include_meta=True))
        found = self.find(**find_kwargs)
        assert type(found) == list, 'Results contain multiple time ranges... not allowed for now'
        selected = beu.make_selections(
            found,
            item_format=menu_item_format,
            wrap=False
        )

        if selected:
            print('\nSelected:')
            if menu_item_format:
                print('\n'.join([menu_item_format.format(**x) for x in selected]) + '\n')
            else:
                print('\n'.join([repr(x) for x in selected]) + '\n')
            results = []
            if action == 'update':
                new_data = {}
                for field in update_fields:
                    resp = beu.user_input('value for {} field'.format(repr(field)))
                    if resp:
                        new_data[field] = resp
                if new_data:
                    for item in selected:
                        results.append(self.update(item['_id'], **new_data))
            elif action == 'delete':
                for item in selected:
                    results.append(self.delete(item['_id']))

            return results

    def find_stats(self, limit=5):
        """Return summary info for temporary sets created during 'find' calls

        - limit: max number of items to return in 'counts' and 'sizes' info
        """
        count_stats = []
        size_stats = []
        results = {}
        for name, num in beu.REDIS.hgetall(self._find_stats_hash_key).items():
            name, _type = beu.decode(name).split('--')
            if _type == 'count':
                count_stats.append((name, int(beu.decode(num))))
            elif _type == 'last_size':
                size_stats.append((name, int(beu.decode(num))))
        count_stats.sort(key=lambda x: x[1], reverse=True)
        size_stats.sort(key=lambda x: x[1], reverse=True)
        results['counts'] = count_stats[:limit]
        results['sizes'] = size_stats[:limit]
        results['timestamps'] = []
        newest = beu.zshow(self._find_searches_zset_key, end=3*(limit-1))
        for name, ts in newest:
            results['timestamps'].append((
                beu.decode(name),
                ts,
                beu.utc_float_to_pretty(ts, fmt=beu.ADMIN_DATE_FMT, timezone=beu.ADMIN_TIMEZONE)
            ))
        return results

    def clear_find_stats(self):
        """Delete all Redis keys under self._find_base_key"""
        pipe = beu.REDIS.pipeline()
        for key in beu.REDIS.scan_iter('{}*'.format(self._find_base_key)):
            pipe.delete(key)
        pipe.execute()
