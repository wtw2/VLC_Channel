# import for regular expressions
import re
import datetime
import time
# for more complex JSON
import demjson
# for urlopen
import urllib
# to launch/exit an application
import os, subprocess, signal
import errno
# for processing CSV strings
import csv
#import ctypes
import ast # for literal_eval
# http://cs518408v4.vk.me/u5723140/videos/a53afa5870.360.mp4 -> NG
# http://cs514220v4.vk.me/u5723140/videos/7917d4cc3f.360.mp4 -> new

# http://dev.plexapp.com/docs/api/constkit.html

# VLC output parameters:
#1) :sout=#transcode{vcodec=h264,vb=800,acodec=mpga,ab=128,channels=2,samplerate=44100}:http{mux=ts,dst=:11223/stream.ts} :sout-all :sout-keep
# vb = video bitrate
# ab = audio bitrate
# acodec = mpga => MP3
# mux = ts => Transport Stream
# http://:ok@127.0.0.1:5555/requests/README.txt
# http://www.videolan.org/developers/vlc/share/lua/intf/modules/httprequests.lua
# https://wiki.videolan.org/VLC_HTTP_requests/
# an alternative:
# http://n0tablog.wordpress.com/2009/02/09/controlling-vlc-via-rc-remote-control-interface-using-a-unix-domain-socket-and-no-programming/
####################################################################################################
# Last updated: 02/18/2014
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
T_MOVIE      = 'Movies-icon.png'
#URL_VLC      = 'http://%s:%s' % (Prefs['vlc_host'], Prefs['vlc_port_stream']) # filled once on start (static)
VLC_APP_PATH = 'C:\Program Files (x86)\VideoLAN\VLC\\'
VLC_APP_FILE = 'vlc.exe'
VLC_APP      = VLC_APP_PATH + VLC_APP_FILE + ' '
VLC_ARGS0    = '--sout=#'
#VLC_ARGS1    = 'transcode{vcodec=h264,vb=800,acodec=mpga,ab=128,channels=2,samplerate=44100}'
#VLC_ARGS1a   = 'mux=ts'
VLC_ARGS2    = 'http{%sdst=:%s/%s} --sout-all --sout-keep'
VLC_ARGS3    = ' --extraintf=http --http-host=%s --http-port=%s --http-password=%s'
VLC_REQ      = 'http://:%s@%s:%s/requests/'
VLC_STAT     = 'status.xml'
VLC_PL       = 'playlist.xml'
VLC_BR       = 'browse.xml'
VLC_META     = 'status.json'
VLC_CON      = 'http://:%s@%s:%s/?control='
PLEX_PREFS   = 'http://localhost:32400/:/plugins/com.plexapp.plugins.vlcplayer/prefs/set?'

# Great regex tester -> http://regex101.com/
ST_DOM_MAP   = '(?:(?:[0-9a-zA-Z_-]+\.){1,3})[a-zA-Z]{2,4}'
RE_DOM_MAP   = Regex('^%s$' % (ST_DOM_MAP))
ST_IP_MAP    = '(?:[0-9]{1,3}\.){3}[0-9]{1,3}'
RE_IP_MAP    = Regex('^%s$' % (ST_IP_MAP))
ST_PORT_MAP  = '[1-9][0-9]{0,4}'
RE_PORT_MAP  = Regex('^%s$' % (ST_PORT_MAP))
ST_PATH_MAP  = '((?P<path2>/)(?(path2)(?:[0-9a-zA-Z _-]+/)+))?' # added space character
ST_FILE_MAP  = '([0-9a-zA-Z _\-\.]+\.[0-9a-zA-Z]{2,4})?' # added space character
ST_FILE_MAP2 = '((?:[0-9a-zA-Z _\-]+(?P<dot>\.))*(?(dot)[0-9a-zA-Z]{2,4}|[0-9a-zA-Z]*))?' # added space character
ST_PAGE_MAP  = '%s(?(path2)|/?)%s' % (ST_PATH_MAP, ST_FILE_MAP) # WARNING: allows for filename only (initial slash optional)
ST_PAGE_MAP2 = '%s(?(path2)|/?)%s' % (ST_PATH_MAP, ST_FILE_MAP2) # WARNING: allows for filename only (initial slash optional)
RE_PAGE_MAP  = Regex('^%s$' % (ST_PAGE_MAP)) # path is group(1), file is group(3) {relative}
ST_URL_MAP   = 'http://%s:%s%s' % (ST_IP_MAP, ST_PORT_MAP, ST_PAGE_MAP)
RE_URL_MAP   = Regex('^%s$' % (ST_URL_MAP))
ST_URL_MAP2  = '(?:(http|mms|rtsp)|(?P<rtp>rtp|udp))://(?(rtp)(?:%s)?@)%s(?(rtp):%s)?(?(rtp)|%s)' % (ST_DOM_MAP, ST_DOM_MAP, ST_PORT_MAP, ST_PAGE_MAP2)
RE_URL_MAP2  = Regex('^%s$' % (ST_URL_MAP2))
# https://wiki.videolan.org/Documentation:Advanced_Use_of_VLC/
ST_FQFILE_MAP = '(?:(?:[a-zA-Z]:)|(?:%%[a-zA-Z_]+%%))%s' % (ST_PAGE_MAP) # must use % to escape % in string
RE_FQFILE_MAP = Regex('^%s$' % (ST_FQFILE_MAP))
RE_YES_NO    = Regex('^(?i)(?:y(?:es)?|no?)$')
RE_COMMAS    = Regex('(,)(?=(?:[^\"]|\"[^\"]*\")*$)') # all commas not between quotes

VLC_VIDEO_FORMATS = ['360p',	'720p',		'1080p']
VLC_FMT           = [18,		22,			37]
VLC_CONTAINERS    = ['mpegts',	'mpegts',	'mpegts']
VLC_VIDEOCODEC    = ['h264',	'h264',		'h264']
VLC_AUDIOCODEC    = ['mp3',		'mp3',		'mp3']
VLC_VIDEORES      = ['360',		'720',		'1080']
VLC_STREAM_OPT    = 'mpegts'

