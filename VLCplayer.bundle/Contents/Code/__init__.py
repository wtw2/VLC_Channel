# import for regular expressions
import re
import datetime
import time
# for more complex JSON
import demjson
# for urlopen
import urllib
# to launch/exit/get_info an application
import os, subprocess, signal # for os.path and os.kill
import ctypes # for ctypes.windll
import errno
# for processing CSV strings
import csv
import ast # for literal_eval
# http://cs514220v4.vk.me/u5723140/videos/228d1d52bc.360.mp4 -> 2/22/2014

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
# Last updated: 02/23/2014
#
# Issues:
# When adding a DirectoryObject to an ObjectContainer (and nothing else), there must be at least two
#	before a thumb and the summary text will appear.
#
# Once the VideoClipObject icon is added to the ObjectContainer and displayed, it cannot be removed
#	from the MainMenu display. Re-entering the channel does not remove it even with no_cache=True.
#	The webpage must be refreshed to remove it.
#
# When using the URL Service, once the stream is playing, if you back up one level and select play again
#	it will start a download (YouTube and Khan transfer you to their website).
#
# Streams can take a long time before they appear on the Roku (like 6 minutes)
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
ST_JSON_MAP  = '.*\"(?P<key>%s)\":(?:(?P<dq>\")|(?P<cy>{)|)(?P<val>(?(dq)[^"]*)|(?(cy)[^}]*)|(?:[\d]*\.?[\d]*))(?:(?(dq)\"|(?(cy)})))(?:,|$|\s)' # no nested braces (simple JSON)
ST_DOM_MAP    = '(?:(?:[0-9a-zA-Z_-]+\.){1,3})[a-zA-Z]{2,4}'
RE_DOM_MAP    = Regex('^%s$' % (ST_DOM_MAP))
ST_IP_MAP     = '(?:[0-9]{1,3}\.){3}[0-9]{1,3}'
RE_IP_MAP     = Regex('^%s$' % (ST_IP_MAP))
ST_PORT_MAP   = '[1-9][0-9]{0,4}'
RE_PORT_MAP   = Regex('^%s$' % (ST_PORT_MAP))
ST_PATH_MAP   = '(?P<path>(?P<path2>/)(?(path2)(?:[0-9a-zA-Z _-]+/)+))?' # added space character
ST_FILE_MAP   = '(?P<file>[0-9a-zA-Z _\-\.]+\.[0-9a-zA-Z]{2,4})?' # added space character
ST_FILE_MAP2  = '((?:[0-9a-zA-Z _\-]+(?P<dot>\.))*(?(dot)[0-9a-zA-Z]{2,4}|[0-9a-zA-Z]*))?' # added space character
ST_PAGE_MAP   = '%s(?(path2)|/?)%s' % (ST_PATH_MAP, ST_FILE_MAP) # WARNING: allows for filename only (initial slash optional)
ST_PAGE_MAP2  = '%s(?(path2)|/?)%s' % (ST_PATH_MAP, ST_FILE_MAP2) # WARNING: allows for filename only (initial slash optional)
RE_PAGE_MAP   = Regex('^%s$' % (ST_PAGE_MAP)) # path is group('path'), file is group('file')
ST_URL_MAP    = 'http://%s:%s%s' % (ST_IP_MAP, ST_PORT_MAP, ST_PAGE_MAP)
RE_URL_MAP    = Regex('^%s$' % (ST_URL_MAP))
ST_URL_MAP2   = '(?:(http|mms|rtsp)|(?P<rtp>rtp|udp))://(?(rtp)(?:%s)?@)%s(?(rtp):%s)?(?(rtp)|%s)' % (ST_DOM_MAP, ST_DOM_MAP, ST_PORT_MAP, ST_PAGE_MAP2)
RE_URL_MAP2   = Regex('^%s$' % (ST_URL_MAP2))
# https://wiki.videolan.org/Documentation:Advanced_Use_of_VLC/
ST_LOC_MAP    = '(?P<loc>(?:[a-zA-Z]:)|(?:%%[a-zA-Z_]+%%))' # must use % to escape % in string
ST_FQFILE_MAP = '%s%s' % (ST_LOC_MAP, ST_PAGE_MAP)
RE_FQFILE_MAP = Regex('^%s$' % (ST_FQFILE_MAP)) # path is group('path'), file is group('file')
RE_YES_NO     = Regex('^(?i)(?:y(?:es)?|no?)$')
RE_COMMAS     = Regex('(,)(?=(?:[^\"]|\"[^\"]*\")*$)') # all commas not between quotes

VLC_VIDEO_FORMATS = ['360p',	'720p',		'1080p']
VLC_FMT           = [18,		22,			37]
VLC_CONTAINERS    = ['mpegts',	'mpegts',	'mpegts']
VLC_VIDEOCODEC    = ['h264',	'h264',		'h264']
VLC_AUDIOCODEC    = ['mp3',		'mp3',		'mp3']
VLC_VIDEORES      = ['360',		'720',		'1080']
VLC_STREAM_OPT    = 'mpegts'

PROCESS_QUERY_INFORMATION = 0x0400

METADATA     = '{"apiVersion":"2.1","data":{"id":"Hx9TwM4Pmhc","uploaded":"2013-04-25T14:00:46.000Z","updated":"2014-01-27T02:24:39.000Z","uploader":"Unknown","category":"Various","title":"VLC Video Stream","description":"This video is being streamed by VLC player from a file, device, or a direct video URL.","thumbnail":{"sqDefault":"http://i1.ytimg.com/vi/Hx9TwM4Pmhc/default.jpg","hqDefault":"http://i1.ytimg.com/vi/Hx9TwM4Pmhc/hqdefault.jpg"},"player":{"default":"http://www.youtube.com/watch?v=Hx9TwM4Pmhc&feature=youtube_gdata_player","mobile":"http://m.youtube.com/details?v=Hx9TwM4Pmhc"},"content":{"5":"http://www.youtube.com/v/Hx9TwM4Pmhc?version=3&f=videos&app=youtube_gdata","1":"rtsp://r6---sn-o097zuek.c.youtube.com/CiILENy73wIaGQkXmg_OwFMfHxMYDSANFEgGUgZ2aWRlb3MM/0/0/0/video.3gp","6":"rtsp://r6---sn-o097zuek.c.youtube.com/CiILENy73wIaGQkXmg_OwFMfHxMYESARFEgGUgZ2aWRlb3MM/0/0/0/video.3gp"},"duration":3600,"aspectRatio":"widescreen","rating":4.1,"likeCount":"1","ratingCount":1,"viewCount":1,"favoriteCount":1,"commentCount":0,"accessControl":{"comment":"allowed","commentVote":"allowed","videoRespond":"moderated","rate":"allowed","embed":"allowed","list":"allowed","autoPlay":"allowed","syndicate":"allowed"}}}'

