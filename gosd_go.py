#!/usr/bin/env python
# show, toggle, or hide the OSD.
# with a dash as the sole argument, read from stdin and send that text to the OSD to display it.
# if the arguments aren't either "-" or "osd", the arguments are treated as the text the OSD should display.

# returns 0 on success (almost all cases), or 1 on failure.
# the only real "failure" condition is if you try to hide the OSD when it's already hidden.

import socket
from sys import argv, stdin

s = socket.socket()
s.connect(('localhost', 9876))
if len(argv) > 1:
 if argv[1] == '-':
  s.send(bytes(stdin.read(), 'utf-8'))
 elif len(argv) == 2 and argv[1] == 'osd':
  s.send(bytes("SHOW\n", 'utf-8'))
 else:
  txt = " ".join(argv[1:])
  s.send(bytes(txt, 'utf-8'))
else:
 s.send(bytes("SHOW\n", 'utf-8'))
response = str(s.recv(10), 'utf-8').rstrip()
s.close()
exit(int(response))
