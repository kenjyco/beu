## About

The `beu` package is intended to be an easy way to explore several complementary
Python packages.

- There is a script to help you get all the system requirements installed
- The `beu` module auto-imports several relevant modules as their preferred
  2-character (or 3-character) shortcuts for quick interaction
- The `beu-ipython` command is a shortcut to start an `ipython` session with the
  `beu` module imported before you see the shell prompt
- The commands provided by the other packages are all installed to the same
  place
- All the advanced features of the packages are made available (since some
  packages will do more when certain other packages can be imported)

See the following docs:

- <https://github.com/kenjyco/input-helper/blob/master/README.md#usage>
- <https://github.com/kenjyco/bg-helper/blob/master/README.md#usage>
- <https://github.com/kenjyco/settings-helper/blob/master/README.md>
- <https://github.com/kenjyco/redis-helper/blob/master/README.md#intro>
- <https://github.com/kenjyco/chloop/blob/master/README.md#usage>
- <https://github.com/kenjyco/parse-helper/blob/master/README.md#usage>
- <https://github.com/kenjyco/yt-helper/blob/master/README.md#usage>
- <https://github.com/kenjyco/dt-helper/blob/master/README.md>
- <https://github.com/kenjyco/fs-helper/blob/master/README.md>
- <https://github.com/kenjyco/aws-info-helper/blob/master/README.md>
- <https://github.com/kenjyco/webclient-helper/blob/master/README.md>
- <https://github.com/kenjyco/mongo-helper#usage>
- <https://github.com/kenjyco/sql-helper#usage>
- <https://github.com/kenjyco/readme-helper#usage>
- <https://github.com/kenjyco/testing-helper#usage>
- <https://github.com/kenjyco/mocp/blob/master/README.md#usage>
- <https://github.com/kenjyco/mocp-cli/blob/master/README.md#usage>
- <https://github.com/kenjyco/vlc-helper/blob/master/README.md#usage>

## Install

Install system requirements and install `beu` package to `~/.beu` (Debian-based
distros and Mac). Also modify one of `~/.zshrc`, `~/.bashrc`, or
`~/.bash_profile`.

```
% curl -o- https://raw.githubusercontent.com/kenjyco/beu/master/install.sh | bash
```

Source the `wrappers.sh` file

```
% source ~/.beu/wrappers.sh
```

#### Mac Note

VLC related things (vlc-helper package, system dbus, etc) are not installed
since VLC cannot be controlled with dbus on mac

#### Linux Cloud Note

VLC related things (vlc-helper package, system dbus, etc) and MOC related things
(mocp & mocp-cli packages, system moc) are not installed since you can't watch
videos or listen to audio.

## Usage

The `beu-ipython` script is provided (with the `b` shortcut set in
`~/.beu/wrappers.sh`)

```
% b --help
Usage: beu-ipython [OPTIONS]

  Start ipython with `beu` and `pprint` imported

Options:
  --no-vi      Do not use vi editing mode
  --no-colors  Do not use colors / syntax highlighting
  --help       Show this message and exit.
```

```
% b
Python 3.6.8 (default, Jan 14 2019, 17:05:23)
Type "copyright", "credits" or "license" for more information.

IPython 7.6.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: beu.ih
Out[1]: <module 'input_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/input_helper/__init__.py'>

In [2]: beu.bh
Out[2]: <module 'bg_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/bg_helper/__init__.py'>

In [3]: beu.rh
Out[3]: <module 'redis_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/redis_helper/__init__.py'>

In [4]: beu.chloop
Out[4]: <module 'chloop' from '/tmp/stuff/venv/lib/python3.6/site-packages/chloop/__init__.py'>

In [5]: beu.ph
Out[5]: <module 'parse_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/parse_helper/__init__.py'>

In [6]: beu.yh
Out[6]: <module 'yt_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/yt_helper/__init__.py'>

In [7]: beu.fh
Out[7]: <module 'fs_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/fs_helper/__init__.py'>

In [8]: beu.dh
Out[8]: <module 'dt_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/dt_helper/__init__.py'>

In [9]: beu.sh
Out[9]: <module 'settings_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/settings_helper/__init__.py'>

In [10]: beu.ah
Out[10]: <module 'aws_info_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/aws_info_helper/__init__.py'>

In [11]: beu.jh
Out[11]: <module 'jira_helper' from '/tmp/stuff/venv/lib/python3.6//site-packages/jira_helper/__init__.py'>

In [12]: beu.ewm
Out[12]: <module 'easy_workflow_manager' from '/tmp/stuff/venv/lib/python3.6/site-packages/easy_workflow_manager/__init__.py'>

In [13]: beu.mh
Out[13]: <module 'mongo_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/mongo_helper/__init__.py'>

In [14]: beu.sqh
Out[14]: <module 'sql_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/sql_helper/__init__.py'>

In [15]: beu.moc
Out[15]: <module 'moc' from '/tmp/stuff/venv/lib/python3.6/site-packages/moc/__init__.py'>

In [16]: beu.mocp_cli
Out[16]: <module 'mocp_cli' from '/tmp/stuff/venv/lib/python3.6/site-packages/mocp_cli/__init__.py'>

In [17]: beu.vh
Out[17]: <module 'vlc_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/vlc_helper/__init__.py'>

In [18]: beu.wh
Out[18]: <module 'webclient_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/webclient_helper/__init__.py'>

In [19]: beu.th
Out[19]: <module 'testing_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/testing_helper/__init__.py'>

In [20]: beu.rmh
Out[20]: <module 'readme_helper' from '/tmp/stuff/venv/lib/python3.6/site-packages/readme_helper/__init__.py'>
```

## Updating

Use `beu-update` to get the latest changes

```
% beu-update
```

## Misc

You should be able to pass the `--help` option to any of the command/shortcuts
listed below for more info.

- Use `m` (`mocplayer`) to start the REPL to control audio playback and making
  annotations
- Use `rh-shell` to explore Collection objects

> Note: see the [wrappers.sh](https://raw.githubusercontent.com/kenjyco/beu/master/wrappers.sh)
> file to see all defined shortcuts.
