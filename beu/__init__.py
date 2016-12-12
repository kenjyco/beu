import configparser
import os.path
from os import getenv
from datetime import datetime
from redis import StrictRedis


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(ROOT_DIR)
SETTINGS_FILE = os.path.join(PROJECT_DIR, 'settings.ini')
APP_ENV = getenv('APP_ENV', 'dev')
_config = configparser.ConfigParser()
_config.read(SETTINGS_FILE)


def get_setting(name, default='', section=APP_ENV):
    try:
        val = _config[section][name]
    except KeyError:
        return default
    else:
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


def utc_now_float_string(fmt='%Y%m%d%H%M%S.%f'):
    return datetime.utcnow().strftime(fmt)


REDIS_URL = get_setting('redis_url')
REDIS = StrictRedis.from_url(REDIS_URL) if REDIS_URL is not '' else None
from beu.redthing import RedThing
