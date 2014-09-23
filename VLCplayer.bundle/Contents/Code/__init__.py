# import for regular expressions
#import re => Use Plex Framework: Regex() etc.
#import datetime => Use Plex Framework: Datetime
#import time -> for sleep => Use Plex Framework: Thread.Sleep()
# for more complex json
#import demjson => Use Plex Framework: JSON
# => urllib.urlopen('http://:ok@127.0.0.1:5555/requests/status.json') works
#import urllib # for urlopen => Use Plex Framework: HTTP.Request() & HTTP.SetPassword()

# Used in: AppHandleCheck(); StopApp(); AppRunning(); StartApp()
# to launch/exit/get_info an application
import os, subprocess, signal # for os.path and os.kill
import ctypes # for ctypes.windll
import errno
#import socket -> see MainMenu(0
# for processing CSV strings
#import csv => csv not needed, regex can do it, see: AppRunning()
#import ast # for literal_eval  => Use Plex Framework: JSON -> encode Dict parameters for Callbacks

####################################################################################################
# DEVELOPMENT LINKS:
#
# http://cs6-8v4.vk.me/p15/822f5915a041.360.mp4 -> 4/1/2014
#
#  Plex:
# http://dev.plexapp.com/docs/api/constkit.html
# http://dev.plexapp.com/docs/genindex.html
# http://dev.plexapp.com/docs/api/objectkit.html
# http://127.0.0.1:32400/  -> XML about PMS
# http://localhost:32400/web  -> Plex/Web
# http://127.0.0.1:32400/video/vlcplayer  -> XML about this channel
#
# C:\Users\User\AppData\Local\Plex Media Server\Transcoding -> temp HLS files
#
# URL decode/encode: http://meyerweb.com/eric/tools/dencoder/
#
# Great regex tester -> http://regex101.com/
#
#  VLC:
# https://wiki.videolan.org/MPEG/
# https://wiki.videolan.org/Media_resource_locator/
# https://wiki.videolan.org/Documentation:Streaming_HowTo/Advanced_Streaming_Using_the_Command_Line/
#
# http://:ok@127.0.0.1:5555/requests/README.txt
# http://www.videolan.org/developers/vlc/share/lua/intf/modules/httprequests.lua
# https://wiki.videolan.org/VLC_HTTP_requests/
# https://wiki.videolan.org/Documentation:Advanced_Use_of_VLC/
# http://www.videolan.org/doc/play-howto/en/apb.html
#
# Macros/websites:
# the html files go in:
# C:\Program Files (x86)\VideoLAN\VLC\lua\http
# see:  http://www.videolan.org/doc/play-howto/en/apb.html
# http://n0tablog.wordpress.com/2009/02/09/controlling-vlc-via-rc-remote-control-interface-using-a-unix-domain-socket-and-no-programming/
#
####################################################################################################
# VLC output parameters:
#1) :sout=#transcode{vcodec=h264,vb=800,acodec=mpga,ab=128,channels=2,samplerate=44100}:http{mux=ts,dst=:11223/stream.ts} :sout-all :sout-keep
# vb = video bitrate: kbps
# ab = audio bitrate: kbps
# fps = frames per second -> changing the fps may result in significant video anomalies
# width
# height
# acodec = mpga => MPEG layer 1 (MP1) or MPEG layer 2 (MP2)
# acodec = mp2a => MPEG layer 2 (MP2)
# acodec = mp3 => MPEG layer 3 (MP3)
	# Playing a file using acodec=mp3 often causes VLC to crash
	# https://trac.videolan.org/vlc/login
# mux = ts => MPEG2 Transport Stream; es - Elementry Stream; ps - Program Stream (.vob files)
# NTSC 486i - 243 interlaced (240p: 320x240), 29.97 fps, 4:3 (WxH; aspect=w:h)
# 360p - 480x360 - 4:3 | 640x360 - 16:9
# 480p - 720x480
# 720p - 1280x720
# 1080p - 1920x1080
# an alternative:
####################################################################################################
# IMPORTANT: READ! (especially "Work in Progress")
# https://plexapp.zendesk.com/hc/en-us/articles/201382293-A-GitHub-Guide-To-Fixing-a-Channel
####################################################################################################
#	Device uri
# https://wiki.videolan.org/Documentation:Advanced_Use_of_VLC/
# 
# DVD with menus=> vlc dvd://[device][@raw_device][@[title][:[chapter][:angle]]]
# DVD without menus=> vlc dvdsimple://[device][@raw_device][@[title][:[chapter][:angle]]]
# VCD=> vlc vcd://[device][@{E|P|E|T|S}[number]]
# Audio CD=> vlc cdda://[device][@[track]]
# 
# HTTP stream=> vlc http://www.example.org/your_file.mpg
# RTSP stream=> vlc rtsp://www.example.org/your_stream
# SSM (source specific multicast) stream=> vlc rtp://server_address.com@multicast_address.com:port
# Unicast RTP/UDP stream (sent by VLC's stream output)=> vlc  rtp://@:5004
# Multicast UDP/RTP stream (sent by VLC's stream output)=> vlc rtp://@multicast_address.com:port
# 
####################################################################################################
# Last updated: 03/28/2014
#
# Plex Settings:
#		Advanced: Channels > Number of seconds to wait before a plugin times out = 30
#		Advanced: Transcoder > Segmented transcoder timeout = 60
#
#	Plex/Web postback/function timeout: (this is not a problem on Roku)
#	C:\Users\User\AppData\Local\Plex Media Server\Plug-ins\WebClient.bundle\Contents\Resources\js\plex.js
#	line 1073; change 2 instances of: {timeout:4e4} to {timeout:6e4} -> 60 seconds
#	line 1799; add argument {timeout:6e4} to this.model.fetch() -> settings timeout
#
# The best/cleanest output stream for Plex to transcode for Roku is:
#	transcode{vcodec=h264,acodec=mpga,ab=128,channels=2,samplerate=44100}
#	it appears the VLC AAC audio encoding is not clean and needs to be transcoded by Plex to play on Roku.
#
# Issues:
# When adding a DirectoryObject to an ObjectContainer (and nothing else), there must be at least two
#	before a thumb and the summary text will appear.
#
# Once the VideoClipObject icon is added to the ObjectContainer and displayed, it cannot be removed
#	from the MainMenu display. Re-entering the channel does not remove it even with no_cache=True.
#	The webpage must be refreshed to remove it. (for Plex/Web integrated only)
#
# When using the URL Service, once the stream is playing, if you back up one level and select play again
#	it will start a download (YouTube and Khan transfer you to their website). (for Plex/Web integrated only)
#
# Streams can take a long time before they appear on the Roku (like 6 minutes)
#
# From schuyler/sullman @ https://github.com/plexinc/roku-client-public/issues/174
# The amount the Roku buffers is entirely up to the Roku. We give the Roku a URL to play, the video player is entirely part of the Roku firmware. The amount that it chooses to load before starting the video is similarly up to the Roku video player. And to be honest, it's quite quirky. There are a variety of unexpected things that affect how much data the Roku wants.
#
####################################################################################################

PREFIX       = '/video/vlcplayer'
NAME         = 'VLC Player'
TITLE        = 'VLC Plugin'
ART          = 'art-default.jpg'
ICON         = 'icon-vlc.png'
# http://www.iconarchive.com/search?q=arrows
T_PLAY       = 'button_blue_play.png'
T_PAUSE      = 'button_blue_pause.png'
T_STOP       = 'button_blue_stop.png'
T_REFRESH    = 'refresh-icon.png' #'gtk-refresh.png' #'button_blue_repeat.png'
T_STATUS     = 'Status-dialog-information-icon.png' #'FAQ-icon.png'
T_PLAYLIST   = 'Status-media-playlist-repeat-icon.png'
T_RIGHT      = 'Arrow-turn-right-icon.png'
T_LEFT       = 'Arrow-turn-left-icon.png'
T_DELETE     = 'Close-icon.png'
T_SYNC       = 'gtk-refresh.png'
T_MOVIE_SEL  = 'Movies-icon.png'
T_MOVIE      = 'videos-icon.png'
T_EMPTY      = 'Dossier-jaune-icon.png'
#URL_VLC      = 'http://%s:%s' % (Prefs['vlc_host'], Prefs['vlc_port_stream']) # filled once on start (static)
VLC_APP_PATH = 'C:\Program Files (x86)\VideoLAN\VLC\\'
VLC_APP_FILE = 'vlc.exe'
VLC_APP      = VLC_APP_PATH + VLC_APP_FILE + ' '
VLC_LOG      = ' --extraintf=http:logger --verbose=2 --file-logging --logfile=vlc-log.txt'
# C:\Users\User\AppData\Local\Plex Media Server\Plug-in Support\Data\com.plexapp.plugins.vlcplayer\vlc-log.txt
# The following line produces AAC audio encoding, but it does not seems to be working to Plex/Roku standards
VLC_MP4A     = ' --sout-avcodec-strict=-2' # for 2.1.x, for 2.0.x use ' --sout-ffmpeg-strict=-2'
# --network-caching=<integer [0 .. 60000]> (ms)
VLC_ARGS0    = ' --network-caching=60000 --sout-transcode-threads 3 --sout=#'
#VLC_ARGS1    = 'transcode{vcodec=h264,vb=800,acodec=mpga,ab=128,channels=2,samplerate=44100}'
#VLC_ARGS1a   = 'mux=ts'
#VLC_ARGS2    = 'http{%sdst=:%s/%s}' # short notation
VLC_ARGS2    = 'standard{access=http,%sdst=:%s/%s}'
VLC_ARGS2a   = ' --sout-all --sout-keep'
VLC_ARGS3    = ' --extraintf=http --http-host=%s --http-port=%s --http-password=%s'
VLC_ADR      = 'http://%s:%s'
VLC_ADR2     = 'http://:%s@%s:%s'
VLC_REQ      = '/requests/'
VLC_STAT     = 'status.xml'
VLC_PL       = 'playlist.xml'
VLC_BR       = 'browse.xml'
VLC_META     = 'status.json'
VLC_COM      = '?command='
VLC_CON      = '/?control='
RE_VLC_W     = Regex('.*width=([^,|}]+)') # xml
RE_VLC_H     = Regex('.*height=([^,|}]+)') # xml
RE_VLC_AC    = Regex('.*acodec=([^,|}]+)') # xml
RE_VLC_VC    = Regex('.*vcodec=([^,|}]+)') # xml
RE_VLC_CH    = Regex('.*channels=([^,|}]+)') # xml
RE_VLC_FPS   = Regex('.*fps=([^,|}]+)') # xml
RE_VLC_MUX   = Regex('.*mux=([^,|}]+)') # xml
RE_VLC_COD   = Regex('.*\(([^\)]+)\)$')
PLEX_PREFS   = 'http://localhost:32400/:/plugins/com.plexapp.plugins.vlcplayer/prefs/set?'

VLC_HLS      = ''
# VLC HTTP Live Stream (this is not HLS or DASH as it does not send a live stream, a server is requird to stream the files)
# The HLS process creates a series of files from the stream.  Could this be faster and better than trying to view the stream on the fly?
# From=> https://wiki.videolan.org/Documentation:Streaming_HowTo/Streaming_for_the_iPhone/
# See also=> http://en.wikipedia.org/wiki/HTTP_Live_Streaming
# "C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"  file:///C:/Users/User/Videos/Physics%20videos/Videos%20360p/Anti-Gravity%20_%20Cold%20Fusion%20Explained%20In%20Detail_%20A%20New%20Era%20In%20Physics%20Pt.%202.flv  --network-caching=60000 --sout=#transcode{vcodec=h264,vb=800,venc=x264{aud,profile=baseline,level=30,keyint=30,ref=1},acodec=mpga,ab=128,channels=2,samplerate=44100}:standard{access=livehttp{seglen=60,delsegs=true,numsegs=0,index=C:\VLCstreaming\stream.m3u8,index-url=C:/VLCstreaming/mystream-###.ts},mux=ts{use-key-frames},dst=/VLCstreaming/mystream-###.ts}

