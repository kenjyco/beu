beu
===

See the following

-  https://github.com/kenjyco/input-helper
-  https://github.com/kenjyco/bg-helper
-  https://github.com/kenjyco/redis-helper
-  https://github.com/kenjyco/chloop
-  https://github.com/kenjyco/parse-helper
-  https://github.com/kenjyco/yt-helper
-  https://github.com/kenjyco/mocp
-  https://github.com/kenjyco/mocp-cli

Install
-------

Install system requirements (Debian-based distros and Mac)

::

    % curl -o- https://raw.githubusercontent.com/kenjyco/beu/master/install-system-requirements.sh | bash

..

    Note: if using a Mac, you need to run
    `jack <http://www.jackaudio.org/>`__ in another terminal EVERY TIME
    you want to use MOC (i.e. ``jackd -d coreaudio``).

Verify that the MOC server can start

::

    % mocp

..

    Press ``q`` to quit.

Install with ``pip``

::

    % pip3 install beu

Usage
-----

The ``beu-ipython`` script is provided

::

    $ venv/bin/beu-ipython --help
    Usage: beu-ipython [OPTIONS]

      Start ipython with `beu` imported

    Options:
      --help  Show this message and exit.

Start ``beu-ipython`` which already has the ``beu`` module imported

    When ``beu`` is imported, it also imports most/all of my PYPI
    packages as their preferred 2-character shortcuts.

::

    % venv/bin/beu-ipython
    Python 3.5.2 (default, Nov 17 2016, 17:05:23)
    Type "copyright", "credits" or "license" for more information.

    IPython 5.3.0 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.

    In [1]: beu.ih
    Out[1]: <module 'input_helper' from '/tmp/stuff/venv/lib/python3.5/site-packages/input_helper/__init__.py'>

    In [2]: beu.bh
    Out[2]: <module 'bg_helper' from '/tmp/stuff/venv/lib/python3.5/site-packages/bg_helper/__init__.py'>

    In [3]: beu.rh
    Out[3]: <module 'redis_helper' from '/tmp/stuff/venv/lib/python3.5/site-packages/redis_helper/__init__.py'>

    In [4]: beu.chloop
    Out[4]: <module 'chloop' from '/tmp/stuff/venv/lib/python3.5/site-packages/chloop/__init__.py'>

    In [5]: beu.ph
    Out[5]: <module 'parse_helper' from '/tmp/stuff/venv/lib/python3.5/site-packages/parse_helper/__init__.py'>

    In [6]: beu.yh
    Out[6]: <module 'yt_helper' from '/tmp/stuff/venv/lib/python3.5/site-packages/yt_helper/__init__.py'>

    In [7]: beu.moc
    Out[7]: <module 'moc' from '/tmp/stuff/venv/lib/python3.5/site-packages/moc/__init__.py'>
