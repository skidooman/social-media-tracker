#!/usr/bin/python
# This class represents Runs, which are individual posts on a social media

from Base import Base

class Artifact(Base):
	name_of_table = 'artifacts'

	@classmethod
	def create(cls):
		# Format is as follows
		# 0: Video horizontal
		# 1: Video vertical
		# 2: Image
		# 10: Other
		command = ('CREATE TABLE artifacts('
		        'id SERIAL PRIMARY KEY,'
		        'format VARCHAR(1),'
		        'language VARCHAR(2),'
		        'seconds INT,'
			'created DATE)')
		#print (command)
		cls.execute_commands([command])
		#print ("OK")

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
		return {"id": result[0], "format": result[1], "language": result[2], "seconds": result[3]}

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
		html = "\n <script>"
		html += '\n    var languageMsg = "Please provide a valid two-letter language code (lower case)";'
		html += '\n    var minsMsg = "Please provide a valid time in minutes or leave empty";'
		html += '\n    var secsMsg = "Please provide a valid time in seconds";'
		html += "\n  function add_artifact() {"
		html += "\n    var table = document.getElementById('artifacts');"
		html += "\n    var row = table.insertRow(1);"
		html += "\n    var id = row.insertCell(0);"
		html += "\n    var orientation = row.insertCell(1);"
		html += "\n    var language = row.insertCell(2);"
		html += "\n    var mins = row.insertCell(3);"
		html += '\n    var secs = row.insertCell(4);'
		html += '\n    var remove = row.insertCell(5);'
		html += '\n    orientation.innerHTML = "<select id=\'new_artifact_orientation\'><option value=\'vertical\'>Vertical</option><option value=\'horizontal\' selected>Horizontal</option></select>";'
		html += '\n    language.innerHTML = "<input type=\'text\' id=\'new_artifact_language\' size=\'2\' number=\'2\' pattern=\'[a-z]{2}\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(languageMsg)\'/>";'
		html += '\n    mins.innerHTML = "<input type=\'text\' id=\'new_artifact_mins\' size=\'3\' number=\'3\' pattern=\'[0-9]*\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(minsMsg)\'/>";'
		html += '\n    secs.innerHTML = "<input type=\'text\' id=\'new_artifact_secs\' size=\'3\' number=\'3\' pattern=\'[0-9]+\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(secsMsg)\'/>";'
		html += '\n    create.innerHTML = "<input type=\'date\' id=\'new_artifact_date\' size=\'3\' number=\'3\' pattern=\'[0-9]+\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(secsMsg)\'/>";'
		html += '\n    save.innerHTML = "<td><button style=\'color:black;\'>&check;</button></td>";'
		html += '\n    remove.innerHTML = "<td><button style=\'color:black;\'>X</button></td>";'		
		html += "\n}"
		html += "</script>"
		html += '\n   <h4>Artifacts                  '
		html += '\n   <button id="add_artifact" onclick="add_artifact();" style="background-color: black; width: 100px;">Add artifact</button></h4>'
		html += '\n<table id="artifacts" width="50%"><tr><th>ID</th><th>Orientation</th><th>Lang</th><th>Mins</th><th>Secs</th><th>Created</td></tr>'
		artifacts = cls.getAllCampaignArtifacts()
		for artifact in artifacts.keys():
			artifact = cls.getArtifact(campaign)
			html += cls.getExistingArtifactsTableRow(artifact)
		html += '\n</table>'
		return html

	@classmethod
	def getExistingArtifactsTableRow(cls, artifact):
		minutes = 0
		seconds = 0
		minutes = int(Math.down(int(artifact['seconds'])/60))
		seconds = int(artifacts['seconds']) - (minutes*60)
		html = '\n   <tr><td>%s</td>' % artifact['id']
		if artifact['format'] == '0':
			html += '\n     <td><select id="artifact_%s_orientation"><option value="horizontal" selected>Horizontal</option><option value="horizontal">Horizontal</option></select></td>' % (artifact['id'])
		elif artifact['format'] == '1':
			html += '\n     <td><select id="artifact_%s_orientation"><option value="vertical" selected>Vertical</option><option value="horizontal">Horizontal</option></select></td>' % (artifact['id'])
		elif artifact['format'] == '2':
			html += '\n     <td><select id="artifact_%s_orientation"><option value="image" selected>Image</option><option value="horizontal">Horizontal</option></select></td>' % (artifact['id'])
		else:
			html += '\n     <td><select id="artifact_%s_orientation"><option value="other">Other</option><option value="horizontal" selected>Horizontal</option></select></td>' % (artifact['id'])
		html += '\n     <td><input type="text" id="artifact_%s_language" value="%s" number=\'2\' pattern=\'[a-z]{2}\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(languageMsg)\'/></td>' % (artifact['id'], artifact['language'])
		html += '\n     <td><input type="text" id="artifact_%s_mins" value="%s" number=\'3\' pattern=\'[0-9]*\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(minsMsg)\'/></td><td><input type="text" id="artifact_%s_secs" value="%s" number=\'3\' pattern=\'[0-9]+\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(secsMsg)\'/></td>' % (artifact['id'], minutes, artifact['id'], seconds)
		html += '\n     <td><input type="date" id="artifact_%s_mins" value="%s" oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(minsMsg)\'/></td><td><input type="text" id="artifact_%s_date" value="%s" number=\'3\' pattern=\'[0-9]+\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(secsMsg)\'/></td>' % (artifact['id'], minutes, artifact['id'], seconds)
		html += '\n     <td><button style="color:black;">&check;</button></td>'
		html += '\n     <td><button style="color:black;">X</button></td>'
		html += '\n   </tr>'
		return html

#Artifact.create()
