#!/usr/bin/python
import socket, mpd
from PyQt4 import Qt, QtGui, QtCore
from time import sleep, time, ctime
from os import popen, listdir
from os.path import expanduser, dirname, splitext

### CONFIGURATION OPTIONS ###

osdOnScreenTime = 7 # time the OSD will stay on screen

### INITIALIZATION ###

global text, lastCall # FIX: remove these
global conf
text = None
lastCall = time()

def mpdConfig(): # FIX: this should be more robust (i.e. remove the double quotes around option values automatically)
 d = {}
 file = open(expanduser('~') + '/.config/mpd/mpd.conf', 'r').readlines()
 for i in file:
  split = i.split()
  if len(split) == 2:
   d[split[0]] = split[1]
 return d

conf = mpdConfig()

def mpdGetPassword():
 if 'password' in conf:
  pw = conf['password']
  return pw[1:pw.find('@')]
 else:
  return None

password = mpdGetPassword()

def mpdMusicDir():
 if 'music_directory' in conf:
  return conf['music_directory'][1:-1]

musicdir = mpdMusicDir()

### FUNCTIONS ###

def ftime(time):
 time = int(time)
 return str(int(time/60)) + ':' + '%.2d' % int(time%60)

def jcText():
 # is jack_capture running?
 tmp = popen("ps -eo etime,cmd|grep '^[ ]*[0-9]*:[0-9]* jack_captu[r]e'", "r")
 txt = tmp.read()
 tmp.close()
 if len(txt) > 0:
  return chr(9679) + "(" + txt.split()[0] + ") "
 else:
  return ""

def volText():
 g = popen('amixer -c 2 get PCM').read().split()
 out = "vol: " + g[-3][1:-1]
 if g[-1] == '[off]':
  out += ' (muted)'
 return out

def timeText():
 return ctime()

def getDefaultText():
 return mpdText() + ' ' + volText() + '\n' + timeText()
 
def currentDir(tfile):
 return dirname(musicdir + '/' + tfile)

def isAnImage(filename):
 ext = splitext(filename)[1]
 return ext.lower() in ['.jpg', '.jpeg', '.bmp', '.png', '.gif']

def findImagesIn(directory):
 return list(filter(isAnImage, listdir(directory)))

def getCoverIn(directory): # FIX: improve this later
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

### FIX THESE ###

def readFromSocket():
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
 global osdOnScreenTime, lastCall, win
 app.processEvents()
 readFromSocket()
 if win.isVisible():
  message()
  win.raise_()
  if not text:
   if (time() - lastCall) > osdOnScreenTime: # hide the OSD
    win.hide()
  else: # text was provided
   if (time() - lastCall) > max(osdOnScreenTime, (len(text.split("\n")))):
    win.hide()

def place():
 global win
 xs = 0
 ys = 0
 for i in range(QtGui.QDesktopWidget().screenCount()):
  res = QtGui.QDesktopWidget().availableGeometry(i)
  xs = xs + res.width()
  ys = ys + res.height()
 x = win.frameSize().width()
 y = win.frameSize().height()
 # win.move(xs-(x+10), ys-(y+17))
 win.move(xs-(x+10), 1080-(y+17))

def mpvText():
 x = popen('ps x').read().split('\n')
 mplayer = None
 for i in x:
  if i.find('mplayer') != -1:
   mplayer = i[i.find('jack ')+5:]
 return mplayer