# Shorthands:
# Resource.ExternalPath() => R()
# Resource.SharedExternalPath() => S()
# Resource.Load() => L()
####################################################################################################
# Global variables
vlc_proc = None
# do not allow the application (VLC) to be bombarded with http requests by MainMenu() and asynchronous methods
class VLC_states:
	stopped, paused, playing = ['stopped', 'paused', 'playing']
class main_states:
	run, wait, open = range(3)
main_state = main_states.open # state machine
Log.Debug('GLOBAL VARIABLES WERE RESET.')
####################################################################################################
def Start():
	Log.Debug("EXECUTING: Start()")

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

	HTTP.CacheTime = CACHE_1HOUR # in seconds
	
	# Store user "globals" in the Dict
	Dict['Initialized'] = False
	Dict['Today'] = datetime.date.today()
	Dict['VLCpid'] = -1
	Dict['current_setting'] = dict()
#	Dict['PLID'] = -1
#	Dict['VLCconfigured'] => performed in MainMenu
#	Dict['PlayList'] = dict() # also: {} => save the playlist for future use
	Dict['PLselect'] = ''
	Dict['PlayLock'] = False
	Dict['duration'] = None
	Dict['Streams'] = dict()
	Dict['VLC_state'] = VLC_states.stopped

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
	Dict['current_setting']['transcode'] = Prefs['transcode']
		
	if Prefs['vlc_transcode'] == None:
		u = urllib.urlopen(PLEX_PREFS+'vlc_transcode=')
	Dict['current_setting']['vlc_transcode'] = Prefs['vlc_transcode']
		
	if Prefs['vlc_mux'] == None:
		u = urllib.urlopen(PLEX_PREFS+'vlc_mux=')
	Dict['current_setting']['vlc_mux'] = Prefs['vlc_mux']
		
	match = re.search(RE_IP_MAP, Prefs['vlc_host'])
	if match == None:
		u = urllib.urlopen(PLEX_PREFS+'vlc_host=')
	Dict['current_setting']['vlc_host'] = Prefs['vlc_host']

	match = re.search(RE_PORT_MAP, Prefs['vlc_port_stream'])
	if match == None:
		u = urllib.urlopen(PLEX_PREFS+'vlc_port_stream=')
	Dict['current_setting']['vlc_port_stream'] = Prefs['vlc_port_stream']
		
	match = re.search(RE_PORT_MAP, Prefs['vlc_port_control'])
	if match == None:
		u = urllib.urlopen(PLEX_PREFS+'vlc_port_control=')
	Dict['current_setting']['vlc_port_control'] = Prefs['vlc_port_control']
		
	match = re.search(RE_PAGE_MAP, Prefs['vlc_page'])
	if match == None:
		u = urllib.urlopen(PLEX_PREFS+'vlc_page=')
	Dict['current_setting']['vlc_page'] = Prefs['vlc_page']
		
	match = re.search(RE_FQFILE_MAP, Prefs['fq_file'])
	if match == None:
		u = urllib.urlopen(PLEX_PREFS+'fq_file=')
	else:
		Dict['current_setting']['fq_file'] = Prefs['fq_file']
		
	match = re.search(RE_URL_MAP2, Prefs['fq_url'])
	if match == None:
		u = urllib.urlopen(PLEX_PREFS+'fq_url=')
	else:
		Dict['current_setting']['fq_url'] = Prefs['fq_url']
	
	Dict['current_setting']['fq_uri'] = Prefs['fq_uri']
	
	return

# Force set a preference:
# u = urllib.urlopen('http://{PMS_IP}:32400/:/plugins/{PLUGIN STRING}/prefs/set?{VARIABLE}={VALUE}')
# set vlc_page to defualt >>
# u = urllib.urlopen('http://localhost:32400/:/plugins/com.plexapp.plugins.vlcplayer/prefs/set?vlc_page=')
	
####################################################################################################
def ValidatePrefs():
# NOTE: MessageContainer() is deprecated
# NOTE: Returning an ObjectContainer() with an error does not display the message.
#       Possibly because Plex is already in a popup (Preferences).
	Log.Debug("EXECUTING: ValidatePrefs()")
	Log.Debug("***************************************")
	
	Dict['VLCconfigured'] = True # allow to return to configured state
#	match = re.search(RE_YES_NO, Prefs['transcode'])
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
						
	match = re.search(RE_IP_MAP, Prefs['vlc_host'])
	if match != None:
		if Prefs['vlc_host'] != Dict['current_setting']['vlc_host']:
			Dict['VLCconfigured'] = False
		Log.Debug("HOST  vlc_host= "+match.group(0))
	else:
		Log.Debug("HOST  vlc_host= INVALID")
		
	match = re.search(RE_PORT_MAP, Prefs['vlc_port_stream'])
	if match != None:
		if Prefs['vlc_port_stream'] != Dict['current_setting']['vlc_port_stream']:
			Dict['VLCconfigured'] = False
		Log.Debug("PORT  vlc_port_stream= "+match.group(0))
	else:
		Log.Debug("PORT  vlc_port_stream= INVALID")
		
	match = re.search(RE_PORT_MAP, Prefs['vlc_port_control'])
	if match != None:
		if Prefs['vlc_port_control'] != Dict['current_setting']['vlc_port_control']:
			Dict['VLCconfigured'] = False
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
		if Prefs['vlc_page'] != Dict['current_setting']['vlc_page']:
			Dict['VLCconfigured'] = False
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
			if fq_file != Dict['current_setting']['fq_file']:
				Dict['current_setting']['fq_file'] = fq_file
				Dict['Streams'].update({'file':{'type': 'file:///', 'fq_uri': 'fq_file'}})
			Log.Debug("FILE  fq_file= "+match.group(0))
		else:
			Log.Debug("FILE: fq_file= INVALID")
		
	if Prefs['fq_url']:
		match = re.search(RE_URL_MAP2, Prefs['fq_url'])
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

	Log.Debug("***************************************")
	return True