ST_JSON_MAP  = '.*\"(?P<key>%s)\":(?:(?P<dq>\")|(?P<cy>{)|)(?P<val>(?(dq)[^"]*)|(?(cy)[^}]*)|(?:[\d]*\.?[\d]*))(?:(?(dq)\"|(?(cy)})))(?:,|$|\s)' # no nested braces (simple JSON)
ST_DOM_MAP    = '(?:(?:[0-9a-zA-Z_-]+\.){1,3})[a-zA-Z]{2,4}' # internet domain name pattern
RE_DOM_MAP    = Regex('^%s$' % (ST_DOM_MAP))
ST_IP_MAP     = '(?:[0-9]{1,3}\.){3}[0-9]{1,3}'
RE_IP_MAP     = Regex('^%s$' % (ST_IP_MAP))
ST_PORT_MAP   = '[1-9][0-9]{0,5}'
RE_PORT_MAP   = Regex('^%s$' % (ST_PORT_MAP))
ST_PATH_MAP   = '(?P<path>(?P<path2>/)(?(path2)(?:[0-9a-zA-Z ()_-]+/)+))?' # added space character and parentheses
ST_FILE_MAP   = '(?P<file>[0-9a-zA-Z _\-\.]+\.[0-9a-zA-Z]{2,4})?' # added space character
ST_FILE_MAP2  = '((?:[0-9a-zA-Z _\-]+(?P<dot>\.))*(?(dot)[0-9a-zA-Z]{2,4}|[0-9a-zA-Z_\-]*))?' # added space character
ST_PAGE_MAP   = '%s(?(path2)|/?)%s' % (ST_PATH_MAP, ST_FILE_MAP) # WARNING: allows for filename only (initial slash optional)
ST_PAGE_MAP2  = '%s(?(path2)|/?)%s' % (ST_PATH_MAP, ST_FILE_MAP2) # WARNING: allows for filename only (initial slash optional)
RE_PAGE_MAP   = Regex('^%s$' % (ST_PAGE_MAP)) # path is group('path'), file is group('file')
ST_URL_MAP    = 'http://%s:%s%s' % (ST_IP_MAP, ST_PORT_MAP, ST_PAGE_MAP)
RE_URL_MAP    = Regex('^%s$' % (ST_URL_MAP))
ST_URL_MAP2   = '(?:(http|mms|rtsp)|(?P<rtp>rtp|udp))://(?(rtp)(?:%s)?@)(?(rtp)(?:%s)?|%s)(?(rtp):%s)?(?(rtp)|%s)' % (ST_DOM_MAP, ST_DOM_MAP, ST_DOM_MAP, ST_PORT_MAP, ST_PAGE_MAP2)
RE_URL_MAP2   = Regex('^%s$' % (ST_URL_MAP2))
ST_LOC_MAP    = '(?P<loc>(?:[a-zA-Z]:)|(?:%%[a-zA-Z_]+%%))' # must use % to escape % in string
RE_LOC_MAP    = Regex(ST_LOC_MAP) # location, like: C: or %PROGRAMFILES% or %LOCALAPPDATA%
ST_FQFILE_MAP = '%s%s' % (ST_LOC_MAP, ST_PAGE_MAP)
RE_FQFILE_MAP = Regex('^%s$' % (ST_FQFILE_MAP)) # path is group('path'), file is group('file')
RE_YES_NO     = Regex('^(?i)(?:y(?:es)?|no?)$')
# all commas not between quotes; split on commas with no capture
RE_COMMAS     = Regex('(?:,)(?=(?:[^\"]|\"[^\"]*\")*$)')
# End Of Line: Windows <CR><LF> or Linux <LF> or <CR> only; split on these, with no capture
RE_EOL        = Regex('(?:(?:\r\n)?|(?:\n)?|(?:\r)?)')
RE_FILE       = Regex('^(?:file:///)(.*)')
RE_STAT_URI   = Regex('.*(?:uri="([^"]*))')
RE_STAT_ID    = Regex('.*(?:id="([^"]*))')
RE_STAT_DUR   = Regex('.*(?:duration="([^"]*))')
RE_STAT_NAME  = Regex('.*(?:name="([^"]*))')

VLC_VIDEO_FORMATS = ['360p',	'720p',		'1080p']
VLC_FMT           = [18,		22,			37]
VLC_CONTAINERS    = ['mpegts',	'mpegts',	'mpegts']
#VLC_CONTAINERS    = ['mp4',		'mp4',		'mp4']
VLC_VIDEOCODEC    = ['h264',	'h264',		'h264']
VLC_AUDIOCODEC    = ['mp3',		'mp3',		'mp3']
VLC_VIDEORES      = ['360',		'720',		'1080']
VLC_STREAM_OPT    = 'mpegts'
#VLC_STREAM_OPT    = 'mp4'

PROCESS_QUERY_INFORMATION = 0x0400

METADATA     = '{"apiVersion":"2.1","data":{"id":"Hx9TwM4Pmhc","uploaded":"2013-04-25T14:00:46.000Z","updated":"2014-01-27T02:24:39.000Z","uploader":"Unknown","category":"Various","title":"VLC Video Stream","description":"This video is being streamed by VLC player from a file, device, or a direct video URL.","thumbnail":{"sqDefault":"http://i1.ytimg.com/vi/Hx9TwM4Pmhc/default.jpg","hqDefault":"http://i1.ytimg.com/vi/Hx9TwM4Pmhc/hqdefault.jpg"},"player":{"default":"http://www.youtube.com/watch?v=Hx9TwM4Pmhc&feature=youtube_gdata_player","mobile":"http://m.youtube.com/details?v=Hx9TwM4Pmhc"},"content":{"5":"http://www.youtube.com/v/Hx9TwM4Pmhc?version=3&f=videos&app=youtube_gdata","1":"rtsp://r6---sn-o097zuek.c.youtube.com/CiILENy73wIaGQkXmg_OwFMfHxMYDSANFEgGUgZ2aWRlb3MM/0/0/0/video.3gp","6":"rtsp://r6---sn-o097zuek.c.youtube.com/CiILENy73wIaGQkXmg_OwFMfHxMYESARFEgGUgZ2aWRlb3MM/0/0/0/video.3gp"},"duration":3600,"aspectRatio":"widescreen","rating":4.1,"likeCount":"1","ratingCount":1,"viewCount":1,"favoriteCount":1,"commentCount":0,"accessControl":{"comment":"allowed","commentVote":"allowed","videoRespond":"moderated","rate":"allowed","embed":"allowed","list":"allowed","autoPlay":"allowed","syndicate":"allowed"}}}'

# Shorthands:
# Resource.ExternalPath() => R()
# Resource.SharedExternalPath() => S()
# Resource.Load() => L()
####################################################################################################
# Global variables
vlc_proc = None
class VLC_states:
	stopped, paused, playing, pending = ['stopped', 'paused', 'playing', 'pending']
Log.Debug('GLOBAL VARIABLES WERE RESET.')
####################################################################################################
@route(PREFIX+'/Start')
def Start():
	Log.Debug("EXECUTING: Start()")
	Thread.Unblock('main')
	Thread.Unblock('valid')

	Plugin.AddPrefixHandler(PREFIX, MainMenu, TITLE, ICON, ART)
	Plugin.Nice(0) # a resource hog

	# set defaults
	ObjectContainer.title1 = NAME
	ObjectContainer.art = R(ART)
	ObjectContainer.no_cache = True

	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON)
	VideoClipObject.art = R(ART)

	TrackObject.thumb = R(ICON)

#	HTTP.CacheTime = CACHE_1HOUR # in seconds
	# When using HTTP.Request(), this value sets the time for how long it will take before the
	#   request is considered expired and a new request will be needed.
	#   If there is an HTTP.Request() in a method/subroutine, that method will not get called again
	#   during the cache period.  This can stop MainMenu() from running during this period.
	#  This does not apply to urllib.urlopen(), which always reloads.
	HTTP.CacheTime = 0 # Always reload the webpage by default
	HTTP.Timeout = 3 # seconds
	
	# Store user "globals" in the Dict
	Dict['Initialized'] = False
	Dict['Today'] = str(Datetime.Now())[0:10] # today's date only; [start:stop:step]
	Dict['VLCpid'] = -1
	Dict['current_setting'] = dict()
#	Dict['PLID'] = -1
#	Dict['VLCconfigured'] => performed in MainMenu
#	Dict['PlayList'] = dict() # also: {} => save the playlist for future use
#	Dict['PLselect'] = ''
	Dict['PlayLock'] = False
	Dict['Streams'] = dict()
	Dict['VLC_state'] = VLC_states.stopped
	Dict['VLC_metadata'] = '' # this holds the VLC metadata (only clear it on startup)

	Log.Debug('VLC_APP= '+VLC_APP)
	Log.Debug('ST_PAGE_MAP= '+ST_PAGE_MAP)
	Log.Debug('ST_URL_MAP= '+ST_URL_MAP)
	Log.Debug('ST_URL_MAP2= '+ST_URL_MAP2)
	Log.Debug('ST_FQFILE_MAP= '+ST_FQFILE_MAP)
	#InitializePrefs() => can't do this here.  It is too early.  Moved to MainMenu()

####################################################################################################
@route(PREFIX+'/InitializePrefs')
def InitializePrefs():
# All non-compliant Prefs will be reset to their default values
	if Dict['Initialized']:
		return
	Log.Debug("EXECUTING: InitializePrefs()")
	Dict['Initialized'] = True

	if Prefs['start_delay'] == None:
		u = HTTP.Request(PLEX_PREFS+'start_delay=').content
		
	if Prefs['url_service'] == None:
		u = HTTP.Request(PLEX_PREFS+'url_service=').content
		
#	match = RE_YES_NO.search(Prefs['transcode'])
#	if match == None:
	if Prefs['transcode'] == None:
		u = HTTP.Request(PLEX_PREFS+'transcode=').content
	Dict['current_setting']['transcode'] = Prefs['transcode']
		
	if Prefs['vlc_transcode'] == None:
		u = HTTP.Request(PLEX_PREFS+'vlc_transcode=').content
	Dict['current_setting']['vlc_transcode'] = Prefs['vlc_transcode']
		
	if Prefs['vlc_mux'] == None:
		u = HTTP.Request(PLEX_PREFS+'vlc_mux=').content
	Dict['current_setting']['vlc_mux'] = Prefs['vlc_mux']
		
	match = RE_IP_MAP.search(Prefs['vlc_host'])
	if match == None:
		u = HTTP.Request(PLEX_PREFS+'vlc_host=').content
	Dict['current_setting']['vlc_host'] = Prefs['vlc_host']

	match = RE_PORT_MAP.search(Prefs['vlc_port_stream'])
	if match == None:
		u = HTTP.Request(PLEX_PREFS+'vlc_port_stream=').content
	Dict['current_setting']['vlc_port_stream'] = Prefs['vlc_port_stream']
		
	match = RE_PORT_MAP.search(Prefs['vlc_port_control'])
	if match == None:
		u = HTTP.Request(PLEX_PREFS+'vlc_port_control=').content
	Dict['current_setting']['vlc_port_control'] = Prefs['vlc_port_control']
		
	if Prefs['password'] == None:
		u = HTTP.Request(PLEX_PREFS+'password=').content
	Dict['current_setting']['password'] = Prefs['password']

	match = RE_PAGE_MAP.search(Prefs['vlc_page'])
	if match == None:
		u = HTTP.Request(PLEX_PREFS+'vlc_page=').content
	Dict['current_setting']['vlc_page'] = Prefs['vlc_page']

#	match = RE_FQFILE_MAP.search(Prefs['fq_file'])
	fq_file = Prefs['fq_file']
	if fq_file:
		fq_file = fq_file.replace('\\', '/') # change backslashes to frontslashes for pattern match
		match = RE_FQFILE_MAP.search(fq_file)
		if match == None:
			u = HTTP.Request(PLEX_PREFS+'fq_file=').content
		elif fq_file != Prefs['fq_file']:
			u = HTTP.Request(PLEX_PREFS+'fq_file='+fq_file.replace(' ', '%20')).content
	Dict['current_setting']['fq_file'] = Prefs['fq_file']
		
	match = RE_URL_MAP2.search(Prefs['fq_url'])
	if match == None:
		u = HTTP.Request(PLEX_PREFS+'fq_url=').content
	Dict['current_setting']['fq_url'] = Prefs['fq_url']
	
	Dict['current_setting']['fq_uri'] = Prefs['fq_uri']

	vlc_exe = Prefs['vlc_exe'] # similar to: fq_file
	if vlc_exe:
		vlc_exe = vlc_exe.replace('\\', '/') # change backslashes to frontslashes for pattern match
		match = RE_FQFILE_MAP.search(vlc_exe)
		if match == None:
			u = HTTP.Request(PLEX_PREFS+'vlc_exe=').content
		elif vlc_exe != Prefs['vlc_exe']:
			u = HTTP.Request(PLEX_PREFS+'vlc_exe='+vlc_exe.replace(' ', '%20')).content
	Dict['current_setting']['vlc_exe'] = Prefs['vlc_exe']

	SetVLCurls()	
	return

# Force set a preference:
# u = HTTP.Request('http://{PMS_IP}:32400/:/plugins/{PLUGIN STRING}/prefs/set?{VARIABLE}={VALUE}')
# set vlc_page to defualt >>
# u = HTTP.Request('http://localhost:32400/:/plugins/com.plexapp.plugins.vlcplayer/prefs/set?vlc_page=')
	
####################################################################################################
@route(PREFIX+'/ValidatePrefs')
def ValidatePrefs():
# WARNING: RACE CONDITION: Calling HTTP.Request() to change Prefs[] will invoke the method again!
# NOTE: MessageContainer() is deprecated
# NOTE: Returning an ObjectContainer() with an error does not display the message.
#       Possibly because Plex is already in a popup (Preferences).
	Log.Debug("EXECUTING: ValidatePrefs()")
	Log.Debug("***************************************")
	
	Dict['VLCconfigured'] = True # allow to return to configured state
