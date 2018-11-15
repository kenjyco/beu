import redis_helper as rh
import input_helper as ih
import yt_helper as yh
import parse_helper as ph
import bg_helper as bh
import fs_helper as fh
import dt_helper as dh
import settings_helper as sh
import aws_info_helper as ah

try:
    import vlc_helper as vh
except ImportError:
    pass
import moc
import mocp_cli
import chloop
import logging
import os.path


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