METADATA     = '{"apiVersion":"2.1","data":{"id":"Hx9TwM4Pmhc","uploaded":"2013-04-25T14:00:46.000Z","updated":"2014-01-27T02:24:39.000Z","uploader":"Unknown","category":"Various","title":"VLC Video Stream","description":"This video is being streamed by VLC player from a file, device, or a direct video URL.","thumbnail":{"sqDefault":"http://i1.ytimg.com/vi/Hx9TwM4Pmhc/default.jpg","hqDefault":"http://i1.ytimg.com/vi/Hx9TwM4Pmhc/hqdefault.jpg"},"player":{"default":"http://www.youtube.com/watch?v=Hx9TwM4Pmhc&feature=youtube_gdata_player","mobile":"http://m.youtube.com/details?v=Hx9TwM4Pmhc"},"content":{"5":"http://www.youtube.com/v/Hx9TwM4Pmhc?version=3&f=videos&app=youtube_gdata","1":"rtsp://r6---sn-o097zuek.c.youtube.com/CiILENy73wIaGQkXmg_OwFMfHxMYDSANFEgGUgZ2aWRlb3MM/0/0/0/video.3gp","6":"rtsp://r6---sn-o097zuek.c.youtube.com/CiILENy73wIaGQkXmg_OwFMfHxMYESARFEgGUgZ2aWRlb3MM/0/0/0/video.3gp"},"duration":3600,"aspectRatio":"widescreen","rating":4.1,"likeCount":"1","ratingCount":1,"viewCount":1,"favoriteCount":1,"commentCount":0,"accessControl":{"comment":"allowed","commentVote":"allowed","videoRespond":"moderated","rate":"allowed","embed":"allowed","list":"allowed","autoPlay":"allowed","syndicate":"allowed"}}}'

# Shorthands:
# Resource.ExternalPath() => R()
# Resource.SharedExternalPath() => S()
# Resource.Load() => L()
####################################################################################################
# Global variables
vlc_proc = None
####################################################################################################
def Start():
	global vlc_proc
	Log.Debug("EXECUTING: Start()")

	Plugin.AddPrefixHandler(PREFIX, MainMenu, TITLE, ICON, ART)
	Plugin.Nice(0) # a resource hog

	ObjectContainer.title1 = NAME
	ObjectContainer.art = R(ART)
	ObjectContainer.no_cache = True

	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON)
	VideoClipObject.art = R(ART)

	TrackObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR
	
	# Store user "globals" in the Dict
	Dict['Initialized'] = False
	Dict['Today'] = datetime.date.today()
	Dict['VLCpid'] = -1
	Dict['fq_file_current'] = ''
	Dict['fq_url_current'] = ''
	Dict['fq_uri_current'] = ''
	Dict['transcode_current'] = ''
#	Dict['PLID'] = -1
	Dict['VLCconfigured'] = AppHandleCheck(vlc_proc)
#	Dict['PlayList'] = dict() # also: {} => save the playlist for future use
	Dict['duration'] = None
	Dict['StreamType'] = None

	Log.Debug('VLC_APP= '+VLC_APP)
	Log.Debug('ST_PAGE_MAP= '+ST_PAGE_MAP)
	Log.Debug('ST_URL_MAP= '+ST_URL_MAP)
	Log.Debug('ST_URL_MAP2= '+ST_URL_MAP2)
	Log.Debug('ST_FQFILE_MAP= '+ST_FQFILE_MAP)
	#InitializePrefs() => can't do this here.  It is too early.  Moved to MainMenu()

####################################################################################################
@route('/video/vlcplayer/InitializePrefs')
def InitializePrefs():
# All non-compliant Prefs will be reset to their default values
	if Dict['Initialized']:
		return
	Log.Debug("EXECUTING: InitializePrefs()")
	Dict['Initialized'] = True

	if Prefs['url_service'] == None:
		u = urllib.urlopen(PLEX_PREFS+'url_service=')
		
#	match = re.search(RE_YES_NO, Prefs['transcode'])
#	if match == None:
	if Prefs['transcode'] == None:
		u = urllib.urlopen(PLEX_PREFS+'transcode=')
	Dict['transcode_current'] = Prefs['transcode']
		
	if Prefs['vlc_transcode'] == None:
		u = urllib.urlopen(PLEX_PREFS+'vlc_transcode=')
	Dict['vlc_transcode_current'] = Prefs['vlc_transcode']
		
	if Prefs['vlc_mux'] == None:
		u = urllib.urlopen(PLEX_PREFS+'vlc_mux=')
	Dict['vlc_mux_current'] = Prefs['vlc_mux']
		
	match = re.search(RE_IP_MAP, Prefs['vlc_host'])
	if match == None:
		u = urllib.urlopen(PLEX_PREFS+'vlc_host=')

	match = re.search(RE_PORT_MAP, Prefs['vlc_port_stream'])
	if match == None:
		u = urllib.urlopen(PLEX_PREFS+'vlc_port_stream=')
		
	match = re.search(RE_PORT_MAP, Prefs['vlc_port_control'])
	if match == None:
		u = urllib.urlopen(PLEX_PREFS+'vlc_port_control=')
		
	match = re.search(RE_PAGE_MAP, Prefs['vlc_page'])
	if match == None:
		u = urllib.urlopen(PLEX_PREFS+'vlc_page=')
		
	match = re.search(RE_FQFILE_MAP, Prefs['fq_file'])
	if match == None:
		u = urllib.urlopen(PLEX_PREFS+'fq_file=')
	else:
		Dict['fq_file_current'] = Prefs['fq_file']
		
	match = re.search(RE_URL_MAP2, Prefs['fq_url'])
	if match == None:
		u = urllib.urlopen(PLEX_PREFS+'fq_url=')
	else:
		Dict['fq_url_current'] = Prefs['fq_url']
	
	Dict['fq_uri_current'] = Prefs['fq_uri']
	
	return

