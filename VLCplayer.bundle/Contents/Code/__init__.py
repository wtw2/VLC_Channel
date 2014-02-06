# import for regular expressions
import re
import datetime
# for more complex JSON
#import demjson
# for urlopen
from urllib import urlopen
#import urllib
# to launch/exit an application
#from subprocess import Popen
import os, subprocess, signal
import errno
# for processing CSV strings
import csv

# http://dev.plexapp.com/docs/api/constkit.html

# VLC output parameters:
#1) :sout=#transcode{vcodec=h264,vb=800,acodec=mpga,ab=128,channels=2,samplerate=44100}:http{mux=ts,dst=:11223/} :sout-all :sout-keep
#2) :sout=#transcode{vcodec=h264,vb=800,acodec=mpga,ab=128,channels=2,samplerate=44100}:http{mux=ts,dst=:11223/stream.ts} :sout-all :sout-keep
# vb = video bitrate
# ab = audio bitrate
# acodec = mpga => MP3
# mux = ts => Transport Stream
####################################################################################################

PREFIX       = '/video/vlcplayer'
NAME         = 'VLC Player'
TITLE        = 'VLC Plugin'
ART          = 'art-default.jpg'
ICON         = 'icon-vlc.png'
VLCURL       = 'http://127.0.0.1:11223'
#VLCURL       = 'http://cs514220v4.vk.me/u5723140/videos/88479e1a6c.360.mp4'
URL_VLC      = 'http://%s:%s' % (Prefs['vlc_host'], Prefs['vlc_port_stream']) # filled once on start (static)
VLC_APP_PATH = 'C:\Program Files (x86)\VideoLAN\VLC\\'
VLC_APP_FILE = 'vlc.exe'
VLC_APP      = VLC_APP_PATH + VLC_APP_FILE + ' '
VLC_FILE     = r'"C:\Users\User\Videos\Physics videos\Videos 360p\Anti-Gravity _ Cold Fusion Explained In Detail_ A New Era In Physics Pt. 1.flv"'
VLC_ARGS     = '--sout=#transcode{vcodec=h264,vb=800,acodec=mpga,ab=128,channels=2,samplerate=44100}:http{dst=:%s/%s} --sout-all --sout-keep --extraintf=http --http-host=%s --http-port=%s --http-password=%s'

# Great regex tester -> http://regex101.com/
ST_IP_MAP    = '(?:[0-9]{1,3}\.){3}[0-9]{1,3}' #WARNING: group must be non-extracting due to use with ST_PATH_MAP in ST_URL_MAP
RE_IP_MAP    = Regex('^%s$' % (ST_IP_MAP))
ST_PORT_MAP  = '[1-9][0-9]{0,4}'
RE_PORT_MAP  = Regex('^%s$' % (ST_PORT_MAP))
ST_PATH_MAP  = '((/)(?(2)(?:[0-9a-zA-Z_-]+/)+))?'
ST_FILE_MAP  = '([0-9a-zA-Z_\-\.]+\.[0-9a-zA-Z]{2,4})?'
ST_PAGE_MAP  = '%s(?(2)|/?)%s' % (ST_PATH_MAP, ST_FILE_MAP) # WARNING: allows for filename only (initial slash optional)
RE_PAGE_MAP  = Regex('^%s$' % (ST_PAGE_MAP)) # path is group(1), file is group(3)
#ST_PAGE_MAP  = '((/)(?(2)(?:[0-9a-zA-Z_-]+/)+))?(?(2)|/?)([0-9a-zA-Z_\-\.]+\.[0-9a-zA-Z]{2,4})?') # path is group(1), file is group(3)
ST_URL_MAP   = 'http://%s:%s%s' % (ST_IP_MAP, ST_PORT_MAP, ST_PAGE_MAP)
RE_URL_MAP   = Regex('^%s$' % (ST_URL_MAP))
#ST_URL_MAP   = '^http://(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[1-9][0-9]{0,4}((/)(?(2)(?:[0-9a-zA-Z_-]+/)+))?(?(2)|/?)([0-9a-zA-Z_\-\.]+\.[0-9a-zA-Z]{2,4})?$'
RE_YES_NO    = Regex('^(?i)(?:y(?:es)?|no?)$')
RE_COMMAS    = Regex('(,)(?=(?:[^\"]|\"[^\"]*\")*$)') # all commas not between quotes

