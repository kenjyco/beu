beu
===

## Clone, setup, and run tests

```
% git clone https://github.com/kenjyco/beu && cd beu
% ./dev-setup.bash
% cp settings.ini.sample settings.ini
% source scripts/beu.sh
% beu-test
```

[beu.sh]: https://github.com/kenjyco/beu/blob/master/scripts/beu.sh
[dev-setup.bash]: https://github.com/kenjyco/beu/blob/master/dev-setup.bash

> Note: the [scripts/beu.sh][beu.sh] script provides **`beu-test`**,
> **`beu-ipython`**, **`beu-help`**, and **`beu-examples`** shell functions when
> sourced, as long as [dev-setup.bash][] was used to install.

## Load up examples and experiment in the shell

> `% beu-examples`

[![asciinema](https://asciinema.org/a/698k7nivkqf30poapp5ujx9yd.png)](https://asciinema.org/a/698k7nivkqf30poapp5ujx9yd?autoplay=1)

## Settings, environments, testing, and debugging

When using `beu-test`, tests will stop running on the first failure and drop you
into a `pdb++` debugger session.

- use `(l)ist` to list context lines
- use `(n)ext` to move on to the next statement
- use `(s)tep` to step into a function
- use `(c)ontinue` to continue to next break point (i.e. `set_trace()` lines in
  your code)
- use `sticky` to toggle sticky mode (to constantly show the currently executing
  code as you move through with the debugger)
- use `pp` to pretty print a variable or statement

If the redis server at `redis_url` (in the test section of settings.ini) is not
running or is not empty, redis server tests will be skipped.

Use the `APP_ENV` environment variable to specify which section of the
`settings.ini` file your settings will be loaded from. Any settings in the
`default` section can be overwritten if explicity set in another section.

- if no `APP_ENV` is explicitly set, `dev` is assumed
- the `APP_ENV` setting is overwritten to be `test` no matter what was set when
  calling `py.test` tests

[![asciinema](https://asciinema.org/a/ctqwly2exssjrg3a9v17xm64h.png)](https://asciinema.org/a/ctqwly2exssjrg3a9v17xm64h?autoplay=1)