# Force set a preference:
# u = urllib.urlopen('http://{PMS_IP}:32400/:/plugins/{PLUGIN STRING}/prefs/set?{VARIABLE}={VALUE}')
# set vlc_page to defualt >>
# u = urllib.urlopen('http://localhost:32400/:/plugins/com.plexapp.plugins.vlcplayer/prefs/set?vlc_page=')
	
####################################################################################################
def ValidatePrefs():
	global vlc_proc
# NOTE: MessageContainer() is deprecated
# NOTE: Returning an ObjectContainer() with an error does not display the message.
#       Possibly because Plex is already in a popup (Preferences).
	Log.Debug("EXECUTING: ValidatePrefs()")
	Log.Debug("***************************************")
	
#	match = re.search(RE_YES_NO, Prefs['transcode'])
#	if match != None:
#		Log.Debug("STRM  transcode= "+match.group(0))
#	else:
#		Log.Debug("STRM  transcode= INVALID")
	if Prefs['transcode'] != Dict['transcode_current']:
		Dict['transcode_current'] = Prefs['transcode']
		vlc_proc = None
		
	if Prefs['vlc_transcode'] != Dict['vlc_transcode_current']:
		Dict['vlc_transcode_current'] = Prefs['vlc_transcode']
		vlc_proc = None
		
	if Prefs['vlc_mux'] != Dict['vlc_mux_current']:
		Dict['vlc_mux_current'] = Prefs['vlc_mux']
		vlc_proc = None
		
	match = re.search(RE_IP_MAP, Prefs['vlc_host'])
	if match != None:
		Log.Debug("HOST  vlc_host= "+match.group(0))
	else:
		Log.Debug("HOST  vlc_host= INVALID")
		
	match = re.search(RE_PORT_MAP, Prefs['vlc_port_stream'])
	if match != None:
		Log.Debug("PORT  vlc_port_stream= "+match.group(0))
	else:
		Log.Debug("PORT  vlc_port_stream= INVALID")
		
	match = re.search(RE_PORT_MAP, Prefs['vlc_port_control'])
	if match != None:
		Log.Debug("PORT  vlc_port_control= "+match.group(0))
	else:
		Log.Debug("PORT  vlc_port_control= INVALID")
	
	str_page = Prefs['vlc_page']
	if str_page[0] != '/':
		if str_page == ' ':
			str_page = ''
		else:
			str_page = '/' + Prefs['vlc_page'] # does not start with a "/"
	match = re.search(RE_PAGE_MAP, str_page)
	if match != None:
		Log.Debug("PAGE  vlc_page= "+match.group(0))
	else:
		Log.Debug("PAGE  vlc_page= INVALID")

	url_vlc = 'http://%s:%s%s' % (Prefs['vlc_host'], Prefs['vlc_port_stream'], str_page) # dynamic
	match = re.search(RE_URL_MAP, url_vlc)
	if match != None:
		Log.Debug("URL  vlc_url= "+match.group(0))
	else:
		Log.Debug("URL  vlc_url= INVALID")
	
	fq_file = Prefs['fq_file']
	if fq_file:
		fq_file_chng = fq_file.find('\\')
		if fq_file_chng >= 0:
			fq_file = fq_file.replace('\\', '/') # change backslashes to frontslashes for pattern match
			Log.Debug('*****'+fq_file)
		match = re.search(RE_FQFILE_MAP, fq_file)
		if match != None:
			if fq_file_chng >= 0:
				u = urllib.urlopen(PLEX_PREFS+'fq_file='+fq_file)
			if fq_file != Dict['fq_file_current']:
				Dict['fq_file_current'] = fq_file
				Dict['StreamType'] = {'type': 'file:///', 'fq_uri': 'fq_file'}
			Log.Debug("FILE  fq_file= "+match.group(0))
		else:
			Log.Debug("FILE: fq_file= INVALID")
		
	if Prefs['fq_url']:
		match = re.search(RE_URL_MAP2, Prefs['fq_url'])
		if match != None:
			if Prefs['fq_url'] != Dict['fq_url_current']:
				Dict['fq_url_current'] = Prefs['fq_url']
				Dict['StreamType'] = {'type': '', 'fq_uri': 'fq_url'} # the 'http://', etc. protocol is already there
			Log.Debug("URL  fq_url= "+match.group(0))
		else:
			Log.Debug("URL: fq_url= INVALID")
		
	if Prefs['fq_uri'] != Dict['fq_uri_current']:
		Dict['fq_uri_current'] = Prefs['fq_uri']
		Dict['StreamType'] = {'type': '', 'fq_uri': 'fq_uri'}
	Log.Debug("URI: fq_uri= "+ClearNoneString(Prefs['fq_uri']))

	Log.Debug("***************************************")
	return True
	
####################################################################################################
@route('/video/vlcplayer/PrefValidationNotice')
def PrefValidationNotice():
	Log.Debug("EXECUTING: PrefValidationNotice()")
	
#	match = re.search(RE_YES_NO, Prefs['transcode'])
#	if match == None:
#		return ObjectContainer(header="Settings Error", message="The stream Transcode setting is invalid.", no_cache=True)

	match = re.search(RE_IP_MAP, Prefs['vlc_host'])
	if match == None:
		return ObjectContainer(header="Settings Error", message="The IP address setting is invalid.", no_cache=True)

	match = re.search(RE_PORT_MAP, Prefs['vlc_port_stream'])
	if match == None:
		return ObjectContainer(header="Settings Error", message="The IP stream port setting is invalid.", no_cache=True)

	match = re.search(RE_PORT_MAP, Prefs['vlc_port_control'])
	if match == None:
		return ObjectContainer(header="Settings Error", message="The IP control port setting is invalid.", no_cache=True)

	str_page = Prefs['vlc_page']
	if str_page[0] != '/':
		if str_page == ' ':
			str_page = ''
		else:
			str_page = '/' + Prefs['vlc_page'] # does not start with a "/"
	
	match = re.search(RE_PAGE_MAP, str_page)
	if match == None:
		return ObjectContainer(header="Settings Error", message="The page setting is invalid.", no_cache=True)

	url_vlc = 'http://%s:%s%s' % (Prefs['vlc_host'], Prefs['vlc_port_stream'], str_page) # dynamic
	match = re.search(RE_URL_MAP, url_vlc)
	if match == None:
		return ObjectContainer(header="Settings Error", message="The settings do not result in a valid url.", no_cache=True)

	if Prefs['fq_file']:
		match = re.search(RE_FQFILE_MAP, Prefs['fq_file'])
		if match == None:
			return ObjectContainer(header="Settings Error", message="The FQ File setting is invalid.", no_cache=True)

	if Prefs['fq_url']:
		match = re.search(RE_URL_MAP2, Prefs['fq_url'])
		if match == None:
			return ObjectContainer(header="Settings Error", message="The FQ URL setting is invalid.", no_cache=True)

	Log.Debug("PASSED: PrefValidationNotice()")
	return None

