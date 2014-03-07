NAME = 'Library Updater'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
PMS_URL = 'http://%s/library/sections/'

####################################################################################################
def Start():

	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')

	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = NAME
	ObjectContainer.view_group = 'List'
	DirectoryObject.thumb = R(ICON)

	HTTP.CacheTime = 0

####################################################################################################
@handler('/video/libraryupdater', NAME, thumb=ICON, art=ART)
def MainMenu():

	oc = ObjectContainer(no_cache=True)
	all_keys = []

	try:
		sections = XML.ElementFromURL(GetPmsHost()).xpath('//Directory')

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
def UpdateType(title, key):

	oc = ObjectContainer(title2=title)

	oc.add(DirectoryObject(key=Callback(UpdateSection, title=title, key=key), title='Scan'))
	oc.add(DirectoryObject(key=Callback(UpdateSection, title=title, key=key, analyze=True), title='Analyze Media'))
	oc.add(DirectoryObject(key=Callback(UpdateSection, title=title, key=key, force=True), title='Force Metadata Refresh'))

	return oc

####################################################################################################
def UpdateSection(title, key, force=False, analyze=False):

	for section in key:
		if analyze:
			url = GetPmsHost() + section + '/analyze'
		else:
			url = GetPmsHost() + section + '/refresh'

			if force:
				url += '?force=1'
		
		update = HTTP.Request(url, cacheTime=0).content

	if title == 'All sections':
		return ObjectContainer(header=title, message='All sections will be updated!')
	elif len(key) > 1:
		return ObjectContainer(header=title, message='All chosen sections will be updated!')
	else:
		return ObjectContainer(header=title, message='Section "' + title + '" will be updated!')

####################################################################################################
def GetPmsHost():

	host = Prefs['host']

	if host.find(':') == -1:
		host += ':32400'

	return PMS_URL % (host)
