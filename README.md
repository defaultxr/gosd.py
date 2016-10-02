gosd.py
=======

simple ~~Gtk~~ Qt OSD written in python 3, designed for use with MPD.

I made this because i couldn't find any decent OSDs for MPD. This one simply does what it says on the tin.

How to Use
==========

Run `python gosd.py` and then you should see the word "Started" in the bottom right corner of your screen. That means the OSD is running. The message will disappear after a few seconds but the OSD is still running. To display it, simply call `python gosd_go.py`. This will make the OSD re-appear, showing you information about MPD, your current volume, and the date. If you want the OSD to go away sooner, you can just click on it.

For the most simple use, that's basically it. There are a few configuration options within gosd.py that you can edit near the top of the file; just simple colors for the text and background as well as how long the OSD stays on screen before disappearing again.

If you want the OSD to display something besides the default information, you can run gosd_go.py with a dash as an argument: `python gosd_go.py -`. gosd_go.py will read from standard input, and once it gets an 'End Of File' (usually you can make this by pressing ctrl+d), it will send all the text to gosd.py to be displayed. This can be very useful, for example, to display MPD's current playlist with pipes: `mpc playlist | python gosd_go.py -`. Alternatively, you can specify the text as the arguments: `python gosd_go.py hi there` will display "hi there" in the OSD.

If you want to hide the OSD without having to click on it, you can send the message "KILL" or "HIDE" to gosd.py like so: `python gosd_go.py KILL`.

TODO
====

Right now gosd.py is 'good enough' for me, but i do have plans to improve it:

* allow gosd_go.py to specify a different amount of time for a message to be displayed (i.e. so that longer messages stay on-screen longer) and then restore the original setting after the message is gone.
