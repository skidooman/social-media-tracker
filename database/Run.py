#!/usr/bin/python
# This class represents Runs, which are individual posts on a social media

from Base import Base
import json, datetime
from Data import Data
#from textblob import TextBlob
import langid

class Run(Base):
	name_of_table = 'runs'

	@classmethod
	def create(cls):
		command = ('CREATE TABLE runs('
			'id VARCHAR(255) UNIQUE PRIMARY KEY,'
			'user_id INTEGER,'
			'CONSTRAINT fk_user_id FOREIGN KEY(user_id) REFERENCES users(id),'
			'publication_date DATE,'
			'publication_date_approx BOOLEAN DEFAULT FALSE,' 
			'text VARCHAR(3000) NOT NULL,'
			'text_link VARCHAR(2083) NOT NULL,'
			'image_link VARCHAR(2083) NOT NULL,'
			'video_link VARCHAR(2083) NOT NULL,'
			'internal_video BOOLEAN DEFAULT FALSE,'
			'social_media VARCHAR(16) NOT NULL,'
			'language VARCHAR(2))')
		cls.execute_commands([command])

	@classmethod
	def add(cls, id, user_id, date, text, social_media, date_approx=False, text_link='', image_link='', video_link='', internal_video=False):
		#Does the entry exists?
		entryExists = cls.recordExistsIdString(cls.name_of_table, id)
		if(entryExists):
			# For the moment, let us not do anything
			# The resolution we would get on the date is likely to be less good, at least for LinkedIn
			'''command = ("UPDATE runs SET publication_date='%s-%s-%s', publication_date_approx='%s', text='%s', text_link='%s', image_link='%s', video_link='%s', internal_video='%s' WHERE (id='%s')" % 
				(date.year, date.month, date.day, date_approx, text.replace('\'', '"'), text_link, image_link, video_link, internal_video, id))
			cls.execute_commands([command])'''
			return entryExists
			
		else:
			# What is the language?
			#lang = TextBlob(text)
			lang_code = langid.classify(text)[0]
			print (lang_code)
			if len(lang_code) > 2:
				lang_code = lang_code[:1]
			command = ("INSERT INTO runs (id, user_id, publication_date, publication_date_approx, text, text_link, image_link, video_link, internal_video, social_media, language)"
				"VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')") % (id, user_id, date, date_approx, text.replace('\'', '"'), text_link, image_link, video_link, internal_video, social_media, lang_code)
			return cls.execute_commands([command])

	@classmethod
	def getLanguages(cls):
		command = "SELECT DISTINCT {language} from Runs"
		results = cls.getUniques('language', 'Runs')
		results.sort()
		return results

	# This imports a properly formatted JSON file
	@classmethod
	def importFile(cls, user_id, media, date_str, filename):
		dateParts = date_str.split('-')
		reportedDate = datetime.datetime(int(dateParts[0]), int(dateParts[1]), int(dateParts[2]))
		with open(filename, 'r') as file:
			data = json.load(file)
			for entry in data:
				#  First, deal with the date
				date = reportedDate
				dateApprox = False
				try:
					dateParts = entry['date'].split('-')
					date = datetime.datetime(int(dateParts[0]), int(dateParts[1]), int(dateParts[2]))
				except Exception:
					# Here, the fun begins, because LinkedIn doesn't report dates.
					# Try to get as close as possible
					dateApprox = True
					if (entry['date'].endswith('yr')):
						year = int(entry['date'][:-2])
						date = date.replace(year= date.year-year)
					elif (entry['date'].endswith('mo')):
						month = int(entry['date'][:-2])
						if (month < date.month):
							diff = date.month-month
							if diff == 2 and date.day > 28:
								date = date.replace(day=28)
							elif diff in [4,6,9,11] and date.day > 30:
								date = date.replace(day=30)
							date = date.replace(month=diff)
						else:
							month = date.month + (-1*(date.month-month))
							if month == 2 and date.day > 28:
								date = date.replace(day=28)
							elif month in [4,6,9,11] and date.day > 30:
								date = date.replace(day=30)
							date = date.replace(year=date.year-1, month=month)
					elif (entry['date'].endswith('w')):
						week = int(entry['date'][:-1])
						dayDiff = week * 7
						if dayDiff > date.day:
							if date.month == 1:
								date = date.replace(month=12)
							if date.month in [4,6,9,11]:
								date = date.replace(day=30 - dayDiff + date.day)
							elif date.month == 2:
								date = date.replace(day=28 - dayDiff + date.day)
							else:
								date = date.replace(day=31-dayDiff+date.day)
						else:
							date = date.replace(date.day-dayDiff)

					elif (entry['date'].endswith('d')):
						day = int(entry['date'][:-1])
						print ('DATE: %s - %s' % (entry['date'], date)) 
						if (day < date.day):
							date = date.replace(day=date.day-day)
						else:
							day = date.day + (-1*(date.day-day))
							if (date.month == 1):
								date = date.replace(year=date.year-1, month=12, day=day)
							else:
								date = date.replace(month=date.month-1, day=day)
					else:
						print ("Date %s could not be converted on entry %s, date will be wrong (%s)" % (entry['date'], entry['id'], date))

				# Now that we have a date, we must determine which type of entry we have
				# Internal video entry?
				if ('video-link' in entry):
					cls.add(entry['id'], user_id, date, entry['text'], media, date_approx=dateApprox, video_link=entry['video-link'])
				elif ('internal_video' in entry):
					cls.add(entry['id'], user_id, date, entry['text'], media, date_approx=dateApprox, internal_video=True)
				elif ('text-link' in entry):
					cls.add(entry['id'], user_id, date, entry['text'], media, date_approx=dateApprox, text_link=entry['text-link'])
				elif ('image-link' in entry):
					cls.add(entry['id'], user_id, date, entry['text'], media, date_approx=dateApprox, image_link=entry['image-link'])
				else:
					cls.add(entry['id'], user_id, date, entry['text'], media, date_approx=dateApprox)

				# Displays and minutes are only from Youtube
				displays = 0
				minutes = 0
				if 'displays' in entry.keys():
					displays = entry['displays']
				if 'minutes' in entry.keys():
					minutes = entry['minutes']

				# Finally, add the details of the run (data)
				Data.add(entry['id'], user_id, reportedDate, entry['views'], entry['likes'], entry['comments'], entry['reposts'], displays, minutes)

	@classmethod
	def getRecord(cls, user_id, entry_id):
		command = "SELECT * FROM runs where user_id = %s and id = '%s'" % (user_id, entry_id)
		results = cls.execute_commands([command], fetching=True)
		return results[0]
		


	@classmethod
	def getRecords(cls, user_id, image=None, external_text=None, internal_video=None, external_video=None, simple=None,
			original_date_before=None, original_date_after=None, linkedin=False, youtube=None, languages=[]):
		command = "SELECT * FROM runs WHERE user_id = %s" % user_id

		def getExternals(target):
			externals = 0
			if image == target:
				externals += 1
			if external_text == target:
				externals += 1
			if internal_video == target:
				externals += 1
			if external_video == target:
				externals += 1
			return externals 

		if simple:
			externals = getExternals(None)
			if externals:
				pos = 0
				command += " AND ("
				if image is None:
					command += "NOT (length(image_link)) > 0"
					pos += 1
				if internal_video is None:
					if pos:
						command  += " AND "
					command += "NOT (internal_video=true)"
					pos += 1
				if external_text is None:
					if pos:
						command  += " AND "
					command += "NOT (length(text_link)) > 0"
					pos += 1
				if external_video is None:
					if pos:
						command  += " AND "
					command += "NOT (length(video_link)) > 0"
				command += ") "
		else:
			# Videos, images, text
			externals = getExternals(True)
			if externals:
				pos = 0
				command += " AND ("
				if image:
					command += "(length(image_link)) > 0"
					pos += 1
				if internal_video:
					if pos:
						command  += " OR "
					command += "(internal_video=true)"
					pos += 1
				if external_text:
					if pos:
						command  += " OR "
					command += "(length(text_link)) > 0"
					pos += 1
				if external_video:
					if pos:
						command  += " OR "
					command += "(length(video_link)) > 0"
				command += ") "
		
		# Date constraints	
		if original_date_before:
			command += " AND publication_date < '%s'" % original_date_before
		if original_date_after:
			command += " AND publication_date > '%s'" % original_date_after

		# Media restrictions
		if not linkedin and not youtube:
			pass
		else:
			keywords = []
			if linkedin:
				keywords.append('linkedin')
			if youtube:
				keywords.append('youtube')
			
			command += " AND ("
			for i in range(0, len(keywords)):
				command += " social_media = '%s'" % keywords[i]
				if i < len(keywords)-1:
					command += ' OR '
			
			command += ")"

		# Languages
		if len(languages):
			command += " AND ("
			for i in range(0, len(languages)):
				command += " language = '%s'" % languages[i]
				if i < len(languages)-1:
					command += ' OR '
			command += ")"

		command += ';'

		return cls.execute_commands([command], fetching=True)


	#id, user_id, publication_date, publication_date_approx, text, text_link, image_link, video_link, internal_video, social_media
	@classmethod
	def getRecordsHTMLTable(cls, user_id, image=None, external_text=None, internal_video=None, external_video=None,
		simple=None, original_date_before=None, original_date_after=None, linkedin=False, youtube=False, languages=[]):

		def cleanText(myString):
			if myString.startswith('<br><br> '):
				return myString[4:]
			else:
				return myString

		def getTotals(user_id, records):
			views = 0
			likes = 0
			comments = 0
			reposts = 0
			for record in records:
				points = Data.getRecords(user_id, record[0])
				try:
					currentPoint = points[len(points)-1]
					views += currentPoint[3]
					likes += currentPoint[4]
					comments += currentPoint[5]
					reposts += currentPoint[6]
				except Exception:
					break
			return views, likes, comments, reposts
				

		records = cls.getRecords(user_id, image, external_text, internal_video, external_video, simple,
			original_date_before, original_date_after, linkedin, youtube, languages)

		##print ('RECORDS: %s' % len(records))
		#html = '<h2>Records: %s</h2>' % len(records)
		html = "<script>"
		html += "\nfunction toggle (id){"
		html += "\n  let expandable = document.getElementById(id);"
		html += "\n  if (expandable.style.overflow == 'hidden') {expandable.style.overflow ='visible'; expandable.style.whiteSpace='normal';}"
		html += "\n  else {expandable.style.overflow = 'hidden'; expandable.style.whiteSpace='nowrap';}"
		html += "\n}"
		html += "\n</script>"

		html += '<div class="table-wrap">\n\t<table class="sortable">'
		html += '\n\t\t<thead>'
		html += '\n\t\t\t<tr>'
		html += '\n\t\t\t\t<th><button>ID<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th><button>Date<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th><button>Text<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th><button>Type<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th><button>Media<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th><button>Lang<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th><button>Last data<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th class="num"><button>Views<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th class="num"><button>Likes<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th class="num"><button>Comment<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th class="num"><button>Repost<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th class="num"><button>Displays<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th class="num"><button>Minutes<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th></th>'
		html += '\n\t\t\t</tr>'

		# Totals
		views, likes, comments, reposts = getTotals(user_id, records)
		html += '\n\t\t\t<tr>'
		html += '\n\t\t\t\t<th style="background-color: white; color: black;">Records: %s</th>' % len(records)
		html += '\n\t\t\t\t<th style="background-color: white; color: black;"></th>'
		html += '\n\t\t\t\t<th style="background-color: white; color: black;"></th>'
		html += '\n\t\t\t\t<th style="background-color: white; color: black;"></th>'
		html += '\n\t\t\t\t<th style="background-color: white; color: black;"></th>'
		html += '\n\t\t\t\t<th style="background-color: white; color: black;"></th>'
		html += '\n\t\t\t\t<th style="background-color: white; color: black;"></th>'
		html += '\n\t\t\t\t<th style="background-color: white; color: black;">%s</th>' % views
		html += '\n\t\t\t\t<th style="background-color: white; color: black;">%s</th>' % likes
		html += '\n\t\t\t\t<th style="background-color: white; color: black;">%s</th>' % comments
		html += '\n\t\t\t\t<th style="background-color: white; color: black;">%s</th>' % reposts
		html += '\n\t\t\t\t<th style="background-color: white; color: black;">%s</th>' % reposts

		html += '\n\t\t\t</tr>'

		html += '\n\t\t</thead>'

		html += '\n\t\t<tbody>'
		
		recordNum = 0
		for record in records:
			recordNum += 1
			html += '\n\t\t\t<tr>'
			if record[9] == 'linkedin':
				html += '\n\t\t\t\t<td class="num"><a href="https://www.linkedin.com/embed/feed/update/%s" target="_top">%s</a></td>' % (record[0], record[0]) # ID
			elif record[9] == 'youtube':
				html += '\n\t\t\t\t<td class="num"><a href="https://www.youtube.com/watch?v=%s" target="_top">%s</a></td>' % (record[0], record[0]) # ID				
			else:
				html += '\n\t\t\t\t<td class="num">%s</td>' % record[0] # ID

			html += '\n\t\t\t\t<td>%s</td>' % record[2] # Publication date
			html += '\n\t\t\t\t<td style="max-width: 200px; overflow:hidden; text-overflow: hidden;" width="200"><div class="expandable" id=\'exp%s\' onclick="toggle(\'exp%s\');" style="max-width:200px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis;">%s</div></td>' % (recordNum, recordNum, cleanText(record[4]))  # Text
			# Type
			if record[8]:
				html += '\n\t\t\t\t<td>Internal video</td>' 	# Internal video
			elif record[7]:
				html += '\n\t\t\t\t<td><a href="%s" target="_top">External video</a></td>' % record[7] # External video
			elif record[6]:
				html += '\n\t\t\t\t<td><a href="%s" target="_top">Image</a></td>' % record[6]	# Image link
			elif record[5]:
				html += '\n\t\t\t\t<td><a href="%s" taget="_top">Article</a></td>' % record[5] # External text
			else:
				html += '\n\t\t\t\t<td>Simple entry</td>'			# Simple


			html += '\n\t\t\t\t<td>%s</td>' % record[9] # Social media
			
			# Languages
			html += '\n\t\t\t\t<td>%s</td>' % record[10] # Language
			
			# Display last data point available
			# run_id, user_id, date, views, likes, comments, reposts
			points = Data.getRecords(user_id, record[0])
			try:
				currentPoint = points[len(points)-1]
				html += '\n\t\t\t\t<td>%s</td>' % currentPoint[2]
				html += '\n\t\t\t\t<td class="num">%s</td>' % currentPoint[3]
				html += '\n\t\t\t\t<td class="num">%s</td>' % currentPoint[4]
				html += '\n\t\t\t\t<td class="num">%s</td>' % currentPoint[5]
				html += '\n\t\t\t\t<td class="num">%s</td>' % currentPoint[6]
				html += '\n\t\t\t\t<td class="num">%s</td>' % currentPoint[7]
				html += '\n\t\t\t\t<td class="num">%s</td>' % currentPoint[8]
			except Exception:
				pass

			html += '\n\t\t\t\t<td><button id="edit_%s" style="color: black;" onclick="edit(\'%s\', \'%s\');">Edit</button></td>' % (record[0], user_id, record[0]) 

			html += '\n\t\t\t</tr>'
		
		html += '\n\t\t</tbody>'
		html += '\n\t</table>'
		html += '\n</div>'

		return html, cls.getKeywordHtml(user_id, records)

	@classmethod
	def getKeywordDict(cls, records):
		capitalLetters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
		keywordDict = {}
		for record in records:
			text = record[4]
			hashes = []
			text = text.replace('＃', ' #')
			words = text.replace(',', ' ').replace('.',' ').replace('?', ' ').replace('!', ' ').replace(':', ' ').replace('<', ' ').replace('\n', ' ').replace('>', ' ').replace('http', ' ').replace(',',' ').replace('#', ' #').split(' ')
			for word in words:
				if len(word) and word[0] == '#':
					hash = word[1:]
					if not hash[0] in capitalLetters:
						for char in range(1, len(hash)):
							if hash[char] in capitalLetters:
								hash = hash.split(hash[char])[0]
								break
					if hash[0].isascii() and not hash[-1].isascii():
						for i in range(len(hash)-1, 0, -1):
							if not hash[i].isascii() and hash[i] not in ['é','è','ù','ì','ò','ù','à','â','ê','î','ô','û','â','ê','î','ô','û','ȩ','ï','ü','ë','ä','ö','è']:
								hash = hash[:-1]
							else:
								break
					hashes.append(hash.replace('(', '').replace('、', '').replace(')','').lower())
			for hash in hashes:
				if hash in keywordDict.keys():
					keywordDict[hash].append(record)
				else:
					keywordDict[hash] = [record]
		return keywordDict

	@classmethod
	def getKeywordHtml(cls, user_id, records):
		records = cls.getKeywordDict(records)
		##print ('RECORDS: %s' % len(records))
		html = '<h2>Hashes: %s</h2>' % len(records.keys())
		html += '<div class="table-wrap">\n\t<table class="sortable">'
		html += '\n\t\t<thead>'
		html += '\n\t\t\t<tr>'
		html += '\n\t\t\t\t<th><button>Hash<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th class="num"><button># entries<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th class="num"><button># displays<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th class="num"><button>Displays per entry<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th class="num"><button>#Likes<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th class="num"><button>Likes per entry<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t</tr>'
		html += '\n\t\t</thead>'

		html += '\n\t\t<tbody>'
		for hash in records.keys():
			html += '\n\t\t\t<tr>'
			html += '\n\t\t\t\t<td>%s</td>' % hash
			html += '\n\t\t\t\t<td class="num">%s</td>' % len(records[hash])
			entries = 0
			likes = 0
			for entry in records[hash]:
				points = Data.getRecords(user_id, entry[0])
				entries = points[0][3]
				likes = points[0][5]
			html += '\n\t\t\t<td class="num">%s</td>' % entries
			html += '\n\t\t\t<td class="num">%.2f</td>' % (entries/ len(records[hash]))
			html += '\n\t\t\t<td class="num">%s</td>' % likes
			html += '\n\t\t\t<td class="num">%.2f</td>' % (likes / len(records[hash]))
			html += '\n\t\t\t</tr>'
		html += '\n\t\t</tbody>'
		html += '\n\t</table>'

		return html
