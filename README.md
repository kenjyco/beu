beu
===

## Install

```
% pip install beu
```

## Usage

Start `beu-ipython` which already has the `beu` module imported 

> When `beu` is imported, it also imports most/all of my PYPI packages as their
> preferred 2-character shortcuts.

```
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

In [2]: beu.ph
Out[2]: <module 'parse_helper' from '/tmp/stuff/venv/lib/python3.5/site-packages/parse_helper/__init__.py'>

In [3]: beu.rh
Out[3]: <module 'redis_helper' from '/tmp/stuff/venv/lib/python3.5/site-packages/redis_helper/__init__.py'>

In [4]: beu.yh
Out[4]: <module 'yt_helper' from '/tmp/stuff/venv/lib/python3.5/site-packages/yt_helper/__init__.py'>

In [5]: beu.moc
Out[5]: <module 'moc' from '/tmp/stuff/venv/lib/python3.5/site-packages/moc/__init__.py'>
```
