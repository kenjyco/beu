import redis_helper as rh
import input_helper as ih
import yt_helper as yh
import parse_helper as ph
import moc
import logging
import os.path
from subprocess import call
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


def run_or_die(cmd):
    """Run a shell command or exit the system"""
    ret_code = call(cmd, shell=True)
    if ret_code != 0:
        exit(ret_code)