####################################################################################################
@route('/video/vlcplayer/PrefValidationNotice')
def PrefValidationNotice():
	Log.Debug("EXECUTING: PrefValidationNotice()")
	
#	match = re.search(RE_YES_NO, Prefs['transcode'])
#	if match == None:
#		return ObjectContainer(header="Settings Error", message="The stream Transcode setting is invalid.")

	match = re.search(RE_IP_MAP, Prefs['vlc_host'])
	if match == None:
		return ObjectContainer(header="Settings Error", message="The IP address setting is invalid.")

	match = re.search(RE_PORT_MAP, Prefs['vlc_port_stream'])
	if match == None:
		return ObjectContainer(header="Settings Error", message="The IP stream port setting is invalid.")

	match = re.search(RE_PORT_MAP, Prefs['vlc_port_control'])
	if match == None:
		return ObjectContainer(header="Settings Error", message="The IP control port setting is invalid.")

	str_page = Prefs['vlc_page']
	if str_page[0] != '/':
		if str_page == ' ':
			str_page = ''
		else:
			str_page = '/' + Prefs['vlc_page'] # does not start with a "/"
	
	match = re.search(RE_PAGE_MAP, str_page)
	if match == None:
		return ObjectContainer(header="Settings Error", message="The page setting is invalid.")

	url_vlc = 'http://%s:%s%s' % (Prefs['vlc_host'], Prefs['vlc_port_stream'], str_page) # dynamic
	match = re.search(RE_URL_MAP, url_vlc)
	if match == None:
		return ObjectContainer(header="Settings Error", message="The settings do not result in a valid url.")

	if Prefs['fq_file']:
		match = re.search(RE_FQFILE_MAP, Prefs['fq_file'])
		if match == None:
			return ObjectContainer(header="Settings Error", message="The FQ File setting is invalid.")

	if Prefs['fq_url']:
		match = re.search(RE_URL_MAP2, Prefs['fq_url'])
		if match == None:
			return ObjectContainer(header="Settings Error", message="The FQ URL setting is invalid.")

	Log.Debug("PASSED: PrefValidationNotice()")
	return None

####################################################################################################
# the following line performs the same as the Plugin.AddPrefixHandler() method above
#@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():
	global vlc_proc
	global main_state
	
	i = 30
	while (main_state == main_states.wait and i > 0): # wait for certain running asynchronous processes
		time.sleep(1)
		--i
	main_state = main_states.run
	
	# Check to see if VLC is actually running
	Dict['VLCpid'] = AppRunning(VLC_APP_FILE)
	Dict['VLCconfigured'], vlc_proc = AppHandleCheck(vlc_proc, VLC_APP, Dict['VLCconfigured'])
	
	InitializePrefs()

#	do = DirectoryObject(key = Callback(SecondMenu), title = "Example Directory") # Don't add: Example Directory
	
	voc = PrefValidationNotice()
	if voc:
		voc.add(DirectoryObject(key = Callback(Refresh), title = "Refresh", thumb = R(T_REFRESH)))
		# attach the settings/preferences
		voc.add(PrefsObject(title = L('Preferences')))
		Log.Debug("FAILED: PrefValidationNotice()")
		return voc
	
	# properties can be filled by parameters in the "New" or set as properties above
#	oc = ObjectContainer(title1=NAME, art=R(ART))
	# The following is required to eliminate a persisting error message (when generated) from PrefValidationNotice()
	oc = ObjectContainer(header='', message='')
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

#	fq_file = '"'+str(Prefs['fq_file']).replace('/', '\\')+'"' # change frontslashes to backslashes (Windows)
	fq_file = 'file:///'+str(Prefs['fq_file']).replace(' ', '%20')
	Dict['app'] = {'app_app':VLC_APP, 'app_file':fq_file, 'app_args':vlc_args, 'vlc':{'url_cmd':url_vlc_cmd, 'cmd_stop':'pl_stop', 'cmd_play':'pl_play', 'url_meta':url_vlc_meta}}

	str_page = Prefs['vlc_page']
	if str_page[0] != '/':
		if str_page == ' ':
			str_page = ''
		else:
			str_page = '/' + Prefs['vlc_page'] # does not start with a "/"
	url_vlc = 'http://%s:%s%s' % (Prefs['vlc_host'], Prefs['vlc_port_stream'], str_page) # dynamic
	if 1==0:
		# Log current settings/preferences click icon
		Log.Debug("#######################################")
		Log.Debug("### vlc_host= "+Prefs['vlc_host'])
		Log.Debug("### vlc_port_stream= "+Prefs['vlc_port_stream'])
		Log.Debug("### vlc_port_control= "+Prefs['vlc_port_control'])
		Log.Debug("### vlc_page= "+Prefs['vlc_page'])
		Log.Debug("### vlc_url= "+url_vlc)
		Log.Debug("#######################################")
	
	if Dict['Streams']:
		i = 0
		j = len(Dict['Streams'])
		for stream in Dict['Streams']:
			result, vco = SourceVLC(url_vlc_cmd, url_vlc_meta, Dict['Streams'][stream]['type'], Prefs[Dict['Streams'][stream]['fq_uri']])
			if result:
				i += 1
		Dict['Streams'] = dict()
		UpdatePlayListVLC(False) # update the list
		if j == 1 and vco:
			return vco
		else:
			return  ObjectContainer(header="Playlist Selection", message=str(i)+" of "+str(j)+" Playlist items were added.")

	if int(Dict['VLCpid']) < 0:
		oc.add(DirectoryObject(key = Callback(StartApp, app=Dict['app']), title = "Launch VLC"))
	elif not Dict['VLCconfigured']:
		oc.add(DirectoryObject(key = Callback(ConfigureApp, app=Dict['app']), title = "Restart VLC"))
	else:
		oc.add(DirectoryObject(key = Callback(StopApp, app_pid=Dict['VLCpid']), title = "Exit VLC"))

	
	if not Dict['PlayLock'] and VLCPlayTest(url_vlc_meta) == 1:
		Log.Debug('MainMenu(): Adding a VCO')
		if Prefs['url_service']:
			title = GetStatusTermsVLC(url_vlc_meta, ['filename'])
			if not title: # this should not happen
				title = 'Play VLC Stream'
			mo = MediaObject(parts=[PartObject(key=HTTPLiveStreamURL(url_vlc))])
			# the following instruction causes the framework to call the URL service
			# see: \Contents\Info.plist -> PlexURLServices
			# see: \Contents\URL Services\VLCplayer\ServiceCode.pys
			vco = VideoClipObject(title=title, url=url_vlc)
