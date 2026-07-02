import socket

import portcheck

NETSTAT = """
Active Connections

  Proto  Local Address          Foreign Address        State           PID
  TCP    0.0.0.0:3000           0.0.0.0:0              LISTENING       4242
  TCP    127.0.0.1:5432         0.0.0.0:0              LISTENING       991
  TCP    127.0.0.1:9999         127.0.0.1:1            ESTABLISHED     12
"""

LSOF = """COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
node    4242 you   23u  IPv4  1234      0t0  TCP *:3000 (LISTEN)
postgres 991 you    7u  IPv4  5678      0t0  TCP 127.0.0.1:5432 (LISTEN)
"""


def test_parse_netstat_finds_listeners():
    assert (3000, 4242) in portcheck.parse_netstat_windows(NETSTAT)

def test_parse_netstat_skips_established():
    ports = [p for p, _ in portcheck.parse_netstat_windows(NETSTAT)]
    assert 9999 not in ports