#	match = RE_YES_NO.search(Prefs['transcode'])
#	if match != None:
#		Log.Debug("STRM  transcode= "+match.group(0))
#	else:
#		Log.Debug("STRM  transcode= INVALID")
	if Prefs['transcode'] != Dict['current_setting']['transcode']:
		Dict['VLCconfigured'] = False
		
	if Prefs['vlc_transcode'] != Dict['current_setting']['vlc_transcode']:
		Dict['VLCconfigured'] = False
		
	if Prefs['vlc_mux'] != Dict['current_setting']['vlc_mux']:
		Dict['VLCconfigured'] = False
						
	match = RE_IP_MAP.search(Prefs['vlc_host'])
	if match != None:
		if Prefs['vlc_host'] != Dict['current_setting']['vlc_host']:
			Dict['VLCconfigured'] = False
		Log.Debug("HOST  vlc_host= "+match.group(0))
	else:
		Log.Debug("HOST  vlc_host= INVALID")
		
	match = RE_PORT_MAP.search(Prefs['vlc_port_stream'])
	if match != None:
		if Prefs['vlc_port_stream'] != Dict['current_setting']['vlc_port_stream']:
			Dict['VLCconfigured'] = False
		Log.Debug("PORT  vlc_port_stream= "+match.group(0))
	else:
		Log.Debug("PORT  vlc_port_stream= INVALID")
		
	match = RE_PORT_MAP.search(Prefs['vlc_port_control'])
	if match != None:
		if Prefs['vlc_port_control'] != Dict['current_setting']['vlc_port_control']:
			Dict['VLCconfigured'] = False
		Log.Debug("PORT  vlc_port_control= "+match.group(0))
	else:
		Log.Debug("PORT  vlc_port_control= INVALID")
	
	if Prefs['password'] != Dict['current_setting']['password']:
		Dict['VLCconfigured'] = False
						
	str_page = Prefs['vlc_page']
	if str_page[0] != '/':
		if str_page == ' ':
			str_page = ''
		else:
			str_page = '/' + Prefs['vlc_page'] # does not start with a "/"
	match = RE_PAGE_MAP.search(str_page)
	if match != None:
		if Prefs['vlc_page'] != Dict['current_setting']['vlc_page']:
			Dict['VLCconfigured'] = False
		Log.Debug("PAGE  vlc_page= "+match.group(0))
	else:
		Log.Debug("PAGE  vlc_page= INVALID")

	url_vlc = 'http://%s:%s%s' % (Prefs['vlc_host'], Prefs['vlc_port_stream'], str_page) # dynamic
	match = RE_URL_MAP.search(url_vlc)
	if match != None:
		Log.Debug("URL  vlc_url= "+match.group(0))
	else:
		Log.Debug("URL  vlc_url= INVALID")

	fq_file = Prefs['fq_file']
	if fq_file:
		fq_file = fq_file.replace('\\', '/') # change backslashes to frontslashes for pattern match
		match = RE_FQFILE_MAP.search(fq_file)
		if match != None:
			if fq_file != Dict['current_setting']['fq_file']:
				Dict['current_setting']['fq_file'] = fq_file
				Dict['Streams'].update({'file':{'type': 'file:///', 'fq_uri': 'fq_file'}})
			Log.Debug("FILE  fq_file= "+match.group(0))
		else:
			Log.Debug("FILE: fq_file= INVALID")
		
	if Prefs['fq_url']:
		match = RE_URL_MAP2.search(Prefs['fq_url'])
		if match != None:
			if Prefs['fq_url'] != Dict['current_setting']['fq_url']:
				Dict['current_setting']['fq_url'] = Prefs['fq_url']
				Dict['Streams'].update({'url':{'type': '', 'fq_uri': 'fq_url'}}) # the 'http://', etc. protocol is already there
			Log.Debug("URL  fq_url= "+match.group(0))
		else:
			Log.Debug("URL: fq_url= INVALID")
		
	if Prefs['fq_uri'] != Dict['current_setting']['fq_uri']:
		Dict['current_setting']['fq_uri'] = Prefs['fq_uri']
		if Prefs['fq_uri']:
			Dict['Streams'].update({'uri':{'type': '', 'fq_uri': 'fq_uri'}})
	Log.Debug("URI: fq_uri= "+ClearNoneString(Prefs['fq_uri']))

	vlc_exe = Prefs['vlc_exe'] # similar to: fq_file
	if vlc_exe:
		vlc_exe = vlc_exe.replace('\\', '/') # change backslashes to frontslashes for pattern match
		if not os.path.isfile(vlc_exe): # see if file exists
			Log.Debug("FILE: vlc_exe= NONEXISTENT")
		else:
			match = RE_FQFILE_MAP.search(vlc_exe)
			if match != None:
				if vlc_exe != Dict['current_setting']['vlc_exe']:
					Dict['current_setting']['vlc_exe'] = vlc_exe
				Log.Debug("FILE  vlc_exe= "+match.group(0))
			else:
				Log.Debug("FILE: vlc_exe= INVALID")
	
	SetVLCurls()
	Log.Debug("VLC: params= "+Dict['app']['app_stream'])
	Log.Debug("***************************************")
	return True

####################################################################################################
@route(PREFIX+'/SetVLCurls')
def SetVLCurls():	
	Log.Debug("EXECUTING: SetVLCurls()")
	# HTTP.Request won't accept HTTP Basic Authentication credentials in the URL, so:
	# https://forums.plex.tv/index.php/topic/53519-httpsetpassword-error/
	# Password bug fix: C:\Users\User\AppData\Local\Plex Media Server\Plug-ins\Framework.bundle\Contents\Resources\Versions\2\Python\Framework\components\networking.py in set_http_password(): line 426=> if self._global_http_auth_enabled: # added "self."
	# Also in: C:\Program Files (x86)\Plex\Plex Media Server\Resources\Plug-ins\Framework.bundle\Contents\Resources\Versions\2\Python\Framework\components
	HTTP.SetPassword(Prefs['vlc_host']+':'+Prefs['vlc_port_stream'], '', Prefs['password']) # Basic Authentication
	HTTP.SetPassword(Prefs['vlc_host']+':'+Prefs['vlc_port_control'], '', Prefs['password']) # Basic Authentication
	
	str_page = Prefs['vlc_page']
	if str_page[0] != '/':
		if str_page == ' ':
			str_page = ''
		else:
			str_page = '/' + Prefs['vlc_page'] # does not start with a "/"
	url_vlc = (VLC_ADR + '%s') % (Prefs['vlc_host'], Prefs['vlc_port_stream'], str_page) # dynamic
	if 1==0:
		# Log current settings/preferences click icon
		Log.Debug("#######################################")
		Log.Debug("### vlc_host= "+Prefs['vlc_host'])
		Log.Debug("### vlc_port_stream= "+Prefs['vlc_port_stream'])
		Log.Debug("### vlc_port_control= "+Prefs['vlc_port_control'])
		Log.Debug("### vlc_page= "+Prefs['vlc_page'])
		Log.Debug("### vlc_url= "+url_vlc)
		Log.Debug("#######################################")
	
	vlc_args = VLC_ARGS0
	temp = ''
	if Prefs['transcode'][0] == 'y':
		if Prefs['vlc_transcode'] != 'none':
			vlc_args += Prefs['vlc_transcode'] + ':'
			vlc_stream = Prefs['vlc_transcode'] + ':'
		if Prefs['vlc_mux'] != 'none':
			temp = Prefs['vlc_mux']+','
	else:
		vlc_stream = ''
	vlc_args += VLC_ARGS2 % (temp, Prefs['vlc_port_stream'], Prefs['vlc_page']) + VLC_ARGS2a
	vlc_args += VLC_ARGS3 % (Prefs['vlc_host'], Prefs['vlc_port_control'], Prefs['password'])
	vlc_stream += VLC_ARGS2 % (temp, Prefs['vlc_port_stream'], Prefs['vlc_page'])
#	Log.Debug('vlc_args= '+vlc_args)
	
	# access requires no username, only a password
	#url_vlc_req = (VLC_ADR2 + VLC_REQ) % (Prefs['password'], Prefs['vlc_host'], Prefs['vlc_port_control'])
	url_vlc_req = (VLC_ADR + VLC_REQ) % (Prefs['vlc_host'], Prefs['vlc_port_control'])
	url_vlc_cmd = url_vlc_req + VLC_STAT + VLC_COM
	url_vlc_meta = url_vlc_req + VLC_META
#	url_vlc_cmd = VLC_CON % (Prefs['password'], Prefs['vlc_host'], Prefs['vlc_port_control']) # doesn't work

#	fq_file = '"'+str(Dict['current_setting']['fq_file']).replace('/', '\\')+'"' # change frontslashes to backslashes (Windows)
	fq_file = 'file:///'+str(Dict['current_setting']['fq_file']).replace(' ', '%20')
	vlc_exe = str(Dict['current_setting']['vlc_exe']) # replace VLC_APP
	Dict['app'] = {'app_app':vlc_exe, 'app_file':fq_file, 'app_args':vlc_args, 'app_stream':vlc_stream, 'vlc':{'url_vlc':url_vlc, 'url_cmd':url_vlc_cmd, 'cmd_stop':'pl_stop', 'cmd_pause':'pl_pause', 'cmd_play':'pl_play', 'cmd_play_id':'pl_play&id=', 'cmd_delete_id':'pl_delete&id=', 'url_meta':url_vlc_meta}}
	return
	
####################################################################################################
@route(PREFIX+'/PrefValidationNotice')
def PrefValidationNotice():
	Thread.AcquireLock('valid')
	Log.Debug("EXECUTING: PrefValidationNotice()")
	
#	match = RE_YES_NO.search(Prefs['transcode'])
#	if match == None:
#		return ObjectContainer(header="Settings Error", message="The stream Transcode setting is invalid.")

	match = RE_IP_MAP.search(Prefs['vlc_host'])
	if match == None:
		Thread.ReleaseLock('valid')
		return ObjectContainer(header="Settings Error", message="The IP address setting is invalid.")

	match = RE_PORT_MAP.search(Prefs['vlc_port_stream'])
	if match == None:
		Thread.ReleaseLock('valid')
		return ObjectContainer(header="Settings Error", message="The IP stream port setting is invalid.")

	match = RE_PORT_MAP.search(Prefs['vlc_port_control'])
	if match == None:
		Thread.ReleaseLock('valid')
		return ObjectContainer(header="Settings Error", message="The IP control port setting is invalid.")

	if Prefs['password'] == None:
		Thread.ReleaseLock('valid')
		return ObjectContainer(header="Settings Error", message="The password setting is invalid.")

	str_page = Prefs['vlc_page']
	if str_page[0] != '/':
		if str_page == ' ':
			str_page = ''
		else:
			str_page = '/' + Prefs['vlc_page'] # does not start with a "/"
	
	match = RE_PAGE_MAP.search(str_page)
	if match == None:
		Thread.ReleaseLock('valid')
		return ObjectContainer(header="Settings Error", message="The page setting is invalid.")

	url_vlc = 'http://%s:%s%s' % (Prefs['vlc_host'], Prefs['vlc_port_stream'], str_page) # dynamic
	match = RE_URL_MAP.search(url_vlc)
	if match == None:
		Thread.ReleaseLock('valid')
		return ObjectContainer(header="Settings Error", message="The settings do not result in a valid url.")

	if Dict['current_setting']['fq_file']:
		match = RE_FQFILE_MAP.search(Dict['current_setting']['fq_file'])
		if match == None:
			Thread.ReleaseLock('valid')
			return ObjectContainer(header="Settings Error", message="The FQ File setting is invalid.")
		elif Dict['current_setting']['fq_file'] != Prefs['fq_file']:
			u = HTTP.Request(PLEX_PREFS+'fq_file='+Dict['current_setting']['fq_file'].replace(' ', '%20')).content

	if Dict['current_setting']['fq_url']:
		match = RE_URL_MAP2.search(Dict['current_setting']['fq_url'])
		if match == None:
			Thread.ReleaseLock('valid')
			return ObjectContainer(header="Settings Error", message="The FQ URL setting is invalid.")

	if Dict['current_setting']['vlc_exe']:
		if not os.path.isfile(Dict['current_setting']['vlc_exe']): # see if file exists
			Thread.ReleaseLock('valid')
			return ObjectContainer(header="Settings Error", message="The FQ VLC executable does not exist.")
		match = RE_FQFILE_MAP.search(Dict['current_setting']['vlc_exe'])
		if match == None:
			Thread.ReleaseLock('valid')
			return ObjectContainer(header="Settings Error", message="The FQ VLC executable setting is invalid.")
		elif Dict['current_setting']['vlc_exe'] != Prefs['vlc_exe']:
			u = HTTP.Request(PLEX_PREFS+'vlc_exe='+Dict['current_setting']['vlc_exe'].replace(' ', '%20')).content

	Log.Debug("PASSED: PrefValidationNotice()")
	Thread.ReleaseLock('valid')
	return None

