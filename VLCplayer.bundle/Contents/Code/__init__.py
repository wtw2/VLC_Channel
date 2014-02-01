# import for regular expressions
import re
import datetime
#import demjson

# http://dev.plexapp.com/docs/api/constkit.html

# VLC output parameters:
# :sout=#transcode{vcodec=h264,vb=800,acodec=mpga,ab=128,channels=2,samplerate=44100}:http{mux=ts,dst=:11223/} :sout-all :sout-keep
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
URL_VLC      = 'http://%s:%s' % (Prefs['vlc_host'], Prefs['vlc_port']) # filled once on start (static)

ST_IP_MAP    = '(?:[0-9]{1,3}\.){3}[0-9]{1,3}' #WARNING: group must be non-extracting due to use with ST_PATH_MAP in ST_URL_MAP
RE_IP_MAP    = Regex('^%s$' % (ST_IP_MAP))
ST_PORT_MAP  = '[1-9][0-9]{0,4}'
RE_PORT_MAP  = Regex('^%s$' % (ST_PORT_MAP))
ST_PATH_MAP  = '((/)(?(2)(?:[0-9a-zA-Z_-]+/)+))?'
ST_FILE_MAP  = '([0-9a-zA-Z_\-\.]+\.[0-9a-zA-Z]{2,4})?'
ST_PAGE_MAP  = '%s(?(2)|/?)%s' % (ST_PATH_MAP, ST_FILE_MAP) # WARNING: allows for filename only (no slashes)
RE_PAGE_MAP  = Regex('^%s$' % (ST_PAGE_MAP)) # path is group(1), file is group(3)
#ST_PAGE_MAP  = '((/)(?(2)(?:[0-9a-zA-Z_-]+/)+))?(?(2)|/?)([0-9a-zA-Z_\-\.]+\.[0-9a-zA-Z]{2,4})?') # path is group(1), file is group(3)
ST_URL_MAP   = 'http://%s:%s%s' % (ST_IP_MAP, ST_PORT_MAP, ST_PAGE_MAP)
RE_URL_MAP   = Regex('^%s$' % (ST_URL_MAP))
#ST_URL_MAP   = '^http://(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[1-9][0-9]{0,4}((/)(?(2)(?:[0-9a-zA-Z_-]+/)+))?(?(2)|/?)([0-9a-zA-Z_\-\.]+\.[0-9a-zA-Z]{2,4})?$'

#ST_URL_MAP = Regex('^(/[0-9a-zA-Z_\-]*)*(?(1)/)(?:[0-9a-zA-Z_\-\.]+\.[0-9a-zA-Z]{2,4})?((/)(?(2)(?:[0-9a-zA-Z_-]+/)+))?(?(2)|/?)([0-9a-zA-Z_\-\.]+\.[0-9a-zA-Z]{2,4})?$')

METADATA     = '{"apiVersion":"2.1","data":{"id":"Hx9TwM4Pmhc","uploaded":"2013-04-25T14:00:46.000Z","updated":"2014-01-27T02:24:39.000Z","uploader":"Unknown","category":"Various","title":"VLC Video Stream","description":"This video is being streamed by VLC player from a direct video URL.","thumbnail":{"sqDefault":"http://i1.ytimg.com/vi/Hx9TwM4Pmhc/default.jpg","hqDefault":"http://i1.ytimg.com/vi/Hx9TwM4Pmhc/hqdefault.jpg"},"player":{"default":"http://www.youtube.com/watch?v=Hx9TwM4Pmhc&feature=youtube_gdata_player","mobile":"http://m.youtube.com/details?v=Hx9TwM4Pmhc"},"content":{"5":"http://www.youtube.com/v/Hx9TwM4Pmhc?version=3&f=videos&app=youtube_gdata","1":"rtsp://r6---sn-o097zuek.c.youtube.com/CiILENy73wIaGQkXmg_OwFMfHxMYDSANFEgGUgZ2aWRlb3MM/0/0/0/video.3gp","6":"rtsp://r6---sn-o097zuek.c.youtube.com/CiILENy73wIaGQkXmg_OwFMfHxMYESARFEgGUgZ2aWRlb3MM/0/0/0/video.3gp"},"duration":3600,"aspectRatio":"widescreen","rating":4.1,"likeCount":"1","ratingCount":1,"viewCount":1,"favoriteCount":1,"commentCount":0,"accessControl":{"comment":"allowed","commentVote":"allowed","videoRespond":"moderated","rate":"allowed","embed":"allowed","list":"allowed","autoPlay":"allowed","syndicate":"allowed"}}}'

# Shorthands:
# Resource.ExternalPath() => R()
# Resource.SharedExternalPath() => S()
# String.Localization() => L()  ????
####################################################################################################
def Start():
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

####################################################################################################
def ValidatePrefs():
# NOTE: MessageContainer() is deprecated
	Log.Debug("***************************************")
	match = re.search(RE_IP_MAP, Prefs['vlc_host'])
	if match == None:
		return ObjectContainer(header="Error", message="This is not a valid IP address.")