####################################################################################################
# the following line performs the same as the Plugin.AddPrefixHandler() method above
#@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():
	global vlc_proc
	
	# Check to see if VLC is actually running
	Dict['VLCpid'] = AppRunning(VLC_APP_FILE)
	Dict['VLCconfigured'] = AppHandleCheck(vlc_proc)

	InitializePrefs()

#	do = DirectoryObject(key = Callback(SecondMenu), title = "Example Directory") # Don't add: Example Directory
	
	voc = PrefValidationNotice()
	if voc:
		voc.add(DirectoryObject(key = Callback(Refresh), title = "Refresh"))
		# attach the settings/preferences
		voc.add(PrefsObject(title = L('Preferences')))
		Log.Debug("FAILED: PrefValidationNotice()")
		return voc
	
	# properties can be filled by parameters in the "New" or set as properties above
#	oc = ObjectContainer(title1=NAME, art=R(ART))
	oc = ObjectContainer()
#	oc.add(do)

	vlc_args = VLC_ARGS0
	temp = ''
	if Prefs['transcode'][0] == 'y':
		if Prefs['vlc_transcode'] != 'none':
			vlc_args += Prefs['vlc_transcode'] + ':'
		if Prefs['vlc_mux'] != 'none':
			temp = Prefs['vlc_mux']+','
	vlc_args += VLC_ARGS2 % (temp, Prefs['vlc_port_stream'], Prefs['vlc_page'])
	vlc_args += VLC_ARGS3 % (Prefs['vlc_host'], Prefs['vlc_port_control'], Prefs['password'])
#	Log.Debug('vlc_args= '+vlc_args)
	
	# access requires no username, only a password
	url_vlc_req = VLC_REQ % (Prefs['password'], Prefs['vlc_host'], Prefs['vlc_port_control'])
	url_vlc_cmd = url_vlc_req + VLC_STAT + '?command='
	url_vlc_meta = url_vlc_req + VLC_META
#	url_vlc_cmd = VLC_CON % (Prefs['password'], Prefs['vlc_host'], Prefs['vlc_port_control']) # doesn't work

	fq_file = 'file:///'+str(Prefs['fq_file']).replace(' ', '%20')
	Dict['app'] = {'app_app':VLC_APP, 'app_file':fq_file, 'app_args':vlc_args, 'vlc':{'url_stop':url_vlc_cmd+'pl_stop', 'url_meta':url_vlc_meta}}

	# Log current settings/preferences click icon
	Log.Debug("#######################################")
	Log.Debug("### vlc_host= "+Prefs['vlc_host'])
	Log.Debug("### vlc_port_stream= "+Prefs['vlc_port_stream'])
	Log.Debug("### vlc_port_control= "+Prefs['vlc_port_control'])
	Log.Debug("### vlc_page= "+Prefs['vlc_page'])
	str_page = Prefs['vlc_page']
	if str_page[0] != '/':
		if str_page == ' ':
			str_page = ''
		else:
			str_page = '/' + Prefs['vlc_page'] # does not start with a "/"
	url_vlc = 'http://%s:%s%s' % (Prefs['vlc_host'], Prefs['vlc_port_stream'], str_page) # dynamic
	Log.Debug("### vlc_url= "+url_vlc)
	Log.Debug("#######################################")
	
	if Dict['StreamType']:
		vco = SourceVLC(url_vlc_cmd, url_vlc_meta, Dict['StreamType']['type'], Prefs[Dict['StreamType']['fq_uri']])
		Dict['StreamType'] = None
		GetPlayListVLC(False) # update the list
		if vco:
			return vco

	if Prefs['url_service']:
		mo = MediaObject(parts=[PartObject(key=HTTPLiveStreamURL(url_vlc))])
		# the following instruction causes the framework to call the URL service
		# see: \Contents\Info.plist -> PlexURLServices
		# see: \Contents\URL Services\VLCplayer\ServiceCode.pys
		vco = VideoClipObject(title="Play VLC Stream", url=url_vlc)
#		vco.add(mo) # not necessary, it is added in: ServiceCode.pys
		Log.Debug('CALLING URL SERVICE')
	else:
		Dict['duration'] = GetCurrentPLdurationVLC(url_vlc_req + VLC_STAT) # can't call GetCurrentPLdurationVLC() inside CreateVideoClipObject()
		vco = CreateVideoClipObject(url_vlc, Dict['Today'], url_meta=url_vlc_meta) # date only
#		vco = CreateVideoClipObject(url_vlc, datetime.datetime.today()) -> CreateVideoClipObject() code commented out

	oc.add(vco)
	# add the settings/preferences object/icon
	oc.add(PrefsObject(title = L('Preferences')))
#	oc.add(InputDirectoryObject(title=L('Search'), key=Callback(SearchMenu))) # The "Search" bubble
	
	# https://wiki.videolan.org/VLC_HTTP_requests/
	oc.add(DirectoryObject(key = Callback(PlayListVLC, url=url_vlc_cmd, url_meta=url_vlc_meta), title = "Play List", thumb = R(T_PLAYLIST)))
	oc.add(DirectoryObject(key = Callback(PlayVLC, url=url_vlc_cmd+'pl_play', url_meta=url_vlc_meta), title = "Play VLC", thumb = R(T_PLAY)))
	oc.add(DirectoryObject(key = Callback(PauseVLC, url=url_vlc_cmd+'pl_pause'), title = "Pause VLC", thumb = R(T_PAUSE)))
	oc.add(DirectoryObject(key = Callback(StopVLC, url=url_vlc_cmd+'pl_stop'), title = "Stop VLC", thumb = R(T_STOP)))
	
	if int(Dict['VLCpid']) < 0:
#		fq_file = '"'+str(Prefs['fq_file']).replace('/', '\\')+'"' # change frontslashes to backslashes (Windows)
		fq_file = 'file:///'+str(Prefs['fq_file']).replace(' ', '%20')
		oc.add(DirectoryObject(key = Callback(StartApp, app=Dict['app']), title = "Launch VLC"))
	elif not Dict['VLCconfigured']:
		fq_file = 'file:///'+str(Prefs['fq_file']).replace(' ', '%20')
		oc.add(DirectoryObject(key = Callback(ConfigureApp, app=Dict['app']), title = "Restart VLC"))
	else:
		oc.add(DirectoryObject(key = Callback(StopApp, app_pid=Dict['VLCpid']), title = "Exit VLC"))		
		
	oc.add(DirectoryObject(key = Callback(GetStatusMetaVLC, url=url_vlc_meta), title = "Status VLC", thumb = R(T_STATUS)))
	oc.add(DirectoryObject(key = Callback(Refresh), title = "Refresh", thumb = R(T_REFRESH)))

#	details = demjson.encode(oc) -> JSONEncodeError('can not encode object into a JSON representation',obj)
#	Log.Debug(details)
	return oc

####################################################################################################
@route('/video/vlcplayer/Refresh')
def Refresh():
	oc = ObjectContainer(title1='Refresh')
	return oc
	
####################################################################################################
@route('/video/vlcplayer/SecondMenu')
def SecondMenu():
	oc = ObjectContainer(title1='Second Menu')
	do = DirectoryObject(key = Callback(ThirdMenu), title = "Example Directory")
	oc.add(do)
	return oc
	
####################################################################################################
@route('/video/vlcplayer/ThirdMenu')
def ThirdMenu():
	oc = ObjectContainer(title1='Third Menu')
	do = DirectoryObject(key = Callback(FourthMenu), title = "Dead end")
	oc.add(do)
	return oc
	
####################################################################################################
@route('/video/vlcplayer/FourthMenu')
def FourthMenu():
	oc = ObjectContainer(title1='Fourth Menu')
	return oc
	
####################################################################################################
@route('/video/vlcplayer/PlayVLC')
def PlayVLC(url, url_meta):
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PlayVLC("+url+")")
		try:
			page = urllib.urlopen(url).read()
			# HTTP.Request won't accept HTTP Basic Authentication credentials in the URL
			#page = HTTP.Request(url).content
			WaitPlayVLC({'url_meta':url_meta})
		except:
			Log.Debug("ERROR: PlayVLC()")
	oc = ObjectContainer(title1='VLC Play')
	return oc
	
####################################################################################################
@route('/video/vlcplayer/WaitPlayVLC')
def WaitPlayVLC(vlc): # vlc is a Dict[]
	Log.Debug("EXECUTING: WaitPlayVLC()")
	i = 20
	j = 1
	while (i > 0): # wait for the counter to start runing
		try:
			page = urllib.urlopen(vlc['url_meta']).read()
			position = re.search('.*"position":([^,]*)', page)
			if position:
				if float(position.group(1)) == 0:
					Log.Debug('WaitPlayVLC(): '+position.group(1))
					time.sleep(j)
					j = 3 - j
					--i
				else:
					if 'url_stop' in vlc:
						page = urllib.urlopen(vlc['url_stop']).read()
					Log.Debug('WaitPlayVLC(): '+position.group(1))
					break
		except:
			time.sleep(2)
			Log.Debug("ERROR: WaitPlayVLC()")
	return
	
####################################################################################################
@route('/video/vlcplayer/PauseVLC')
def PauseVLC(url):
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PauseVLC("+url+")")
		try:
			page = urllib.urlopen(url).read()
		except:
			Log.Debug("ERROR: PauseVLC()")
	oc = ObjectContainer(title1='VLC Pause')
	return oc
	
####################################################################################################
@route('/video/vlcplayer/StopVLC')
def StopVLC(url):
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: StopVLC("+str(url)+")")
		try:
			page = urllib.urlopen(url).read()
		except:
			Log.Debug("ERROR: StopVLC()")
	oc = ObjectContainer(title1='VLC Stop')
	return oc
	
####################################################################################################
@route('/video/vlcplayer/SourceVLC')
def SourceVLC(url, url_meta, type, source):
	oc = None
	if int(Dict['VLCpid']) > 0 and source: # source cannot be = None
		Log.Debug("EXECUTING: SourceVLC("+str(url)+"in_play&input="+type+source+")")
		try:
			page = urllib.urlopen(url+'pl_stop').read()
			uri = type+source
#			page = urllib.urlopen(url+'in_enqueue&input='+uri.replace(' ', '%20')).read() # just add it, don't play it
			if str(uri) in Dict['PlayList']:
				Log.Debug('SourceVLC(): Playlist ID: '+str(Dict['PlayList'][uri][0]))
				page = urllib.urlopen(url+'pl_play&id='+str(Dict['PlayList'][uri][0])).read()
				oc = VLCPlayCheck(oc, url_meta, Dict['PlayList'][uri][2])
				page = urllib.urlopen(url+'pl_stop').read()
			else:
				Log.Debug('SourceVLC: Not in Playlist')
				page = urllib.urlopen(url+'in_play&input='+uri.replace(' ', '%20')).read()
				oc = ObjectContainer(header="Playlist Selection", message="The Playlist item was added.", no_cache=True)
				oc = VLCPlayCheck(oc, url_meta, uri)
				page = urllib.urlopen(url+'pl_stop').read()
		except:
			Log.Debug("ERROR: SourceVLC()")
	return oc
	