#			vco.add(mo) # not necessary, it is added in: ServiceCode.pys
			Log.Debug('CALLING URL SERVICE')
		else:
			key_string = Dict['PLselect']
			if not key_string:
				key_string = 'VLC Player rating_key'
#			Log.Debug('>>>> Selected_uri= '+key_string)
			Dict['duration'] = GetStatusTermsVLC(url_vlc_meta, ['length'])[0] # can't call GetStatusTermsVLC() inside CreateVideoClipObject()
			vco = CreateVideoClipObject(url_vlc, Dict['Today'], url_meta=url_vlc_meta, key_string=key_string) # date only
#			vco = CreateVideoClipObject(url_vlc, datetime.datetime.today()) -> CreateVideoClipObject() code commented out
#	else:
#		vco = VideoClipObject(title='', key=' ', rating_key='VLC Player rating_key')
		oc.add(vco)
	
	# https://wiki.videolan.org/VLC_HTTP_requests/
	oc.add(DirectoryObject(key = Callback(PlayListVLC, url=url_vlc_cmd, url_meta=url_vlc_meta), title = "Play List", thumb = R(T_PLAYLIST)))
	if Dict['VLC_state'] == VLC_states.playing or Dict['VLC_state'] == VLC_states.paused:
		text = "VLC is Playing"
	else:
		text = "Play VLC"
	oc.add(DirectoryObject(key = Callback(PlayVLC, url=url_vlc_cmd+'pl_play', url_meta=url_vlc_meta), title = text, thumb = R(T_PLAY)))
	if Dict['VLC_state'] == VLC_states.paused:
		text = "VLC is Paused"
	else:
		text = "Pause VLC"
	oc.add(DirectoryObject(key = Callback(PauseVLC, url=url_vlc_cmd+'pl_pause', url_meta=url_vlc_meta), title = text, thumb = R(T_PAUSE)))
	if Dict['VLC_state'] == VLC_states.stopped:
		text = "VLC is Stopped"
	else:
		text = "Stop VLC"
	oc.add(DirectoryObject(key = Callback(StopVLC, url=url_vlc_cmd+'pl_stop'), title = text, thumb = R(T_STOP)))
	
	oc.add(DirectoryObject(key = Callback(GetStatusMetaVLC, url=url_vlc_meta), title = "Status VLC", thumb = R(T_STATUS)))
	oc.add(DirectoryObject(key = Callback(Refresh, vlc = Dict['app']['vlc']), title = "Refresh", thumb = R(T_REFRESH)))

	# the problem with removing a VCO is not limited to the MainMenu:
#	oc.add(DirectoryObject(key = Callback(SecondMenu, url=url_vlc, date=Dict['Today'], url_meta=url_vlc_meta), title = "Second Menu", thumb = ''))

	# add the settings/preferences object/icon
	oc.add(PrefsObject(title = L('Preferences')))
#	oc.add(InputDirectoryObject(title=L('Search'), key=Callback(SearchMenu))) # The "Search" bubble
#	details = demjson.encode(oc) -> JSONEncodeError('can not encode object into a JSON representation',obj)
#	Log.Debug(details)
	main_state = main_states.open
	return oc

####################################################################################################
#	vlc = Dict['app']['vlc']
#
@route('/video/vlcplayer/Refresh')
def Refresh(vlc):
	Log.Debug("EXECUTING: Refresh("+demjson.encode(vlc)+")")
	oc = ObjectContainer(header="Refresh", message="Updated VLC player status.")
	if isinstance(vlc, str):
		vlc = ast.literal_eval(vlc) # convert string back to Dict
	if int(Dict['VLCpid']) > 0:
		Dict['PlayLock'] = True
		pl_list = GetPlayListVLC()
		if pl_list:
			values = GetStatusTermsVLC(vlc['url_meta'], ['state','filename'])
			if values: # requires: len(values) > 0
				state = values[0]
				if state == VLC_states.paused:
					Dict['VLC_state'] = VLC_states.paused
				elif state == VLC_states.playing:
					Dict['VLC_state'] = VLC_states.playing
				elif state == VLC_states.stopped:
					try:
						page = urllib.urlopen(vlc['url_cmd']+vlc['cmd_play']).read()
						result = WaitPlayVLC(vlc, ['filename'])
						values[1] = result[1][0]
					except:
						oc = ObjectContainer(header="Refresh Error", message="An exception ocurred.")
						Log.Debug("ERROR: Refresh()")
				for list in pl_list:
					if list[3] == values[1]: # filenames match
						Dict['PLselect'] = list[0] # set uri
			elif values == None: # check for exception
				oc = ObjectContainer(header="Refresh Error", message="An exception ocurred.")
				Log.Debug("ERROR: Refresh()")
		Dict['PlayLock'] = False
	else:
		oc = ObjectContainer(header="Refresh Error", message="VLC is not running.")
	return oc
	
