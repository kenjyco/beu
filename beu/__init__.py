import re
import configparser
import os.path
import textwrap
import requests
import pytz
from os import getenv
from datetime import datetime, timedelta, timezone as dt_timezone
from functools import partial
from itertools import product, zip_longest, chain
from redis import StrictRedis
from bs4 import BeautifulSoup, FeatureNotFound


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(ROOT_DIR)
SETTINGS_FILE = os.path.join(PROJECT_DIR, 'settings.ini')
APP_ENV = getenv('APP_ENV', 'dev')
FLOAT_STRING_FMT = '%Y%m%d%H%M%S.%f'
requests.packages.urllib3.disable_warnings()
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/45.0.2454.85 Chrome/45.0.2454.85 Safari/537.36'
_config = configparser.RawConfigParser()
_config.read(SETTINGS_FILE)
__doc__ = """

A thing that can be used to prototype backend/cli ideas.
"""


def from_string(val):
    if val.lower() == 'true':
        val = True
    elif val.lower() == 'false':
        val = False
    else:
        try:
            val = float(val)
            if val.is_integer():
                val = int(val)
        except ValueError:
            try:
                val = int(val)
            except ValueError:
                pass
    return val


def get_setting(name, default='', section=APP_ENV):
    try:
        val = _config[section][name]
    except KeyError:
        try:
            val = _config['default'][name]
        except KeyError:
            return default
        else:
            val = from_string(val)
    else:
        val = from_string(val)
    return val


def string_to_set(s):
    """Return a set of strings from s where items are separated by any of , ; |"""
    return set(re.split(r'\s*[,;\|]\s*', s)) - set([''])


def dt_to_float_string(dt, fmt=FLOAT_STRING_FMT):
    return dt.strftime(fmt)


def float_string_to_dt(float_string, fmt=FLOAT_STRING_FMT):
    return datetime.strptime(float_string, fmt)


def utc_now_iso():
    return datetime.utcnow().isoformat()


def utc_now_float_string(fmt=FLOAT_STRING_FMT):
    return dt_to_float_string(datetime.utcnow(), fmt)


def utc_ago_float_string(num_unit, now=None, fmt=FLOAT_STRING_FMT):
    """Return a float_string representing a UTC datetime in the past

    - num_unit: a string 'num:unit' (i.e. 15:seconds, 1.5:weeks, etc)
    - now: a utc_float or None

    Valid units are: (se)conds, (mi)nutes, (ho)urs, (da)ys, (we)eks, hr, wk
    """
    if now is None:
        now = datetime.utcnow()
    else:
        now = float_string_to_dt(now)
    val = None
    num, unit = num_unit.split(':')
    _trans = {
        'se': 'seconds', 'mi': 'minutes', 'ho': 'hours', 'hr': 'hours',
        'da': 'days', 'we': 'weeks', 'wk': 'weeks'
    }
    try:
        kwargs = {_trans[unit.lower()[:2]]: float(num)}
    except (KeyError, ValueError) as e:
        pass
    else:
        td = timedelta(**kwargs)
        val = dt_to_float_string(now - td, fmt)
    return val


def utc_float_to_pretty(utc_float=None, fmt=None, timezone=None):
    if not utc_float:
        utc_float = float(utc_now_float_string())
    if not fmt:
        if ADMIN_DATE_FMT:
            fmt = ADMIN_DATE_FMT
            timezone = ADMIN_TIMEZONE
        else:
            return utc_float
    dt = datetime.strptime(str(utc_float), FLOAT_STRING_FMT)
    if timezone:
        dt = dt.replace(tzinfo=dt_timezone.utc)
        dt = dt.astimezone(pytz.timezone(timezone))
    return dt.strftime(fmt)


