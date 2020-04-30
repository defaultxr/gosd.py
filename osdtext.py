#!/usr/bin/env python
import socket, mpd
from os import popen
from os.path import expanduser
from time import ctime
from shlex import quote

# utility functions

def ftime(time): # "format time". take a time in seconds and return a prettified string like 3:22
  time = int(time)
  return str(int(time/60)) + ':%.2d' % int(time%60)

# unused / WIP mpd stuff

global conf
def mpdConfig(): # FIX: this should be more robust (i.e. remove the double quotes around option values automatically)
  """Parse the MPD config file to get the necessary information from it."""
  d = {}
  file = open(expanduser('~/.config/mpd/mpd.conf'), 'r').readlines() # FIX: use $XDG_CONFIG_DIR instead
  for i in file:
    split = i.split()
    if len(split) == 2:
      d[split[0]] = split[1]
  return d

conf = mpdConfig()

def mpdGetPassword():
  """Return the MPD password as parsed from the config file."""
  if 'password' in conf:
    pw = conf['password']
    return pw[1:pw.find('@')]
  else:
    return None

password = mpdGetPassword()

def mpdMusicDir():
  """Return the directory where the music is stored, as parsed from the MPD config file."""
  if 'music_directory' in conf:
    return conf['music_directory'][1:-1]

# actual mpd stuff

def mpdConnect():
  global mpdc
  if mpdc == None:
    mpdc = mpd.MPDClient()
    try:
      mpdc.connect('localhost', 6600) # FIX: get this info from the mpd conf file
      # FIX: password
    except ConnectionRefusedError:
      mpdc = None
  else:
    try:
      mpdc.ping()
    except:
      mpdc = None
      return mpdConnect()
  return mpdc

def mpdCurrentSong():
  mp = mpdConnect()
  if mp == None:
    return None
  else:
    return mp.currentsong()

def mpdStatus():
  mp = mpdConnect()
  if mp == None:
    return None
  else:
    return mp.status()

# tmsu tag functions

def getTags(file):
  """Get the tmsu tags of FILE."""
  handle = popen('tmsu -D /media/music/.tmsu/db tags %s' % quote(file))
  tags = handle.read().rstrip()
  handle.close()
  tags = tags[tags.rfind(':')+1:]
  tags = tags.split()
  return tags
 
def tagText():
  """Return the text representing whether the current artist and album directories, and the current track are tagged with TMSU."""
  cs = mpdCurrentSong()
  if cs == None:
    return ''
  file = cs['file']
  albumdir = '/'.join(file.split('/')[:-1])
  artistdir = '/'.join(file.split('/')[:-2])
  if artistdir == '': # this seems to fix the problem when songs are in the artist directory directly instead of being in an album directory
    artistdir = albumdir
    albumdir = ''
  tags = getTags('/media/music/' + file)
  albumtags = getTags('/media/music/' + albumdir)
  artisttags = getTags('/media/music/' + artistdir)
  res = ""
  if "good.song" in tags:
    res = res + "\N{HEAVY BLACK HEART}"
  try:
    tags.remove('good.song')
  except:
    pass
  if len(tags) > 0:
    res = "T" + res
  if len(albumtags) > 0:
    res = "a" + res
  if len(artisttags) > 0:
    res = "A" + res
  res = res + " "
  return res

# other media players (not used)

# def mpvtext():
#   """Return text if mpv is playing. This doesn't actually work, though, and is not used."""
#   x = popen('ps x').read().split('\n')
#   mplayer = none
#   for i in x:
#     if i.find('mpv') != -1:
#       mplayer = i[i.find('jack ')+5:]
#   return mplayer

# jack_capture

def jcText():
  """Return the text representing the jack_capture status (i.e. shows a circle if it is)."""
  tmp = popen("ps -eo etime,cmd|grep '^[ ]*[0-9]*:[0-9]* jack_captu[r]e'", "r")
  txt = tmp.read()
  tmp.close()
  if len(txt) > 0:
    return chr(9679) + "(" + txt.split()[0] + ") "
  else:
    return ""

# volume

def volText():
  """Returns the text representing the current ALSA volume."""
  g = popen('amixer -c 1 get Master').read().split()
  out = "vol: " + g[-3][1:-1]
  if g[-1] == '[off]':
    out += ' (muted)'
  return out

# date and time

def timeText():
  """Returns the date and time string."""
  return ctime()

# mpd information

def mpdText(retrying=False):
  """Returns the text showing MPD information."""
  global mpdc
  cs = mpdCurrentSong()
  ss = mpdStatus()
  if cs == None or ss == None:
    return "MPD is offline. " + jcText()
  else:
    # random mode
    if ss['random'] == '0':
      random = chr(8594)
    else:
      random = chr(8644)
    if ss['state'] == 'stop':
      return "MPD is stopped. " + random + ' ' + jcText()
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
    if ss['single'] == '1':
      single = chr(128472) + ' '
    else:
      single = ''
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
    return artist + ' - ' + title + '\n' + track + ' - ' + album + '\n' + tagText() + num + '/' + length + ' ' + jcText() + single + consume + state + ' ' + cur_time + '/' + total_time + ' ' + random

def getText():
  """The actual function called to get the full default text of the OSD."""
  return mpdText() + ' ' + volText() + '\n' + timeText()

mpdc = None
mpdConnect()

if __name__ == '__main__':
  print(getText())