####################################################################################################
@route('/video/vlcplayer/SecondMenu')
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
#	url = url_vlc_cmd+'pl_play'
#	url_meta = url_vlc_meta
#
@route('/video/vlcplayer/PlayVLC')
def PlayVLC(url, url_meta):
	if int(Dict['VLCpid']) > 0:
		if Dict['VLC_state'] == VLC_states.stopped:
			Log.Debug("EXECUTING: PlayVLC("+url+")")
			try:
				page = urllib.urlopen(url).read()
				# HTTP.Request won't accept HTTP Basic Authentication credentials in the URL
				#page = HTTP.Request(url).content
				if WaitPlayVLC({'url_meta':url_meta}):
					oc = ObjectContainer(header="VLC Play", message="VLC is now playing.")
					Dict['VLC_state'] = VLC_states.playing
				else:
					oc = ObjectContainer(header="VLC Play Error", message="VLC play state is uncertain.")
			except:
				oc = ObjectContainer(header="VLC Play Error", message="An exception ocurred.")
				Log.Debug("ERROR: PlayVLC()")
		elif Dict['VLC_state'] == VLC_states.playing:
			oc = ObjectContainer(header="VLC Play", message="VLC is already playing.")
		elif  Dict['VLC_state'] == VLC_states.paused:
			oc = ObjectContainer(header="VLC Play", message="VLC is already playing and paused.")
	else:
		oc = ObjectContainer(header="VLC Play Error", message="VLC is not running.")
	return oc
	
####################################################################################################
#	vlc = Dict['app']['vlc'] or equivalent
#	terms = ['filename','length','state',...]
#
@route('/video/vlcplayer/WaitPlayVLC')
def WaitPlayVLC(vlc, terms=None): # vlc is a Dict[]
	Log.Debug("EXECUTING: WaitPlayVLC()")
	i = 15
	j = 1
	result = False
	currentplid = -1
	values = None
	# don't send commands to VLC too quickly; it fails to answer leaving Plex with a request timeout
	while (i > 0): # wait for the counter to start runing
		try:
			checks = GetStatusTermsVLC(vlc['url_meta'], ['position','state','length','currentplid'])
			if checks:
#				Log.Debug('WaitPlayVLC() CHEKCS: '+demjson.encode(checks))
				position = checks[0] # varies from 0 to 1
				# time = position * length
				if int(Dict['VLCpid']) > 0:
					state = checks[1]
				else:
					state = VLC_states.playing
				if checks[3] and int(checks[3]) > currentplid:
					currentplid = int(checks[3])
				if float(position) == 0 and state == VLC_states.playing:
					time.sleep(j)
					j = 3 - j
					--i
				elif state == VLC_states.playing:
					values = GetStatusTermsVLC(vlc['url_meta'], terms)
					if 'url_cmd' in vlc and 'cmd_stop' in vlc:
						page = urllib.urlopen(vlc['url_cmd']+vlc['cmd_stop']).read()
						Dict['VLC_state'] = VLC_states.stopped
					result = True
					break
				else:
					break
		except:
			time.sleep(2)
	if terms != None:
		return [result, values, str(currentplid)]
	return result
	
####################################################################################################
#	url = url_vlc_cmd+'pl_pause'
#	url_meta = url_vlc_meta
#
@route('/video/vlcplayer/PauseVLC')
def PauseVLC(url, url_meta):
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PauseVLC("+url+")")
		try:
			page = urllib.urlopen(url).read()
			time.sleep(1)
			res = VLCPlayTest(url_meta)
			if res == 1:
				oc = ObjectContainer(header="VLC Pause", message="VLC playing continues.")
				Dict['VLC_state'] = VLC_states.playing
			elif res == 0:
				oc = ObjectContainer(header="VLC Pause", message="VLC is paused.")
				Dict['VLC_state'] = VLC_states.paused
			else:
				oc = ObjectContainer(header="VLC Pause Error", message="An exception ocurred.")
		except:
			oc = ObjectContainer(header="VLC Pause Error", message="An exception ocurred.")
			Log.Debug("ERROR: PauseVLC()")
	else:
		oc = ObjectContainer(header="VLC Pause Error", message="VLC is not running.")
	return oc
	
####################################################################################################
#	url = url_vlc_cmd+'pl_stop'
#
@route('/video/vlcplayer/StopVLC')
def StopVLC(url):
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: StopVLC("+str(url)+")")
		try:
			page = urllib.urlopen(url).read()
			oc = ObjectContainer(header="VLC Stop", message="VLC is now stopped.")
			Dict['VLC_state'] = VLC_states.stopped
		except:
			oc = ObjectContainer(header="VLC Stop Error", message="An exception ocurred.")
			Log.Debug("ERROR: StopVLC()")
	else:
		oc = ObjectContainer(header="VLC Stop Error", message="VLC is not running.")
	return oc
	
####################################################################################################
#	url = url_vlc_cmd
#	url_meta = url_vlc_meta
#	type = Dict['Streams'][stream]['type']
#	source = Dict['Streams'][stream]['fq_uri']
#
@route('/video/vlcplayer/SourceVLC')
def SourceVLC(url, url_meta, type, source):
	oc = None
	result = False
	if int(Dict['VLCpid']) > 0 and source: # source cannot be = None
		Log.Debug("EXECUTING: SourceVLC("+str(url)+"in_play&input="+type+source+")")
		try:
			page = urllib.urlopen(url+'pl_stop').read()
			Dict['VLC_state'] = VLC_states.stopped
			uri = type+source
#			page = urllib.urlopen(url+'in_enqueue&input='+uri.replace(' ', '%20')).read() # just add it, don't play it
			if str(uri) in Dict['PlayList']:
				Log.Debug('SourceVLC(): Playlist ID: '+str(Dict['PlayList'][uri][0]))
				page = urllib.urlopen(url+'pl_play&id='+str(Dict['PlayList'][uri][0])).read()
				results = WaitPlayVLC({'url_meta':url_meta},[])
				if results[0]:
					oc = VLCPlayCheck(oc, url_meta, Dict['PlayList'][uri][2])
					if not oc:
						oc = ObjectContainer(header="Playlist Selection", message="The Playlist item was selected.")
						result = True
				else:
					oc = ObjectContainer(header="Play Error", message="The play selection could not be opened.")
			else:
				Log.Debug('SourceVLC: Not in Playlist')
				page = urllib.urlopen(url+'in_play&input='+uri.replace(' ', '%20')).read()
				results = WaitPlayVLC({'url_meta':url_meta},[])
				if results[0]:
					oc = VLCPlayCheck(oc, url_meta, uri)
					if not oc:
						oc = ObjectContainer(header="Playlist Selection", message="The Playlist item was added and selected.")
						result = True
				else:
					oc = ObjectContainer(header="Play Error", message="The play selection could not be opened.")
			page = urllib.urlopen(url+'pl_stop').read()
			if result:
				Dict['PLselect'] = uri
			else:
				page = urllib.urlopen(url+'pl_delete&id='+results[2]).read()
		except:
			Log.Debug("ERROR: SourceVLC()")
	return [result, oc]
	