def mpdText(retrying=False):
 global win
 cs = win.mpdCurrentSong()
 ss = win.mpdStatus()
 if cs == None or ss == None:
  return "MPD is offline. " + jcText()
 else:
  if ss['state'] == 'stop':
   return "MPD is stopped. " + jcText()
  # artist
  try:
   artist = cs['artist']
  except KeyError:
   artist = ''
  # album
  try:
   album = cs['album']
  except KeyError:
   album = ''
  # title
  try:
   title = cs['title']
  except KeyError:
   title = ''
  # track
  try:
   track = cs['track']
   if type(track) == list:
    print("track value is: " + track)
    track = track[0]
  except:
   track = ''
  # playlist number
  try:
   num = str(int(ss['song'])+1)
  except KeyError:
   num = 'KeyError'
  # playlist length
  length = ss['playlistlength']
  # state
  if ss['state'] == 'play':
   state = chr(9654)
  else:
   state = chr(9632)
  if ss['consume'] == '1':
   consume = chr(5607) + ' '
  else:
   consume = ''
  # current time
  try:
   cur_time = ftime(ss['time'].split(':')[0])
  except KeyError:
   cur_time = "KeyError"
  # total time
  total_time = ftime(cs['time'])
  # random mode
  if ss['random'] == '0':
   random = chr(8594)
  else:
   random = chr(8644)
  return artist + ' - ' + title + '\n' + track + ' - ' + album + '\n' + num + '/' + length + ' ' + jcText() + consume + state + ' ' + cur_time + '/' + total_time + ' ' + random
 # else:
 #  return "MPD is offline. " + jcText()

def message():
 global win, text
 if not text:
  ntext = getDefaultText()
 else:
  ntext = text
 win.label.setText(ntext)
 updatePic()
 win.resize(win.sizeHint()) 
 app.processEvents()
 place()
 win.show()

def updatePic():
 global win
 cs = win.mpdCurrentSong()
 if cs == None or len(cs) == 0:
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
  win.piclabel.setPixmap(win.realPixmap.scaledToHeight(win.label.sizeHint().height(), 1)) # the 1 = smooth transformation.

class MyWindow(QtGui.QWidget):
 def __init__(self):
  QtGui.QMainWindow.__init__(self, None, QtCore.Qt.X11BypassWindowManagerHint | QtCore.Qt.WindowStaysOnTopHint)
  self.layout = QtGui.QHBoxLayout()
  self.layout.setMargin(0)
  self.layout.setSpacing(1)
  self.layout.setSizeConstraint(Qt.QLayout.SetFixedSize)
  self.setStyleSheet('color:white;background-color:black;font-size:8pt;')
  self.piclabel = Qt.QLabel()
  # self.piclabel.setStyleSheet('color:white;background-color:red;font-size:8pt;')
  self.piclabel.setSizePolicy(Qt.QSizePolicy.Minimum, Qt.QSizePolicy.Minimum)
  self.layout.addWidget(self.piclabel)
  self.label = Qt.QLabel()
  # self.label.setStyleSheet('color:white;background-color:black;font-size:8pt;')
  self.label.setAlignment(QtCore.Qt.AlignRight)
  self.label.setSizePolicy(Qt.QSizePolicy.Minimum, Qt.QSizePolicy.Minimum)
  self.layout.addWidget(self.label)
  self.setLayout(self.layout)
  self.mpd = None
  self.mpdConnect()
  self.cdir = None
  self.realPixmap = None

 def mpdConnect(self):
  if self.mpd == None:
   self.mpd = mpd.MPDClient()
   try:
    self.mpd.connect('localhost', 6600) # FIX: get this info from the mpd conf file
    # FIX: password
   except ConnectionRefusedError:
    self.mpd = None
  else:
   try:
    self.mpd.ping()
   except:
    self.mpd = None
    return self.mpdConnect()
  return self.mpd

 def mpdCurrentSong(self):
  mp = self.mpdConnect()
  if mp == None:
   return None
  else:
   return mp.currentsong()

 def mpdStatus(self):
  mp = self.mpdConnect()
  if mp == None:
   return None
  else:
   return mp.status()

 def hide(self):
  super(MyWindow, self).hide()
  
 def mouseReleaseEvent(self, ev):
  self.hide()

if __name__ == '__main__':
 global s
 # server
 s = socket.socket()
 s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 s.bind(('localhost', 9876))
 s.settimeout(0)
 s.listen(1)
 app = QtGui.QApplication([])
 win = MyWindow()
 win.show()
 text = "Started"
 message()
 while True:
  main()
  sleep(0.1)
