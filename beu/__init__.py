import redis_helper as rh
import input_helper as ih
import yt_helper as yh
import parse_helper as ph
import moc
from subprocess import call
from datetime import datetime


def utc_now_iso():
    """Return current UTC timestamp in ISO format"""
    return datetime.utcnow().isoformat()


def run_or_die(cmd):
    """Run a shell command or exit the system"""
    ret_code = call(cmd, shell=True)
    if ret_code != 0:
        exit(ret_code)