####################################################################################################
@route('/video/vlcplayer/VLCPlayCheck')
def VLCPlayCheck(oc_in, url, uri):
	time.sleep(5)
	Log.Debug("EXECUTING: VLCPlayCheck()")
	oc = oc_in
	try:
		page = urllib.urlopen(url).read() # get status.json
		state = re.search('.*("state":"playing")', page)
		file = re.search('^(?:file:///)?(.*)', uri)
		if file:
			file = re.search(RE_FQFILE_MAP, file.group(1)) # check if this is a fully qualified filename
		if file:
			uri = file.group(3) # get just the filename
#		filename = re.search('.*(?:"filename":"([^"]*))', page).group(1) # get filename
		filename = re.search('.*"filename":"'+uri+'"', page) # check for a match (it is supposed to be playing)
		if not state or not filename:
			oc = ObjectContainer(header="Play Error", message="The source could not be opened.", no_cache=True)
		else:
			Log.Debug('PLAYING STATUS: '+ClearNoneString(state.group(1)))
	except:
		oc = ObjectContainer(header="Play Error", message="An exception occurred trying to access VLC.", no_cache=True)
		Log.Debug("ERROR: VLCPlayCheck()")
	return oc
	
####################################################################################################
@route('/video/vlcplayer/GetStatusMetaVLC')
def GetStatusMetaVLC(url):
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: GetStatusMetaVLC("+url+")")
		try:
			page = urllib.urlopen(url).read()
			Log.Debug('STATUS: '+page)
		except:
			Log.Debug("ERROR: GetStatusMetaVLC()")
	else:
		Log.Debug("ERROR: No VLCpid")
	oc = ObjectContainer(title1='Status VLC')
	return oc
	
####################################################################################################
@route('/video/vlcplayer/GetPlayListVLC')
def GetPlayListVLC(new=False):
	if int(Dict['VLCpid']) > 0:
		url = VLC_REQ % (Prefs['password'], Prefs['vlc_host'], Prefs['vlc_port_control'])+ VLC_PL
		Log.Debug("EXECUTING: GetPlayListVLC("+url+")")
		try:
			page = urllib.urlopen(url).read()
			page = page.split('\n')
			if new:
				Dict['PlayList'] = dict() # or {}
			for line in page:
				if line.startswith('<leaf'):
					uri = re.search('.*(?:uri="([^"]*))', line).group(1).replace('%20', ' ')
					id = re.search('.*(?:id="([^"]*))', line).group(1)
					duration = re.search('.*(?:duration="([^"]*))', line).group(1)
					name = re.search('.*(?:name="([^"]*))', line).group(1)
					if uri in Dict['PlayList']: # update the playlist
						Dict['PlayList'][uri][0] = id
						Dict['PlayList'][uri][1] = duration
						Dict['PlayList'][uri][2] = name
					else: # add the new item(s)
						Dict['PlayList'].update({uri:[id, duration, name]})
			Log.Debug('PLAYLIST: '+demjson.encode(Dict['PlayList']))
		except:
			Log.Debug("ERROR: GetPlayListVLC()")
	return
	
####################################################################################################
@route('/video/vlcplayer/GetCurrentPLdurationVLC')
def GetCurrentPLdurationVLC(url):
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: GetCurrentPLdurationVLC("+url+")")
		try:
			page = urllib.urlopen(url).read()
			page = page.split('\n')
			for line in page:
	#			if line.startswith('<currentplid>'):
	#				Dict['PLID'] = re.search('.*(?:<currentplid>([^<]*))', line).group(1)
				if line.startswith('<length>'):
					return re.search('.*(?:<length>([^<]*))', line).group(1)
		except IOError as err:
			Log.Debug('IOError at GetCurrentPLdurationVLC()')
	return None
	
####################################################################################################
@route('/video/vlcplayer/PlayListVLC')
def PlayListVLC(url, url_meta):
	oc = ObjectContainer(title1='Play List')
	Log.Debug("EXECUTING: PlayListVLC()")
	if len(Dict['PlayList']) == 0:
		Log.Debug("PlayList is Empty")
		oc.add(DirectoryObject(key = Callback(PLEmpty), title = "Play List is Empty"))
	else:
		for item in Dict['PlayList']:
			title = str(Dict['PlayList'][item][2])
			match = re.search(RE_PAGE_MAP, title)
			if match and len(match.group(0)) > 0:
				label = match.group(0)
				ext = label.rfind('.')
				if ext > 0:
					label = label[0:ext]
			else:
				label = title
			oc.add(DirectoryObject(key = Callback(PLItem, url=url, url_meta=url_meta, uri=item, label=label), title = title, thumb = R(T_MOVIE)))
	oc.add(DirectoryObject(key = Callback(PLVSync, url=url), title = 'SYNC -> VLC Playlist', thumb = R(T_SYNC)))
	oc.add(DirectoryObject(key = Callback(PLVClear, url=url), title = 'CLEAR -> VLC Playlist', thumb = R(T_DELETE)))
	oc.add(DirectoryObject(key = Callback(PLVAdd, url=url), title = 'ADD -> Plex Playlist to VLC', thumb = R(T_LEFT)))
	oc.add(DirectoryObject(key = Callback(PLVReplace), title = 'REPLACE -> Plex Playlist with VLC', thumb = R(T_RIGHT)))
	return oc
	
####################################################################################################
@route('/video/vlcplayer/PLEmpty')
def PLEmpty():
	oc = ObjectContainer(title1='PLEmpty')
	return oc
	
####################################################################################################
@route('/video/vlcplayer/PLItem')
def PLItem(url, url_meta, uri, label=''):
	oc = ObjectContainer(title1='Play List Item')
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLItem()")
		if str(uri) in Dict['PlayList']:
			oc.add(DirectoryObject(key = Callback(PLItemSelect, url=url, url_meta=url_meta, uri=uri), title = 'SELECT -> '+label, thumb = R(T_MOVIE)))
			oc.add(DirectoryObject(key = Callback(PLItemDelete, url=url, uri=uri), title = 'DELETE -> '+label, thumb = R(T_DELETE)))
	return oc
	
