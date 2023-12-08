#!/usr/bin/env python
import os, os.path, time, socket, osdtext
from qtpy import QtWidgets, QtGui, QtCore

# NOTES:
# - "Pop-ups, notifications, and all similar windows should be mapped as WM_TRANSIENT_FOR and/or _NET_WM_WINDOW_TYPE_DIALOG windows, as has been explained by the ICCCM and the FreeDesktop EWMH specifications for decades" - https://www.jwz.org/xscreensaver/faq.html#popup-windows

# TODO/FIX:
# - can use 'ffmpeg -i file.mp3 cover.png -y' to get the album cover from file.mp3 as a png. alternatively, exiftool also works.

# configuration

osdOnScreenTime = 10 # time in seconds that the OSD will stay on screen
style = 'color:"#F81894";background-color:"#111111";font-size:10pt;' # font color, background color, font size, etc.
screenNumber = 0 # which monitor the OSD should appear on.
osdOffset = (10, 17) # the OSD's offset from the corner of the screen

# code

text = None
lastCall = time.time()

# album cover functions

def isAnImage(filename):
  ext = os.path.splitext(filename)[1]
  return ext.lower() in ['.bmp', '.gif', '.jpeg', '.jpg', '.png', '.webp']

def findImagesIn(directory):
  return list(map(lambda i: os.path.join(directory, i), filter(isAnImage, os.listdir(directory))))

def isCoverLike(filename):
  f = filename.lower()
  for m in ['front', 'cover']:
    if m in f:
      return True
  return False

def getCoverIn(directory):
  images = findImagesIn(directory)
  if len(images) == 0:
    return None
  if len(images) == 1:
    return images[0]
  try:
    coverLike = next(filter(isCoverLike, images))
  except StopIteration:
    images.sort()
    return images[0]
  else:
    return coverLike

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
    if received == 'HIDE':
      if not win.isVisible():
        reply = '1'
      win.hide()
    elif received == 'TOGGLE':
      if win.isVisible():
        win.hide()
      else:
        text = None
        lastCall = time.time()
        win.show()
    elif received == 'SHOW':
      text = None
      lastCall = time.time()
      win.show()
    else:
      text = received
      lastCall = time.time()
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
  place(win)
  win.show()
  win.raise_()
  if not text:
    if (time.time() - lastCall) > osdOnScreenTime:
      win.hide()
  else: # text was provided
    if (time.time() - lastCall) > max(osdOnScreenTime, (len(text.split("\n")))):
      win.hide()

# gui stuff

def updatePic():
  global win
  cs = osdtext.mpdCurrentSong()
  if cs == None or len(cs) == 0 or osdtext.mpdStatus()['state'] == 'stop':
    win.piclabel.clear()
    return
  curdir = os.path.dirname(os.path.join(osdtext.mpdConfigValue('music_directory'), cs['file']))
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

def place(win):
  """Place the window in the correct position on the screen."""
  screenBottomRight = QtWidgets.QDesktopWidget().availableGeometry(screenNumber).bottomRight()
  screenBottomRight = [screenBottomRight.x(), screenBottomRight.y()]
  frameSize = win.frameSize()
  frameSize = [frameSize.width(), frameSize.height()]
  zipped = zip(screenBottomRight, [-1 * i for i in osdOffset], [-1 * i for i in frameSize])
  loc = [sum(item) for item in zipped]
  win.move(*loc)

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
    time.sleep(0.1)
