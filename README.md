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

## Output

```
PORT     PID      PROCESS
3000     4242     node.exe
5432     991      postgres.exe

to stop it:  taskkill /PID 4242 /F
```

The kill command printed is the right one for the platform you are on.

## How it finds them

| platform | uses |
|----------|------|
| Windows  | `netstat -ano` + `tasklist` for the process name |
| macOS / BSD | `lsof -iTCP -sTCP:LISTEN` |
| Linux    | `lsof` if present, otherwise `ss -ltnp` |

`--free` does not shell out at all — it just tries to connect, which is what
you want inside a script deciding whether to start a server.

## In a script

```sh
python portcheck.py 8000 --free || python portcheck.py 8000
```
