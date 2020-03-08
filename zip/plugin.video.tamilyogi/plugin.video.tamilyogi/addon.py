import sys
import urllib2
import urllib
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import json
import re
from BeautifulSoup import BeautifulSoup
from t0mm0.common.addon import Addon

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = Addon('plugin.video.tamilyogi', sys.argv)

xbmcplugin.setContent(addon_handle, 'movies')

def build_url(query):
	return base_url + '?' + urllib.urlencode(query)

mode = args.get('mode', None)

def getMovieList():
	movie_list = {}
	index = 0
	req = urllib2.Request('http://tamilyogi.cool/category/tamilyogi-full-movie-online/')
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	page_content = response.read()
	response.close()
	soup = BeautifulSoup(page_content)

	div_main = soup.find('div', {'id': 'main'})
	if div_main:
		div_archive = div_main.find('div', {'id': 'archive'})
		movies_loop = div_archive.find('ul', {'id': 'loop'})
		for litag in movies_loop.findAll('li'):
			div_cover = litag.find('div', {'class': 'cover'})
			if div_cover:
				movie_href = div_cover.find('a', href=True)
				url = movie_href['href']
				title = movie_href['title']
				icon_tag = movie_href.find('img', {'class': 'Thumbnail thumbnail large '})
				movie_list.update({index:'mode=movietitle,title='+ title + ',url=' + url + ',icon=' + icon_tag['src']})
				index = index + 1

	return movie_list

def getVimeoDetails(vimeoUrl):
	req = urllib2.Request(vimeoUrl)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	page_content = response.read()
	response.close()
	soup = BeautifulSoup(page_content)
	scriptTag = soup.find('script').string
	m = re.search(r'\"sd\":{(.*?)}', scriptTag)
	sdContent = m.group(1)
	ms = re.search(r'\"url\":\"(.*?)\"', sdContent)

	return ms.group(1)

def getPlayHdDetails(playHdUrl):
	hdArgs = urlparse.urlparse(playHdUrl).query
	video_id = urlparse.parse_qs(hdArgs).get('vid')[0]
	movie_url = 'http://www.playhd.video/media/videos/hd/' + video_id + '.mp4'
	try:
		response = urllib2.urlopen(movie_url)
	except urllib2.URLError:
		response = urllib2.urlopen(playHdUrl)
		page_content = response.read()
		soup = BeautifulSoup(page_content)
		videoTag = soup.find('video')
		if videoTag:
			sourceTag = videoTag.findAll('source', {'type':'video/mp4'})
			if sourceTag:
				for tag in sourceTag:
					if tag['data-res']:
							if 'HD' in tag['data-res']:
								movie_url = tag['src']
								break
							elif 'SD' in tag['data-res']:
								movie_url = tag['src']
								break
							else:
								movie_url = tag['src']
		else:
			movie_url = None

	return movie_url

def getToolsTubeDetails(toolsTubeUrl):
	req = urllib2.Request(toolsTubeUrl)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	page_content = response.read()
	response.close()
	movie_urls = {}
	soup = BeautifulSoup(page_content)
	for scriptTag in soup.findAll('script'):
		for content in scriptTag.contents:
			if 'webpath' in content:
				files = re.search(r'var files = \'{(.*?)}\';', content)
				if files:
					videoRes = files.group(1)
					video240 = re.search(r'\"240\":\"(.*?)\"', videoRes)
					if video240:
						movie_urls.update({'240': video240.group(1)})
					video360 = re.search(r'\"360\":\"(.*?)\"', videoRes)
					if video360:
						movie_urls.update({'360': video360.group(1)})
					video480 = re.search(r'\"480\":\"(.*?)\"', videoRes)
					if video480:
						movie_urls.update({'480': video480.group(1)})
					video720 = re.search(r'\"720\":\"(.*?)\"', videoRes)
					if video720:
						movie_urls.update({'720': video720.group(1)})

	return movie_urls