####################################################################################################
@route('/video/vlcplayer/PLItemSelect')
def PLItemSelect(url, url_meta, uri):
	oc = ObjectContainer(header="Playlist Selection", message="The Playlist item was selected.", no_cache=True)
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLItemSelect("+str(uri)+")")
		if str(uri) in Dict['PlayList']:
			try:
				page = urllib.urlopen(url+'pl_play&id='+str(Dict['PlayList'][uri][0])).read()
				oc = VLCPlayCheck(oc, url_meta, Dict['PlayList'][uri][2])
				page = urllib.urlopen(url+'pl_stop').read()
				Log.Debug("SUCCESS: PLItemSelect()")
			except:
				oc = ObjectContainer(title1='PLItemSelect')
				Log.Debug("ERROR: PLItemSelect()")
		else:
			oc = ObjectContainer(header="Playlist Error", message="The Playlist item does not exist.", no_cache=True)
	return oc
	
####################################################################################################
@route('/video/vlcplayer/PLItemDelete')
def PLItemDelete(url, uri):
	oc = ObjectContainer(title1='PLItemDelete')
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLItemDelete("+str(uri)+")")
		if str(uri) in Dict['PlayList']:
			try:
				page = urllib.urlopen(url+'pl_delete&id='+str(Dict['PlayList'][uri][0])).read()
				oc = ObjectContainer(header="Playlist Deletion", message="The Playlist item was deleted.", no_cache=True)
			except:
				Log.Debug("ERROR: PLItemDelete()")
			del Dict['PlayList'][uri]
		else:
			oc = ObjectContainer(header="Playlist Error", message="The Playlist item does not exist.", no_cache=True)
	return oc
	
####################################################################################################
@route('/video/vlcplayer/PLVClear')
def PLVClear(url):
	oc = ObjectContainer(title1='PLVClear')
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLVClear()")
		try:
			page = urllib.urlopen(url+'pl_stop')
			page = urllib.urlopen(url+'pl_empty')
		except:
			Log.Debug("ERROR: PLVClear()")
	return oc
	
####################################################################################################
@route('/video/vlcplayer/PLVAdd')
def PLVAdd(url):
	oc = ObjectContainer(title1='PLVAdd')
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLVAdd()")
		for uri in Dict['PlayList']:
			try:
				page = urllib.urlopen(url+'in_enqueue&input='+str(uri).replace(' ', '%20')).read()
			except:
				Log.Debug("ERROR: PLVAdd()")
		GetPlayListVLC(False)
	return oc
	
####################################################################################################
@route('/video/vlcplayer/PLVReplace')
def PLVReplace():
	oc = ObjectContainer(title1='PLVReplace')
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLVReplace()")
		GetPlayListVLC(True)
	return oc
	
####################################################################################################
@route('/video/vlcplayer/PLVSync')
def PLVSync(url):
	oc = ObjectContainer(title1='PLVSync')
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLVSync()")
		GetPlayListVLC(False) # update (some Plex Playlist items may have bogus IDs)
		PLVClear(url) # clear
		PLVAdd(url) # replace
		PLVReplace() # Synchronize
	return oc
	
####################################################################################################
#   This function checks to see if the application launched by this Plex channel is running.
#   If it is, then it should be poperly configured.
#
@route('/video/vlcplayer/AppHandleCheck')
def AppHandleCheck(app):
	Log.Debug("EXECUTING: AppHandleCheck()")
	if app and not app.poll(): # the application is still running
		Log.Debug('APP is RUNNING!')
		return True
	else:
		Log.Debug('APP is MISSING!')
		return False
	return None
	
####################################################################################################
#   This function checks to see if the application is running.
#   It does not determine if the application was launched by this Plex channel.
#       app_app_file - application file name only (with extension)
#
@route('/video/vlcplayer/AppRunning')
def AppRunning(app_app_file):
	Log.Debug("EXECUTING: AppRunning()")
	# get PID for vlc.exe if running
	procs = subprocess.check_output(['tasklist', '/fo', 'csv']) # get the list of processes
	procEntry = [row for row in procs.split('\n') if row.find(app_app_file) > 0]
	if len(procEntry) > 0:
		if len(procEntry) > 1:
			Log.Debug("# App Procs= " + str(len(procEntry)))
#		Log.Debug("@@@@@@@ " + procEntry[0])
		temp = re.split(RE_COMMAS, procEntry[0])[0::2] # remove all commas not between quotes
#		Log.Debug("@@@@@@@ "+temp[1])
		procArray = list(csv.reader(temp, delimiter=','))
#		Log.Debug("@@@@@@@ "+str(procArray))
		ret = int(procArray[1][0]) # set the indicator
	else:
		ret = -1
	Log.Debug("APP_PID= "+str(ret))
	return ret
	
####################################################################################################
#   This function configures the application.
#       Uses: [Dict['app']
#           app_app - fully qualified application name
#           app_file - file to open using the application
#           app_args - application arguments
#
@route('/video/vlcplayer/ConfigureApp')
def ConfigureApp(app=None):
	Log.Debug("EXECUTING: ConfigureApp()")
	if int(Dict['VLCpid']) > 0:
		oc = StopApp(Dict['VLCpid'])
		time.sleep(1)
		oc = StartApp(app)
	oc = ObjectContainer(title1='Restarted App')
	return oc
	
####################################################################################################
#   This function launches the application.
#       Uses: [Dict['app']
#           app_app - fully qualified application name
#           app_file - file to open using the application
#           app_args - application arguments
#
@route('/video/vlcplayer/StartApp')
def StartApp(app=None):
	global vlc_proc
	if int(Dict['VLCpid']) < 0:
		if isinstance(app, str):
			app = ast.literal_eval(app) # convert string back to Dict
		elif app and not isinstance(app, dict):
			return ObjectContainer(header="StartApp Error", message="StartApp() was called with an inappropriate parameter.", no_cache=True)
		Log.Debug("EXECUTING: StartApp()")
		# Start the app in a new thread in the security context of the calling process
		vlc_proc = subprocess.Popen([Dict['app']['app_app'], [ClearNoneString(Dict['app']['app_file'])], [ClearNoneString(Dict['app']['app_args'])]])
		WaitPlayVLC(app['vlc'])
