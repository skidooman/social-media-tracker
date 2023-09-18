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
		print ('id %s' % id)
		entryExists = cls.recordExistsIdString(cls.name_of_table, id)
		if(entryExists):
			command = ("UPDATE runs SET publication_date='%s-%s-%s', publication_date_approx='%s', text='%s', text_link='%s', image_link='%s', video_link='%s', internal_video='%s' WHERE (id='%s')" % 
				(date.year, date.month, date.day, date_approx, text.replace('\'', '"'), text_link, image_link, video_link, internal_video, id))
			cls.execute_commands([command])
			return entryExists
			
		else:
			print ('else')
			command = ("INSERT INTO runs (id, user_id, publication_date, publication_date_approx, text, text_link, image_link, video_link, internal_video, social_media)"
				"VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')") % (id, user_id, date, date_approx, text.replace('\'', '"'), text_link, image_link, video_link, internal_video, social_media)
			return cls.execute_commands([command])
		'''command = ("INSERT INTO users (first_name, last_name, email, password) "
			"VALUES('%s', '%s', '%s', '%s')") % (firstName, lastName, email, password)
		cls.execute_commands([command])
		return '1' '''


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
						date.replace(year= date.year-year)
					elif (entry['date'].endswith('mo')):
						month = int(entry['date'][:-2])
						if (month < date.month):
							date.replace(month= date.month-month)
						else:
							month = date.month + (-1*(date.month-month))
							date.replace(year=date.year-1, month=month)
					elif (entry['date'].endswith('d')):
						day = int(entry['date'][:-1])
						if (day < date.day):
							date.replace(day=date.day-day)
						else:
							day = date.day + (-1*(date.day-day))
							if (date.month == 1):
								date.replace(year=date.year-1, month=12, day=day)
							else:
								date.replace(month=date.month-1, day=day)
					else:
						print ("Date %s could not be converted on entry %s, date will be wrong (%s)" % (entry['date'], entry['id'], date))

				# Now that we have a date, we must determine which type of entry we have
				# Internal video entry?
				if ('internal_video' in entry):
					cls.add(entry['id'], user_id, date, entry['text'], media, date_approx=dateApprox, internal_video=True)
				elif ('video-link' in entry):
					cls.add(entry['id'], user_id, date, entry['text'], media, date_approx=dateApprox, video_link=entry['video-link'])
				elif ('text-link' in entry):
					cls.add(entry['id'], user_id, date, entry['text'], media, date_approx=dateApprox, text_link=entry['text-link'])
				else:
					cls.add(entry['id'], user_id, date, entry['text'], media, date_approx=dateApprox)

				# Finally, add the details of the run (data)
				Data.add(entry['id'], user_id, reportedDate, entry['views'], entry['likes'], entry['comments'], entry['reposts'])