def getVideoRajDetails(videoRajUrl):
	movie_url = ''
	req = urllib2.Request(videoRajUrl)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	page_content = response.read()
	response.close()
	soup = BeautifulSoup(page_content)
	cid = ''
	cid2 = ''
	cid3 = 'tamilrasigan.com'
	num_errors = ''
	key = ''
	filevalue = ''
	uservalue = ''
	passvalue = ''
	domainvalue = ''

	for scriptTag in soup.findAll('script'):
		for content in scriptTag.contents:
			cid_node = re.search(r'cid:"(.*?)",', content)
			if cid_node:
				cid = cid_node.group(1)

			cid2_node = re.search(r'cid2: "(.*?)",', content)
			if cid2_node:
				cid2 = cid2_node.group(1)

			cid3_node = re.search(r'cid3:"(.*?)",', content)
			if cid3_node:
				cid3 = cid3_node.group(1)

			user_node = re.search(r'user:"(.*?)",', content)
			if user_node:
				uservalue = user_node.group(1)

			pass_node = re.search(r'pass:"(.*?)",', content)
			if pass_node:
				passvalue = pass_node.group(1)

			domain_node = re.search(r'domain: "(.*?)",', content)
			if domain_node:
				domainvalue = domain_node.group(1)

			key_node = re.search(r'key: "(.*?)",', content)
			if key_node:
				key = key_node.group(1)

			file_node = re.search(r'file:"(.*?)",', content)
			if file_node:
				filevalue = file_node.group(1)

			errors_node = re.search(r'numOfErrors: "(.*?)",', content)
			if errors_node:
				num_errors = errors_node.group(1)
	
	videoraj_base_url = 'http://www.videoraj.sx/api/player.api.php'
	params = { "user": uservalue, "pass": passvalue, "cid": cid, "cid2": cid2, "cid3": cid3, "numOfErrors": num_errors, "file": filevalue, "key": key}
	video_req = urllib2.Request(videoraj_base_url + '?' + urllib.urlencode(params))
	video_req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	video_resp = urllib2.urlopen(video_req)
	video_content = video_resp.read()
	video_resp.close()
	movie_url = urllib.unquote(video_content[4:].split('&')[0])

	return movie_url

def getCloudyDetails(cloudyUrl):
	movie_url = None
	req = urllib2.Request(cloudyUrl)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	page_content = response.read()
	response.close()
	soup = BeautifulSoup(page_content)
	cid = ''
	cid2 = ''
	cid3 = 'tamilrasigan.com'
	num_errors = ''
	key = ''
	filevalue = ''
	uservalue = ''
	passvalue = ''
	domainvalue = ''

	for scriptTag in soup.findAll('script'):
		for content in scriptTag.contents:
			cid_node = re.search(r'cid:"(.*?)",', content)
			if cid_node:
				cid = cid_node.group(1)

			cid2_node = re.search(r'cid2: "(.*?)",', content)
			if cid2_node:
				cid2 = cid2_node.group(1)

			cid3_node = re.search(r'cid3:"(.*?)",', content)
			if cid3_node:
				cid3 = cid3_node.group(1)

			user_node = re.search(r'user:"(.*?)",', content)
			if user_node:
				uservalue = user_node.group(1)

			pass_node = re.search(r'pass:"(.*?)",', content)
			if pass_node:
				passvalue = pass_node.group(1)

			domain_node = re.search(r'domain: "(.*?)",', content)
			if domain_node:
				domainvalue = domain_node.group(1)

			key_node = re.search(r'key: "(.*?)",', content)
			if key_node:
				key = key_node.group(1)

			file_node = re.search(r'file:"(.*?)",', content)
			if file_node:
				filevalue = file_node.group(1)

			errors_node = re.search(r'numOfErrors: "(.*?)",', content)
			if errors_node:
				num_errors = errors_node.group(1)
	
	videoraj_base_url = 'https://www.cloudy.ec/api/player.api.php'
	params = { "user": uservalue, "pass": passvalue, "cid": cid, "cid2": cid2, "cid3": cid3, "numOfErrors": num_errors, "file": filevalue, "key": key}
	video_req = urllib2.Request(videoraj_base_url + '?' + urllib.urlencode(params))
	video_req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	video_resp = urllib2.urlopen(video_req)
	video_content = video_resp.read()
	video_resp.close()
	movie_url = urllib.unquote(video_content[4:].split('&')[0])

	return movie_url

