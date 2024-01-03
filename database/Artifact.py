#!/usr/bin/python
# This class represents Runs, which are individual posts on a social media

from Base import Base

class Artifact(Base):
	name_of_table = 'artifacts'

	@classmethod
	def create(cls):
		command = ('CREATE TABLE artifacts('
		        'id SERIAL PRIMARY KEY,'
		        'vertical BOOLEAN,'
		        'language VARCHAR(2),'
		        'seconds INT)')
		cls.execute_commands([command])

		command = ('CREATE TABLE artifacts_to_runs('
		        'video_id INT,'
		        'run_id VARCHAR(255),'
			'PRIMARY KEY (video_id, run_id))')
		cls.execute_commands([command])

		command = ('CREATE TABLE campaigns_to_artifacts('
		        'campaign_id INT,'
		        'video_id INT, '
			'PRIMARY KEY (campaign_id, video_id))')
		cls.execute_commands([command])

	@classmethod
	def getArtifact(cls, id):
		command = "SELECT * FROM artifacts"
		result = cls.execute_commands([command], fetching=True)
		return {"id": result[0], "vertical": result[1], "language": result[2], "seconds": result[3]}

	# Find all campaigns associated with runs
	@classmethod
	def getAllCampaignArtifacts(cls):
	        dict = {}
	        command = "SELECT * FROM campaigns_to_artifacts"
	        results = cls.execute_commands([command], fetching=True)
	        for result in results:
	                if result[0] in dict.keys():
                        	dict[result[0]].append(result[1])
	                else:
                        	dict[result[0]] = [result[1]]
	        return dict


	@classmethod
	def getExistingArtifactsTable(cls):
		html = '\n<table id="artifacts" width="50%"><tr><th>ID</th><th>Orientation</th><th>Lang</th><th>Mins</th><th>Secs</th></tr>'
		campaigns = cls.getAllCampaignArtifacts()
		for campaign in campaigns.keys():
			artifact = cls.getArtifact(campaign)
			minutes = 0
			seconds = 0
			minutes = int(Math.down(int(artifact['seconds'])/60))
			seconds = int(artifacts['seconds']) - (minutes*60)
			html += '\n   <tr><td>%s</td>' % artifact['id']
			if artifact['vertical']:
				html += '\n     <td><select id="artifact_%s_orientation"><option value="vertical" selected>Vertical</option><option value="horizontal">Horizontal</option></select></td>' % (artifact['id'])
			else:
				html += '\n     <td><select id="artifact_%s_orientation"><option value="vertical">Vertical</option><option value="horizontal" selected>Horizontal</option></select></td>' % (artifact['id'])
			html += '\n     <td><input type="text" id="artifact_%s_language" value="%s" number=\'2\' pattern=\'[a-z]{2}\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(languageMsg)\'/></td>' % (artifact['id'], artifact['language'])
			html += '\n     <td><input type="text" id="artifact_%s_mins" value="%s" number=\'3\' pattern=\'[0-9]*\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(minsMsg)\'/></td><td><input type="text" id="artifact_%s_secs" value="%s" number=\'3\' pattern=\'[0-9]+\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(secsMsg)\'/></td>' % (artifact['id'], minutes, artifact['id'], seconds)
			html += '\n     <td><button style="color:black;">X</button></td>'
			html += '\n   </tr>'
		html += '\n</table>'
		return html