def date_string_to_utc_float_string(date_string, timezone=None):
    """Return a utc_float_string for a given date_string

    - date_string: string form between 'YYYY' and 'YYYY-MM-DD HH:MM:SS.f'
    """
    dt = None
    s = None
    for fmt in [
        '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d %H', '%Y-%m-%d', '%Y-%m', '%Y'
    ]:
        try:
            dt = datetime.strptime(date_string, fmt)
        except ValueError:
            continue
        else:
            break

    if dt:
        if timezone:
            tz = pytz.timezone(timezone)
            dt = tz.localize(dt).astimezone(pytz.utc)
        s = dt_to_float_string(dt)
    return s


def get_time_ranges_and_args(**kwargs):
    """Return a dict of time range strings and start/end tuples

    Multiple values in (start_ts, end_ts, since, until) must be separated
    by any of , ; |

    - tz: timezone
    - now: float_string
    - start: utc_float
    - end: utc_float
    - start_ts: timestamps with form between YYYY and YYYY-MM-DD HH:MM:SS.f (in tz)
    - end_ts: timestamps with form between YYYY and YYYY-MM-DD HH:MM:SS.f (in tz)
    - since: 'num:unit' strings (i.e. 15:seconds, 1.5:weeks, etc)
    - until: 'num:unit' strings (i.e. 15:seconds, 1.5:weeks, etc)

    The start/end kwargs returned are meant to be used with any of
    REDIS functions zcount, zrangebyscore, or zrevrangebyscore
    """
    tz = kwargs.get('tz') or ADMIN_TIMEZONE
    now = kwargs.get('now') or utc_now_float_string()
    results = {}
    _valid_args = [
        ('start_ts', 'end_ts', partial(date_string_to_utc_float_string, timezone=tz)),
        ('since', 'until', partial(utc_ago_float_string, now=now)),
    ]
    for first, second, func in _valid_args:
        first_string = kwargs.get(first, '')
        second_string = kwargs.get(second, '')
        if first_string or second_string:
            first_vals = string_to_set(first_string)
            second_vals = string_to_set(second_string)
            if first_vals and second_vals:
                _gen = product(first_vals, second_vals)
                gen = chain(
                    _gen,
                    ((f, '') for f in first_vals),
                    (('', s) for s in second_vals)
                )
            else:
                gen = zip_longest(first_vals, second_vals)

            for _first, _second in gen:
                if _first and _second:
                    return_key = '{}={},{}={}'.format(first, _first, second, _second)
                    start_float = float(func(_first))
                    end_float = float(func(_second))
                elif _first:
                    return_key = '{}={}'.format(first, _first)
                    start_float = float(func(_first))
                    end_float = float('inf')
                elif _second:
                    return_key = '{}={}'.format(second, _second)
                    end_float = float(func(_second))
                    start_float = 0
                else:
                    continue
                if start_float >= end_float:
                    continue

                results[return_key] = (start_float, end_float)

    start = kwargs.get('start')
    end = kwargs.get('end')
    if start and end:
        return_key = 'start={},end={}'.format(start, end)
        results[return_key] = (float(start), float(end))
    elif start:
        return_key = 'start={}'.format(start)
        results[return_key] = (float(start), float('inf'))
    elif end:
        return_key = 'end={}'.format(end)
        results[return_key] = (0, float(end))
    if not results:
        results['all'] = (0, float('inf'))
    return results


def get_timestamp_formatter_from_args(ts_fmt=None, ts_tz=None, admin_fmt=False):
    """Return a function that can be applied to a utc_float

    - ts_fmt: strftime format for the returned timestamp
    - ts_tz: a timezone to convert the timestamp to before formatting
    - admin_fmt: if True, use format and timezone defined in settings file
    """
    if admin_fmt:
        func = partial(
            utc_float_to_pretty, fmt=ADMIN_DATE_FMT, timezone=ADMIN_TIMEZONE
        )
    elif ts_tz and ts_fmt:
        func = partial(utc_float_to_pretty, fmt=ts_fmt, timezone=ts_tz)
    elif ts_fmt:
        func = partial(utc_float_to_pretty, fmt=ts_fmt)
    else:
        func = lambda x: x
    return func


def new_requests_session():
    """Return a new requests Session object"""
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    return session


