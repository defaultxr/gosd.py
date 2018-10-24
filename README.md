gosd.py
=======

A simple Qt OSD written in Python 3 and designed for use with [MPD](https://www.musicpd.org/).

I made this because I ffcouldn't find any OSDs I liked. This OSD shows the following information by default:

- MPD now playing information (artist, song title, track number, album).
- Whether the artist directory, album directory, and track itself are tagged with [TMSU](https://tmsu.org/).
- Index of the current track in MPD's playlist, and the total playlist length.
- Whether jack_capture is running (represented with ●).
- Whether MPD's "single" mode is on (represented with 🗘)
- Whether MPD is in consume mode (represented with ᗧ).
- MPD status (i.e. playing or paused, represented with ▶ and ■).
- Current time and total time of the track.
- MPD random mode (i.e. random or no random, represented with ⇄ and →).
- ALSA volume.
- Current time and date.
- Thumbnail of the album cover of the current track, if an image of such appears in the directory of the track.

It also has the following features:

- Automatically updates the displayed information while visible.
- Automatically hides after 10 seconds (by default), or can be manually hidden by clicking on the OSD or with `python gosd_go.py HIDE`.
  - When other text is specified, the length of time it is shown on screen depends on the number of lines in the text (the default hide time, or 1 second per line, whichever is greater).
- Somewhat easy to customize (if you know Python); just edit the `osdtext.py` file.

It has the following problems:

- Written in Python (which is slow, though it's not a huge problem in this case). In the (probably far) future I'd like to rewrite this in Rust.
- User customizations must be done by editing the source of the script itself.
- No functionality to detect the number of screens you have, nor to easily change the position of the OSD (you'll need to edit the `place` function in `gosd.py`).
- Plenty others.

How to Use
==========

Run `python gosd.py &` and then you should see the word "Started" in the bottom right corner of your screen. That means the OSD is running. The message will disappear after a few seconds, but the OSD is still running. To display it, simply call `python gosd_go.py`. This will make the OSD re-appear, showing you the default text. If you want the OSD to go away sooner, you can click on it or use the command `python gosd_go.py HIDE`.

If you want the OSD to display something else, you can run gosd_go.py with a dash as an argument: `python gosd_go.py -`. gosd_go.py will read from standard input, and once it gets an 'End Of File' (usually you can make this by pressing `ctrl+d`), it will send all the text to the gosd process to be displayed. This can be very useful, for example, to display MPD's current playlist with pipes: `mpc playlist | python gosd_go.py -`. Alternatively, you can specify the text as the arguments: `python gosd_go.py hi there` will display "hi there" in the OSD.

TODO
====

Right now gosd.py is "good enough" for me, but I do want to improve a few things:

- Improve the command-line argument syntax of `gosd_go.py`.

- Allow specifying the hide time on the command line.

- Allow specifying the text alignment on the command line.

- Hide the album cover when showing something other than the default text.
