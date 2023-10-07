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
			'run_id VARCHAR(255),'
			'campaign_id INT,'
			'PRIMARY KEY (run_id, campaign_id))')
		cls.execute_commands([command]) 

	@classmethod
	def add(cls, user_id, title=None, description=None, location=None, is_subcampaign=None, runs=[]):
		command = ("INSERT INTO campaigns (title, description, location, is_subcampaign, user_id) VALUES (NULL, NULL, NULL, NULL, %s) RETURNING id" % user_id)
		id = cls.execute_commands([command], fetching=True)[0]
		cls.update(id=id, title=title, description=description, location=location, is_subcampaign=is_subcampaign, runs=runs)
		return id

	@classmethod
	def deleteRecord(cls, user_id, campaign_id):
		command1 = "DELETE FROM runs_to_campaigns WHERE campaign_id=%s" % campaign_id
		command2 = "DELETE FROM campaigns where id=%s" % campaign_id
		return cls.execute_commands([command1, command2])

	@classmethod
	def getRecord(cls, user_id, campaign_id):
		command = "SELECT * FROM campaigns where user_id = %s and id = '%s'" % (user_id, campaign_id)
		results = cls.execute_commands([command], fetching=True)
		if len(results):
			return results[0]
		else:
			return []

	@classmethod
	#def getRecords(cls, user_id):
	def getRecords(cls, user_id, image=None, external_text=None, internal_video=None, external_video=None, simple=None,
                        original_date_before=None, original_date_after=None, linkedin=False, youtube=None, languages=[]):
		command = "SELECT * FROM campaigns WHERE user_id = %s" % user_id
		# Do we need to restrict that list?
		if image or external_text or internal_video or external_video or simple or original_date_before or original_date_after or linkedin or youtube or languages:
			campaigns = cls.execute_commands([command], fetching=True)
			all_runs = Run.getRecords(user_id, image, external_text, internal_video, external_video, simple, 
					original_date_before, original_date_after, linkedin, youtube, languages)
			runs_to_campaigns = cls.execute_commands(["SELECT * FROM runs_to_campaigns"], fetching=True)
			final_campaign_list = []

			# First restrict the all runs down to whatever runs are present
			runs_dict = {}
			relevant_campaign_ids = []
			for duo in runs_to_campaigns:
				if duo[0] in runs_dict.keys():
					runs_dict[duo[0]].append(duo[1])
				else:
					runs_dict[duo[0]] = [duo[1]]
			for run in all_runs:
				if run[0] in runs_dict.keys():
					for campaign_id in runs_dict[run[0]]:
						if not campaign_id in relevant_campaign_ids:
							relevant_campaign_ids.append(campaign_id)

			relevant_campaigns = []
			for campaign in campaigns:
				if campaign[0] in relevant_campaign_ids:
					relevant_campaigns.append(campaign)
			
			return relevant_campaigns
		else:
			return cls.execute_commands([command], fetching=True)

	@classmethod
	def getRuns(cls, campaign_id):
		command = "SELECT * FROM runs_to_campaigns WHERE campaign_id = %s" % campaign_id
		return cls.execute_commands([command], fetching=True)


	#id, user_id, publication_date, publication_date_approx, text, text_link, image_link, video_link, internal_video, social_media
	@classmethod
	#def getRecordsHTMLTable(cls, user_id):	
	def getRecordsHTMLTable(cls, user_id, image=None, external_text=None, internal_video=None, external_video=None, simple=None,
                        original_date_before=None, original_date_after=None, linkedin=False, youtube=None, languages=[]):
		records = cls.getRecords(user_id, image, external_text, internal_video, external_video, simple, original_date_before,
			original_date_after, linkedin, youtube, languages)

		##print ('RECORDS: %s' % len(records))
		html = '<h2>Records: %s</h2>' % len(records)
		html += '<div class="table-wrap">\n\t<table class="sortable">'
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
		html += '\n\t\t\t\t<th></th>'
		html += '\n\t\t\t</tr>'
		html += '\n\t\t</thead>'

		html += '\n\t\t<tbody>'
		
		recordNum = 0
		for record in records:
			html += '\n\t\t\t<tr>'
			html += '\n\t\t\t\t<td class="num">%s</td>' % record[0] # Campaign ID
			html += '\n\t\t\t\t<td>%s</td>' % record[1] # Title
			html += '\n\t\t\t\t<td style="max-width: 200px; overflow:hidden; text-overflow: hidden;" width="200"><div class="expandable" id=\'exp%s\' onclick="toggle(\'exp%s\');" style="max-width:200px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis;">%s</div></td>' % (record[2], record[2], record[2])
			#html += '\n\t\t\t\t<td>%s</td>' % record[2] # Description

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
			html += '\n\t\t\t\t<td><table border="0"><tr><td><button id="edit_%s" style="color: black;" onclick="edit_campaign(\'%s\', \'%s\');">Edit</button></td><td><button id="del_%s" style="color: black; background-color: transparent;" onclick="del_campaign(\'%s\', \'%s\');">Del</button></td></tr></table></td>' % (record[0], user_id, record[0], record[0], user_id, record[0]) 
			html += '\n\t\t\t</tr>'
		
		html += '\n\t\t</tbody>'
		html += '\n\t</table>'
		html += '\n</div>'

		return html, None

	@classmethod
	def update(cls, id, title=None, description=None, location=None, is_subcampaign=None, runs=[]):
		if not (title or description or location or is_subcampaign or len(runs)):
			return
		fields = []
		if title:
			fields.append("title='%s'" % title.replace("'", "\""))
		if description:
			fields.append("description='%s'" % description.replace("'", "\""))
		if location:
			fields.append("location='%s'" % location)
		if is_subcampaign:
			fields.append("is_subcampaign='%s'" % is_subcampaign)
		if len(fields):
			command = "UPDATE campaigns SET "
			pos = 0
			for field in fields:
				command += field
				pos += 1
				if pos < len(fields):
					command += ', '
				
			command += " WHERE id=%s" % id
			cls.execute_commands([command])
		
		# Here ID could be an array if doing a new entry or not. Test
		try:
			newInt = int(id)
		except Exception:
			id = id[0]

		if len(runs):
			# Here we need to first delete previous entries
			command_del = "DELETE FROM runs_to_campaigns WHERE campaign_id=%s" % id
			cls.execute_commands([command_del])
			command = "SELECT * FROM runs_to_campaigns"
			command_insert = "INSERT INTO runs_to_campaigns (run_id, campaign_id) VALUES "
			pos = 0
			for run in runs:
				command_insert += "('%s', %s)" % (run, id) # No idea why ID should be having more than one value!
				pos += 1
				if pos < len(runs):
					command_insert += ", "
			cls.execute_commands([command_insert])