def fetch_html(url, session=None):
    """Fetch url and return the page's html (or None)"""
    session = session or new_requests_session()
    try:
        response = session.head(url)
    except requests.exceptions.ConnectionError:
        print('Could not access {}'.format(repr(url)))
    else:
        if 'text/html' in response.headers['content-type']:
            response = session.get(url, verify=False)
            return response.content
        else:
            print('Not html content')


def get_soup(url, session=None):
    """Fetch url and return a BeautifulSoup object (or None)"""
    html = fetch_html(url, session)
    if html:
        try:
            return BeautifulSoup(html, 'lxml')
        except FeatureNotFound:
            return BeautifulSoup(html)


def zshow(key, start=0, end=-1, desc=True, withscores=True):
    """Wrapper to REDIS.zrange"""
    return REDIS.zrange(key, start, end, withscores=withscores, desc=desc)


def decode(obj, encoding='utf-8'):
    try:
        return obj.decode(encoding)
    except (AttributeError, UnicodeDecodeError):
        return obj


def identity(x):
    return x


def user_input(prompt_string='input', ch='> '):
    """Prompt user for input

    - prompt_string: string to display when asking for input
    - ch: string appended to the main prompt_string
    """
    try:
        return input(prompt_string + ch)
    except (EOFError, KeyboardInterrupt):
        print()
        return ''


def make_selections(items, prompt='', wrap=True, item_format=''):
    """Return a subset of the items provided

    - items: list of strings or list of dicts
    - prompt: string to display when asking for input
    - wrap: True/False for whether or not to wrap long lines
    - item_format: format string for each item (when items are dicts)
    """
    if not items:
        return items

    selected = []

    if not prompt:
        prompt = 'Make selections (separate by space): '

    make_string = identity
    if item_format:
        make_string = lambda x: item_format.format(**x)

    # Generate the menu and display the items user will select from
    for i, item in enumerate(items):
        if i % 5 == 0 and i > 0:
            print('-' * 70)
        try:
            line = '{:4}) {}'.format(i, make_string(item))
        except UnicodeEncodeError:
            item = {
                k: v.encode('ascii', 'replace')
                for k, v in item.items()
            }
            line = '{:4}) {}'.format(i, make_string(item))
        if wrap:
            print(textwrap.fill(line, subsequent_indent=' '*6))
        else:
            print(line)

    print()
    indices = user_input(prompt)
    if not indices:
        return []

    for index in indices.split():
        try:
            selected.append(items[int(index)])
        except (IndexError, ValueError):
            pass

    return selected


class RedKeyMaker(object):
    """RedKeyMaker is a base class for things that need to make redis keys

    The sub-class should set the `self._base_key` string in order for
    `show_keyspace` and `clear_keyspace` methods to work
    """
    def _make_key(self, *parts):
        return ':'.join([str(part) for part in parts])

    def _get_next_key(self, next_id_string_key, base_key=None):
        if base_key is None:
            base_key = ':'.join(next_id_string_key.split(':')[:-1])
        pipe = REDIS.pipeline()
        pipe.setnx(next_id_string_key, 1)
        pipe.get(next_id_string_key)
        pipe.incr(next_id_string_key)
        result = pipe.execute()
        return self._make_key(base_key, int(result[1]))

    def show_keyspace(self):
        if self.size <= 500:
            return sorted([
                (decode(key), decode(REDIS.type(key)))
                for key in REDIS.scan_iter('{}*'.format(self._base_key))
            ])
        else:
            print('Keyspace is too large')

    def clear_keyspace(self):
        for key in REDIS.scan_iter('{}*'.format(self._base_key)):
            REDIS.delete(key)


ADMIN_TIMEZONE = get_setting('admin_timezone')
ADMIN_DATE_FMT = get_setting('admin_date_fmt')
REDIS_URL = get_setting('redis_url')
REDIS = StrictRedis.from_url(REDIS_URL) if REDIS_URL is not '' else None
import beu.page_parser
from beu.redthing import RedThing
from beu.unique_redthing import UniqueRedThing
