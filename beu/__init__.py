import redis_helper as rh
import input_helper as ih
import yt_helper as yh
import parse_helper as ph
import bg_helper as bh
try:
    import vlc_helper as vh
except ImportError:
    pass
import moc
import chloop
import logging
import os.path
from datetime import datetime


LOGFILE = os.path.abspath('log--beu.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOGFILE, mode='a')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(funcName)s: %(message)s'
))
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def utc_now_iso():
    """Return current UTC timestamp in ISO format"""
    return datetime.utcnow().isoformat()
