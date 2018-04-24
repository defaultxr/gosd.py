#!/usr/bin/env python
import socket
import osdtext
from PyQt4 import Qt, QtGui, QtCore
from time import sleep, time
from os import listdir
from os.path import dirname, splitext

### CONFIGURATION OPTIONS ###

osdOnScreenTime = 10 # time the OSD will stay on screen

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
  try:
    (a, b) = s.accept()
  except socket.error:
    pass
  else:
    text = str(a.recv(10000), 'utf-8').rstrip()
    if text == 'HIDE' or text == 'KILL':
      win.hide()
    elif text == 'TOGGLE':
      if win.isVisible():
        win.hide()
      else:
        text = None
        lastCall = time()
        win.show()
    else:
      lastCall = time()
      win.show()
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
      win.realPixmap = Qt.QPixmap(cover)
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
  for i in range(2): # adjust this number
    res = QtGui.QDesktopWidget().availableGeometry(i)
    xs = xs + res.width()
    ys = ys + res.height()
  x = win.frameSize().width()
  y = win.frameSize().height()
  # win.move(xs-(x+10), ys-(y+17))
  win.move(xs-(x+10), 1080-(y+17))

class MyWindow(QtGui.QWidget):
  def __init__(self):
    QtGui.QMainWindow.__init__(self, None, QtCore.Qt.X11BypassWindowManagerHint | QtCore.Qt.WindowStaysOnTopHint)
    self.layout = QtGui.QHBoxLayout()
    self.layout.setMargin(0)
    self.layout.setSpacing(1)
    self.layout.setSizeConstraint(Qt.QLayout.SetFixedSize)
    self.setStyleSheet('color:white;background-color:black;font-size:8pt;')
    self.piclabel = Qt.QLabel()
    self.piclabel.setSizePolicy(Qt.QSizePolicy.Minimum, Qt.QSizePolicy.Minimum)
    self.layout.addWidget(self.piclabel)
    self.label = Qt.QLabel()
    self.label.setAlignment(QtCore.Qt.AlignRight)
    self.label.setSizePolicy(Qt.QSizePolicy.Minimum, Qt.QSizePolicy.Minimum)
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
  app = QtGui.QApplication([])
  win = MyWindow()
  win.show()
  text = "Started"
  while True:
    main()
    sleep(0.1)