####################################################################################################
#	oc_in = input ObjectContainer (possibly replaced with a returned ObjectContainer)
#	url = url_vlc_meta
#	url_meta = url_vlc_meta
#	uri = a uri from Dict['Streams'][stream] or VLC playlist
#
@route('/video/vlcplayer/VLCPlayCheck')
def VLCPlayCheck(oc_in, url, uri=None):
	Log.Debug("EXECUTING: VLCPlayCheck()")
	res = VLCPlayTest(url, uri)
	if res == 0:
		oc = ObjectContainer(header="Play Error", message="The play selection could not be opened.")
	elif res == 1:
		oc = oc_in
	else:
		oc = ObjectContainer(header="Play Error", message="An exception occurred trying to access VLC.")
	return oc
	
####################################################################################################
#	url = url_vlc_meta
#	uri = a uri from Dict['Streams'][stream] or VLC playlist
#
@route('/video/vlcplayer/VLCPlayTest')
def VLCPlayTest(url, uri=None):
	Log.Debug("EXECUTING: VLCPlayTest()")
	try:
		page = urllib.urlopen(url).read() # get status.json
		state = re.search('.*("state":"'+VLC_states.playing+'")', page)
		if uri:
			file = re.search('^(?:file:///)?(.*)', uri)
			if file:
				file = re.search(RE_FQFILE_MAP, file.group(1)) # check if this is a fully qualified filename
			if file:
				uri = file.group('file') # get just the filename
			filename = re.search('.*"filename":"'+uri+'"', page) # check for a match (it is supposed to be playing)
		else: # don't care what is playing
			filename = True
		if not state or not filename: # play status NOT confirmation playing
			res = 0
		else: # play status confirmation playing
			res = 1
	except:
		res = -1
	return res
####################################################################################################
# There appears to be no good way to display a lot of text.
#	url = url_vlc_meta
#
@route('/video/vlcplayer/GetStatusMetaVLC')
def GetStatusMetaVLC(url):
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: GetStatusMetaVLC("+url+")")
		try:
			page = urllib.urlopen(url).read()
			oc = ObjectContainer(title1='Status Results', message=page)
#			oc = ObjectContainer(title1='Status Results', message='')
#			oc.add(DirectoryObject(key = Callback(StatusResults), title = "VLC Status", summary = page, thumb = R(T_STATUS)))
			Log.Debug('STATUS: '+page)
		except:
			oc = ObjectContainer(header="VLC Status Error", message="An exception ocurred.")
			Log.Debug("ERROR: GetStatusMetaVLC()")
	else:
		oc = ObjectContainer(header="VLC Status Error", message="VLC is not running.")
	return oc
	
####################################################################################################
@route('/video/vlcplayer/StatusResults')
def StatusResults():
	oc = ObjectContainer(header="Status", message='Don''t click on this.')
	return oc
	
####################################################################################################
#	url = url_vlc_meta
#	terms = ['filename','length','state',...]
#
@route('/video/vlcplayer/GetStatusTermsVLC')
def GetStatusTermsVLC(url, terms=None):
	Log.Debug("EXECUTING: GetStatusTermsVLC()")
	try:
		page = urllib.urlopen(url).read()
		term_values = []
		if terms and isinstance(terms, list):
			for item in terms:
				term = re.search(ST_JSON_MAP % (str(item)), page)
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
@route('/video/vlcplayer/UpdatePlayListVLC')
def UpdatePlayListVLC(new=False):
	if int(Dict['VLCpid']) > 0:
		url = VLC_REQ % (Prefs['password'], Prefs['vlc_host'], Prefs['vlc_port_control'])+ VLC_PL
		Log.Debug("EXECUTING: UpdatePlayListVLC("+url+")")
		pl_list = GetPlayListVLC()
		if pl_list or new:
			if new:
				Dict['PlayList'] = dict() # or {}
			for list in pl_list:
				uri = list[0]
				if uri in Dict['PlayList']: # update the playlist
					Dict['PlayList'][uri][0] = list[1]
					Dict['PlayList'][uri][1] = list[2]
					Dict['PlayList'][uri][2] = list[3]
				else: # add the new item(s)
					Dict['PlayList'].update({uri:[list[1], list[2], list[3]]})
		else:
			Log.Debug("ERROR: UpdatePlayListVLC()")
	return
	
####################################################################################################
@route('/video/vlcplayer/GetPlayListVLC')
def GetPlayListVLC():
	if int(Dict['VLCpid']) > 0:
		url = VLC_REQ % (Prefs['password'], Prefs['vlc_host'], Prefs['vlc_port_control'])+ VLC_PL
		Log.Debug("EXECUTING: GetPlayListVLC()")
		try:
			pl_list = []
			page = urllib.urlopen(url).read()
			page = page.split('\n')
			for line in page:
				if line.startswith('<leaf'):
					uri = re.search('.*(?:uri="([^"]*))', line).group(1).replace('%20', ' ')
					id = re.search('.*(?:id="([^"]*))', line).group(1)
					duration = re.search('.*(?:duration="([^"]*))', line).group(1)
					name = re.search('.*(?:name="([^"]*))', line).group(1)
					pl_list.append([uri,id,duration,name])
			return pl_list
		except:
			Log.Debug("ERROR: GetPlayListVLC()")
	return None
	
