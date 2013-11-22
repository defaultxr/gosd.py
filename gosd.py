#!/usr/bin/python
import socket, mpd
from gi.repository import Gtk, Gdk
from gi.repository.Pango import font_description_from_string
from time import sleep, time, ctime
from os import popen
from cgi import escape

### CONFIGURATION OPTIONS ###

background = "#000"
foreground = "#FFF" # color of the text
osdOnScreenTime = 7 # time the OSD will stay on screen

### INITIALIZATION ###

# server
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('localhost', 9876))
s.settimeout(0)
s.listen(1)

# gui global variables
global visible, text, lastCall
visible = False
text = None
lastCall = time()

# mpd connection
m = None

### FUNCTIONS ###

def ftime(time):
 time = int(time)
 return str(int(time/60)) + ':' + '%.2d' % int(time%60)

def mpdGet(rec=False):
 global m
 if not m or rec:
  m = mpd.MPDClient()
  try:
   m.connect('localhost', 6600)
  except:
   return None
  else:
   return m
 else:
  return m

def readFromSocket():
 global text, lastCall
 try:
  (a, b) = s.accept()
 except socket.error:
  pass
 else:
  text = str(a.recv(10000), 'utf-8').rstrip()
  if text == 'HIDE' or text == 'KILL':
   hide()
  elif text == 'TOGGLE':
   if visible:
    hide()
   else:
    text = None
    lastCall = time()
    show()
  else:
   lastCall = time()
   show()
  a.close()

def main():
 global visible, osdOnScreenTime, lastCall, win
 Gtk.main_iteration_do(False)
 readFromSocket()
 if visible:
  message()
  win.present()
  if not text:
   if (time() - lastCall) > osdOnScreenTime: # hide the OSD
    hide()
  else: # text was provided
   if (time() - lastCall) > max(osdOnScreenTime, (len(text.split("\n")))):
    hide()

def hide():
 global visible, win, text
 visible = False
 win.hide()
 text = None

def show():
 global visible, win, lastCall
 win.show()
 win.present()
 visible = True

def damage(window, event):
 global win, visible
 if visible:
  win.present()
 
def place():
 global win
 x, y = win.get_size()
 win.move(Gdk.Screen.width()-(x+10), Gdk.Screen.height()-(y+17))
  
def getThumbnail(pic):
 """Returns either None if no thumbnail can be made, or the tkinter PhotoImage object if one has been made."""
 # FIX: this was copied from the old version, needs to be updated
 img = None
 if pic:
  if basename(pic)[-4:] == '.ppm':
   img = PhotoImage(file=pic)
  else:
   npic = dirname(pic) + '/.c_thumb.ppm' # we'll store the thumbnail in the same directory, but we'll call it .c_thumb.ppm
   system('convert -geometry 75x75 "%s" "%s"' % (pic, npic)) # we have to convert the image to .ppm because tkinter doesn't support most image formats.
   img = PhotoImage(file=npic)
 return img

def mplayerText():
 x = popen('ps x').read().split('\n')
 mplayer = None
 for i in x:
  if i.find('mplayer') != -1:
   mplayer = i[i.find('jack ')+5:]
 return mplayer

def mpdText(retrying=False):
 v = mpdGet()
 if v:
  try:
   cs = v.currentsong()
  except mpd.ConnectionError:
   if retrying:
    return "MPD is offline."
   else:
    mpdGet(True)
    return mpdText(True)
  except socket.error:
   mpdGet(True)
   return "Error."
  else:
   ss = v.status()
   if ss['state'] == 'stop':
    return "MPD is stopped."
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
   return artist + ' - ' + title + '\n' + track + ' - ' + album + '\n' + num + '/' + length + ' ' + consume + state + ' ' + cur_time + '/' + total_time + ' ' + random
 else:
  return "MPD is offline."

def volText():
 g = popen('amixer get Master').read().split()
 out = "vol: " + g[-3][1:-1]
 if g[-1] == '[off]':
  out += ' (muted)'
 return out

def timeText():
 return ctime()

def getDefaultText():
 return mpdText() + ' ' + volText() + '\n' + timeText()
 
def message():
 global win, text, visible
 if not text:
  ntext = getDefaultText()
 else:
  ntext = text
 win.label.set_markup('<small>' + escape(ntext) + '</small>')
 Gtk.main_iteration_do(False)
 if visible:
  place()
  show()
 
class MyWindow(Gtk.Window):
 def __init__(self):
  Gtk.Window.__init__(self, title="OSD", decorated=False, resizable=False, opacity=0.0, type=True)
  self.label = Gtk.Label(label="OSD server started.")
  self.label.modify_font(font_description_from_string("DejaVu Sans 10"))
  self.label.set_justify(Gtk.Justification.RIGHT)
  self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1))
  self.label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))
  self.hbox = Gtk.HBox()
  self.add(self.hbox)
  # self.image = Gtk.Image()
  # self.allocation = self.hbox.get_parent.get_allocation()
  # print(allocation.height)
  # desired_width = allocation.width
  # desired_height = allocation.height
  # self.image.set_from_file("/home/modula/splat1.gif")
  # self.pixbuf = self.image.get_pixbuf()
  # self.pixbuf = self.pixbuf.scale_simple(33, 33, 1)
  # self.image.set_from_pixbuf(self.pb)
  # self.image.scale_simple(33,33)
  # self.hbox.add(self.image)
  self.hbox.add(self.label)
  # self.hbox.remove(self.image)

if __name__ == '__main__':
 # global win, text
 win = MyWindow()
 win.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
 win.connect('button-press-event', lambda w, e: hide())
 win.connect("delete-event", Gtk.main_quit)
 win.connect('visibility-notify-event', damage)
 win.show_all()
 text = "Started"
 visible = True
 # message()
 while True:
  main()
  sleep(0.01)