VLC_VIDEO_FORMATS = ['360p',	'720p',		'1080p']
VLC_FMT           = [18,		22,			37]
VLC_CONTAINERS    = ['mpegts',	'mpegts',	'mpegts']
VLC_VIDEOCODEC    = ['h264',	'h264',		'h264']
VLC_AUDIOCODEC    = ['mp3',		'mp3',		'mp3']
VLC_VIDEORES      = ['360',		'720',		'1080']
VLC_STREAM_OPT    = 'mpegts'

METADATA     = '{"apiVersion":"2.1","data":{"id":"Hx9TwM4Pmhc","uploaded":"2013-04-25T14:00:46.000Z","updated":"2014-01-27T02:24:39.000Z","uploader":"Unknown","category":"Various","title":"VLC Video Stream","description":"This video is being streamed by VLC player from a direct video URL.","thumbnail":{"sqDefault":"http://i1.ytimg.com/vi/Hx9TwM4Pmhc/default.jpg","hqDefault":"http://i1.ytimg.com/vi/Hx9TwM4Pmhc/hqdefault.jpg"},"player":{"default":"http://www.youtube.com/watch?v=Hx9TwM4Pmhc&feature=youtube_gdata_player","mobile":"http://m.youtube.com/details?v=Hx9TwM4Pmhc"},"content":{"5":"http://www.youtube.com/v/Hx9TwM4Pmhc?version=3&f=videos&app=youtube_gdata","1":"rtsp://r6---sn-o097zuek.c.youtube.com/CiILENy73wIaGQkXmg_OwFMfHxMYDSANFEgGUgZ2aWRlb3MM/0/0/0/video.3gp","6":"rtsp://r6---sn-o097zuek.c.youtube.com/CiILENy73wIaGQkXmg_OwFMfHxMYESARFEgGUgZ2aWRlb3MM/0/0/0/video.3gp"},"duration":3600,"aspectRatio":"widescreen","rating":4.1,"likeCount":"1","ratingCount":1,"viewCount":1,"favoriteCount":1,"commentCount":0,"accessControl":{"comment":"allowed","commentVote":"allowed","videoRespond":"moderated","rate":"allowed","embed":"allowed","list":"allowed","autoPlay":"allowed","syndicate":"allowed"}}}'

# Shorthands:
# Resource.ExternalPath() => R()
# Resource.SharedExternalPath() => S()
# Resource.Load() => L()
####################################################################################################
# Global variables
vlc_proc = None
####################################################################################################
def Start():
	Log.Debug("EXECUTING: Start()")

	Plugin.AddPrefixHandler(PREFIX, MainMenu, TITLE, ICON, ART)

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
	Dict["Initialized"] = False
	Dict["Today"] = datetime.date.today()
	Dict["VLCpid"] = -1
	#InitializePrefs() => can't do this here.  It is too early.  Moved to MainMenu()

####################################################################################################
@route('/video/vlcplayer/InitializePrefs')
def InitializePrefs():
# All non-compliant Prefs must be reset to their default values
	if Dict["Initialized"]:
		return
	Log.Debug("EXECUTING: InitializePrefs()")
	Dict["Initialized"] = True

	match = re.search(RE_YES_NO, Prefs['url_service'])
	if match == None:
		u = urllib.urlopen('http://localhost:32400/:/plugins/com.plexapp.plugins.vlcplayer/prefs/set?url_service=')
		
	match = re.search(RE_IP_MAP, Prefs['vlc_host'])
	if match == None:
		u = urllib.urlopen('http://localhost:32400/:/plugins/com.plexapp.plugins.vlcplayer/prefs/set?vlc_host=')

	match = re.search(RE_PORT_MAP, Prefs['vlc_port_stream'])
	if match == None:
		u = urllib.urlopen('http://localhost:32400/:/plugins/com.plexapp.plugins.vlcplayer/prefs/set?vlc_port_stream=')
		
	match = re.search(RE_PORT_MAP, Prefs['vlc_port_control'])
	if match == None:
		u = urllib.urlopen('http://localhost:32400/:/plugins/com.plexapp.plugins.vlcplayer/prefs/set?vlc_port_control=')
		
	match = re.search(RE_PAGE_MAP, Prefs['vlc_page'])
	if match == None:
		u = urllib.urlopen('http://localhost:32400/:/plugins/com.plexapp.plugins.vlcplayer/prefs/set?vlc_page=')
	return

