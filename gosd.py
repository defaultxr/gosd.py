#!/usr/bin/env python
# FIX: can use 'ffmpeg -i file.mp3 cover.png -y' to get the album cover from file.mp3 as a png. alternatively, exiftool also works.
import socket
import osdtext
from qtpy import QtWidgets, QtGui, QtCore
from time import sleep, time
from os import listdir
from os.path import dirname, splitext

### CONFIGURATION OPTIONS ###

osdOnScreenTime = 10 # time the OSD will stay on screen
style = 'color:"#F81894";background-color:"#111111";font-size:10pt;' # font color, background color, font size, etc.

### INITIALIZATION ###

text = None
lastCall = time()
musicdir = osdtext.mpdMusicDir()

### FUNCTIONS ###

# album cover functions

def currentDir(tfile):
  return dirname(musicdir + '/' + tfile)

def isAnImage(filename):
  ext = splitext(filename)[1]
  return ext.lower() in ['.jpg', '.jpeg', '.bmp', '.png', '.gif']

def findImagesIn(directory):
  return list(filter(isAnImage, listdir(directory)))

def getCoverIn(directory):
  results = findImagesIn(directory)
  res = None
  if len(results) > 0:
    for i in results:
      if i.lower().find('front') != -1:
        res = i
        break
      elif i.lower().find('cover') != -1:
        res = i
        break
    if res == None:
      results.sort()
      res = results[0]
  if res:
    return directory + '/' + res
  else:
    return None

# behavior/logic functions

def readFromSocket(): # process the data coming in from the socket
  global text, lastCall
  reply = '0'
  try:
    (a, b) = s.accept()
  except socket.error:
    pass
  else:
    received = str(a.recv(10000), 'utf-8').rstrip()
    if received == 'HIDE' or received == 'KILL':
      if not win.isVisible():
        reply = '1'
      win.hide()
    elif received == 'TOGGLE':
      if win.isVisible():
        win.hide()
      else:
        text = None
        lastCall = time()
        win.show()
    elif received == 'SHOW':
      text = None
      lastCall = time()
      win.show()
    else:
      text = received
      lastCall = time()
      win.show()
    a.send(bytes(reply + '\n', 'utf-8'))
    a.close()

def main():
  global osdOnScreenTime, lastCall, win, text
  app.processEvents()
  readFromSocket()
  if not win.isVisible():
    return
  if not text:
    ntext = osdtext.getText()
  else:
    ntext = text
  win.label.setText(ntext)
  updatePic()
  win.resize(win.sizeHint()) 
  app.processEvents()
  place()
  win.show()
  win.raise_()
  if not text:
    if (time() - lastCall) > osdOnScreenTime: # hide the OSD
      win.hide()
  else: # text was provided
    if (time() - lastCall) > max(osdOnScreenTime, (len(text.split("\n")))):
      win.hide()

# gui stuff

def updatePic():
  global win
  cs = osdtext.mpdCurrentSong()
  if cs == None or len(cs) == 0 or osdtext.mpdStatus()['state'] == 'stop':
    win.piclabel.clear()
    return
  curdir = currentDir(cs['file'])
  if win.cdir != curdir:
    win.cdir = curdir
    cover = getCoverIn(curdir)
    if cover:
      win.realPixmap = QtGui.QPixmap(cover)
    else:
      win.realPixmap = None
  if win.realPixmap == None:
    win.piclabel.clear()
  else:
    win.piclabel.setPixmap(win.realPixmap.scaledToHeight(win.label.sizeHint().height(), 1)) # 1 = linear interpolation for image scaling

def place():
  global win
  xs = 0
  ys = 0
  for i in range(2): # adjust this number to set which monitor you want the OSD to show up on. # FIX
    res = QtWidgets.QDesktopWidget().availableGeometry(i)
    xs = xs + res.width()
    ys = ys + res.height()
  x = win.frameSize().width()
  y = win.frameSize().height()
  # win.move(xs-(x+10), ys-(y+17))
  win.move(xs-(x+10), 1080-(y+17))

class MyWindow(QtWidgets.QWidget):
  def __init__(self):
    QtWidgets.QMainWindow.__init__(self, None, QtCore.Qt.X11BypassWindowManagerHint | QtCore.Qt.WindowStaysOnTopHint)
    self.layout = QtWidgets.QHBoxLayout()
    self.layout.setContentsMargins(0, 0, 0, 0)
    self.layout.setSpacing(1)
    self.layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
    self.setStyleSheet(style)
    self.piclabel = QtWidgets.QLabel()
    self.piclabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    self.layout.addWidget(self.piclabel)
    self.label = QtWidgets.QLabel()
    self.label.setAlignment(QtCore.Qt.AlignRight)
    self.label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    self.layout.addWidget(self.label)
    self.setLayout(self.layout)
    self.cdir = None
    self.realPixmap = None

  def hide(self):
    super(MyWindow, self).hide()
   
  def mouseReleaseEvent(self, ev):
    self.hide()

if __name__ == '__main__':
  global s # server
  s = socket.socket()
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind(('localhost', 9876))
  s.settimeout(0)
  s.listen(1)
  app = QtWidgets.QApplication([])
  win = MyWindow()
  win.show()
  text = "Started"
  while True:
    main()
    sleep(0.1)