####################################################################################################
#	url = url_vlc_cmd
#	url = url_vlc_meta
#
@route('/video/vlcplayer/PlayListVLC')
def PlayListVLC(url, url_meta):
	oc = ObjectContainer(title1='Play List')
	Log.Debug("EXECUTING: PlayListVLC()")
	if len(Dict['PlayList']) == 0:
		Log.Debug("PlayList is Empty")
		oc.add(DirectoryObject(key = Callback(PLEmpty), title = "Play List is Empty", thumb = R(T_EMPTY)))
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
			if item == Dict['PLselect']:
				thumb = R(T_MOVIE_SEL)
			else:
				thumb = R(T_MOVIE)
			oc.add(DirectoryObject(key = Callback(PLItem, url=url, url_meta=url_meta, uri=item, label=label), title = title, summary=title, thumb = thumb))
	oc.add(DirectoryObject(key = Callback(PLVSync, url=url), title = 'SYNC -> Plex & VLC Playlist', thumb = R(T_SYNC)))
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
#	url = url_vlc_cmd
#	url_meta = url_vlc_meta
#	uri = Dict['PlayList'] key name
#	label = summary text
#
@route('/video/vlcplayer/PLItem')
def PLItem(url, url_meta, uri, label=''):
	oc = ObjectContainer(title1='Play List Item')
	Log.Debug("EXECUTING: PLItem()")
	if str(uri) == Dict['PLselect']:
		thumb = R(T_MOVIE_SEL)
	else:
		thumb = R(T_MOVIE)
	if str(uri) in Dict['PlayList']:
		oc.add(DirectoryObject(key = Callback(PLItemSelect, url=url, url_meta=url_meta, uri=uri), title = 'SELECT -> ', summary=label, thumb = thumb))
		oc.add(DirectoryObject(key = Callback(PLItemDelete, url=url, uri=uri), title = 'DELETE -> ', summary=label, thumb = R(T_DELETE)))
	else:
		oc.add(DirectoryObject(key = Callback(PLEmpty), title = 'DELETED', thumb = ''))
	return oc
	
####################################################################################################
#	url = url_vlc_cmd
#	url_meta = url_vlc_meta
#	uri = Dict['PlayList'] key name
#
@route('/video/vlcplayer/PLItemSelect')
def PLItemSelect(url, url_meta, uri):
	oc = None
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLItemSelect("+str(uri)+")")
		if str(uri) in Dict['PlayList']:
			Dict['PlayLock'] = True
			try:
				page = urllib.urlopen(url+'pl_stop').read()
				Dict['VLC_state'] = VLC_states.stopped
				page = urllib.urlopen(url+'pl_play&id='+str(Dict['PlayList'][uri][0])).read()
				WaitPlayVLC({'url_meta':url_meta})
				oc = VLCPlayCheck(oc, url_meta, Dict['PlayList'][uri][2])
				if not oc:
					oc = ObjectContainer(header="Playlist Selection", message="The Playlist item was selected.")
				page = urllib.urlopen(url+'pl_stop').read()
				Dict['VLC_state'] = VLC_states.stopped
				Dict['PLselect'] = uri
				Log.Debug("SUCCESS: PLItemSelect()")
			except:
				oc = ObjectContainer(header="Playlist Selection Error", message="An exception ocurred.")
				Log.Debug("ERROR: PLItemSelect()")
			Dict['PlayLock'] = False
		else:
			oc = ObjectContainer(header="Playlist Selection Error", message="The Playlist item does not exist.")
	else:
		oc = ObjectContainer(header="Playlist Selection Error", message="VLC is not running.")
	return oc
	
####################################################################################################
#	url = url_vlc_cmd
#	uri = Dict['PlayList'] key name
#
@route('/video/vlcplayer/PLItemDelete')
def PLItemDelete(url, uri):
#	oc = ObjectContainer(title1='PLItemDelete')
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLItemDelete("+str(uri)+")")
		if str(uri) in Dict['PlayList']:
			try:
				page = urllib.urlopen(url+'pl_delete&id='+str(Dict['PlayList'][uri][0])).read()
				oc = ObjectContainer(header="Playlist Deletion", message="The Playlist item was deleted.")
				del Dict['PlayList'][uri]
				if uri == Dict['PLselect']:
					Dict['PLselect'] = ''
					Dict['VLC_state'] = VLC_states.stopped
			except:
				oc = ObjectContainer(header="Playlist Deletion Error", message="An exception ocurred.")
				Log.Debug("ERROR: PLItemDelete()")
		else:
			oc = ObjectContainer(header="Playlist Deletion Error", message="The Playlist item does not exist.")
	else:
		oc = ObjectContainer(header="Playlist Deletion Error", message="VLC is not running.")
	return oc
	
####################################################################################################
#	url = url_vlc_cmd
#
@route('/video/vlcplayer/PLVClear')
def PLVClear(url):
#	oc = ObjectContainer(title1='PLVClear')
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLVClear()")
		try:
			page = urllib.urlopen(url+'pl_stop')
			Dict['VLC_state'] = VLC_states.stopped
			page = urllib.urlopen(url+'pl_empty')
			oc = ObjectContainer(header="VLC Clear", message="The VLC playlist was cleared.")
		except:
			oc = ObjectContainer(header="VLC Clear Error", message="An exception ocurred.")
			Log.Debug("ERROR: PLVClear()")
	else:
		oc = ObjectContainer(header="VLC Clear Error", message="VLC is not running.")
	return oc
	
####################################################################################################
#	url = url_vlc_cmd
#	select = set Dict['PLselect']
#
@route('/video/vlcplayer/PLVAdd')
def PLVAdd(url, select=False):
#	oc = ObjectContainer(title1='PLVAdd')
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLVAdd()")
		oc = ObjectContainer(header="VLC Add", message="Added the entire Playlist to VLC.")
		url_pl = VLC_REQ % (Prefs['password'], Prefs['vlc_host'], Prefs['vlc_port_control'])+ VLC_PL
		try:
			page = urllib.urlopen(url_pl).read()
			page = page.split('\n')
			VLC_PList = []
			for line in page: # get the VLC playlist
				if line.startswith('<leaf'):
					uri = re.search('.*(?:uri="([^"]*))', line).group(1).replace('%20', ' ')
					VLC_PList.append(uri)
			if len(VLC_PList) == 0:
				select = True # VLC playlist is empty
			added = 0
			for uri in Dict['PlayList']: # check against the Plex playlist
				if not (uri in VLC_PList): # add new item to the VLC playlist
					try:
						page = urllib.urlopen(url+'in_enqueue&input='+str(uri).replace(' ', '%20')).read()
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
			oc = ObjectContainer(header="VLC Add Error", message="An exception ocurred.")
			Log.Debug("ERROR: PLVAdd()")
		UpdatePlayListVLC(False)
	else:
		oc = ObjectContainer(header="VLC Add Error", message="VLC is not running.")
	return oc
	
