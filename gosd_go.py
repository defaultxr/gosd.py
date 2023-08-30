#!/usr/bin/env python
# gosd_go.py - Show, toggle, or hide the OSD.
# With a dash as the sole argument, it will send the text read from stdin to the OSD to display it.
# Arguments other than "-" or "osd" are treated as text to be displayed by the OSD.
# Returns 0 on success, 1 if attempting to hide an already-hidden OSD, 2 on timeout, or 3 on some other type of error.

import sys, socket

if __name__ == '__main__':
  s = socket.socket()
  s.settimeout(2)
  try:
    s.connect(('localhost', 9876))
    if len(sys.argv) > 1:
      if sys.argv[1] == '-':
        s.send(bytes(sys.stdin.read(), 'utf-8'))
      elif len(sys.argv) == 2 and argv[1] == 'osd':
        s.send(bytes("SHOW\n", 'utf-8'))
      else:
        txt = " ".join(sys.argv[1:])
        s.send(bytes(txt, 'utf-8'))
    else:
      s.send(bytes("SHOW\n", 'utf-8'))
    response = str(s.recv(10), 'utf-8').rstrip()
    s.close()
    exit(int(response))
  except TimeoutError:
    exit(2)
  except:
    exit(3)
