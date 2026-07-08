# portcheck

> Show which process is listening on which port, cross-platform, so you can kill the right one.

## Why

`Error: listen EADDRINUSE :::3000`. Now you need to know what is on 3000 and
how to stop it, and the incantation is different on every OS. `portcheck` is
the same command everywhere.

## Usage

```
python portcheck.py              # everything listening
python portcheck.py 3000         # just this port, plus how to kill it
python portcheck.py 5432 --free  # exit 0 if free, 1 if in use
```
