#!/usr/bin/env python
import os, socket, mpd, shlex
from time import ctime

# You shouldn't need to edit this file, as it will automatically (attempt to) parse MPD's configuration file.
# Note that it will only parse until the first line ending in an opening curly bracket ({)
# so you should make sure your global MPD settings should come before that.

# configuration

music_directory = None # None = autodetect from MPD's configuration file.
password = None # None = autodetect from MPD's configuration file.

# utility functions

def ftime(time): # "format time". take a time in seconds and return a prettified string like 3:22
  time = int(time)
  return str(int(time/60)) + ':%.2d' % int(time%60)

# mpd stuff

global mpd_conf # the MPD configuration parsed as a dictionary.
mpd_conf = None

def mpdConfigFile():
  """Get the location of the MPD config file."""
  try:
    xdg_config_home = os.environ['XDG_CONFIG_HOME']
  except KeyError:
    xdg_config_home = os.path.expanduser('~/.config')
  possibilities = [xdg_config_home + '/mpd/mpd.conf', os.path.expanduser('~/.mpdconf'), os.path.expanduser('~/.mpd/mpd.conf'), '/etc/mpd.conf']
  try:
    possibilities += [os.environ['CONF_FILE']]
  except KeyError:
    pass
  for maybe in possibilities:
    if os.path.exists(maybe):
      return maybe

def mpdConfig(reparse=False):
  """Parse the MPD config file into a dictionary."""
  global mpd_conf
  if reparse or not mpd_conf:
    mpd_conf = {}
    with open(mpdConfigFile()) as inp:
      for line in inp.readlines():
        line = line.rstrip()
        split = shlex.split(line, comments=True)
        if line[-1] == '{':
          break
        if len(split) != 2:
          continue
        mpd_conf[split[0]] = split[1]
  return mpd_conf

def mpdConfigValue(key):
  conf = mpdConfig()
  if not key in conf:
    return None
  if key == 'password':
    pw = conf['password']
    return pw[1:pw.find('@')]
  if key == 'music_directory':
    global music_directory
    if music_directory:
      return music_directory
  return conf[key]

def mpdConnect():
  global mpdc
  if mpdc == None:
    mpdc = mpd.MPDClient()
    try:
      pw = mpdConfigValue('password')
      if pw:
        mpdc.password(pw)
      mpdc.connect('localhost', int(mpdConfigValue('port')))
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
  handle = os.popen('tmsu -D /media/music/.tmsu/db tags %s' % shlex.quote(file))
  tags = handle.read().rstrip()
  handle.close()
  tags = tags[tags.rfind(':')+1:]
  tags = tags.split()
  return tags

def tagSymbols(tags):
  res = str(len(tags))
  if "on.phone" in tags:
    res += "\N{BLACK TELEPHONE}"
  for good in ['good.song', 'good.album', 'good.artist']:
    if good in tags:
      res += "\N{HEAVY BLACK HEART}" # 💿 🎜
      break
  return res
 
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
  music_dir = mpdConfigValue('music_directory')
  tags = getTags(music_dir + '/' + file)
  albumtags = getTags(music_dir + '/' + albumdir)
  artisttags = getTags(music_dir + '/' + artistdir)
  return "A" + tagSymbols(artisttags) + " a" + tagSymbols(albumtags) + " t" + tagSymbols(tags) + " "

# other media players (not used)

# def mpvtext():
#   """Return text if mpv is playing. This doesn't actually work, though, and is not used."""
#   x = os.popen('ps x').read().split('\n')
#   mplayer = none
#   for i in x:
#     if i.find('mpv') != -1:
#       mplayer = i[i.find('jack ')+5:]
#   return mplayer

# jack_capture

def jcText():
  """Return the text representing the jack_capture status (i.e. shows a circle if it is)."""
  tmp = os.popen("ps -eo etime,cmd|grep '^[ ]*[0-9]*:[0-9]* jack_captu[r]e'", "r")
  txt = tmp.read()
  tmp.close()
  if len(txt) > 0:
    return chr(9679) + "(" + txt.split()[0] + ") "
  else:
    return ""

# volume

def volText():
  """Returns the text representing the current ALSA volume."""
  query = 'amixer'
  for line in os.popen(query).readlines():
    if '%' in line:
      split = line.split()
      vol = split[-2]
      on = split[-1]
      mutetext = ''
      if on != '[on]':
        mutetext = ' (muted)'
      return 'vol: ' + vol[1:-1] + mutetext

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
    if type(title) == list:
      title = ''.join(title)
    # disc number
    try:
      disc = cs['disc']
      if type(disc) == list:
        disc = disc[0] + '/' + disc[1]
      disc = 'd ' + disc + ' - ' # 💿🖸
    except KeyError:
      disc = ''
    # track
    try:
      track = cs['track']
      if type(track) == list:
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
    try:
      total_time = ftime(cs['time'])
    except KeyError:
      total_time = "KeyError"
    return artist + ' - ' + title + '\n' + disc + track + ' - ' + album + '\n' + tagText() + num + '/' + length + ' ' + jcText() + single + consume + state + ' ' + cur_time + '/' + total_time + ' ' + random

def getText():
  """The actual function called to get the full default text of the OSD."""
  return mpdText() + ' ' + volText() + '\n' + ctime()

mpdc = None
mpdConnect()

if __name__ == '__main__':
  print(getText())