####################################################################################################
@route('/video/vlcplayer/PLVReplace')
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
@route('/video/vlcplayer/PLVSync')
def PLVSync(url):
#	oc = ObjectContainer(title1='PLVSync')
	if int(Dict['VLCpid']) > 0:
		Log.Debug("EXECUTING: PLVSync()")
		UpdatePlayListVLC(False) # update (some Plex Playlist items may have bogus IDs)
		PLVClear(url) # clear
		PLVAdd(url, True) # replace
		PLVReplace() # Synchronize
		oc = ObjectContainer(header="VLC Sync", message="The Playlist was synchronized with VLC.")
	else:
		oc = ObjectContainer(header="VLC Sync Error", message="VLC is not running.")
	return oc
	
####################################################################################################
#   This function checks to see if the application launched by this Plex channel is running.
#   If it is, then it should be poperly configured.
#
#	app = vlc_proc (object handle)
#	fq_app = VLC_APP
#
@route('/video/vlcplayer/AppHandleCheck')
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
#			Log.Debug('>>>>>> '+s1[i::][::-1]+'  '+re.search(ST_LOC_MAP, fq_app).group('loc'))
			if int(Dict['VLCpid']) == pid and re.search(ST_LOC_MAP, fq_app).group('loc') == s1[i::][::-1]:
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
		temp = re.split(RE_COMMAS, procEntry[0])[0::2] # remove all commas not between quotes -> [start:stop:step]
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
#       Uses: app = [Dict['app']
#           app_app - fully qualified application name
#           app_file - file to open using the application
#           app_args - application arguments
#
@route('/video/vlcplayer/ConfigureApp')
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
@route('/video/vlcplayer/StartApp')
def StartApp(app=None):
	global vlc_proc
	global main_state
	if int(Dict['VLCpid']) < 0:
		if isinstance(app, str):
			app = ast.literal_eval(app) # convert string back to Dict
		elif app and not isinstance(app, dict):
			return ObjectContainer(header="StartApp Error", message="StartApp() was called with an inappropriate parameter.")
		Log.Debug("EXECUTING: StartApp()")
		while (main_state == main_states.run):  # wait for MainMenu to complete
			time.sleep(1)
		main_state = main_states.wait
		# Start the app in a new thread in the security context of the calling process
		vlc_proc = subprocess.Popen([Dict['app']['app_app'], [ClearNoneString(Dict['app']['app_file'])], [ClearNoneString(Dict['app']['app_args'])]])
		if WaitPlayVLC(app['vlc']): # don't send commands to VLC too quickly; it fails to answer leaving Plex with a request timeout
			Dict['VLCpid'] = int(vlc_proc.pid)
			# this handle is different if the channel is restarted, so it cannot be used for a consistency test
	#		Dict['VLChandle'] = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, int(vlc_proc.pid))
			Dict['VLCconfigured'] = True
			Dict['Initialized'] = False
			Dict['VLC_state'] = VLC_states.stopped
			time.sleep(2)
			PLVSync(app['vlc']['url_cmd'])
			oc = ObjectContainer(header="Application Start", message="The application is now running.")
		else:
			oc = ObjectContainer(header="Application Start", message="The application state is uncertain.")
#		Log.Debug('Running Application:  {' + str(app_app) + '}, with the following arguments {' + subprocess.list2cmdline([[ClearNoneString(app_file)], [ClearNoneString(app_args)]]) + '}')
	else:
		Log.Debug("StartApp(): Application is already running")
		oc = ObjectContainer(header="Application Start Error", message="The application is already running.")
	main_state = main_states.open
	return oc
	
####################################################################################################
#   This function terminates the application.
#
#	app_pid = Dict['VLCpid']
#
@route('/video/vlcplayer/StopApp')
def StopApp(app_pid):
	global vlc_proc
	global main_state
	if int(app_pid) > 0:
		Log.Debug("EXECUTING: StopApp()")
		while (main_state == main_states.run):  # wait for MainMenu to complete
			time.sleep(1)
		main_state = main_states.wait
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
	main_state = main_states.open
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
# This method combines the ability to create a VideoClipObject and the MetadataObjectForURL() method
#   sometimes set as a call back in the VideoClipObject key parameter
@route('/video/vlcplayer/CreateVideoClipObject')
def CreateVideoClipObject(url, originally_available_at, url_meta, key_string, include_container=False):

	try:
		details = JSON.ObjectFromString(METADATA, encoding=None)['data']
	except:
		raise Ex.MediaNotAuthorized

	if Dict['VLCpid'] > 0:
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
	#	Log.Debug("### STR->DATE OAA= "+originally_available_at.isoformat())
	#else:
	#	if isinstance(originally_available_at, datetime.date):
	#		Log.Debug("### DATE OAA= "+originally_available_at.strftime('%Y-%m-%d')) # for date only
#			Log.Debug("### DATE OAA= "+originally_available_at.isoformat())
	#	else:
	#		Log.Debug("### DATE OAA= ERROR")
	
	vco = VideoClipObject(
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

	if include_container: # a Metadata call
		return ObjectContainer(objects=[vco])
	else: # a create VideoClipObject call
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
# The IndirectResponse() is a Plex Framework function that tells the client to only execute this function when the user hits play so there is no delays. 
@route('/video/vlcplayer/PlayVideo')
def PlayVideo(url=None, default_fmt=None, **kwargs):
	
	if not url:
		return None
	return IndirectResponse(VideoClipObject, key=url)
#	return Redirect(url) # this results in a file download of the stream

####################################################################################################