####################################################################################################
# the following line performs the same as the Plugin.AddPrefixHandler() method above
#@handler(PREFIX, TITLE, thumb=ICON, art=ART)
@route(PREFIX+'/MainMenu')
def MainMenu():
	global vlc_proc
	# do not allow the application (VLC) to be bombarded with http requests by MainMenu() 
	#   and asynchronous methods simultaneously
	Thread.AcquireLock('main')
	Log.Debug("EXECUTING: MainMenu()")
#	socket.setdefaulttimeout(60.0)
#	Log.Debug(JSON.StringFromObject(socket.getdefaulttimeout()))
	
	InitializePrefs()
	
#	do = DirectoryObject(key = Callback(SecondMenu), title = "Example Directory") # Don't add: Example Directory
	
	voc = PrefValidationNotice()
	if voc:
		voc.add(DirectoryObject(key = Callback(Refresh, vlc=None), title = "Refresh", thumb = R(T_REFRESH)))
		# attach the settings/preferences
		voc.add(PrefsObject(title = L('Preferences')))
		Log.Debug("FAILED: PrefValidationNotice()")
		Thread.ReleaseLock('main')
		return voc
	
	# Check to see if VLC is actually running
	Dict['VLCpid'] = AppRunning(VLC_APP_FILE)
	vlc_exe = str(Dict['current_setting']['vlc_exe']) # replace VLC_APP
	Dict['VLCconfigured'], vlc_proc = AppHandleCheck(vlc_proc, vlc_exe, Dict['VLCconfigured'])

	# properties can be filled by parameters in the "New" or set as properties above
#	oc = ObjectContainer(title1=NAME, art=R(ART))
	# The following is required to eliminate a persisting error message (when generated) from PrefValidationNotice()
	oc = ObjectContainer(header='', message='')
#	oc.add(do)

	app_json = JSON.StringFromObject(Dict['app'])
	url_vlc = Dict['app']['vlc']['url_vlc']
	vlc = Dict['app']['vlc']
	vlc_json = JSON.StringFromObject(vlc)

	if Dict['Streams']:
		i = 0
		j = len(Dict['Streams'])
		for stream in Dict['Streams']:
			result, vco = SourceVLC(vlc, Dict['Streams'][stream]['type'], Dict['current_setting'][Dict['Streams'][stream]['fq_uri']])
			if result:
				i += 1
		Dict['Streams'] = dict()
		UpdatePlayListVLC(False) # update the list
		if j == 1 and vco:
			Thread.ReleaseLock('main')
			return vco
		else:
			Thread.ReleaseLock('main')
			return ObjectContainer(header="Playlist Selection", message=str(i)+" of "+str(j)+" Playlist items were added.")

	if int(Dict['VLCpid']) < 0:
		oc.add(DirectoryObject(key = Callback(StartApp, app=app_json), title = "Launch VLC"))
	elif not Dict['VLCconfigured']:
		oc.add(DirectoryObject(key = Callback(ConfigureApp, app=app_json), title = "Restart VLC"))
	else:
		oc.add(DirectoryObject(key = Callback(StopApp, app_pid=Dict['VLCpid']), title = "Exit VLC"))

	if Dict['VLCconfigured'] and not Dict['PlayLock'] and (VLCPlayTest(vlc['url_meta']) == 1 and Dict['VLC_state'] != VLC_states.pending  or Prefs['start_delay'] == 'none'):
		Log.Debug('MainMenu(): Adding a VCO')
		if Prefs['url_service']:
			title = GetStatusTermsVLC(vlc['url_meta'], ['filename'])
			if not title: # this should not happen
				title = 'Play VLC Stream'
#			mo = MediaObject(parts=[PartObject(key=HTTPLiveStreamURL(url_vlc))])
			# the following instruction causes the framework to call the URL service
			# see: \Contents\Info.plist -> PlexURLServices
			# see: \Contents\URL Services\VLCplayer\ServiceCode.pys
			vco = VideoClipObject(title=title, url=url_vlc)
#			vco.add(mo) # not necessary, it is added in: ServiceCode.pys
			Log.Debug('CALLING URL SERVICE')
		else:
			Dict['VCO_sequence'] = False # CreateVideoClipObject gets called more than once, initialize the sequence point
			key_string = Dict['PLselect'] # the selected item uri string
			if not key_string:
				key_string = 'VLC Player rating_key'
#			Log.Debug('>>>> Selected_uri= '+key_string)
			vco = CreateVideoClipObject(url_vlc, Dict['Today'], url_meta=vlc['url_meta'], key_string=key_string) # date only
		oc.add(vco)
	
	oc.add(DirectoryObject(key = Callback(PlayListVLC, vlc=vlc_json), title = "Play List", thumb = R(T_PLAYLIST)))
	if Dict['VLC_state'] == VLC_states.playing or Dict['VLC_state'] == VLC_states.paused:
		text = "VLC is Playing"
	elif Dict['VLC_state'] == VLC_states.pending:
		text = "VLC play is pending"
	else:
		text = "Play VLC"
	oc.add(DirectoryObject(key = Callback(PlayVLC, vlc=vlc_json), title = text, thumb = R(T_PLAY)))
	if Dict['VLC_state'] == VLC_states.paused and Dict['VLC_state'] != VLC_states.pending:
		text = "VLC is Paused"
	else:
		text = "Pause VLC"
	oc.add(DirectoryObject(key = Callback(PauseVLC, vlc=vlc_json), title = text, thumb = R(T_PAUSE)))
	if Dict['VLC_state'] == VLC_states.stopped and int(Dict['VLCpid']) > 0:
		text = "VLC is Stopped"
	else:
		text = "Stop VLC"
	oc.add(DirectoryObject(key = Callback(StopVLC, vlc=vlc_json), title = text, thumb = R(T_STOP)))
	
	oc.add(DirectoryObject(key = Callback(GetStatusMetaVLC, url=vlc['url_meta']), title = "Status VLC", thumb = R(T_STATUS)))
	oc.add(DirectoryObject(key = Callback(Refresh, vlc=vlc_json), title = "Refresh VLC State", thumb = R(T_REFRESH)))

	# the Plex/Web problem with removing a VCO is not limited to the MainMenu:
#	oc.add(DirectoryObject(key = Callback(SecondMenu, url=url_vlc, date=Dict['Today'], url_meta=vlc['url_meta']), title = "Second Menu", thumb = ''))

	# add the settings/preferences object/icon
	oc.add(PrefsObject(title = L('Settings')))
#	oc.add(InputDirectoryObject(title=L('Search'), key=Callback(PLNew), prompt = 'Search')) # The "Search" bubble
	# It always prompts "Search VLC Player" on Plex/Web; no prompt on Roku
#	details = demjson.encode(oc) -> JSONEncodeError('can not encode object into a JSON representation',obj)
#	Log.Debug(details)

	Log.Debug("EXITING: MainMenu()")
	Thread.ReleaseLock('main')
	return oc

####################################################################################################
#	vlc = JSON(Dict['app']['vlc'])
#
@route(PREFIX+'/Refresh')
def Refresh(vlc):
	Thread.AcquireLock('main')
	Log.Debug("EXECUTING: Refresh()")
	oc = ObjectContainer(header="Refresh", message="Updated VLC player status.")
	if not os.path.isfile(Dict['current_setting']['vlc_exe']): # see if file exists
		Thread.ReleaseLock('main')
		return ObjectContainer(header="Refresh Error", message="The FQ VLC executable in SETTINGS does not exist.")
	if vlc:
		if isinstance(vlc, str):
			vlc = JSON.ObjectFromString(vlc)
		elif not isinstance(vlc, dict):
			Thread.ReleaseLock('main')
			return ObjectContainer(header="Refresh Error", message="Refresh() was called with an inappropriate parameter.")
		if int(Dict['VLCpid']) > 0:
			Dict['PlayLock'] = True
			pl_list = GetPlayListVLC()
			Log.Debug(JSON.StringFromObject(pl_list))
			if pl_list:
				values = GetStatusTermsVLC(vlc['url_meta'], ['state','filename'])
				Log.Debug(JSON.StringFromObject(values))
				if values: # requires: len(values) > 0
					oc1 = PendingVLC(vlc) # check for play pending
					if oc1:
						oc = oc1
					elif values[0] == VLC_states.playing:
						Dict['VLC_state'] = VLC_states.playing
					elif values[0] == VLC_states.stopped:
						try:
							page = HTTP.Request(vlc['url_cmd']+vlc['cmd_play']).content
							page = HTTP.Request(vlc['url_cmd']+vlc['cmd_pause']).content
							result = WaitPlayVLC(vlc, terms=['filename'])
							values[1] = result[1][0]
						except:
							oc = ObjectContainer(header="Refresh Error", message="An exception ocurred."+VLCconfigText())
							Log.Debug("ERROR: Refresh()")
					for list in pl_list:
						if list[3] == values[1]: # filenames match
							Dict['PLselect'] = list[0] # set uri
				elif values == None: # check for exception
					oc = ObjectContainer(header="Refresh Error", message="An exception ocurred."+VLCconfigText())
					Log.Debug("ERROR: Refresh()")
			else:
				oc = ObjectContainer(header="Refresh Error", message="An exception ocurred."+VLCconfigText())
				Log.Debug("ERROR: Refresh()")
			Dict['PlayLock'] = False
		else:
			oc = ObjectContainer(header="Refresh Error", message="VLC is not running.")
	Log.Debug("EXITING: Refresh()")
	Thread.ReleaseLock('main')
	return oc
	
####################################################################################################
@route(PREFIX+'/SecondMenu')
def SecondMenu(url, date, url_meta):
	Log.Debug("EXECUTING: SecondMenu()")
	oc = ObjectContainer(title1='Second Menu')
	do = DirectoryObject(key = Callback(ThirdMenu), title = "Example Directory")
	oc.add(do)
	if VLCPlayTest(url_meta) == 1:
		Log.Debug('SecondMenu(): VLC is playing.')
		vco = CreateVideoClipObject(url, date, url_meta=url_meta, key_string='VLC Player rating_key')
		oc.add(vco)
	return oc
	
####################################################################################################
@route(PREFIX+'/ThirdMenu')
def ThirdMenu():
	oc = ObjectContainer(title1='Third Menu')
	do = DirectoryObject(key = Callback(FourthMenu), title = "Dead end")
	oc.add(do)
	return oc
	
####################################################################################################
@route(PREFIX+'/FourthMenu')
def FourthMenu():
	oc = ObjectContainer(title1='Fourth Menu')
	return oc

####################################################################################################
@route(PREFIX+'/PlayVLCtimer')
def PlayVLCtimer(delay):
	Log.Debug("EXECUTING: PlayVLCtimer()")
	url = Dict['app']['vlc']['url_cmd']+Dict['app']['vlc']['cmd_play']
	if Prefs['start_delay'] != 'none':
		Thread.Sleep(delay)
	page = HTTP.Request(url).content
	return
	
####################################################################################################
#	vlc = Dict['app']['vlc'] or equivalent
#
@route(PREFIX+'/PlayVLC')
def PlayVLC(vlc):
	Log.Debug("EXECUTING: PlayVLC()")
	if int(Dict['VLCpid']) > 0:
		if isinstance(vlc, str):
			vlc = JSON.ObjectFromString(vlc)
		elif not isinstance(vlc, dict):
			return ObjectContainer(header="PlayVLC Error", message="PlayVLC() was called with an inappropriate parameter.")
		VLCPlayTest(vlc['url_meta'])
		if Dict['VLC_state'] == VLC_states.stopped:
			Thread.AcquireLock('main')
			try:
				Log.Debug("EXECUTING: PlayVLC()")
				page = HTTP.Request(vlc['url_cmd']+vlc['cmd_play']).content
				if Prefs['start_delay'] != 'none':
					page = HTTP.Request(vlc['url_cmd']+vlc['cmd_pause']).content
				values = GetStatusTermsVLC(vlc['url_meta'], ['state','readbytes'])
				if values:
					if values[0] == VLC_states.paused or values[0] == VLC_states.playing:
						Dict['VLC_readbytes'] = values[1]
						if WaitPlayVLC({'url_meta':vlc['url_meta']}):
							if values[0] == VLC_states.playing:
								Dict['VLC_state'] = VLC_states.playing
								oc = ObjectContainer(header="VLC Play", message="VLC is playing.")
							else:
								Dict['VLC_state'] = VLC_states.pending
								oc = ObjectContainer(header="VLC Play", message="VLC play is now pending.")
						else:
							oc = ObjectContainer(header="VLC Play Error", message="VLC play state is uncertain.")
					else:
						oc = ObjectContainer(header="VLC Play Error", message="VLC play state is uncertain.")
				elif values == None: # check for exception
					oc = ObjectContainer(header="VLC Play Error", message="An exception ocurred."+VLCconfigText())
					Log.Debug("ERROR: PlayVLC()")
			except:
				oc = ObjectContainer(header="VLC Play Error", message="An exception ocurred."+VLCconfigText())
				Log.Debug("ERROR: PlayVLC()")
			Log.Debug("EXITING: PlayVLC()")
			Thread.ReleaseLock('main')
		elif Dict['VLC_state'] == VLC_states.playing:
			oc = ObjectContainer(header="VLC Play", message="VLC is already playing.")
		elif Dict['VLC_state'] == VLC_states.paused:
			oc = ObjectContainer(header="VLC Play", message="VLC is already playing and paused.")
		elif Dict['VLC_state'] == VLC_states.pending:
			oc = PendingVLC(vlc)
	else:
		oc = ObjectContainer(header="VLC Play Error", message="VLC is not running.")
	return oc
	