def getEstreamDetails(estreamUrl):
	movie_url = None
	req = urllib2.Request(cloudyUrl)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	page_content = response.read()
	response.close()
	soup = BeautifulSoup(page_content)
	cid = ''
	cid2 = ''
	cid3 = 'tamilrasigan.com'
	num_errors = ''
	key = ''
	filevalue = ''
	uservalue = ''
	passvalue = ''
	domainvalue = ''

	for scriptTag in soup.findAll('script'):
		for content in scriptTag.contents:
			cid_node = re.search(r'cid:"(.*?)",', content)
			if cid_node:
				cid = cid_node.group(1)

			cid2_node = re.search(r'cid2: "(.*?)",', content)
			if cid2_node:
				cid2 = cid2_node.group(1)

			cid3_node = re.search(r'cid3:"(.*?)",', content)
			if cid3_node:
				cid3 = cid3_node.group(1)

			user_node = re.search(r'user:"(.*?)",', content)
			if user_node:
				uservalue = user_node.group(1)

			pass_node = re.search(r'pass:"(.*?)",', content)
			if pass_node:
				passvalue = pass_node.group(1)

			domain_node = re.search(r'domain: "(.*?)",', content)
			if domain_node:
				domainvalue = domain_node.group(1)

			key_node = re.search(r'key: "(.*?)",', content)
			if key_node:
				key = key_node.group(1)

			file_node = re.search(r'file:"(.*?)",', content)
			if file_node:
				filevalue = file_node.group(1)

			errors_node = re.search(r'numOfErrors: "(.*?)",', content)
			if errors_node:
				num_errors = errors_node.group(1)
	
	videoraj_base_url = 'https://www.cloudy.ec/api/player.api.php'
	params = { "user": uservalue, "pass": passvalue, "cid": cid, "cid2": cid2, "cid3": cid3, "numOfErrors": num_errors, "file": filevalue, "key": key}
	video_req = urllib2.Request(videoraj_base_url + '?' + urllib.urlencode(params))
	video_req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	video_resp = urllib2.urlopen(video_req)
	video_content = video_resp.read()
	video_resp.close()
	movie_url = urllib.unquote(video_content[4:].split('&')[0])

	return movie_url

def getVidmadDetails(vidmadUrl):
	movie_url = None
	req = urllib2.Request(vidmadUrl)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	page_content = response.read()
	response.close()
	soup = BeautifulSoup(page_content)
	div_main = soup.find('div', {'id': 'vplayer'})
	if div_main:
		div_archive = div_main.find('video', {'class': 'jw-video jw-reset'})
		if div_archive:
			movie_url = div_archive['src']

	return movie_url

def getFastplayDetails(fastplayUrl):
	movie_url = None
	req = urllib2.Request(fastplayUrl)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	page_content = response.read()
	response.close()
	soup = BeautifulSoup(page_content)
	script_node = soup.findAll('script')
	for snode in script_node:
		for content in snode.contents:
			if 'sources' in content:
				script_content = re.search(r'sources:(.*?),', content)
				if script_content:
					file_url = re.search(r'file:\"(.*?)\"', script_content.group(1))
					if file_url:
						movie_url = file_url.group(1)
	return movie_url

def getMovieUrls(baseUrl):
	movie_urls = {}
	index = 0
	req = urllib2.Request(baseUrl)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	page_content = response.read()
	response.close()
	soup = BeautifulSoup(page_content)

	for iframe in soup.findAll('iframe'):
		iframe_src = iframe.get('src')
		if 'vimeo.com' in iframe_src:
			vimeo_url = getVimeoDetails(iframe_src)
			if vimeo_url:
				movie_urls.update({'vimeo':'label=Vimeo,url=' + vimeo_url})
		elif 'playhd.video' in iframe_src:
			playhd_url = getPlayHdDetails(iframe_src)
			if playhd_url:
				movie_urls.update({'playhd':'label=PlayHD,url=' + playhd_url})
		elif 'toolstube.com' in iframe_src:
			toolstube_urls = getToolsTubeDetails(iframe_src)
			if toolstube_urls:
				for key, value in toolstube_urls.iteritems():
					parsedUrl = value.replace('\\', '')
					movie_urls.update({'playhd' + key:'label=ToolsTube - ' + key + ',referer=' + iframe_src + ',url=' + parsedUrl})
		elif 'videoraj.sx' in iframe_src:
			videoraj_url = getVideoRajDetails(iframe_src)
			if videoraj_url:
				movie_urls.update({'videoraj':'label=VideoRaj,url=' + videoraj_url})
		elif 'cloudy.ec' in iframe_src:
			cloudy_url = getCloudyDetails(iframe_src)
			if cloudy_url:
				movie_urls.update({'cloudy':'label=Cloudy.ec,url=' + cloudy_url})
		elif 'estream.to' in iframe_src:
			estream_url = getEstreamDetails(iframe_src)
			if estream_url:
				movie_urls.update({'estream':'label=Estream.to,url=' + estream_url})
		elif 'vidmad.net' in iframe_src:
			vidmad_url = getFastplayDetails(iframe_src)
			if vidmad_url:
				movie_urls.update({'vidmad':'label=Vidmad.net,url=' + vidmad_url})
		elif 'fastplay.cc' in iframe_src:
			fastplay_url = getFastplayDetails(iframe_src)
			if fastplay_url:
				movie_urls.update({'fastplay':'label=Fastplay.cc,url=' + fastplay_url})
	
	return movie_urls

