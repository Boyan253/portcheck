#!/usr/bin/env python3
"""List listening ports and the processes behind them."""

import argparse
import os
import re
import socket
import subprocess
import sys

WINDOWS = os.name == "nt"


def parse_netstat_windows(output):
    """Parse `netstat -ano` LISTENING lines into (port, pid) pairs."""
    rows = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) < 5 or parts[0] not in ("TCP", "UDP"):
            continue
        if parts[0] == "TCP" and "LISTENING" not in line:
            continue
        local = parts[1]
        port = local.rsplit(":", 1)[-1]
        pid = parts[-1]
        if port.isdigit() and pid.isdigit():
            rows.append((int(port), int(pid)))
    return sorted(set(rows))


def parse_lsof(output):
    """Parse `lsof -iTCP -sTCP:LISTEN -P -n` into (port, pid, name) rows."""
    rows = []
    for line in output.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 9:
            continue
        name, pid = parts[0], parts[1]
        match = re.search(r":(\d+)$", parts[8])
        if match and pid.isdigit():
            rows.append((int(match.group(1)), int(pid), name))
    return sorted(set(rows))


def process_name(pid):
    try:
        if WINDOWS:
            out = subprocess.run(["tasklist", "/fi", "PID eq %d" % pid, "/fo", "csv", "/nh"],
                                 text=True, capture_output=True).stdout
            first = out.strip().split(",")[0].strip('"')
            return first or "?"
        with open("/proc/%d/comm" % pid, encoding="utf-8") as fh:
            return fh.read().strip()
    except (OSError, IndexError):
        return "?"


def listening():
    """Return [(port, pid, name)] for everything listening on this machine."""
    if WINDOWS:
        out = subprocess.run(["netstat", "-ano"], text=True, capture_output=True).stdout
        return [(port, pid, process_name(pid)) for port, pid in parse_netstat_windows(out)]
    try:
        out = subprocess.run(["lsof", "-iTCP", "-sTCP:LISTEN", "-P", "-n"],
                             text=True, capture_output=True).stdout
        if out.strip():
            return parse_lsof(out)
    except FileNotFoundError:
        pass
    out = subprocess.run(["ss", "-ltnp"], text=True, capture_output=True).stdout
    rows = []
    for line in out.splitlines()[1:]:
        match = re.search(r":(\d+)\s", line)
        pid_match = re.search(r"pid=(\d+)", line)
        if match:
            pid = int(pid_match.group(1)) if pid_match else 0
            rows.append((int(match.group(1)), pid, process_name(pid) if pid else "?"))
    return sorted(set(rows))


def is_free(port, host="127.0.0.1"):
    with socket.socket() as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) != 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("port", nargs="?", type=int, help="only show this port")
    ap.add_argument("--free", action="store_true",
                    help="just test whether the port is free (exit 0 if it is)")
    args = ap.parse_args(argv)

    if args.free:
        if args.port is None:
            ap.error("--free needs a port")
        free = is_free(args.port)
        print("port %d is %s" % (args.port, "free" if free else "in use"))
        return 0 if free else 1

    rows = listening()
    if args.port is not None:
        rows = [r for r in rows if r[0] == args.port]
        if not rows:
            print("nothing is listening on port %d" % args.port)
            return 1
    print("%-8s %-8s %s" % ("PORT", "PID", "PROCESS"))
    for port, pid, name in rows:
        print("%-8d %-8d %s" % (port, pid, name))
    if args.port is not None and rows:
        killer = "taskkill /PID %d /F" % rows[0][1] if WINDOWS else "kill %d" % rows[0][1]
        print("\nto stop it:  %s" % killer, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