####################################################################################################
#	vlc = Dict['app']['vlc'] or equivalent
#	terms = ['filename','length','state',...]
#
@route(PREFIX+'/WaitPlayVLC')
def WaitPlayVLC(vlc, terms=None, file=None, limit=60): # vlc is a Dict[]
	Log.Debug("EXECUTING: WaitPlayVLC()")
	i = 0
	j = 5
	result = False
	currentplid = -1
	values = None
	Dict['delay'] = i
	# don't send commands to VLC too quickly; it fails to answer leaving Plex with a request timeout
	while (i < limit): # wait for the counter to start runing
		try:
			values = GetStatusTermsVLC(vlc['url_meta'], ['time','state','length','currentplid'])
			#position varies from 0 to 1
			# time = position * length
			#Log.Debug('WaitPlayVLC() VALUES: '+JSON.StringFromObject(values))
			if values:
				Log.Debug('VLC State('+str(i)+'): '+values[1]+': '+values[0]+'s')
				time = int(values[0])
				state = values[1]
				if state == VLC_states.stopped:
					Thread.Sleep(2)
					i = i + 2
					if currentplid == -1:
						currentplid = -2 # indicates that VLC answered
						if file:
							Log.Debug(vlc['url_cmd']+'in_enqueue&input='+file)
							#page = HTTP.Request(vlc['url_cmd']+'in_play&input='+file.replace(' ', '%20')).content
							page = HTTP.Request(vlc['url_cmd']+'in_enqueue&input='+file.replace(' ', '%20')).content
							Thread.Sleep(1)
							page = HTTP.Request(vlc['url_cmd']+vlc['cmd_play']).content
							Thread.Sleep(1)
							i = i + 2
				elif int(values[0]) < 2 and state == VLC_states.playing:
					Thread.Sleep(2)
					i = i + 2
				elif state == VLC_states.playing or state == VLC_states.paused: # works for VLC_states.pending too
					currentplid = int(values[3])
					values = GetStatusTermsVLC(vlc['url_meta'], terms) # get values for terms requested
					if state == VLC_states.playing:
						Dict['delay'] = i - time
					if 'url_cmd' in vlc and 'cmd_stop' in vlc:
						Thread.Sleep(1) # don't send stop command too quickly
						page = HTTP.Request(vlc['url_cmd']+vlc['cmd_stop']).content
						Dict['VLC_state'] = VLC_states.stopped
						Log.Debug('VLC State: stop by command')
					result = True
					break
				else:
					break
			elif currentplid == -1:
				Log.Debug('VLC State('+str(i)+'): no response')
				Thread.Sleep(j)
				i = i + j
				j = max(j - 2, 2)
			else:
				Log.Debug('VLC State('+str(i)+'): Crashed')
				break
		except:
			Log.Debug('VLC State('+str(i)+'): Exception')
			Thread.Sleep(2)
			i = i + 2
	if terms != None:
		return [result, values, str(currentplid)]
	return result
	
####################################################################################################
#	vlc = Dict['app']['vlc'] or equivalent
#
@route(PREFIX+'/PauseVLC')
def PauseVLC(vlc):
	if int(Dict['VLCpid']) > 0:
		if isinstance(vlc, str):
			vlc = JSON.ObjectFromString(vlc)
		elif not isinstance(vlc, dict):
			return ObjectContainer(header="PauseVLC Error", message="PauseVLC() was called with an inappropriate parameter.")
		Thread.AcquireLock('main')
		try:
			Log.Debug("EXECUTING: PauseVLC()")
			oc = PendingVLC(vlc) # check for play pending
			if not oc:
				page = HTTP.Request(vlc['url_cmd']+vlc['cmd_pause']).content
				Thread.Sleep(1)
				res = VLCPlayTest(vlc['url_meta'])
				if res == 1:
					oc = ObjectContainer(header="VLC Pause", message="VLC playing continues.")
					Dict['VLC_state'] = VLC_states.playing
				elif res == 0:
					oc = ObjectContainer(header="VLC Pause", message="VLC is paused.")
					Dict['VLC_state'] = VLC_states.paused
				else:
					oc = ObjectContainer(header="VLC Pause Error", message="An exception ocurred."+VLCconfigText())
		except:
			oc = ObjectContainer(header="VLC Pause Error", message="An exception ocurred."+VLCconfigText())
			Log.Debug("ERROR: PauseVLC()")
		Log.Debug("EXITING: PauseVLC()")
		Thread.ReleaseLock('main')
	else:
		oc = ObjectContainer(header="VLC Pause Error", message="VLC is not running.")
	return oc
	
####################################################################################################
#	vlc = Dict['app']['vlc'] or equivalent
#
@route(PREFIX+'/PendingVLC')
def PendingVLC(vlc):
	if int(Dict['VLCpid']) > 0:
		if isinstance(vlc, str):
			vlc = JSON.ObjectFromString(vlc)
		elif not isinstance(vlc, dict):
			return ObjectContainer(header="PendingVLC Error", message="PendingVLC() was called with an inappropriate parameter.")
		try:
			oc = None
			Log.Debug("EXECUTING: PendingVLC()")
			state, readbytes, length = GetStatusTermsVLC(vlc['url_meta'], ['state','readbytes', 'length'])
			if state == VLC_states.paused:
				if Dict['VLC_state'] != VLC_states.pending:
					Dict['VLC_state'] = VLC_states.paused
				elif readbytes == Dict['VLC_readbytes'] and int(length) > 0:
					Dict['VLC_state'] = VLC_states.paused
					oc = ObjectContainer(header="VLC Pending", message="VLC is now ready to play.")
				else:
					Dict['VLC_readbytes'] = readbytes
					oc = ObjectContainer(header="VLC Pending", message="VLC play is still pending.")
		#Log.Debug('state='+state+'   length='+str(length)+'   readbytes='+str(readbytes))
		except:
			oc = ObjectContainer(header="VLC Pending Error", message="An exception ocurred."+VLCconfigText())
			Log.Debug("ERROR: PendingVLC()")
	else:
		oc = ObjectContainer(header="VLC Pending Error", message="VLC is not running.")
	return oc

####################################################################################################
#	vlc = Dict['app']['vlc'] or equivalent
#
@route(PREFIX+'/StopVLC')
def StopVLC(vlc):
	if int(Dict['VLCpid']) > 0:
		if isinstance(vlc, str):
			vlc = JSON.ObjectFromString(vlc)
		elif not isinstance(vlc, dict):
			return ObjectContainer(header="StopVLC Error", message="StopVLC() was called with an inappropriate parameter.")
		Thread.AcquireLock('main')
		try:
			Log.Debug("EXECUTING: StopVLC()")
			url = vlc['url_cmd']+vlc['cmd_stop']
			page = HTTP.Request(url).content
			oc = ObjectContainer(header="VLC Stop", message="VLC is now stopped.")
			Dict['VLC_state'] = VLC_states.stopped
		except:
			oc = ObjectContainer(header="VLC Stop Error", message="An exception ocurred."+VLCconfigText())
			Log.Debug("ERROR: StopVLC()")
		Log.Debug("EXITING: StopVLC()")
		Thread.ReleaseLock('main')
	else:
		oc = ObjectContainer(header="VLC Stop Error", message="VLC is not running.")
	return oc
	
####################################################################################################
#	vlc = Dict['app']['vlc'] or equivalent
#	type = Dict['Streams'][stream]['type']
#	source = Dict['Streams'][stream]['fq_uri']
#
@route(PREFIX+'/SourceVLC')
def SourceVLC(vlc, type, source):
	oc = None
	result = False
	if source: # source cannot be = None
		Log.Debug("EXECUTING: SourceVLC(input="+type+source+")")
		if int(Dict['VLCpid']) > 0:
			if isinstance(vlc, str):
				vlc = JSON.ObjectFromString(vlc)
			elif not isinstance(vlc, dict):
				return [False, ObjectContainer(header="SourceVLC Error", message="SourceVLC() was called with an inappropriate parameter.")]
			url = vlc['url_cmd']
			url_meta = vlc['url_meta']
			try:
				page = HTTP.Request(url+vlc['cmd_stop']).content
				Dict['VLC_state'] = VLC_states.stopped
				uri = type+source
#				page = HTTP.Request(url+'in_enqueue&input='+uri.replace(' ', '%20')).content # just add it, don't play it
				if str(uri) in Dict['PlayList']:
					Log.Debug('SourceVLC(): Playlist ID: '+str(Dict['PlayList'][uri][0]))
					page = HTTP.Request(url+vlc['cmd_play_id']+str(Dict['PlayList'][uri][0])).content
					results = WaitPlayVLC({'url_meta':url_meta}, terms=[])
					if results[0]:
						oc = VLCPlayCheck(oc, url_meta, Dict['PlayList'][uri][2])
						if not oc:
							oc = ObjectContainer(header="Playlist Selection", message="The Playlist item was selected.")
							result = True
					else:
						oc = ObjectContainer(header="Source Error", message="The Source selection could not be opened.")
				else:
					Log.Debug('SourceVLC: Not in Playlist')
					page = HTTP.Request(url+'in_play&input='+uri.replace(' ', '%20')).content
					results = WaitPlayVLC({'url_meta':url_meta}, terms=[])
					if results[0]:
						oc = VLCPlayCheck(oc, url_meta, uri)
						if not oc:
							oc = ObjectContainer(header="Playlist Selection", message="The Playlist item was added and selected.")
							result = True
					else:
						oc = ObjectContainer(header="Source Error", message="The Source selection could not be opened.")
				page = HTTP.Request(url+vlc['cmd_stop']).content
				if result:
					Dict['PLselect'] = uri
				else: # remove item that did not play
					page = HTTP.Request(url+vlc['cmd_delete_id']+results[2]).content
			except:
				Log.Debug("ERROR: SourceVLC()")
		else:
			oc = ObjectContainer(header="Source Error", message="VLC is not running; can't verify the source.")
	else:
		oc = ObjectContainer(header="Source Error", message="Invalid call: 'source' parameter not specified.")
		Log.Debug("ERROR: SourceVLC()")
	return [result, oc]
	
####################################################################################################
#	oc_in = input ObjectContainer (possibly replaced with a returned ObjectContainer)
#	url = url_vlc_meta
#	uri = a uri from Dict['Streams'][stream] or VLC playlist
#
@route(PREFIX+'/VLCPlayCheck')
def VLCPlayCheck(oc_in, url, uri=None):
	Log.Debug("EXECUTING: VLCPlayCheck()")
	res = VLCPlayTest(url, uri)
	if res == 0:
		oc = ObjectContainer(header="Play Error", message="The play selection could not be opened.")
	elif res == 1:
		oc = oc_in
	else:
		oc = ObjectContainer(header="Play Error", message="An exception occurred."+VLCconfigText())
	return oc
	
####################################################################################################
#	url = url_vlc_meta
#	uri = a uri from Dict['Streams'][stream] or VLC playlist
#
@route(PREFIX+'/VLCPlayTest')
def VLCPlayTest(url, uri=None):
	Log.Debug("EXECUTING: VLCPlayTest()")
	try:
		state, filename = GetStatusTermsVLC(url, ['state','filename'])
		if state in [VLC_states.playing,VLC_states.paused,VLC_states.stopped]:
			if state != VLC_states.paused or Dict['VLC_state'] != VLC_states.pending:
				Dict['VLC_state'] = state # update the VLC player state
		if uri:
			file = RE_FILE.search(uri)
			if file: # is it a file uri
				file = RE_FQFILE_MAP.search(file.group(1)) # check if this is a fully qualified filename
			if file:
				uri = file.group('file') # get just the filename
			rightfile = (filename == uri)
		else: # don't care what is playing
			rightfile = True
		if (state == VLC_states.stopped) or not rightfile: # play status NOT confirmed playing
			res = 0
		else: # play status confirmed playing
			res = 1
		if state in [VLC_states.playing,VLC_states.paused]: # update the item being played
			Dict['PLselect'] = ''
			for uri in Dict['PlayList']:
				if Dict['PlayList'][uri][2] == filename:
					Dict['PLselect'] = uri
					break
	except:
		res = -1
	return res
####################################################################################################
# There appears to be no good way to display a lot of text.
#	url = url_vlc_meta
#
@route(PREFIX+'/GetStatusMetaVLC')
def GetStatusMetaVLC(url):
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: GetStatusMetaVLC()")
		try:
			page = HTTP.Request(url).content
			oc = ObjectContainer(header='Status Results', message=page)
