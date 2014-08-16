PREFIX = '/video/libraryupdater'
NAME = 'Library Updater'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
PMS_URL = 'http://127.0.0.1:32400/library/sections/'

####################################################################################################
def Start():

	HTTP.CacheTime = 0

####################################################################################################
@handler(PREFIX, NAME, thumb=ICON, art=ART)
def MainMenu():

	oc = ObjectContainer(no_cache=True)
	all_keys = []

	try:
		sections = XML.ElementFromURL(PMS_URL).xpath('//Directory')

		for section in sections:
			key = section.get('key')
			title = section.get('title')
			Log(' --> %s: %s' %(title, key))

			oc.add(DirectoryObject(key=Callback(UpdateType, title=title, key=[key]), title='Update section "' + title + '"'))

			all_keys.append(key)
	except:
		pass

	if len(all_keys) > 0:
		oc.add(DirectoryObject(key=Callback(UpdateType, title='All sections', key=all_keys), title='Update all sections'))

	oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))

	return oc

####################################################################################################
@route(PREFIX + '/type', key=int)
def UpdateType(title, key):

	oc = ObjectContainer(title2=title)

	oc.add(DirectoryObject(key=Callback(UpdateSection, title=title, key=key), title='Scan'))
	oc.add(DirectoryObject(key=Callback(UpdateSection, title=title, key=key, analyze=True), title='Analyze Media'))
	oc.add(DirectoryObject(key=Callback(UpdateSection, title=title, key=key, force=True), title='Force Metadata Refresh'))

	return oc

####################################################################################################
@route(PREFIX + '/section', key=int, force=bool, analyze=bool)
def UpdateSection(title, key, force=False, analyze=False):

	for section in key:
		if analyze:
			url = PMS_URL + section + '/analyze'
			method="PUT"
		else:
			method = "GET"
			url = PMS_URL + section + '/refresh'

			if force:
				url += '?force=1'
		
		Thread.Create(Update, url=url,method=method)

	if title == 'All sections':
		return ObjectContainer(header=title, message='All sections will be updated!')
	elif len(key) > 1:
		return ObjectContainer(header=title, message='All chosen sections will be updated!')
	else:
		return ObjectContainer(header=title, message='Section "' + title + '" will be updated!')
	
####################################################################################################
@route(PREFIX + '/update')
def Update(url, method):
	update = HTTP.Request(url, cacheTime=0, method=method).content
	return