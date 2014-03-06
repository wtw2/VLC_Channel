VLC_Channel
===========

Plex Media Server Channel Plugin

Currently for Windows.  __init__.py imports a couple libraries to check the status of the VLC process which was only coded for Windows.  Modifications may be required for non-Windows platforms.

There are some values like VLC_APP_PATH that are Windows based, and some Regex expressions like RE_LOC_MAP that are Windows based.

This channel is probably not ready for "plug and play" performance.  Some perseverance may be required.

Still working on trying to eliminate a very long delay (about 5 minutes) for Roku to start playing the stream.  At least it starts at the time when it first starts receiving the stream instead of when it actually starts displaying it several minutes later.

Read the Current Problems doc.

I can be contacted through the Plex Forum.