#			oc.add(DirectoryObject(key = Callback(StatusResults), title = "VLC Status", summary = page, thumb = R(T_STATUS)))
			Log.Debug('STATUS: '+page)
		except:
			oc = ObjectContainer(header="VLC Status Error", message="An exception ocurred."+VLCconfigText())
			Log.Debug("ERROR: GetStatusMetaVLC()")
	else:
		oc = ObjectContainer(header="VLC Status Error", message="VLC is not running.")
	return oc
	
####################################################################################################
@route(PREFIX+'/StatusResults')
def StatusResults():
	oc = ObjectContainer(header="Status", message='Don''t click on this.')
	return oc
	
####################################################################################################
#	url = url_vlc_meta
#	terms = ['filename','length','state',...]
#
@route(PREFIX+'/GetStatusTermsVLC')
def GetStatusTermsVLC(url, terms=None):
	Log.Debug("EXECUTING: GetStatusTermsVLC()")
	try:
		page = HTTP.Request(url, timeout=1.0).content
		Dict['VLC_metadata'] = page # save the metadata for CreateVideoClipObject()
		term_values = []
		if terms and isinstance(terms, list):
			for item in terms:
				RE_TEMP = Regex(ST_JSON_MAP % (str(item)))
				term = RE_TEMP.search(page)
				if term:
#					Log.Debug('>>>>> '+term.group('key')+' => '+term.group('val'))
					term_values.append(term.group('val'))
				else:
					term_values.append('')
		return term_values
	except:
		Log.Debug("ERROR: GetStatusTermsVLC()")
	return None
	
####################################################################################################
#	new = T/F -> to replace the Playlist Dict
#
@route(PREFIX+'/UpdatePlayListVLC')
def UpdatePlayListVLC(new=False):
	result = False
	if int(Dict['VLCpid']) > 0:
		url = (VLC_ADR + VLC_REQ) % (Prefs['vlc_host'], Prefs['vlc_port_control'])+ VLC_PL
		Log.Debug("EXECUTING: UpdatePlayListVLC()")
		pl_list = GetPlayListVLC()
		#Log.Debug(JSON.StringFromObject(pl_list))
		if pl_list or new:
			if new:
				Dict['PlayList'] = dict() # or {}
			for list in pl_list:
				uri = list[0] # uri
				if uri in Dict['PlayList']: # update the playlist
					Dict['PlayList'][uri][0] = list[1] # playlist id
					Dict['PlayList'][uri][1] = list[2] # length/duration
					Dict['PlayList'][uri][2] = list[3] # filename/url
				else: # add the new item(s)
					Dict['PlayList'].update({uri:[list[1], list[2], list[3]]})
			result = True
		else:
			Log.Debug("ERROR: UpdatePlayListVLC()")
	return result
	
####################################################################################################
@route(PREFIX+'/GetPlayListVLC')
def GetPlayListVLC():
	if int(Dict['VLCpid']) > 0:
		url = (VLC_ADR + VLC_REQ) % (Prefs['vlc_host'], Prefs['vlc_port_control'])+ VLC_PL
		Log.Debug("EXECUTING: GetPlayListVLC()")
		try:
			pl_list = []
			page = HTTP.Request(url).content
			page = page.split('\n')
			for line in page:
				if line.startswith('<leaf'):
					uri = RE_STAT_URI.search(line).group(1).replace('%20', ' ')
					id = RE_STAT_ID.search(line).group(1)
					duration = RE_STAT_DUR.search(line).group(1)
					name = RE_STAT_NAME.search(line).group(1)
					pl_list.append([uri,id,duration,name])
			return pl_list
		except:
			Log.Debug("ERROR: GetPlayListVLC()")
	return None
	
####################################################################################################
#	vlc = Dict['app']['vlc'] or equivalent
#
@route(PREFIX+'/PlayListVLC')
def PlayListVLC(vlc):
	oc = ObjectContainer(title1='Play List')
	Log.Debug("EXECUTING: PlayListVLC()")
	if isinstance(vlc, str):
		vlc = JSON.ObjectFromString(vlc)
	elif not isinstance(vlc, dict):
		return ObjectContainer(header="PlayListVLC Error", message="PlayListVLC() was called with an inappropriate parameter.")
	if len(Dict['PlayList']) == 0:
		Log.Debug("PlayList is Empty")
		oc.add(DirectoryObject(key = Callback(PLEmpty), title = "Play List is Empty", thumb = R(T_EMPTY)))
	# >>> InputDirectoryObject is not yet supported by Plex/Web
#	oc.add(InputDirectoryObject(key = Callback(PLNew), title = 'New Item', thumb = R(T_MOVIE), summary = 'Add a New Playlist URI', prompt='')) # This is not displayed by Plex/Web
	# Prompt text is not displayed.  If it is "Search", it presents the Search screen, else it presents the Data input screen
	if len(Dict['PlayList']) > 0:
		for item in Dict['PlayList']:
			title = str(Dict['PlayList'][item][2])
			match = RE_PAGE_MAP.search(title)
			if match and len(match.group(0)) > 0:
				label = match.group(0)
				ext = label.rfind('.')
				if ext > 0:
					label = label[0:ext]
			else:
				label = title
			if item == Dict['PLselect']:
				thumb = R(T_MOVIE_SEL)
			else:
				thumb = R(T_MOVIE)
			oc.add(DirectoryObject(key = Callback(PLItem, vlc=JSON.StringFromObject(vlc), uri=item, label=label), title = title, summary=title, thumb = thumb))
	oc.add(DirectoryObject(key = Callback(Refresh, vlc=JSON.StringFromObject(vlc)), title = "Refresh VLC State", summary='Refresh the Playlist with information from the VLC Player', thumb = R(T_REFRESH)))
	url = vlc['url_cmd']
	oc.add(DirectoryObject(key = Callback(PLVSync, url=url), title = 'SYNC -> Plex & VLC Playlist', thumb = R(T_SYNC)))
	oc.add(DirectoryObject(key = Callback(PLVClear, url=url), title = 'CLEAR -> VLC Playlist', thumb = R(T_DELETE)))
	oc.add(DirectoryObject(key = Callback(PLVAdd, url=url), title = 'ADD -> Plex Playlist to VLC', thumb = R(T_LEFT)))
	oc.add(DirectoryObject(key = Callback(PLVReplace), title = 'REPLACE -> Plex Playlist with VLC', thumb = R(T_RIGHT)))
	return oc
	
####################################################################################################
@route(PREFIX+'/PLEmpty')
def PLEmpty():
	oc = ObjectContainer(title1='PLEmpty')
	return oc
	
####################################################################################################
@route(PREFIX+'/PLNew')
def PLNew(query):
	Log.Debug("EXECUTING: PLNew()")
	oc = ObjectContainer(title1='PLNew')
	oc.add(DirectoryObject(key = Callback(PLNew2), title = 'Test', thumb = R(T_EMPTY)))
	return oc
	
####################################################################################################
@route(PREFIX+'/PLNew2')
def PLNew2():
	Log.Debug("EXECUTING: PLNew2()")
	oc = ObjectContainer(title1='PLNew2')
	return oc
	
####################################################################################################
#	vlc = Dict['app']['vlc'] or equivalent
#	uri = Dict['PlayList'] key name
#	label = summary text
#
@route(PREFIX+'/PLItem')
def PLItem(vlc, uri, label=''):
	oc = ObjectContainer(title1='Play List Item')
	Log.Debug("EXECUTING: PLItem()")
	if isinstance(vlc, str):
		vlc = JSON.ObjectFromString(vlc)
	elif not isinstance(vlc, dict):
		return ObjectContainer(header="PLItem Error", message="PLItem() was called with an inappropriate parameter.")
	if str(uri) == Dict['PLselect']:
		thumb = R(T_MOVIE_SEL)
	else:
		thumb = R(T_MOVIE)
	if str(uri) in Dict['PlayList']:
		oc.add(DirectoryObject(key = Callback(PLItemSelect, vlc=JSON.StringFromObject(vlc), uri=uri), title = 'SELECT -> ', summary=label, thumb = thumb))
		oc.add(DirectoryObject(key = Callback(PLItemDelete, vlc=JSON.StringFromObject(vlc), uri=uri), title = 'DELETE -> ', summary=label, thumb = R(T_DELETE)))
	else:
		oc.add(DirectoryObject(key = Callback(PLEmpty), title = 'DELETED', thumb = ''))
	return oc
	
####################################################################################################
#	vlc = Dict['app']['vlc'] or equivalent
#	uri = Dict['PlayList'] key
#
@route(PREFIX+'/PLItemSelect')
def PLItemSelect(vlc, uri):
	oc = None
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLItemSelect("+str(uri)+")")
		if isinstance(vlc, str):
			vlc = JSON.ObjectFromString(vlc)
		elif not isinstance(vlc, dict):
			return ObjectContainer(header="PLItemSelect Error", message="PLItemSelect() was called with an inappropriate parameter.")
		if str(uri) in Dict['PlayList']:
			Dict['PlayLock'] = True
			try:
				page = HTTP.Request(vlc['url_cmd']+vlc['cmd_stop']).content
				Dict['VLC_state'] = VLC_states.stopped
				page = HTTP.Request(vlc['url_cmd']+vlc['cmd_play_id']+str(Dict['PlayList'][uri][0])).content
				page = HTTP.Request(vlc['url_cmd']+vlc['cmd_pause']).content
				WaitPlayVLC({'url_meta':vlc['url_meta']})
				oc = VLCPlayCheck(oc, vlc['url_meta'], Dict['PlayList'][uri][2])
				if not oc:
					oc = ObjectContainer(header="Playlist Selection", message="The Playlist item was selected.")
				page = HTTP.Request(vlc['url_cmd']+vlc['cmd_stop']).content
				Dict['VLC_state'] = VLC_states.stopped
				Dict['PLselect'] = uri
				Log.Debug("SUCCESS: PLItemSelect()")
			except:
				oc = ObjectContainer(header="Playlist Selection Error", message="An exception ocurred."+VLCconfigText())
				Log.Debug("ERROR: PLItemSelect()")
			Dict['PlayLock'] = False
		else:
			oc = ObjectContainer(header="Playlist Selection Error", message="The Playlist item does not exist.")
	else:
		oc = ObjectContainer(header="Playlist Selection Error", message="VLC is not running.")
	return oc
	
####################################################################################################
#	vlc = Dict['app']['vlc'] or equivalent
#	uri = Dict['PlayList'] key
#
@route(PREFIX+'/PLItemDelete')
def PLItemDelete(vlc, uri):
#	oc = ObjectContainer(title1='PLItemDelete')
	Log.Debug("EXECUTING: PLItemDelete("+str(uri)+")")
	if isinstance(vlc, str):
		vlc = JSON.ObjectFromString(vlc)
	elif not isinstance(vlc, dict):
		return ObjectContainer(header="PLItemDelete Error", message="PLItemDelete() was called with an inappropriate parameter.")
	if str(uri) in Dict['PlayList']:
		if int(Dict['VLCpid']) > 0:
			try:
				page = HTTP.Request(vlc['url_cmd']+vlc['cmd_delete_id']+str(Dict['PlayList'][uri][0])).content
				oc = ObjectContainer(header="Playlist Deletion", message="The Playlist item was deleted.")
				del Dict['PlayList'][uri]
				if uri == Dict['PLselect']:
					Dict['PLselect'] = ''
					Dict['VLC_state'] = VLC_states.stopped
			except:
				oc = ObjectContainer(header="Playlist Deletion Error", message="An exception ocurred."+VLCconfigText())
				Log.Debug("ERROR: PLItemDelete()")
		else:
			oc = ObjectContainer(header="Playlist Deletion", message="The Playlist item was deleted.")
			del Dict['PlayList'][uri] # or -> Dict['PlayList'].pop(uri)
	else:
		oc = ObjectContainer(header="Playlist Deletion Error", message="The Playlist item does not exist.")
	return oc
	
####################################################################################################
#	url = url_vlc_cmd
#
@route(PREFIX+'/PLVClear')
def PLVClear(url):
#	oc = ObjectContainer(title1='PLVClear')
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLVClear()")
		try:
			page = HTTP.Request(url+'pl_stop').content
			Dict['VLC_state'] = VLC_states.stopped
			page = HTTP.Request(url+'pl_empty').content
			oc = ObjectContainer(header="VLC Clear", message="The VLC playlist was cleared.")
		except:
			oc = ObjectContainer(header="VLC Clear Error", message="An exception ocurred."+VLCconfigText())
			Log.Debug("ERROR: PLVClear()")
	else:
		oc = ObjectContainer(header="VLC Clear Error", message="VLC is not running.")
	return oc
	
