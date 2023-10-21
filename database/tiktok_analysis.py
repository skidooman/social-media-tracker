from dateutil.parser import parse
import datetime
from collections import OrderedDict
from bs4 import BeautifulSoup
import time

def augmentDict(filename, dict={}):
	file = open(filename, 'r')
	soup = BeautifulSoup(file, 'html.parser')

	# Entries are all the posts
	tbodies = soup.find_all("tbody", {"data-tt": "Table_VirtualizedTable_TBody"})
	for tbody in tbodies:
		rows = tbody.find_all("tr", {"data-tt": "Table_VirtualizedTable_Tr_18"})
		for row in rows:
			# Tiktok makes it nearly impossible to get anywhere
			# As far as I know, the only way to get to something like an ID is through the sole image
			# they are posting
			# There should be in theory only one image, so for now let us use the path to the image as an ID
			imgTag = row.find("img")
			link = imgTag['src']
			#print (link)

			timeTag = row.find("span", {"data-tt":"components_VideoCover_TUXText"})
			time = timeTag.text

			textTags = row.find_all("span", {"data-tt":"components_VideoInfoCard_TUXText"})

			text = ''
			displays = 0
			likes = 0
			comments = 0
			reposts = 0
			saved = 0

			if len(textTags):
				text = textTags[0].text
			if len(textTags) > 1:
				if textTags[1].text.endswith('K'):
					displays = int(float(textTags[1].text[:-1])*1000)
				elif textTags[1].text.endswith('M'):
					displays = int(float(textTags[1].text[:-1])*1000000)
				else:
					displays = int(textTags[1].text)
			if len(textTags) > 2:
				likes = int(textTags[2].text)
			if len(textTags) > 3:
				comments = int(textTags[3].text)
			if len(textTags) > 4:
				reposts = int(textTags[4].text)
			if len(textTags) > 5:
				saved = int(textTags[5].text)

			dataTag = row.find("span", {"data-tt":"components_Cells_TUXText"})
			time = dataTag.text
			parsedTime = parse(time)
			date = parsedTime.strftime('%Y-%m-%d')
			print (date)

			dict[time] = {'text':text, 'displays':displays, 'likes':likes, 'comments':comments, 'reposts':reposts, 'date':date, 'id':time}
	    
	print ('length of dict is now %s' % len(dict))
	return dict

def saveJSON(database, filename):
	with open(filename, 'w') as file:
		file.write('[')
		counter = 0
		for key in database:
			values = database[key]
			file.write('\t\t{"id":"' +  key + '",')
			file.write('"date":"' + values['date'] + '",')
			file.write('"views":"%i",' % values['displays'])
			file.write('"internal_video":"true",')
			file.write('"text":"%s",' % values['text'].replace('"', '\'').replace('\n','<br><br>').replace('\t',''))
			file.write('"comments":"%s", "likes":"%s", "reposts":"%s"' % (values['comments'], values['likes'], values['reposts']))
			if (counter == len(database)-1):
				file.write('}]\n')
			else:
				file.write('},\n')
				counter += 1

# First, log on to TikTok and go to https://www.tiktok.com/creator-center/content

#dict = {}
#augmentDict('tiktok_dump.html', dict)
#saveJSON(dict, 'tiktok.json')
