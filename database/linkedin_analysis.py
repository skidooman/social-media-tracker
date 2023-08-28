
from collections import OrderedDict
from bs4 import BeautifulSoup


def buildDatabase(filename):
	database = []

	file = open(filename, 'r')
	soup = BeautifulSoup(file, 'html.parser')

	# Entries are all the posts
	entries = soup.find_all("div", {"class": "feed-shared-update-v2"})

	for entry in entries:
	    # Find the URN
	    urn = str(entry['data-urn']).split(':')[-1]

	    # Find the Impressions
	    impressions = entry.find('span', {"class": "ca-entry-point__num-views"})
	    #print(impressions.text.replace('\n','').replace(',','').replace('  ', ''))
	    #print(impressions.text.replace('\n', '').replace(',','').split(' '))
	    impressions_num = None
	    impressions_num = int(impressions.text.replace('\n','').replace(',','').replace('  ','').split(' ')[0])
	    # Find the date as a string from the date of saving
	    date = str(entry.find('span', {'aria-hidden': 'true'}).text).split(' ')[0]

	    # Find the text
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
	    article = entry.find('article', {"class": "feed-shared-article"})
	    video = entry.find('div', {"class": "video-js"})
	    external_video = entry.find('a', {"class": "feed-shared-article__image-link"})
	    if (external_video and (external_video['href'].startswith('https://www.youtube.com') or external_video['href'].startswith('https://youtu.be'))):
	        video_url = external_video['href']
	        database.append({'urn':urn, 'date':date, 'impressions':impressions_num, 'type': 'external_video', 'text': articleText, 'tags': tags, 'people': people, 'link_url': video_url, 'comments': comments, 'likes': likes, 'reposts': reposts})
	    elif (article):
	        article_url = article.find('a',  {"class": "app-aware-link"})['href']
	        # Save everything to the database
	        database.append({'urn':urn, 'date':date, 'impressions':impressions_num, 'type': 'article', 'text': articleText, 'tags': tags, 'people': people, 'link_url': article_url, 'comments': comments, 'likes': likes, 'reposts': reposts})
	    elif (video):
	        database.append({'urn':urn, 'date':date, 'impressions':impressions_num, 'type': 'internal_video', 'text': articleText, 'tags': tags, 'people': people, 'link_url': None, 'comments': comments, 'likes': likes, 'reposts': reposts})

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

database = buildDatabase('LinkedIn_oct22.html')
saveJSON(database, 'LinkedIn_oct22.html.json')
