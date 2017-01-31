import re
import requests
import redis_helper as rh
import input_helper as ih
from subprocess import call
from sys import exit
from bs4 import BeautifulSoup, FeatureNotFound
from datetime import datetime, timedelta, timezone as dt_timezone
from functools import partial


requests.packages.urllib3.disable_warnings()
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/45.0.2454.85 Chrome/45.0.2454.85 Safari/537.36'


def utc_now_iso():
    """Return current UTC timestamp in ISO format"""
    return datetime.utcnow().isoformat()


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


def run_or_die(cmd):
    """Run a shell command or exit the system"""
    ret_code = call(cmd, shell=True)
    if ret_code != 0:
        exit(ret_code)


import beu.download
