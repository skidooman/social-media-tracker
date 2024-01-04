from datetime import datetime
from collections import OrderedDict
from bs4 import BeautifulSoup
import os, calendar

# LinkedIn makes it difficult to calculate dates, probably on purpose
def correctDate(date, filename):

	dateParts = date.split('-')
	print ("trying %s (%s)" % (date, type(date)))

	# First case: the string we are getting is perfect as it is. Proceed.
	try:
		myDate = datetime(int(dateParts[0]), int(dateParts[1]), int(dateParts[2]))
		print ('this date is fine')
		return date

	except Exception as e:
		dt = os.path.getmtime(filename)
		filedate = datetime.fromtimestamp(dt)
		newDate = filedate.day
		newMonth = filedate.month
		newYear = filedate.year
		if (date.endswith('d')):
			# Date - days, from today
			newDate = filedate.day - int(date[:-1])
		elif (date.endswith('w')):
			# Date - x * 7 from today
			newDate = filedate.day - (int(date[:-1])*7)
		elif (date.endswith('mo')):
			# Month - month from today
			newMonth = filedate.month - int(date[:-2])
		elif (date.endswith('yr')):
			newYear = filedate.year - int(date[:-2])
		else:
			print ('Cannot convert date %s' % date)

		print ('newDate: %s' % newDate)

		# The logic here is that only one of these numbers will have changed
		# Let us start with the smallest - the date
		# If newDate is 1 and up, we are fine. Otherwise, we have to step back one month
		if newDate < 1:
			newMonth = newMonth - 1
		# Likewise, if the month is under 1, we are wrapping around the year
		if newMonth < 1:
			newYear = newYear - 1

		# Now that we know the we can take a look at the month again and decide what it should be
		# If newMonth is 1 or up, we should be fine. Otherwise, we have some gymnastics to do
		if newMonth < 1:
			newMonth = 12 + newMonth

		# Now that we know the month and year, we can do something similar for the date
		# However, here we have a problem since months have unique number of days. Accout for that
		if newDate < 1:
			lastDayOfMonth = calendar.monthrange(newYear, newMonth)[1]
			newDate = lastDayOfMonth + newDate

			# I guess there can be a limit case here too. Say we have -30 and we reset to Feb, what then?
			# Let us then make it 1
			if newDate < 1:
				newDate = 1

		# Update the date and send to the caller
		filedate = filedate.replace(year=newYear, month=newMonth, day=newDate)
		print ('old date: %s' % date)
		print ('new date: %s' % filedate)
		return filedate.strftime('%Y-%m-%d')