#		Log.Debug('Running Application:  {' + str(app_app) + '}, with the following arguments {' + subprocess.list2cmdline([[ClearNoneString(app_file)], [ClearNoneString(app_args)]]) + '}')
		Dict['VLCpid'] = int(vlc_proc.pid)
		Dict['VLCconfigured'] = True
		oc = ObjectContainer(title1='Launched App')
	else:
		oc = ObjectContainer(title1='App is running')
	return oc
	
####################################################################################################
#   This function terminates the application.
#       [Takes no arguments]
#
@route('/video/vlcplayer/StopApp')
def StopApp(app_pid):
	global vlc_proc
	if int(app_pid) > 0:
		Log.Debug("EXECUTING: StopApp()")
		if vlc_proc:
			Log.Debug("app_proc exists")
			vlc_proc.terminate()
			vlc_proc.wait() # wait for process to stop
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
		oc = ObjectContainer(title1='Exited App')
	else:
		oc = ObjectContainer(title1='App is not running')
	Dict['VLCconfigured'] = False
	vlc_proc = None
	return oc
	
####################################################################################################
#   Converts a string with a None value, to an empty string.
#       value - the value to convert to an empty string, if it is of None value
#
@route('/video/vlcplayer/ClearNoneString')
def ClearNoneString(value):
	if value is None:
		return ''
	return str(value)
	
####################################################################################################
@route('/video/vlcplayer/CreateVideoClipObject')
def CreateVideoClipObject(url, originally_available_at, url_meta, include_container=False):

	try:
		details = JSON.ObjectFromString(METADATA, encoding=None)['data']
	except:
		raise Ex.MediaNotAuthorized

	try:
		details2 = JSON.ObjectFromString(urllib.urlopen(url_meta).read())
	except:
		Log.Debug('ERROR: VLC meta data retrieval failed.')
	
	try:
		title = details2['information']['category']['meta']['filename']
		if title and len(title) > 0:
			ext = title.rfind('.')
			if ext > 0:
				title = title[0:ext]
				title2 = title
		else:
			raise ValueError('No VLC filename found.')
	except:
		try:
			title = details['title']
		except:
			title = 'No title'

	try:
		summary = ''
		if title2:
			summary = title2 + '\n\n'
		summary += details['description']
	except:
		summary += 'No description'

	thumb = ''
	thumb_pic = R(T_MOVIE)
	
	try:
		rating = details['rating'] * 2
	except:
		rating = None
	
	try:
		tags = details['tags']
	except:
		tags = []
	
	try:
		if Dict['duration']:
			duration = int(Dict['duration']) * 1000
		else:
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
	
#	types = demjson.encode(Container) # Framework.api.constkit.Containers -> can't convert to JSON
#	Log.Debug("### "+Container.MP4)

	# When re-entering CreateVideoClipObject(), originally_available_at can become a string object instead of a datetime.date or a datetime.datetime object
	if isinstance(originally_available_at, str):
		# someting changes the space between the date and time to a '+' when using a datetime object
		originally_available_at = originally_available_at.replace('+',' ')
		originally_available_at = originally_available_at[0:10] # for date only
		Log.Debug("### STR OAA= "+originally_available_at)
		originally_available_at = datetime.datetime.strptime(originally_available_at, '%Y-%m-%d') # for date only
#		#originally_available_at = datetime.datetime.strptime(originally_available_at, '%Y-%m-%d %H:%M:%S.%f') => %f is not supported: use the following
#		nofrag, frag = originally_available_at.split('.')
#		nofrag_dt = datetime.datetime.strptime(nofrag, "%Y-%m-%d %H:%M:%S")
#		originally_available_at = nofrag_dt.replace(microsecond=int(frag))
		Log.Debug("### STR->DATE OAA= "+originally_available_at.isoformat())
	else:
		if isinstance(originally_available_at, datetime.date):
			Log.Debug("### DATE OAA= "+originally_available_at.strftime('%Y-%m-%d')) # for date only
#			Log.Debug("### DATE OAA= "+originally_available_at.isoformat())
		else:
			Log.Debug("### DATE OAA= ERROR")
	
	vco = VideoClipObject(
		key = Callback(CreateVideoClipObject, url=url, originally_available_at=originally_available_at, url_meta=url_meta, include_container=True),
		rating_key = 'VLC Player rating_key', #url,
		title = title,
		summary = summary,
		thumb = thumb_pic,
#		thumb = Resource.ContentsOfURLWithFallback(thumb),
		rating = rating,
		tags = tags,
		originally_available_at = originally_available_at,
		duration = duration,
		genres = genres,
		items = MediaObjectsForURL(url)
#		items = [
#			MediaObject(
#				parts = [PartObject(key=url)],
#				container = 'mpegts', # no Container.MPEGTS
#				video_codec = VideoCodec.H264,
#				video_resolution = '360',
#				audio_codec = AudioCodec.MP3,
#				audio_channels = 2,
#				optimized_for_streaming = True
#			)
#		]
	)

	if include_container:
		return ObjectContainer(objects=[vco])
	else:
		return vco
		
####################################################################################################
@route('/video/vlcplayer/MediaObjectsForURL')
def MediaObjectsForURL(url):

	items = []
	
	fmts = list(VLC_VIDEO_FORMATS)
	fmts.reverse()
	
	for fmt in fmts:
		index = VLC_VIDEO_FORMATS.index(fmt)
		
		items.append(MediaObject(
#			parts = [PartObject(key=Callback(PlayVideo, url=url, default_fmt=fmt))],
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
@route('/video/vlcplayer/PlayVideo')
def PlayVideo(url=None, default_fmt=None, **kwargs):
	
	if not url:
		return None
	return IndirectResponse(VideoClipObject, key=url)
#	return Redirect(url) # this results in a file download of the stream

####################################################################################################
