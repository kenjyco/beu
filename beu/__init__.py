import re
import configparser
import os.path
import textwrap
import pytz
from os import getenv
from datetime import datetime, timedelta, timezone as dt_timezone
from redis import StrictRedis


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(ROOT_DIR)
SETTINGS_FILE = os.path.join(PROJECT_DIR, 'settings.ini')
APP_ENV = getenv('APP_ENV', 'dev')
_config = configparser.RawConfigParser()
_config.read(SETTINGS_FILE)


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


def dt_to_float_string(dt, fmt='%Y%m%d%H%M%S.%f'):
    return dt.strftime(fmt)


def utc_now_float_string(fmt='%Y%m%d%H%M%S.%f'):
    return dt_to_float_string(datetime.utcnow(), fmt)


def utc_ago_float_string(num_unit, fmt='%Y%m%d%H%M%S.%f'):
    """Return a float_string representing a UTC datetime in the past

    - num_unit: a string 'num.unit' (i.e. 15.seconds, 2.weeks, etc)

    Valid units are: (se)conds, (mi)nutes, (ho)urs, (da)ys, (we)eks
    """
    val = None
    num, unit = num_unit.split('.')
    _trans = {
        'se': 'seconds', 'mi': 'minutes', 'ho': 'hours',
        'da': 'days', 'we': 'weeks'
    }
    try:
        kwargs = {_trans[unit.lower()[:2]]: int(num)}
    except (KeyError, ValueError):
        pass
    else:
        td = timedelta(**kwargs)
        val = dt_to_float_string(datetime.utcnow() - td, fmt)
    return val


def utc_float_to_pretty(f=None, fmt=None, timezone=None):
    if not f:
        f = float(utc_now_float_string())
    if not fmt:
        if ADMIN_DATE_FMT:
            fmt = ADMIN_DATE_FMT
            timezone = ADMIN_TIMEZONE
        else:
            return f
    dt = datetime.strptime(str(f), '%Y%m%d%H%M%S.%f')
    if timezone:
        dt = dt.replace(tzinfo=dt_timezone.utc)
        dt = dt.astimezone(pytz.timezone(timezone))
    return dt.strftime(fmt)


def date_string_to_utc_float_string(date_string, timezone=None):
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


def zshow(key, start=0, end=-1, desc=True, withscores=True):
    """Wrapper to REDIS.zrange"""
    return REDIS.zrange(key, start, end, withscores=withscores, desc=desc)


def decode(obj, encoding='utf-8'):
    try:
        return obj.decode(encoding)
    except (AttributeError, UnicodeDecodeError):
        return obj


def user_input(prompt='input: '):
    """Prompt user for input

    - prompt: string to display when asking for input
    """
    try:
        return input(prompt)
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

    make_string = lambda x: x
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


ADMIN_TIMEZONE = get_setting('admin_timezone')
ADMIN_DATE_FMT = get_setting('admin_date_fmt')
REDIS_URL = get_setting('redis_url')
REDIS = StrictRedis.from_url(REDIS_URL) if REDIS_URL is not '' else None
from beu.redthing import RedThing