# Force set a prference:
# u = urllib.urlopen('http://{PMS_IP}:32400/:/plugins/{PLUGIN STRING}/prefs/set?{VARIABLE}={VALUE}')
# set vlc_page to defualt >>
# u = urllib.urlopen('http://localhost:32400/:/plugins/com.plexapp.plugins.vlcplayer/prefs/set?vlc_page=')
	
####################################################################################################
def ValidatePrefs():
# NOTE: MessageContainer() is deprecated
# NOTE: Returning an ObjectContainer() with an error does not display the message.
#       Probably because Plex is already in a popup (Preferences).
	Log.Debug("EXECUTING: ValidatePrefs()")
	Log.Debug("***************************************")
	match = re.search(RE_YES_NO, Prefs['url_service'])
	if match != None:
		Log.Debug("SERV  url_service= "+match.group(0))
	else:
		Log.Debug("SERV  url_service= INVALID")
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
	Log.Debug("***************************************")
	return
	
####################################################################################################
@route('/video/vlcplayer/PrefValidationNotice')
def PrefValidationNotice():
	Log.Debug("EXECUTING: PrefValidationNotice()")
	match = re.search(RE_YES_NO, Prefs['url_service'])
	if match == None:
		return ObjectContainer(header="Settings Error", message="The URL Service setting is invalid.", no_cache=True)

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
	Log.Debug("PASSED: PrefValidationNotice()")
	return None

####################################################################################################
# the following line performs the same as the Plugin.AddPrefixHandler() method above
#@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():
	global vlc_proc
	InitializePrefs()

	do = DirectoryObject(key = Callback(SecondMenu), title = "Example Directory")

	voc = PrefValidationNotice()
	if not voc == None:
		voc.add(do)
		# attach the settings/preferences
		voc.add(PrefsObject(title = L('Preferences')))
		Log.Debug("FAILED: PrefValidationNotice()")
		return voc
		
# properties can be filled by parameters in the "New" or set as properties above
#	oc = ObjectContainer(title1=NAME, art=R(ART))
	oc = ObjectContainer()
	oc.add(do)
	
	vlc_args = VLC_ARGS % (Prefs['vlc_port_stream'], Prefs['vlc_page'], Prefs['vlc_host'], Prefs['vlc_port_control'], Prefs['password'])
	# Check to see if VLC is actually running
	Dict["VLCpid"] = AppRunning(VLC_APP_FILE)
	if int(Dict["VLCpid"]) > 0:
		oc.add(DirectoryObject(key = Callback(StopApp, app_pid=Dict["VLCpid"]), title = "Exit VLC"))
	else:
		oc.add(DirectoryObject(key = Callback(StartApp, app_app=VLC_APP, app_file=VLC_FILE, app_args=vlc_args), title = "Launch VLC"))

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
	
	url_vlc_req = 'http://%s:%s/requests/status.xml' % (Prefs['vlc_host'], Prefs['vlc_port_control'])
	url_vlc_cmd = url_vlc_req + '?command='
	# https://wiki.videolan.org/VLC_HTTP_requests/
	oc.add(DirectoryObject(key = Callback(PlayVLC, url=url_vlc_cmd+'pl_play'), title = "Play VLC"))
	oc.add(DirectoryObject(key = Callback(PauseVLC, url=url_vlc_cmd+'pl_pause'), title = "Pause VLC"))
	temp = str(url_vlc_cmd+'pl_stop')
	oc.add(DirectoryObject(key = Callback(StopVLC, url=temp), title = "Stop VLC"))