#		return MessageContainer("Error", "That is not a valid IP address.")
	Log.Debug("HOST  vlc_host= "+match.group(0))
	match = re.search(RE_PORT_MAP, Prefs['vlc_port'])
	if match == None:
		return ObjectContainer(header="Error", message="That is not a valid IP port.")
	Log.Debug("PORT  vlc_port= "+match.group(0))
	str_page = Prefs['vlc_page']
	if str_page[0] != '/':
		str_page = '/' + Prefs['vlc_page'] # does not start with a "/"
	match = re.search(RE_PAGE_MAP, str_page)
	if match == None:
		return ObjectContainer(header="Error", message="That is not a valid page.")
	Log.Debug("PAGE  vlc_page= "+match.group(0))

	url_vlc = 'http://%s:%s%s' % (Prefs['vlc_host'], Prefs['vlc_port'], str_page) # dynamic
	match = re.search(RE_URL_MAP, url_vlc)
	if match == None:
		return ObjectContainer(header="Error", message="That is does not result in a valid url.")
	Log.Debug("URL  vlc_url= "+match.group(0))
	return
	
####################################################################################################
# the following line performs the same as the Plugin.AddPrefixHandler() method above
#@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():
# properties can be filled by parameters in the "New" or set as properties above
#	oc = ObjectContainer(title1=NAME, art=R(ART))

	oc = ObjectContainer()
	do = DirectoryObject(key = Callback(SecondMenu), title = "Example Directory")
	oc.add(do)
#	eo = createEpisodeObject(
#		url=VLCURL,
#		title=TITLE,
#		summary=TITLE,
#		thumb=R(ICON),
#		rating_key=TITLE)
#	oc.add(eo)

	# Log current settings/preferences
	Log.Debug("### vlc_host= "+Prefs['vlc_host'])
	Log.Debug("### vlc_port= "+Prefs['vlc_port'])
#	url_vlc = 'http://%s:%s' % (Prefs['vlc_host'], Prefs['vlc_port']) # dynamic
	str_page = Prefs['vlc_page']
	if str_page[0] != '/':
		str_page = '/' + Prefs['vlc_page'] # does not start with a "/"
	url_vlc = 'http://%s:%s%s' % (Prefs['vlc_host'], Prefs['vlc_port'], str_page) # dynamic
	Log.Debug("### vlc_url= "+url_vlc)
	
# the following strategy does appear to work
	mo = MediaObject(parts=[PartObject(key=HTTPLiveStreamURL(url_vlc))])
	# the following instruction causes the framework to call the URL service
	# see: \Contents\Info.plist -> PlexURLServices
	# see: \Contents\URL Services\VLCplayer\ServiceCode.pys
	vco = VideoClipObject(title="Play VLC Stream", url=url_vlc)
	vco.add(mo)
	
# the following strategy does not appear to work (yet)
#	vco = CreateVideoClipObject(url_vlc, datetime.date.today())
	oc.add(vco)
	# provide for changing the host and port
	oc.add(PrefsObject(title = L('Preferences')))
	
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
	
#	types = demjson.encode(Container) # Framework.api.constkit.Containers
#	Log.Debug("### "+Container.MP4)
	if isinstance(originally_available_at, str):
		Log.Debug("### STR OAA= "+originally_available_at)
		originally_available_at = datetime.datetime.strptime(originally_available_at, '%Y-%m-%d')
	else:
		if isinstance(originally_available_at, datetime.date):
			Log.Debug("### DATE OAA= "+originally_available_at.strftime('%m/%d/%Y'))
		else:
			Log.Debug("### DATE OAA= ERROR")
	
	vco = VideoClipObject(
		key = Callback(CreateVideoClipObject, url=url, originally_available_at=originally_available_at, include_container=True),
		rating_key = url,
#		key = Callback(Callback(PlayVideo, url=url, default_fmt='360p'),
#		rating_key = url,
		title = title,
		summary = summary,
		thumb = Resource.ContentsOfURLWithFallback(thumb),
		rating = rating,
		tags = tags,
		originally_available_at = originally_available_at,
		duration = duration,
		genres = genres,
		items = [
			MediaObject(
				parts = [PartObject(key=Callback(PlayVideo, url=url, default_fmt='360p'))],
				container = 'mpegts', # no Container.MPEGTS
				video_codec = VideoCodec.H264,
				video_resolution = '360',
				audio_codec = AudioCodec.MP3,
				audio_channels = 2,
				optimized_for_streaming = True
			)
		]
	)

	if include_container:
		return ObjectContainer(objects=[vco])
	else:
		return vco
		
####################################################################################################
@indirect
def PlayVideo(url=None, default_fmt=None, **kwargs):
	
	if not url:
		return None
	return IndirectResponse(VideoClipObject, key=url)
#	return Redirect(url) # this results in a file download of the stream

####################################################################################################