####################################################################################################
#	url = url_vlc_cmd
#	select = set Dict['PLselect']
#
@route(PREFIX+'/PLVAdd')
def PLVAdd(url, select=False):
#	oc = ObjectContainer(title1='PLVAdd')
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLVAdd()")
		oc = ObjectContainer(header="VLC Add", message="Added the entire Playlist to VLC.")
		url_pl = (VLC_ADR + VLC_REQ) % (Prefs['vlc_host'], Prefs['vlc_port_control'])+ VLC_PL
		try:
			page = HTTP.Request(url_pl).content
			page = page.split('\n')
			VLC_PList = []
			for line in page: # get the VLC playlist
				if line.startswith('<leaf'):
					uri = RE_STAT_URI.search(line).group(1).replace('%20', ' ')
					VLC_PList.append(uri)
			if len(VLC_PList) == 0:
				select = True # VLC playlist is empty
			added = 0
			for uri in Dict['PlayList']: # check against the Plex playlist
				if not (uri in VLC_PList): # add new item to the VLC playlist
					try:
						page = HTTP.Request(url+'in_enqueue&input='+str(uri).replace(' ', '%20')).content
						added += 1
						if select: # the selected one will be the first in the list (assuming VLC playlist is empty)
							Dict['PLselect'] = uri
							select = False
#							Log.Debug('SELECTED URI: '+uri)
					except:
						raise 'in_enqueue error'
			if added == 0:
				oc = ObjectContainer(header="VLC Add", message="No new Playlist items to add to VLC.")
			elif added > 0 and added < len(Dict['PlayList']):
				oc = ObjectContainer(header="VLC Add", message="Added "+str(added)+" Playlist item(s) to VLC.")
		except:
			oc = ObjectContainer(header="VLC Add Error", message="An exception ocurred."+VLCconfigText())
			Log.Debug("ERROR: PLVAdd()")
		UpdatePlayListVLC(False)
	else:
		oc = ObjectContainer(header="VLC Add Error", message="VLC is not running.")
	return oc
	
####################################################################################################
@route(PREFIX+'/PLVReplace')
def PLVReplace():
#	oc = ObjectContainer(title1='PLVReplace')
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLVReplace()")
		UpdatePlayListVLC(True)
		oc = ObjectContainer(header="VLC Replace", message="The Playlist was replaced by VLC.")
	else:
		oc = ObjectContainer(header="VLC Replace Error", message="VLC is not running.")
	return oc
	
####################################################################################################
#	url = url_vlc_cmd
#
@route(PREFIX+'/PLVSync')
def PLVSync(url):
#	oc = ObjectContainer(title1='PLVSync')
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLVSync()")
		if UpdatePlayListVLC(False): # update (some Plex Playlist items may have bogus IDs)
			PLVClear(url) # clear
			PLVAdd(url, True) # replace
			PLVReplace() # Synchronize
			oc = ObjectContainer(header="VLC Sync", message="The Playlist was synchronized with VLC.")
		else:
			oc = ObjectContainer(header="VLC Sync Error", message="VLC is not running.")
	else:
		oc = ObjectContainer(header="VLC Sync Error", message="VLC is not running.")
	return oc
	
####################################################################################################
@route(PREFIX+'/VLCconfigText')
def VLCconfigText():
	if Dict['VLCconfigured']:
		str = ''
	else:
		str = ' VLC is not configured. Restart it.'
	return str
####################################################################################################
#   This function checks to see if the application launched by this Plex channel is running.
#   If it is, then it should be poperly configured.
#
#	app = vlc_proc (object handle)
#	fq_app = VLC_APP
#
@route(PREFIX+'/AppHandleCheck')
def AppHandleCheck(app, fq_app, flag):
	Log.Debug("EXECUTING: AppHandleCheck()")
#	interesting function: determines if a string occurs anywhere in any of a list of strings
#	http://stackoverflow.com/questions/2892931/longest-common-substring-from-more-than-two-strings-python
#	is_common_substr = lambda s, strings: all(s in x for x in strings) # "all" not recognized keyword here
			
	app_found = False
	if not app and Dict['VLCpid'] > 0:
	# Try to determine if the running instance of the app was launched by this channel
		# http://msdn.microsoft.com/en-us/library/ms684880.aspx
		# http://msdn.microsoft.com/en-us/library/ms684320(v=vs.85).aspx -> OpenProcess
		# http://msdn.microsoft.com/en-us/library/ms683215(v=vs.85).aspx -> GetProcessId
		# http://stackoverflow.com/questions/6980246/how-can-i-find-a-process-by-name-and-kill-using-ctypes
#		Psapi = ctypes.WinDLL('Psapi.dll')
#		GetProcessImageFileName = Psapi.GetProcessImageFileNameA
#		Kernel32 = ctypes.WinDLL('kernel32.dll')
#		OpenProcess = Kernel32.OpenProcess

		MAX_PATH_LEN = 260
		hProcess = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, int(Dict['VLCpid']))
		if hProcess:
			pid = ctypes.windll.kernel32.GetProcessId(hProcess) # kind of redundant
			ImageFileName = (ctypes.c_char*MAX_PATH_LEN)()
			if ctypes.windll.psapi.GetProcessImageFileNameA(hProcess, ImageFileName, MAX_PATH_LEN) > 0:
				filename = os.path.basename(ImageFileName.value)
			s1 = fq_app.strip(' ')[::-1] # trim spaces and reverse the strings
			s2 = ImageFileName.value.strip(' ')[::-1]
			i = 0
			while (s1[i] == s2[i]):
				i += 1 # compare the filename and path
#			Log.Debug('>>>>>> '+s1[i::][::-1]+'  '+RE_LOC_MAP.search(fq_app).group('loc'))
			if int(Dict['VLCpid']) == pid and RE_LOC_MAP.search(fq_app).group('loc') == s1[i::][::-1]:
				app_found = True

	if app_found or (app and app.poll() == None): # the application is still running
		Log.Debug('APP is RUNNING!')
		list = [flag, app] # don't override current setting
	else:
		Log.Debug('APP is MISSING!')
		list = [False, None]
	return list
	
####################################################################################################
#   This function checks to see if the application is running.
#   It does not determine if the application was launched by this Plex channel.
#       app_app_file - application file name only (with extension)
#
#	app_app_file = VLC_APP_FILE
#
@route(PREFIX+'/AppRunning')
def AppRunning(app_app_file):
	Log.Debug("EXECUTING: AppRunning()")
	# get PID for vlc.exe if running
	procs = subprocess.check_output(['tasklist', '/fo', 'csv']) # get the list of processes
	procs = RE_EOL.split(procs)
#	Log.Debug("@@@@@@@ " +JSON.StringFromObject(procs))
	procEntry = [row for row in procs if row.find(app_app_file) > 0] # CSV list of lines; find line(s)
	if len(procEntry) > 0:
		if len(procEntry) > 1: # multiple instances of App are running
			Log.Debug("# App Procs= " + str(len(procEntry)))
#		Log.Debug("@@@@@@@ " +procEntry[0])
		procArray = [val.replace('"','') for val in RE_COMMAS.split(procEntry[0])] # CSV list of values
#		Log.Debug("@@@@@@@ "+JSON.StringFromObject(procArray))
		ret = int(procArray[1]) # set the indicator
#		Log.Debug("@@@@@@@ "+str(ret))
	else:
		ret = -1
	Log.Debug("APP_PID= "+str(ret))
	return ret
	
####################################################################################################
#   This function configures the application.
#       Uses: app = Dict['app']
#           app_app - fully qualified application name
#           app_file - file to open using the application
#           app_args - application arguments
#
@route(PREFIX+'/ConfigureApp')
def ConfigureApp(app=None):
	Log.Debug("EXECUTING: ConfigureApp()")
	if int(Dict['VLCpid']) > 0:
		oc = StopApp(Dict['VLCpid'])
		oc = StartApp(app)
		oc = ObjectContainer(header="Application Restart", message="The application was restarted.")
	else:
		Log.Debug("ConfigureApp(): Application is not running")
		oc = ObjectContainer(header="Application Restart Error", message="The application is not running.")
	return oc
	
####################################################################################################
#   This function launches the application.
#       Uses: app = [Dict['app']
#           app_app - fully qualified application name
#           app_file - file to open using the application
#           app_args - application arguments
#
@route(PREFIX+'/StartApp')
def StartApp(app=None):
	global vlc_proc
	if int(Dict['VLCpid']) < 0:
		if isinstance(app, str):
			app = JSON.ObjectFromString(app)
		elif app and not isinstance(app, dict):
			return ObjectContainer(header="StartApp Error", message="StartApp() was called with an inappropriate parameter.")
		Thread.AcquireLock('main')
		Log.Debug("EXECUTING: StartApp()")
		# Start the app in a new thread in the security context of the calling process
	#	vlc_proc = subprocess.Popen([Dict['app']['app_app'], [ClearNoneString(Dict['app']['app_file'])], [ClearNoneString(Dict['app']['app_args'])]])
		# Start VLC without an <mrl> (Media Resource Locator) for repeatable startups
		vlc_proc = subprocess.Popen([Dict['app']['app_app'], [ClearNoneString(Dict['app']['app_args'])]])
		Log.Debug(ClearNoneString(Dict['app']['app_app'])+' '+ClearNoneString(Dict['app']['app_args']))
		Log.Debug(ClearNoneString(Dict['app']['app_file']))
		# pass the initial file (<mrl> to be provided after VLC startup is confirmed
		if WaitPlayVLC(app['vlc'], file=ClearNoneString(Dict['app']['app_file'])): # don't send commands to VLC too quickly; it fails to answer leaving Plex with a request timeout
			Dict['VLCpid'] = int(vlc_proc.pid)
			# this handle is different if the channel is restarted, so it cannot be used for a consistency test
	#		Dict['VLChandle'] = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, int(vlc_proc.pid))
			Dict['VLCconfigured'] = True
			Dict['Initialized'] = False
			Dict['VLC_state'] = VLC_states.stopped
			Thread.Sleep(2)
			PLVSync(app['vlc']['url_cmd'])
			oc = ObjectContainer(header="Application Start", message="The application is now running.")
		else:
			oc = ObjectContainer(header="Application Start", message="The application state is uncertain.")
#		Log.Debug('Running Application:  {' + str(app_app) + '}, with the following arguments {' + subprocess.list2cmdline([[ClearNoneString(app_file)], [ClearNoneString(app_args)]]) + '}')
		Log.Debug("EXITING: StartApp()")
		Thread.ReleaseLock('main')
	else:
		Log.Debug("StartApp(): Application is already running")
		oc = ObjectContainer(header="Application Start Error", message="The application is already running.")
	return oc
	
####################################################################################################
#   This function terminates the application.
#
#	app_pid = Dict['VLCpid']
#
@route(PREFIX+'/StopApp')
def StopApp(app_pid):
	global vlc_proc
	Thread.AcquireLock('main')
	Log.Debug("EXECUTING: StopApp()")
	if int(app_pid) > 0:
		if vlc_proc:
			Log.Debug("app_proc exists")
			vlc_proc.terminate()
			vlc_proc.wait() # wait for process to stop
			oc = ObjectContainer(header="Application Stop", message="The application closed.")
		else:
			Log.Debug("no app_proc")
			try:
				os.kill(int(app_pid), signal.SIGTERM)
				# alternate process:  http://saurabh-python.blogspot.com/2011/01/to-kill-process-in-windows-using-python.html
				#PROCESS_TERMINATE = 1
				#handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, int(app_pid))
				#ctypes.windll.kernel32.TerminateProcess(handle, -1)
				#ctypes.windll.kernel32.CloseHandle(handle)
				Log.Debug('App_pid = '+str(app_pid)+' KILLED')
#				os.kill(pid, 0) #  test to see if process is running (pid > 0)
				oc = ObjectContainer(header="Application Stop", message="The application closed.")
			except OSError as err:
				if err.errno == errno.ESRCH:
					# ESRCH == No such process
					Log.Debug("%%%%% No such process: "+str(app_pid))
				elif err.errno == errno.EPERM:
					# EPERM clearly means there's a process to deny access to
					Log.Debug("%%%%% Access denied to process: "+str(app_pid))
				else:
					# According to "man 2 kill" possible error values are
					# (EINVAL, EPERM, ESRCH)
					Log.Debug("%%%%% Error killing process: "+str(app_pid))
				oc = ObjectContainer(header="Application Stop Error", message="An exception ocurred.")
	else:
		Log.Debug("StopApp(): Application is not running")
		oc = ObjectContainer(header="Application Stop Error", message="The application is not running.")
	Dict['VLCconfigured'] = False
	Dict['VLCpid'] = -1
	vlc_proc = None
	Dict['VLC_state'] = VLC_states.stopped
	Log.Debug("EXITING: StopApp()")
	Thread.ReleaseLock('main')
	return oc
	
####################################################################################################
#   Converts a string with a None value, to an empty string.
#       value - the value to convert to an empty string, if it is of None value
#
@route(PREFIX+'/ClearNoneString')
def ClearNoneString(value):
	if value is None:
		return ''
	return str(value)
	
