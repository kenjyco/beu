About
-----

The ``beu`` package is intended to be an easy way to explore several
complementary Python packages.

-  There is a script to help you get all the system requirements
   installed
-  The ``beu`` module auto-imports several relevant modules as their
   preferred 2-character shortcuts for quick interaction
-  The ``beu-ipython`` command is a shortcut to start an ``ipython``
   session with the ``beu`` module imported before you see the shell
   prompt
-  The commands provided by the other packages are all installed to the
   same place
-  All the advanced features of the packages are made available (since
   some packages will do more when certain other packages can be
   imported)

See the following docs:

-  https://github.com/kenjyco/input-helper/blob/master/README.md#usage
-  https://github.com/kenjyco/bg-helper/blob/master/README.md#usage
-  https://github.com/kenjyco/redis-helper/blob/master/README.md#intro
-  https://github.com/kenjyco/chloop/blob/master/README.md#usage
-  https://github.com/kenjyco/parse-helper/blob/master/README.md#usage
-  https://github.com/kenjyco/yt-helper/blob/master/README.md#usage
-  https://github.com/kenjyco/mocp/blob/master/README.md#usage
-  https://github.com/kenjyco/mocp-cli/blob/master/README.md#usage

Install
-------

Install system requirements and install ``beu`` package to ``~/.beu``
(Debian-based distros and Mac). Also modify one of ``~/.zshrc``,
``~/.bashrc``, or ``~/.bash_profile``.

::

    % curl -o- https://raw.githubusercontent.com/kenjyco/beu/master/install.sh | bash

    Note: if using a Mac, you need to run
    `jack <http://www.jackaudio.org/>`__ in another terminal EVERY TIME
    you want to use MOC (i.e. ``jackd -d coreaudio``).

Source the ``wrappers.sh`` file

::

    % source ~/.beu/wrappers.sh

Verify that the MOC server can start

::

    % mocp

    Press ``q`` to quit.

Usage
-----

The ``beu-ipython`` script is provided (with the ``b`` shortcut set in
``~/.beu/wrappers.sh``)

::

    % b --help
    Usage: beu-ipython [OPTIONS]

      Start ipython with `beu` imported

    Options:
      --help  Show this message and exit.

::

    % b
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

Updating
--------

Use ``beu-update`` to get the latest changes

::

    % beu-update

Misc
----

You should be able to pass the ``--help`` option to any of the
command/shortcuts listed below for more info.

-  Use ``a`` (``yt-search --audio-only``) to search for and download
   audio files
-  Use ``v`` (``yt-search``) to search for and download video files
-  Use ``m`` (``mocplayer``) to start the REPL to control audio playback
   and making annotations
-  Use ``pdfsearch`` (``ph-goo --filetype pdf``) to search for and
   download PDF files
-  Use ``rh-shell`` to explore Collection objects

    Note: see the
    `wrappers.sh <https://raw.githubusercontent.com/kenjyco/beu/master/wrappers.sh>`__
    file to see all defined shortcuts.