#	oc.add(DirectoryObject(key = Callback(GetStatusMetaVLC, url=url_vlc_req), title = "Status VLC"))

	if Prefs['url_service'][0] == 'y':
		mo = MediaObject(parts=[PartObject(key=HTTPLiveStreamURL(url_vlc))])
		# the following instruction causes the framework to call the URL service
		# see: \Contents\Info.plist -> PlexURLServices
		# see: \Contents\URL Services\VLCplayer\ServiceCode.pys
		vco = VideoClipObject(title="Play VLC Stream", url=url_vlc)
		vco.add(mo)
	else:
		vco = CreateVideoClipObject(url_vlc, Dict["Today"]) # date only
#		vco = CreateVideoClipObject(url_vlc, datetime.datetime.today()) -> CreateVideoClipObject() code commented out

	oc.add(vco)
	# provide for changing the host and port etc.
	oc.add(PrefsObject(title = L('Preferences')))
	
#	details = demjson.encode(oc) -> JSONEncodeError('can not encode object into a JSON representation',obj)
#	Log.Debug(details)
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
def PlayVLC(url):
	Log.Debug("EXECUTING: PlayVLC("+url+")")
	page = HTTP.Request(url).content
	Log.Debug('PLAY: '+page)
	oc = ObjectContainer(title1='VLC Play')
	return oc
	
####################################################################################################
@route('/video/vlcplayer/PauseVLC')
def PauseVLC(url):
	Log.Debug("EXECUTING: PauseVLC("+url+")")
	page = HTTP.Request(url).content
	Log.Debug('PAUSE: '+page)
	oc = ObjectContainer(title1='VLC Pause')
	return oc
	
####################################################################################################
@route('/video/vlcplayer/StopVLC')
def StopVLC(url):
	Log.Debug("EXECUTING: StopVLC("+str(url)+")")
#	page = HTTP.Request(url).content
#	Log.Debug('STOP: '+page)
	oc = ObjectContainer(title1='VLC Stop')
	return oc
	
####################################################################################################
@route('/video/vlcplayer/GetStatusMetaVLC')
def GetStatusMetaVLC(url):
	Log.Debug("EXECUTING: GetStatusMetaVLC("+url+")")
	page = HTTP.Request(url).content
	Log.Debug('STATUS: '+page)
	oc = ObjectContainer(title1='Status VLC')
	return oc
	
####################################################################################################
#   This function checks to see if the application is running.
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
#   This function launches the application.
#       app_app - fully qualified application name
#       app_file - file to open using the application
#       app_args - application arguments
#
@route('/video/vlcplayer/StartApp')
def StartApp(app_app, app_file, app_args):
	global vlc_proc
	if int(Dict["VLCpid"]) < 0:
		Log.Debug("EXECUTING: StartApp()")
		Log.Debug('Running Application:  {' + str(app_app) + '}, with the following arguments {' + subprocess.list2cmdline([[ClearNoneString(app_file)], [ClearNoneString(app_args)]]) + '}')
		# Start the app in a new thread in the security context of the calling process
		vlc_proc = subprocess.Popen([str(app_app), [ClearNoneString(app_file)], [ClearNoneString(app_args)]])
		Dict["VLCpid"] = int(vlc_proc.pid)
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
	return oc
	
####################################################################################################
#   Converts a string with a None value, to an empty string.
#       value - the value to convert to an empty string, if it is of None value
#
@route('/video/vlcplayer/ClearNoneString')
def ClearNoneString(value):
	if((value is None) or (value is '{noneText}')):
		return ''
	return value
	
####################################################################################################
@route('/video/vlcplayer/CreateVideoClipObject')
def CreateVideoClipObject(url, originally_available_at, include_container=False):

	try:
		details = JSON.ObjectFromString(METADATA, encoding=None)['data']
	except:
		raise Ex.MediaNotAuthorized

	try:
		title = details['title']
	except:
		title = 'No title'

	try:
		summary = details['description']
	except:
		summary = 'No description'

	thumb = ''
	
	try:
		rating = details['rating'] * 2
	except:
		rating = None
	
	try:
		tags = details['tags']
	except:
		tags = []
	
	try:
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
		# someting changes the space between the date and time to a '+' when using datetime
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
		key = Callback(CreateVideoClipObject, url=url, originally_available_at=originally_available_at, include_container=True),
		rating_key = 'VLC Player rating_key', #url,
		title = title,
		summary = summary,
		thumb = Resource.ContentsOfURLWithFallback(thumb),
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