####################################################################################################
# This method combines the ability to create a VideoClipObject and the MetadataObjectForURL() method
#   sometimes set as a call back in the VideoClipObject key parameter
@route(PREFIX+'/CreateVideoClipObject')
def CreateVideoClipObject(url, originally_available_at, url_meta, key_string, include_container=False, maxVideoBitrate=None, protocol=None, partIndex=None, session=None, offset=None, videoQuality=None, videoResolution=None, directStream=None, audioBoost=None, fastSeek=None, directPlay=None, subtitleSize=None, mediaIndex=None):
	Log.Debug("EXECUTING: CreateVideoClipObject()")
	if session:
		# This only has data following a browse to the url following=> /video/:/transcode/universal/start.m3u8?path=...
		#   out of the "Plex Media Server.log"
		#	maxVideoBitrate is set in the Roku Plex Channel Preferences
		json = "{\"url\":\""+url+"\",\"originally_available_at\":"+originally_available_at+",\"url_meta\":\""+url_meta+"\",\"key_string\":\""+key_string+"\",\"include_container\":"+str(include_container)+",\"maxVideoBitrate\":"+str(maxVideoBitrate)+",\"protocol\":\""+str(protocol)+"\",\"partIndex\":"+str(partIndex)+",\"session\":\""+str(session)+"\",\"offset\":"+str(offset)+",\"videoQuality\":"+str(videoQuality)+",\"videoResolution\":\""+str(videoResolution)+"\",\"directStream\":"+str(directStream)+",\"audioBoost\":"+str(audioBoost)+",\"fastSeek\":"+str(fastSeek)+",\"directPlay\":"+str(directPlay)+",\"subtitleSize\":"+str(subtitleSize)+",\"mediaIndex\":"+str(mediaIndex)+"}"
		Log.Debug(json)

	try:
		details = JSON.ObjectFromString(METADATA, encoding=None)['data']
	except:
		raise Ex.MediaNotAuthorized

	if Dict['VLCpid'] > 0 and str(originally_available_at).find('+') < 0:
		try:
			# when a Select Quality item is selected (after "Play"), this HTTP.Request call will throw an exception
			# This occurs on the second call here with include_container='True' (Metadata call)
			# This can be detected because on the 2nd such call, the date gets encoded where the 
			#   space between the date and time is converted to '+'
			# The first such call occurs when the VideoClipObject Icon is selected, and 
			#   it does not experience said date encoding
			if Prefs['start_delay'] == 'none' and VLCPlayTest(vlc['url_meta']) != 1 or len(Dict['VLC_metadata']) == 0:
				# Don't try to get metadata if there is no delay and VLC is not playing anything and there is previous data
				Dict['VLC_metadata'] = HTTP.Request(url_meta).content # save the metadata -> VLC source, not VLC output
		except:
			Log.Debug('ERROR: VLC meta data retrieval failed.')
	elif Prefs['start_delay'] != 'direct': # this is the second Metadata call
		Thread.CreateTimer(0.0, PlayVLCtimer, True, 5) # start VLC after starting the player 
	if len(Dict['VLC_metadata']) > 0: # hopefully there is metadata
		details2 = JSON.ObjectFromString(Dict['VLC_metadata'])
#	Log.Debug('details2= '+JSON.StringFromObject(details2))
	if Prefs['start_delay'] == 'direct':
		file = RE_FILE.search(key_string)
		if file: # is it a file uri -> NOT CURRENTLY SUPPORTED
			url = file.group(1).replace('+',' ').replace('/','\\')
		else:
			url = key_string
	
	ext = ''
	try:
		title = details2['information']['category']['meta']['filename']
		if title and len(title) > 0:
			ext = title.rfind('.')
			if ext > 0:
				title2 = title
				title = title[0:ext]
				ext = title2[ext+1:]
		else:
			raise ValueError('No VLC filename found.')
	except:
		try:
			title = details['title']
		except:
			title = 'No title'
	title = 'Play VLC Stream' # force for now
			
	try:
		summary = ''
		if title2:
			summary = title2 + '\n\n'
		if Prefs['start_delay'] != 'direct':
			summary += details['description']
		else:
			summary += 'This video is being streamed by Plex from a direct video URL.'
	except:
		summary += 'No description'

	thumb = ''
	thumb_pic = R(T_MOVIE_SEL)
	
	try:
		rating = details['rating'] * 2
	except:
		rating = None
	
	try:
		tags = details['tags']
	except:
		tags = []
	
	try:
		# the duration seen on the video player is retrieved on the second Metadata call
		try:
			duration = details2['length'] * 1000
		except:
			duration = details['duration'] * 1000
	except:
		raise Ex.MediaNotAvailable
	if not isinstance(duration, int):
		raise Ex.MediaNotAvailable
	
	try:
		# can be more than one
		genres = [details['category']]
	except:
		genres = ['Unknown genre']
	
	# Some of this additional information does not appear to help as far as I can tell
	# The MediaObject information is passed to the stream source url in a query string
	# VLC ignores that information
	try:
		if details2['information']['category']['Stream 0']['Type'] == 'Video':
			stream_video = details2['information']['category']['Stream 0']
		elif details2['information']['category']['Stream 1']['Type'] == 'Video':
			stream_video = details2['information']['category']['Stream 1']
		else:
			stream_video = None
	except:
		stream_video = None
	try:
		if details2['information']['category']['Stream 0']['Type'] == 'Audio':
			stream_audio = details2['information']['category']['Stream 0']
		elif details2['information']['category']['Stream 1']['Type'] == 'Audio':
			stream_audio = details2['information']['category']['Stream 1']
		else:
			stream_audio = None
	except:
		stream_audio = None
	vlc_transcode = str(Prefs['vlc_transcode'])
	try:
		video_codec = RE_VLC_VC.search(vlc_transcode).group(1)
	except:
		try:
			video_codec = RE_VLC_COD.search(stream_video['Codec']).group(1)
		except:
			video_codec = VideoCodec.H264
	if video_codec == 'avc1':
		video_codec = VideoCodec.H264
	try:
		audio_codec = RE_VLC_AC.search(vlc_transcode).group(1)
	except:
		try:
			audio_codec = RE_VLC_COD.search(stream_audio['Codec']).group(1)
		except:
			audio_codec  = AudioCodec.MP3
	if audio_codec == 'mpga' or audio_codec == 'mp2a':
		audio_codec = 'mp2'
	elif audio_codec == 'mp3':
		audio_codec = AudioCodec.MP3
#	elif audio_codec == 'mp4a':
#		audio_codec = AudioCodec.AAC # generates an error on Roku
	try:
		audio_channels = int(RE_VLC_CH.search(vlc_transcode).group(1))
	except:
		audio_channels = 2
	try:
		video_frame_rate = RE_VLC_FPS.search(vlc_transcode).group(1)
	except:
		try:
			video_frame_rate = stream_video['Frame_rate'] # not float!
			#video_frame_rate = int(round(float(video_frame_rate)) - .5) + (float(video_frame_rate) > 0)
		except:
			video_frame_rate = None
	try:
		audio_bitrate = Regex('\d+').findall(stream_audio['Bitrate'])[0]
	except:
		audio_bitrate = None
	try:
		resolution = stream_video['Resolution']
		i = resolution.find('x')
		width = resolution[:i]
		height = resolution[i+1:]
	except:
		width = None
		height = None
	try:
		width = int(RE_VLC_W.search(vlc_transcode).group(1))
	except:
		width = width
	try:
		height = int(RE_VLC_H.search(vlc_transcode).group(1))
	except:
		height = height
	if height:
		video_resolution = str(height)
	else:
		video_resolution = '360'
	try:
		aspect_ratio = str(float(width) / float(height)) # not float!
	except:
		aspect_ratio = None
	try:
		if not ext or Prefs['start_delay'] != 'direct':
			container = RE_VLC_MUX.search(Prefs['vlc_mux']).group(1)
		else:
			container = ext
	except:
		container = 'ts'
	if container.find('mp4') >= 0:
		container = Container.MP4
	elif container.find('avi') >= 0:
		container = Container.AVI
	else:
		container = 'mpegts'
	protocols = 'HTTPMP4Video,HTTPVideo,HTTPMP4Streaming' #[Protocol.HTTPMP4Video] # Protocol has no attributes

#	types = demjson.encode(Container) # Framework.api.constkit.Containers -> can't convert to JSON
#	Log.Debug("### "+Container.MP4)

	# When a Metadata call, originally_available_at will be a string object instead of a datetime object
	if isinstance(originally_available_at, str):
		# when the Quality is selected, the automatic encoding changes the space between the date and time to a '+'
		originally_available_at = originally_available_at.replace('+',' ')
		originally_available_at = originally_available_at[0:10] # for date only
#		Log.Debug("### STR OAA= "+originally_available_at)
		originally_available_at = Datetime.ParseDate(originally_available_at)
		
	if Prefs['start_delay'] == 'direct': # it doesn't seem to matter which one is used
		po = [PartObject(key=url, duration=duration)]
	else:
		po = [PartObject(key=Callback(PlayVideo, url=url, default_fmt='360p'), duration=duration)]
	vco = VideoClipObject(
		# The Callback converts all the arguments to strings
		key = Callback(CreateVideoClipObject, url=url, originally_available_at=originally_available_at, url_meta=url_meta, key_string=key_string, include_container=True),
		rating_key = key_string, #url,
		title = title,
		summary = summary,
		thumb = thumb_pic,
#		thumb = Resource.ContentsOfURLWithFallback(thumb),
		rating = rating,
		tags = tags,
		originally_available_at = originally_available_at,
		duration = duration,
		genres = genres,
#		items = MediaObjectsForURL(url) # -> not applicable here, this is set by VLC
		items = [
			MediaObject(
#				parts = [PartObject(key=url, duration=duration)] # works about the same as next line
			#	parts = [PartObject(key=Callback(PlayVideo, url=url, default_fmt='360p'), duration=duration)]
				parts = po
				,container = container # no Container.MPEGTS attribute
				# video_codec & video_resolution are beneficial to Plex for video sync (required for VLC)
				,video_codec = video_codec
				,video_resolution = video_resolution
				,audio_codec = audio_codec
				,audio_channels = audio_channels
				,video_frame_rate = video_frame_rate # "29.917" NTSC
#				,aspect_ratio = aspect_ratio
				,duration = duration
				,width = width
				,height = height
				,bitrate = 900 # video_bitrate in Kbps, not bps
#				,protocol = protocols
				,optimized_for_streaming = True
			)
		]
	)

	if str(include_container) == 'True': # a Metadata call
		return ObjectContainer(objects=[vco])
	else: # a create VideoClipObject call
		return vco
		
####################################################################################################
@route(PREFIX+'/MediaObjectsForURL')
def MediaObjectsForURL(url):
	Log.Debug('EXECUTING: MediaObjectsForURL()')
	items = []
	
	fmts = list(VLC_VIDEO_FORMATS)
	fmts.reverse()
	
	for fmt in fmts:
		index = VLC_VIDEO_FORMATS.index(fmt)
		
		items.append(MediaObject(
#			parts = [PartObject(key=Callback(PlayVideo, url=url, default_fmt=fmt))], # -> Cannot load M3U8
#			parts = [PartObject(key=HTTPLiveStreamURL(url))], # No playable sources found
			parts = [PartObject(key=url)],
			container = VLC_CONTAINERS[index],
			video_codec = VLC_VIDEOCODEC[index],
			audio_codec = VLC_AUDIOCODEC[index],
			video_resolution = VLC_VIDEORES[index],
			audio_channels = 2,
			optimized_for_streaming = (VLC_CONTAINERS[index] == VLC_STREAM_OPT),
		))
			
	return items
	
####################################################################################################
# The IndirectResponse() is a Plex Framework function that tells the client to only execute this function when the user hits play so there is no delays. 
@indirect
@route(PREFIX+'/PlayVideo')
def PlayVideo(url=None, default_fmt=None, **kwargs):
	Log.Debug('EXECUTING: PlayVideo()')
	if not url:
		return None
	Log.Debug('EXITING: PlayVideo()')
	return IndirectResponse(VideoClipObject, key=url)
#	return IndirectResponse(VideoClipObject, key=HTTPLiveStreamURL(url)) # Error loading player: No playable sources found
#	return Redirect(url) # this results in a file download of the stream

####################################################################################################
# passing block of parameters to methods:
# mylist = [1,2,3]
# foo(*mylist)
# def foo(x, y, z)
# x=1
# y=2
# z=3

# mydict = {'x':4,'y':5,'z':6}
# foo(**mydict)
# def foo(x=None, y=None, z=None)
# x=4
# y=5
# z=6

# Debugging exeptions:
# import sys, urllib2
#	try:
#		req = HTTP.Request(vlc['url_meta'])
#		req.load()
#		page = req.content
#		Log.Debug(page)
#	except NameError as ex:
#		Log.Debug('EXCEPTION:NameError: '+str(ex))
#	except urllib2.URLError as ex:
#		Log.Debug('EXCEPTION:URLError: '+str(ex))
#	except:
#		ex = sys.exc_info()[0]
#		Log.Debug('EXCEPTION: '+str(ex))
