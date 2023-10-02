#!/usr/bin/python
# This class represents Runs, which are individual posts on a social media

from Base import Base
from Data import Data
from Run import Run
import json, datetime

class Campaign(Base):
	name_of_table = 'campaigns'

	@classmethod
	def create(cls):
		command = ('CREATE TABLE campaigns('
			'id SERIAL PRIMARY KEY,'
			'title VARCHAR(255),'
			'description VARCHAR(2084),'
			'location VARCHAR(255),'
			'is_subcampaign INT,'
			'user_id INT)')
		cls.execute_commands([command])

		# Here, we need a second table that associates Runs and Campaigns
		command = ('CREATE TABLE runs_to_campaigns('
			'run_id VARCHAR(255) PRIMARY KEY,'
			'campaign_id INT,'
			'UNIQUE (run_id, campaign_id))')
		cls.execute_commands([command]) 

	@classmethod
	def add(cls, user_id, title=None, description=None, location=None, is_subcampaign=None, runs=[]):
		print ("Adding title %s" % title)
		print ("Runs: %s" % runs)
		command = ("INSERT INTO campaigns (title, description, location, is_subcampaign, user_id) VALUES (NULL, NULL, NULL, NULL, %s) RETURNING id" % user_id)
		id = cls.execute_commands([command], fetching=True)[0]
		cls.update(id=id, title=title, description=description, location=location, is_subcampaign=is_subcampaign, runs=runs)
		return id

	'''@classmethod
	def getLanguages(cls):
		command = "SELECT DISTINCT {language} from Runs"
		results = cls.getUniques('language', 'Runs')
		results.sort()
		return results

	@classmethod
	def getRecord(cls, user_id, entry_id):
		command = "SELECT * FROM runs where user_id = %s and id = '%s'" % (user_id, entry_id)
		results = cls.execute_commands([command], fetching=True)
		return results[0]
	'''	

	@classmethod
	def getRecords(cls, user_id):
		command = "SELECT * FROM campaigns WHERE user_id = %s" % user_id
		return cls.execute_commands([command], fetching=True)

	@classmethod
	def getRuns(cls, campaign_id):
		command = "SELECT * FROM runs_to_campaigns WHERE campaign_id = %s" % campaign_id
		return cls.execute_commands([command], fetching=True)


	#id, user_id, publication_date, publication_date_approx, text, text_link, image_link, video_link, internal_video, social_media
	@classmethod
	def getRecordsHTMLTable(cls, user_id):	
		records = cls.getRecords(user_id)

		##print ('RECORDS: %s' % len(records))
		#html = '<h2>Records: %s</h2>' % len(records)
		html = '<div class="table-wrap">\n\t<table class="sortable">'
		html += '\n\t\t<thead>'
		html += '\n\t\t\t<tr>'
		html += '\n\t\t\t\t<th><button class="num">ID<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th><button>Title<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th><button>Description<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th><button class="num"># Runs<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th><button>First run<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th><button>Last run<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th><button>Languages<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t\t<th><button class="num">Views<span aria=hidden="true"></span></button></th>'
		html += '\n\t\t\t</tr>'
		html += '\n\t\t</thead>'

		html += '\n\t\t<tbody>'
		
		recordNum = 0
		for record in records:
			print (record)
			html += '\n\t\t\t<tr>'
			html += '\n\t\t\t\t<td class="num">%s</td>' % record[0] # Campaign ID
			html += '\n\t\t\t\t<td>%s</td>' % record[1] # Title
			html += '\n\t\t\t\t<td>%s</td>' % record[2] # Description

			# Runs
			runs = cls.getRuns(record[0])
			html += '\n\t\t\t\t<td class="num">%s</td>' % len(runs)

			first_run = None
			last_run = None
			languages = []
			views = 0
			for run in runs:
				runRecord = Run.getRecord(user_id, run[0])
				if not runRecord[10] in languages:
					languages.append(runRecord[10])
				if first_run is None or first_run > runRecord[2]:
					first_run = runRecord[2]
				if last_run is None or last_run < runRecord[2]:
					last_run = runRecord[2]
				datapoints = Data.getRecords(user_id, runRecord[0])
				views += datapoints[-1][3]

			html += '\n\t\t\t\t<td>%s</td>' % first_run
			html += '\n\t\t\t\t<td>%s</td>' % last_run
			html += '\n\t\t\t\t<td>'
			pos = 0
			for language in languages:
				html += language
				pos += 1
				if pos < len(languages):
					html += ', '
			html += '</td>'
			html += '\n\t\t\t\t<td class="num">%s</td>' % views

			html += '\n\t\t\t</tr>'
		
		html += '\n\t\t</tbody>'
		html += '\n\t</table>'
		html += '\n</div>'

		return html, None

	@classmethod
	def update(cls, id, title=None, description=None, location=None, is_subcampaign=None, runs=[]):
		if not (title or description or location or is_subcampaign or len(runs)):
			print ('esc')
			return
		fields = []
		print ('in update for id %s' % id)
		if title:
			fields.append("title='%s'" % title)
		if description:
			fields.append("description='%s'" % description)
		if location:
			fields.append("location='%s'" % location)
		if is_subcampaign:
			fields.append("is_subcampaign='%s'" % is_subcampaign)
		print (fields)
		if len(fields):
			command = "UPDATE campaigns SET "
			pos = 0
			for field in fields:
				command += field
				pos += 1
				if pos < len(fields):
					command += ', '
				
			command += " WHERE id=%s" % id
			print (command)
			cls.execute_commands([command])
		
		print ('here id is %s' % id)
		ID = id
		if len(runs):
			command = "INSERT INTO runs_to_campaigns (run_id, campaign_id) VALUES "
			pos = 0
			for run in runs:
				command += "('%s', %s)" % (run, id[0]) # No idea why ID should be having more than one value!
				pos += 1
				if pos < len(runs):
					command += ", "
			print (command)
			cls.execute_commands([command])