def buildDatabase(filename):
	database = []

	file = open(filename, 'r')
	soup = BeautifulSoup(file, 'html.parser')

	# Entries are all the posts
	entries = soup.find_all("div", {"class": "feed-shared-update-v2"})
	#print ('entries: %s' % entries)
	counter = 0
	for entry in entries:
	    counter += 1
	    # Find the URN
	    urn = str(entry['data-urn']).split(':')[-1]
	    # Find the Impressions
	    try: 
	       impressions = entry.find('span', {"class": "ca-entry-point__num-views"})
	       if impressions is None:
	          print ('skipped urn %s ' % urn)
	          continue
	    except:
	       print ('entry %s does not seem to have an impression tag')
	       continue
	    #print(impressions.text.replace('\n','').replace(',','').replace('  ', ''))
	    #print(impressions.text.replace('\n', '').replace(',','').split(' '))
	    impressions_num = None
	    print ('about to do num')
	    impressions_num = int(impressions.text.replace('\n','').replace(',','').replace('  ','').split(' ')[0])
	    print ('impression')
	    # Find the date as a string from the date of saving
	    date = None
	    possibleDates = entry.find_all('span', {'aria-hidden': 'true'})
	    #print ('possibleDates %s' % possibleDates)
	    for possibleDate in possibleDates:
	       if possibleDate.text and possibleDate.text[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
	          date = str(possibleDate.text.split(' ')[0])
	          break
	    if date is None:
	       possibleDates = entry.find_all('div', {'class':'inline-block'})
	       for possibleDate in possibleDates:
	          print (possibleDate)
	          text = possibleDate.text.split('\n')[1].replace(' ','')
	          if text and text[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
	             if text[-1] == 'h' or text[-1] == 'm' or text[-1] == 's':
	                #date = datetime.today().strftime('%Y-%m-%d')
	                dt = os.path.getctime(filename)
	                date = datetime.fromtimestamp(dt).strftime("%Y-%m-%d")
	             else:
	                date = str(text.split(' ')[0])
	          break
	    # Attempting to correct dates that have been marked as yr, mo, d, etc
	    date = correctDate(date, filename)

	    #   date = datetime.today().strftime('%Y-%m-%d')
	    # Find the text
	    print ("find the text")
	    articleText = entry.find('span', {"class": "break-words"}).text
	    words = articleText.split()
	    tags = []
	    people = []
	    for word in words:
	        if (word.find("#") > -1 and not word[0] == '#'):
	            word = word.split("#")[1]
	            tags.append(word)
	        elif (word.find("@") > -1 and not word[0] == '@'):
	            word = word.split("#")[1]
	            people.append(word)
	        elif (len(word) and word[0] == '#'):
	            tags.append(word[1:])
	        elif (len(word) and word[0] == '@'):
	            people.append(word[1:])

	    # Trying to find comments
	    comments = 0
	    commentsEntry = entry.find('li', {"class": "social-details-social-counts__comments"})
	    if (commentsEntry):
	        commentTxt = commentsEntry.text.replace('\n','')
	        while (len(commentTxt) and commentTxt[0] == ' '):
	           commentTxt = commentTxt[1:]
	        if(commentTxt.split(' ')[1].startswith('comment')):
	           comments = int(commentTxt.split(' ')[0])

	    # Likes
	    likes = 0
	    likesEntry = entry.find('span', {"class": "social-details-social-counts__social-proof-fallback-number"})
	    if (likesEntry):
	        likes = int(likesEntry.text)

	    # Reposts
	    reposts = 0
	    repostsEntry = entry.find('li', {"class": "social-details-social-counts__item--with-social-proof"})
	    if (repostsEntry):
	        repostsTxt = repostsEntry.text.replace('\n','')
	        while (len(repostsTxt) and repostsTxt[0] == ' '):
	            repostsTxt = repostsTxt[1:]
	        if(repostsTxt.split(' ')[1].startswith('repost')):
	            reposts = int(repostsTxt.split(' ')[0])

	    # Find the type
	    type = None
	    poll = None
	    poll = entry.find('div', {"class": "update-components-poll__header"})
	    article_url = None
	    article = entry.find('article', {"class": "feed-shared-article"})
	    if article:
	        article_url = article.find('a', {'class': "app-aware-link"})['href']
	    if not article:
	        # It could be located into another div
	        article = entry.find('div', {'class': 'update-components-article__link-container'})
	        if article:
	           article_url = entry.find('a')['href']
	    video = entry.find('div', {"class": "video-js"})
	    external_video = entry.find('a', {"class": "feed-shared-article__image-link"})
	    if not external_video:
	        external_video = entry.find('div', {'class':'external-video-viewer'})
	        if external_video:
	           external_video = external_video.find('a')
	    if (external_video and (external_video['href'].startswith('https://www.youtube.com') or external_video['href'].startswith('https://youtu.be'))):
	        video_url = external_video['href']
	        database.append({'urn':urn, 'date':date, 'impressions':impressions_num, 'type': 'external_video', 'text': articleText, 'tags': tags, 'people': people, 'link_url': video_url, 'comments': comments, 'likes': likes, 'reposts': reposts})
	    elif (article_url):
	        # Save everything to the database
	        database.append({'urn':urn, 'date':date, 'impressions':impressions_num, 'type': 'article', 'text': articleText, 'tags': tags, 'people': people, 'link_url': article_url, 'comments': comments, 'likes': likes, 'reposts': reposts})
	    elif (video):
	        database.append({'urn':urn, 'date':date, 'impressions':impressions_num, 'type': 'internal_video', 'text': articleText, 'tags': tags, 'people': people, 'link_url': None, 'comments': comments, 'likes': likes, 'reposts': reposts})
	    elif (poll):
	        database.append({'urn':urn, 'date':date, 'impressions':impressions_num, 'type': 'poll', 'text': articleText, 'tags': tags, 'people': people, 'link_url': None, 'comments': comments, 'likes': likes, 'reposts': reposts})

	        '''if (str(video).find("licdn.com")):
	            database.append({'urn':urn, 'date':date, 'impressions':impressions_num, 'type': 'internal_video', 'text': articleText, 'tags': tags, 'people': people, 'link_url': None})
	        else:
	            print ("Video not supported %s" % impression_num)
	            break'''

	    else:
	        database.append({'urn':urn, 'date':date, 'impressions':impressions_num, 'type': 'simple', 'text': articleText, 'tags': tags, 'people': people, 'link_url': None, 'comments': comments, 'likes': likes, 'reposts': reposts})
	return database

def saveJSON(database, filename):
	with open(filename, 'w') as file:
		file.write('[')
		counter = 0
		for entry in database:
			file.write('\t\t{"id":"' +  entry['urn'] + '",')
			file.write('"date":"' + entry['date'] + '",')
			file.write('"views":"%i",' % entry['impressions'])
			if entry['type'] == 'article':
				file.write('"text-link":"%s",' % entry['link_url'])
			elif entry['type'] == 'internal_video':
				file.write('"internal_video":"true",')
			elif entry['type'] == 'external_video':
	                        file.write('"video-link":"%s",' % entry['link_url'])
			file.write('"text":"%s",' % entry['text'].replace('"', '\'').replace('\n','<br><br>').replace('\t',''))
			file.write('"comments":"%s", "likes":"%s", "reposts":"%s"' % (entry['comments'], entry['likes'], entry['reposts']))
			if (counter == len(database)-1):
				file.write('}]\n')
			else:
				file.write('},\n')
				counter += 1


if __name__ == '__main__':
	import sys
	filename = sys.argv[1]
	database = buildDatabase(filename)
	for entry in database:
		print ("%s \t %s" % (entry['urn'], entry['date']))
	#print (database)
	print (len(database))
