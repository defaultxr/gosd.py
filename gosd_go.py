#!/usr/bin/env python
import socket
from sys import argv, stdin
from time import sleep

s = socket.socket()
s.connect(('localhost', 9876))
if len(argv) > 1:
 if argv[1] == '-':
  s.send(bytes(stdin.read(), 'utf-8'))
 elif len(argv) == 2 and argv[1] == 'osd':
  s.send(bytes("", 'utf-8'))
 else:
  s.send(bytes(" ".join(argv[1:]), 'utf-8'))
sleep(0.05)
s.close()
