#!/usr/bin/python
# This class represents Runs, which are individual posts on a social media

from Base import Base
import json, datetime
from Data import Data

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
			'social_media VARCHAR(16) NOT NULL)')
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
			command = ("INSERT INTO runs (id, user_id, publication_date, publication_date_approx, text, text_link, image_link, video_link, internal_video, social_media)"
				"VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')") % (id, user_id, date, date_approx, text.replace('\'', '"'), text_link, image_link, video_link, internal_video, social_media)
			return cls.execute_commands([command])

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
							date = date.replace(month= date.month-month)
						else:
							month = date.month + (-1*(date.month-month))
							date = date.replace(year=date.year-1, month=month)
					elif (entry['date'].endswith('d')):
						day = int(entry['date'][:-1])
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

				# Finally, add the details of the run (data)
				Data.add(entry['id'], user_id, reportedDate, entry['views'], entry['likes'], entry['comments'], entry['reposts'])


	@classmethod
	def getRecords(cls, user_id, image=None, external_text=None, internal_video=None, external_video=None, simple=None,
			original_date_before=None, original_date_after=None):
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
			print ("SIMPLE")
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

		command += ';'

		print (command)
		return cls.execute_commands([command], fetching=True)


	#id, user_id, publication_date, publication_date_approx, text, text_link, image_link, video_link, internal_video, social_media
	@classmethod
	def getRecordsHTMLTable(cls, user_id, image=None, external_text=None, internal_video=None, external_video=None,
		simple=None, original_date_before=None, original_date_after=None):
		records = cls.getRecords(user_id, image, external_text, internal_video, external_video, simple,
			original_date_before, original_date_after)
		print (records)
		##print ('RECORDS: %s' % len(records))
		html = '<h2>Records: %s</h2>' % len(records)
		html += '<div class="table-wrap">\n\t<table class="sortable" border="1">'
		html += '\n\t\t<thead>'
		html += '\n\t\t\t<tr>'
		html += '\n\t\t\t\t<th><button>ID</button></th>'
		html += '\n\t\t\t\t<th><button>Date</button></th>'
		html += '\n\t\t\t\t<th><button>Text</button></th>'
		html += '\n\t\t\t\t<th><button>Type</button></th>'
		html += '\n\t\t\t\t<th><button>Link</button></th>'
		html += '\n\t\t\t\t<th><button>Media</button></th>'
		html += '\n\t\t\t\t<th><button>Last data point</button></th>'
		html += '\n\t\t\t\t<th><button>Views</button></th>'
		html += '\n\t\t\t\t<th><button>Likes</button></th>'
		html += '\n\t\t\t\t<th><button>Comments</button></th>'
		html += '\n\t\t\t\t<th><button>Reposts</button></th>'
		html += '\n\t\t\t</tr>'
		html += '\n\t\t</thead>'

		html += '\n\t\t<tbody>'
		
		for record in records:
			html += '\n\t\t\t<tr>'
			html += '\n\t\t\t\t<td>%s</td>' % record[0] # ID
			html += '\n\t\t\t\t<td>%s</td>' % record[2] # Publication date
			html += '\n\t\t\t\t<td style="max-width: 200px; overflow:hidden; text-overflow: hidden;" width="200"><div style="max-width:200px; white-space:nowrap; overflow: hidden; text-overflow: hidden;">%s</div></td>' % record[4] # Text
			# Type
			if record[8]:
				html += '\n\t\t\t\t<td>Internal video</td>' 	# Internal video
				html += '\n\t\t\t\t<td></td>' 			# No link
			elif record[7]:
				html += '\n\t\t\t\t<td>External video</td>'			# External video
				html += '\n\t\t\t\t<td><a href="%s">Link</a></td>' % record[7]	# Link
			elif record[6]:
				html += '\n\t\t\t\t<td>Image</td>'				# Image link
				html += '\n\t\t\t\t<td><a href="%s">Link</a></td>' % record[6]	# Link
			elif record[5]:
				html += '\n\t\t\t\t<td>Article</td>'				# External text
				html += '\n\t\t\t\t<td><a href="%s">Link</a></td>' % record[5]	# Link
			else:
				html += '\n\t\t\t\t<td>Simple entry</td>'			# Simple
				html += '\n\t\t\t\t<td></td>'					# No link


			html += '\n\t\t\t\t<td>%s</td>' % record[9] # Social media

			# Display last data point available
			# run_id, user_id, date, views, likes, comments, reposts
			points = Data.getRecords(user_id, record[0])
			currentPoint = points[len(points)-1]
			html += '\n\t\t\t\t<td>%s</td>' % currentPoint[2]
			html += '\n\t\t\t\t<td>%s</td>' % currentPoint[3]
			html += '\n\t\t\t\t<td>%s</td>' % currentPoint[4]
			html += '\n\t\t\t\t<td>%s</td>' % currentPoint[5]
			html += '\n\t\t\t\t<td>%s</td>' % currentPoint[6]

			html += '\n\t\t\t</tr>'
		
		html += '\n\t\t\t</tr>'
		html += '\n\t\t</tbody>'
		html += '\n\t</table>'
		html += '\n</div>'
		return html
