import configparser
import os.path
import textwrap
from os import getenv
from datetime import datetime
from redis import StrictRedis


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(ROOT_DIR)
SETTINGS_FILE = os.path.join(PROJECT_DIR, 'settings.ini')
APP_ENV = getenv('APP_ENV', 'dev')
_config = configparser.ConfigParser()
_config.read(SETTINGS_FILE)


def from_string(val):
    if val.lower() == 'true':
        val = True
    elif val.lower() == 'false':
        val = False
    else:
        try:
            val = float(val)
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
        return default
    else:
        val = from_string(val)
    return val


def utc_now_float_string(fmt='%Y%m%d%H%M%S.%f'):
    return datetime.utcnow().strftime(fmt)


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
        print
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

    print
    indices = user_input(prompt)
    if not indices:
        return []

    for index in indices.split():
        try:
            selected.append(items[int(index)])
        except (IndexError, ValueError):
            pass

    return selected


REDIS_URL = get_setting('redis_url')
REDIS = StrictRedis.from_url(REDIS_URL) if REDIS_URL is not '' else None
from beu.redthing import RedThing