def getSearchUrls(searchText):
	movie_list = {}
	baseUrl = 'http://tamilrasigan.com/?s=' + searchText.replace(" ", "+")
	index = 0
	req = urllib2.Request(baseUrl)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	page_content = response.read()
	response.close()
	soup = BeautifulSoup(page_content)

	for figureTag in soup.findAll('header', {'class':'genpost-entry-header'}):
		hrefTag = figureTag.find('a', {'rel':'bookmark'})
		title = hrefTag.text
		if 'Movie Watch Online' in title:
			trimmedTitle = title[:-19]
			url = hrefTag.get('href')
			movie_list.update({index:'mode=movietitle,title=' + trimmedTitle + ',url=' + url})
		index = index + 1

	return movie_list

if mode is None:
	movie_list = getMovieList()
	title = ''
	url = ''
	mode = ''
	movie_icon = ''
	for key, value in movie_list.iteritems():
		values = value.split(',')
		for eachSplit in values:
			if 'mode' in eachSplit:
				mode = eachSplit[5:]
			elif 'title' in eachSplit:
				title = eachSplit[6:]
			elif 'url' in eachSplit:
				url = eachSplit[4:]
			elif 'icon' in eachSplit:
				movie_icon = eachSplit[5:]

		movieUrl = build_url({'mode': mode, 'movieName': title, 'url': url})
		li = xbmcgui.ListItem(title, iconImage=movie_icon)
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=movieUrl, listitem=li, isFolder=True)
	
	searchUrl = build_url({'mode': 'search'})
	li = xbmcgui.ListItem('Search', iconImage=movie_icon)
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=searchUrl, listitem=li)
	
	xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'movietitle':
	movieName = args['movieName'][0]
	url = args['url'][0]
	movieUrls = getMovieUrls(url)
	label = ''
	siteUrl = ''
	referer = ''
	for key, value in movieUrls.iteritems():
		values = value.split(',')
		for  eachSplit in values:
			if 'label' in eachSplit:
				label = eachSplit[6:]
			elif 'url' in eachSplit:
				siteUrl = eachSplit[4:]
			elif 'referer' in eachSplit:
				referer = eachSplit[8:]
		
		if referer:
			siteUrl = siteUrl+ '|' + urllib.urlencode({'Referer': referer})
		
		li = xbmcgui.ListItem(label, iconImage='DefaultVideo.png')
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=siteUrl, listitem=li)

	xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'search':
	keyboard = xbmc.Keyboard('', xbmcaddon.Addon().getLocalizedString(30208))
	keyboard.doModal()
	if keyboard.isConfirmed and keyboard.getText():
		searchText = keyboard.getText()
		movie_list = getSearchUrls(searchText)
		title = ''
		url = ''
		mode = ''
		for key, value in movie_list.iteritems():
			values = value.split(',')
			for eachSplit in values:
				if 'mode' in eachSplit:
					mode = eachSplit[5:]
				elif 'title' in eachSplit:
					title = eachSplit[6:]
				elif 'url' in eachSplit:
					url = eachSplit[4:]

			movieUrl = build_url({'mode': mode, 'movieName': title, 'url': url})
			li = xbmcgui.ListItem(title, iconImage='DefaultFolder.png')
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=movieUrl, listitem=li, isFolder=True)
		
		xbmcplugin.endOfDirectory(addon_handle)
