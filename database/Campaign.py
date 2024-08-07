#!/usr/bin/python
# This class represents Runs, which are individual posts on a social media

from Base import Base
from Data import Data
from Run import Run
import json, datetime
from dateutil.relativedelta import relativedelta

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
		commands = []
		# This is a bit more complex than before. If you delete a campaign, make sure all
		# related Artifacts are deleted
		command = "SELECT * FROM campaigns_to_artifacts WHERE campaign_id=%s" % campaign_id
		results = cls.execute_commands([command], fetching=True)
		for result in results:
			commands.append("DELETE FROM artifacts_to_run WHERE video_id=%s" % result[1])
			commands.append("DELETE FROM artifacts WHERE id=%s" % result[1])
		commands.append("DELETE FROM campaigns_to_artifacts WHERE campaign_id=%s" % campaign_id)
		commands.append("DELETE FROM runs_to_campaigns WHERE campaign_id=%s" % campaign_id)
		commands.append("DELETE FROM campaigns where id=%s" % campaign_id)
		return cls.execute_commands(commands)

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
                        original_date_before=None, original_date_after=None, linkedin=False, tiktok=None, youtube=None, 
			languages=[]):
		command = "SELECT * FROM campaigns WHERE user_id = %s" % user_id
		# Do we need to restrict that list?
		if image or external_text or internal_video or external_video or simple or original_date_before or original_date_after or linkedin or youtube or tiktok or languages:
			campaigns = cls.execute_commands([command], fetching=True)
			all_runs = Run.getRecords(user_id, image, external_text, internal_video, external_video, simple, 
					original_date_before, original_date_after, linkedin, tiktok, youtube, languages)
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
	def getRerunRecommendations(cls, user_id):
		# First get all campaigns
		campaigns = cls.getRecords(user_id)
		linkedIn_deadline = datetime.datetime.now() - relativedelta(year=1, month=2)
		recommendations = {'linkedin':[], 'tiktok':[], 'youtube':[]}
		for campaign in campaigns:
			languageDict = {}
			mediaDict = {}
			runs = cls.getRuns(campaign[0])
			linkedIn_reruns = []
			linkedIn_stillValid = []
			for run in runs:
				runDetails = Run.getRecord(user_id, run[0])
				if not(runDetails[8] or runDetails[9]):
					continue
				if runDetails[10] in languageDict.keys():
					if runDetails[9] not in languageDict[runDetails[10]]:
						languageDict[runDetails[10]].append(runDetails[9])
				else:
					languageDict[runDetails[10]] = [runDetails[9]]
				if runDetails[9] in mediaDict.keys():
					if runDetails[10] not in mediaDict[runDetails[9]]:
						mediaDict[runDetails[9]].append(runDetails[10])
				else:
					mediaDict[runDetails[9]] = [runDetails[10]]

				if runDetails[9] == 'linkedin':
					if runDetails[2] < linkedIn_deadline.date():
						linkedIn_reruns.append({'campaign':campaign[0], 'title':campaign[1], 'msg':'Rerun candidate (%s)' % runDetails[10], 'language':[runDetails[10]]})
					else:
						linkedIn_stillValid.append(runDetails[10])
		
			coveredLang = []
			for candidate in linkedIn_reruns:
				if candidate['language'] not in linkedIn_stillValid and candidate['language'] not in coveredLang:
					recommendations['linkedin'].append(candidate)
					coveredLang.append(candidate['language'])


			for medium in recommendations.keys():
				# Case 1: Missing video on one media
				if medium not in mediaDict.keys():
					if campaign[0] == 26:
						recommendations[medium].append({'campaign':campaign[0], 'title':campaign[1], 'msg':'New run', 'language':languageDict.keys()})
				# Case 2: Media exist but not in all languages
				else:
					for lang in languageDict.keys():
						if not lang in mediaDict[medium]:
							recommendations[medium].append({'campaign':campaign[0], 'title':campaign[1], 'msg':'New language (%s)' % lang, 'language':[lang]}) 
		return recommendations

	@classmethod
	def getRerunRecommendationsHTML(cls, user_id):
		recommendations = cls.getRerunRecommendations(user_id)
		html = ''
		for medium in recommendations.keys():
			html += '<h2>Medium: %s</h2>' % medium 
			html += '<div class="table-wrap">\n\t<table class="sortable">'
			html += '\n\t\t<thead>'
			html += '\n\t\t\t<tr>'
			html += '\n\t\t\t\t<th class="num"><button>Campaign ID<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t\t<th><button style="width: 400;">Title<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t\t<th><button>Message<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t\t<th><button>Language<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t</tr>'
			html += '\n\t\t</thead>'
			html += '\n\t\t<tbody>'
			for recommendation in recommendations[medium]:
				for lang in recommendation['language']:
					html += '\n\t\t\t<tr>'
					html += '\n\t\t\t\t<td class="num">%s</td><td style="width: 400;">%s</td><td>%s</td><td>%s</td>' % (recommendation['campaign'], recommendation['title'], recommendation['msg'], lang)
					html += '\n\t\t\t</tr>'
			html += '\n\t\t</tbody>'
			html += '\n\t</table>'
		return html

	@classmethod
	def getRuns(cls, campaign_id):
		command = "SELECT * FROM runs_to_campaigns WHERE campaign_id = %s" % campaign_id
		return cls.execute_commands([command], fetching=True)


	#id, user_id, publication_date, publication_date_approx, text, text_link, image_link, video_link, internal_video, social_media
	@classmethod
	#def getRecordsHTMLTable(cls, user_id):	
	def getRecordsHTMLTable(cls, user_id, image=None, external_text=None, internal_video=None, external_video=None, simple=None,
                        original_date_before=None, original_date_after=None, linkedin=False, tiktok=None, youtube=None, 
			languages=[], startRecord=0, endRecord=-1):
		records = cls.getRecords(user_id, image, external_text, internal_video, external_video, simple, original_date_before,
			original_date_after, linkedin, tiktok, youtube, languages)

		# Provide the range of record. If the request is larger than the last record, return until last record
		# If the start record is over the last record, then []
		total_records = len(records) 
		if endRecord != -1:
			if startRecord > len(records) - 1:
				records = []
			else:
				if endRecord > len(records) - 1:
					endRecord = len(records)
				records = records[startRecord:endRecord]

		html = ""
		if startRecord == 0:
			html = '<h2>Records: %s</h2>' % total_records
			html += '<div class="table-wrap">\n\t<table class="sortable">'
			html += '\n\t\t<thead>'
			html += '\n\t\t\t<tr>'
			html += '\n\t\t\t\t<th><button class="num">ID<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t\t<th><button>Title<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t\t<th><button>Description<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t\t<th style="width:50; max-width:50;"><button class="num"># Runs<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t\t<th><button>First run<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t\t<th><button>Last run<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t\t<th><button>Types<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t\t<th><button>Languages<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t\t<th><button>Media<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t\t<th><button class="num">Displays<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t\t<th><button>Path<span aria=hidden="true"></span></button></th>'
			html += '\n\t\t\t\t<th></th>'
			html += '\n\t\t\t</tr>'
			html += '\n\t\t</thead>'

			html += '\n\t\t<tbody>'
		
		recordNum = 0
		for record in records:
			html += '\n\t\t\t<tr>'
			html += '\n\t\t\t\t<td class="num">%s</td>' % record[0] # Campaign ID
			html += '\n\t\t\t\t<td>%s</td>' % record[1] # Title
			html += '\n\t\t\t\t<td style="max-width: 200px; overflow:hidden; text-overflow: hidden;" width="200"><div class="expandable" id=\'exp%s\' onclick="toggle(\'exp%s\');" style="max-width:200px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis;">%s</div></td>' % (recordNum, recordNum, record[2])
			#html += '\n\t\t\t\t<td>%s</td>' % record[2] # Description

			# Runs
			runs = cls.getRuns(record[0])
			html += '\n\t\t\t\t<td class="num"  style="width:50; max-width:50;">%s</td>' % len(runs)

			first_run = None
			last_run = None
			languages = []
			media = []
			mediaDict = {'linkedin':'LI', 'tiktok':'TT', 'youtube':'YT'}
			types = {}
			views = 0
			for run in runs:
				runRecord = Run.getRecord(user_id, run[0])
				if not mediaDict[runRecord[9]] in media:
					media.append(mediaDict[runRecord[9]])
				if not runRecord[10] in languages:
					languages.append(runRecord[10])
				if first_run is None or first_run > runRecord[2]:
					first_run = runRecord[2]
				if last_run is None or last_run < runRecord[2]:
					last_run = runRecord[2]
				datapoints = Data.getRecords(user_id, runRecord[0])
				try:
					views += datapoints[-1][3]
				except Exception:
					pass
				# Types
				if runRecord[5]:
					types['A'] = 0
				elif runRecord[6]:
					types['I'] = 0
				elif runRecord[7] or runRecord[8]:
					types['V'] = 0
				else:
					types['S'] = 0

			languages.sort()
			media.sort()
			types_list = list(types.keys())
			types_list.sort()

			html += '\n\t\t\t\t<td>%s</td>' % first_run
			html += '\n\t\t\t\t<td>%s</td>' % last_run

			# Types
			html += '\n\t\t\t\t<td>'
			pos = 0
			for type in types_list:
				html += type
				pos += 1
				if pos < len(types):
					html += ', '
			html += '</td>'

			html += '\n\t\t\t\t<td>'
			pos = 0
			for language in languages:
				html += language
				pos += 1
				if pos < len(languages):
					html += ', '
			html += '</td>'
			html += '\n\t\t\t\t<td>'
			pos = 0
			for medium in media:
				html += medium
				pos += 1
				if pos < len(media):
					html += ', '
			html += '</td>'
			html += '\n\t\t\t\t<td class="num">%s</td>' % views
			html += '\n\t\t\t\t<td style="max-width: 50px; overflow:hidden; text-overflow: hidden;" width="50"><div class="expandable" id=\'path%s\' onclick="toggle(\'path%s\');" style="max-width:200px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis;">%s</div></td>' % (recordNum, recordNum, record[3])
			html += '\n\t\t\t\t<td><table border="0"><tr><td><button id="edit_%s" style="color: black;" onclick="edit_campaign(\'%s\', \'%s\');">Edit</button></td><td><button id="del_%s" style="color: black; background-color: transparent;" onclick="del_campaign(\'%s\', \'%s\');">Del</button></td></tr></table></td>' % (record[0], user_id, record[0], record[0], user_id, record[0]) 
			html += '\n\t\t\t</tr>'
			recordNum += 1
		
		if startRecord == 0:	
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
