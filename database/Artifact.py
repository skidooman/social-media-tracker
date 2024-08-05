#!/usr/bin/python
# This class represents Runs, which are individual posts on a social media

from Base import Base
from config import config
import psycopg2

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
	def addArtifact(cls, video_id, campaign_id, language, format, seconds, date_creation):
		if (video_id == -1):
			command = "INSERT INTO artifacts (format, language, seconds, created) VALUES ('%s', '%s', %s, '%s') RETURNING id" % (format, language, seconds, date_creation)
			params = config()
			# connect to the PostgreSQL server
			conn = psycopg2.connect(**params)
			cursor = conn.cursor()
			# create table one by one
			result = cursor.execute(command)
			video_id = cursor.fetchone()[0]
			command = "INSERT INTO campaigns_to_artifacts (campaign_id, video_id) VALUES (%s, %s)" % (campaign_id, video_id)
			cursor.execute(command)
			conn.commit()
			conn.close()
			cursor.close()
		else:
			print ('UPDATING')
			print (format)
			command = "UPDATE artifacts SET format='%s', language='%s', seconds=%s, created='%s' WHERE id=%s" % (format, language, seconds,  date_creation, video_id)
			cls.execute_commands([command], failOnException=True)
		return video_id

	@classmethod
	def add_run_videos(cls, video_id, run_id):
		# The logic here is that a run can only have one video
		# So if you delete all of these entries, you should be good.
		command = "DELETE FROM artifacts_to_runs WHERE run_id = '%s'" % run_id
		cls.execute_commands([command], failOnException=True)

		# If this is done correct, then and only then should you insert the following
		command = "INSERT INTO artifacts_to_runs (video_id, run_id) VALUES (%s, '%s')" % (video_id, run_id)
		cls.execute_commands([command], failOnException=True)

	# Deletes all mentions of a specific video id
	@classmethod
	def delete_video(cls, video_id):
		params = config()
		# connect to the PostgreSQL server
		conn = psycopg2.connect(**params)
		cursor = conn.cursor()

		# Any mention in artifacts_to_runs need to be dropped
		command = "DELETE FROM artifacts_to_runs WHERE video_id=%s" % int(video_id)
		result = cursor.execute(command)

		# Any mention in campaigns_to_artifacts need to be dropped
		command = "DELETE FROM campaigns_to_artifacts WHERE video_id=%s" % int(video_id)
		result = cursor.execute(command)

		# Artifact can now be dropped
		command = "DELETE FROM artifacts WHERE id=%s" % int(video_id)
		result = cursor.execute(command)

		# If everything went fine, then you can commit
		conn.commit()
		conn.close()
		cursor.close()

	@classmethod
	def delete_run_videos(cls, run_id):
		# The logic here is that a run can only have one video
		# So if you delete all of these entries, you should be good.
		command = "DELETE FROM artifacts_to_runs WHERE run_id = '%s'" % run_id
		cls.execute_commands([command], failOnException=True)

	@classmethod
	def getArtifact(cls, id):
		command = "SELECT * FROM artifacts WHERE id=%s" % id
		result = cls.execute_commands([command], fetching=True)
		return {"id": result[0][0], "format": result[0][1], "language": result[0][2], "seconds": result[0][3], "date":result[0][4]}

	# Find all campaigns associated with runs
	@classmethod
	def getAllCampaignArtifacts(cls, campaign_id):
	        list = []
	        command = "SELECT * FROM campaigns_to_artifacts WHERE campaign_id=%s" % campaign_id
	        results = cls.execute_commands([command], fetching=True)
	        for result in results:
	                list.append(result[1])
	        return list

	# This should return a map run_id => video_id
	@classmethod
	def getArtifactsForCampaign(cls, campaign):
		command = "SELECT * FROM campaigns_to_artifacts WHERE campaign_id=%s" % campaign
		results = cls.execute_commands([command], fetching=True)
		myDict = {}
		for result in results:
			artifacts = cls.getRunsForArtifact(result[1])
			for artifact in artifacts:
				myDict[artifact[1]] = result
		return myDict

	@classmethod
	def getRunsForArtifact(cls, artifact):
		command = "SELECT * from artifacts_to_runs WHERE video_id=%s" % artifact
		results = cls.execute_commands([command], fetching=True)
		return results


	@classmethod
	def getExistingArtifactsTable(cls, campaign_id):
		html = "\n <script>"
		html += '\n    var languageMsg = "Please provide a valid two-letter language code (lower case)";'
		html += '\n    var minsMsg = "Please provide a valid time in minutes or leave empty";'
		html += '\n    var secsMsg = "Please provide a valid time in seconds";'
		html += '\n    var newCounter = -1;'
		html += "\n  function add_artifact() {"
		html += "\n    var table = document.getElementById('artifacts');"
		html += "\n    var row = table.insertRow(1);"
		html += "\n    var id = row.insertCell(0);"
		html += "\n    var format = row.insertCell(1);"
		html += "\n    var language = row.insertCell(2);"
		html += "\n    var mins = row.insertCell(3);"
		html += '\n    var secs = row.insertCell(4);'
		html += '\n    var create = row.insertCell(5);'
		html += '\n    var save = row.insertCell(6);'
		html += '\n    var remove = row.insertCell(7);'
		html += '\n    id.innerHTML = "<div id=\'" + newCounter + "_artifact_id\'>Unsaved</div>"'
		html += '\n    format.innerHTML = "<select id=\'" + newCounter + "_artifact_format\'><option value=\'0\' selected>Horizontal</option><option value=\'1\'>Vertical</option><option value=\'2\'>Image</option><option value=\'9\'>Other</option></select>";'
		html += '\n    language.innerHTML = "<input type=\'text\' id=\'" + newCounter + "_artifact_language\' size=\'2\' number=\'2\' pattern=\'[a-z]{2}\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(languageMsg)\'/>";'
		html += '\n    mins.innerHTML = "<input type=\'text\' id=\'" + newCounter + "_artifact_mins\' size=\'3\' number=\'3\' pattern=\'[0-9]*\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(minsMsg)\'/>";'
		html += '\n    secs.innerHTML = "<input type=\'text\' id=\'" + newCounter + "_artifact_secs\' size=\'3\' number=\'3\' pattern=\'[0-9]+\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(secsMsg)\'/>";'
		html += '\n    create.innerHTML = "<input type=\'date\' id=\'" + newCounter + "_artifact_date\' size=\'3\' number=\'3\' pattern=\'[0-9]+\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(secsMsg)\'/>";'
		html += '\n    save.innerHTML = "<td><button style=\'color:black;\' onclick=\'save_artifact(" + newCounter + ");\'>&check;</button></td>";'
		html += '\n    remove.innerHTML = "<td><button style=\'color:black;\' onclick=\'delete_video(" + newCounter + ");\'>X</button></td>";'
		html += '\n    newCounter--;'
		html += "\n}"
		
		html += '\n async function save_artifact(index) {'
		# Verify if the data is clean
		html += '\n    var lang = 0; var secs = 0; var date = 0;'
		html += '\n    var langCell = document.getElementById(index+"_artifact_language").value;'
		html += '\n    var minsCell = document.getElementById(index+"_artifact_mins").value;'
		html += '\n    var secsCell = document.getElementById(index+"_artifact_secs").value;'
		html += '\n    var idCell = document.getElementById(index+"_artifact_id").innerHTML;'
		html += '\n    var formatCell = document.getElementById(index+"_artifact_format").value;'
		html += '\n    var dateCell = document.getElementById(index+"_artifact_date").value;'

		# Phase 1: If date, mins or secs are not clean, throw
		html += '\n    if (langCell.toLowerCase() != langCell || langCell.length < 2) lang++;'
		html += '\n    if (!/^\d+$/.test(secsCell)) secs++;'
		html += '\n    if (minsCell != "" && !/^\d+$/.test(minsCell)) mins++;'
		html += '\n    if (dateCell == "") date++;'
		html += '\n    if (lang || secs || date) { var msg="Missing or faulty: "; if(lang) msg += " language"; if(mins) msg += " minutes"; if(secs) msg += " seconds"; if(date) msg += " date";  alert(msg); return;}'
		
		# Phase 2: Attempt to save to server
		html += '\n  var id = idCell; if (!/^\d+$/.test(id)) id = -1;'
		html += '\n  var seconds = parseInt(secsCell); if (minsCell != "") seconds += parseInt(minsCell)*60;'
		html += '\n  var myDate = new Date(dateCell);'
		html += '\n  var format = document.getElementById(index+"_artifact_format").value;'
		html += '\n  var campaign = document.getElementById("id").value;'
		html += "\n  var payload = JSON.stringify({" 
		html += "\n      id: id,"
		html += "\n      language: langCell,"
		html += "\n      seconds: seconds,"
		html += "\n      date: myDate.toISOString().split('T')[0],"
		html += "\n      campaign: campaign,"
		html += "\n      format: format,"
		html += "\n        });"
		html += "\n  try{"
		html += "\n  const response = await fetch('/update_artefact', {"
		html += "\n    method: 'POST',"
		html += "\n    body: payload,"
		html += "\n    headers: {'Content-type': 'application/json; charset=UTF-8', }"
		html += "\n  });"
		html += "\n  if (response.ok) { alert('Saved'); id=await response.text(); update_selector(id, format, langCell, seconds, myDate.toISOString().split('T')[0]); document.getElementById(index+'_artifact_id').innerHTML=id;  } else { alert('Server did not honor request'); }} catch {alert('Unknown failure');}" 

		html += '\n}'

		html += "</script>"
		html += "\n   <div id='artifact_selector' z-index='50' style='visibility: hidden; position: absolute; background-color: black; color: white;'><center><b>Select</b><br><select id='artifact_selected'><option value='null'></option>"
		artifacts = cls.getAllCampaignArtifacts(campaign_id)
		print ("ARTIFACTS: %s" % artifacts)
		for artifact in artifacts:
			data = cls.getArtifact(artifact)
			description = ''
			if data['format'] == '0':
				description += 'Video Horizontal: '
			elif data['format'] == '1':
				description += 'Video Vertical: '
			elif data['format'] == '2':
				description += 'Image'
			else:
				description += 'Other'
			if data['format'] == '0' or data['format'] == '1': 
				seconds = data['seconds']
				import math
				mins = math.floor(seconds/60)
				seconds = seconds - (mins*60)
				description += "%d:%02d %s" % (mins, seconds, data['language'])
			html += "\n      <option value='%s'>%s</option>" % (data['id'], description)
		html += "\n   </select><br><b><table border='0' width='100%'><tr><td width='20%'></td><td width='20%'><button onclick='link_artifact();'>&check;</button></td><td width='20%'></td><td width='20%'><button onclick='document.getElementById(\"artifact_selector\").style.visibility=\"hidden\";'>X</button></td><td width='20%'></td></tr></table></b></center></div>"
		html += '\n   <h4>Artifacts                  '
		html += '\n   <button id="add_artifact" onclick="add_artifact();" style="background-color: black; width: 40px;">Add</button></h4>'
		html += '\n<table id="artifacts" width="25%"><tr><th>ID</th><th>Orientation</th><th>Lang</th><th>Mins</th><th>Secs</th><th>Created</th></tr>'

		for artifact in artifacts:
			print ('artifact number is %s' % artifact)
			artifact = cls.getArtifact(artifact)
			print ('description: %s' % artifact)
			html += cls.getExistingArtifactsTableRow(artifact)
		html += '\n</table>'
		return html

	@classmethod
	def getExistingArtifactsTableRow(cls, artifact):
		minutes = 0
		seconds = 0
		import math
		minutes = int(math.floor(int(artifact['seconds'])/60))
		seconds = int(artifact['seconds']) - (minutes*60)
		myDate = artifact['date']
		html = '\n   <tr><td><div id="%s_artifact_id">%s</div></td>' % (artifact['id'], artifact['id'])
		html += '\n     <td><select id="%s_artifact_format"><option value="0" ' % (artifact['id'])
		if artifact['format'] == '0':
			html += 'selected'
		html += '>Horizontal</option><option value="1" '
		if artifact['format'] == '1':
			html += 'selected'
		html += '>Vertical</option><option value="2" '
		if artifact['format'] == '2':
			html += 'selected'
		html += '>Image</option><option value="9" '
		if artifact['format'] == '9':
			html += 'selected'
		html += '>Other</option></select></td>'
		html += '\n     <td><input type="text" id="%s_artifact_language" value="%s" size=\'2\' number=\'2\' pattern=\'[a-z]{2}\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(languageMsg)\'/></td>' % (artifact['id'], artifact['language'])
		html += '\n     <td><input type="text" id="%s_artifact_mins" value="%s" size=\'3\' number=\'3\' pattern=\'[0-9]*\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(minsMsg)\'/></td><td><input type="text" id="%s_artifact_secs" value="%s" size=\'3\' number=\'3\' pattern=\'[0-9]+\' oninput=\'this.reportValidity()\' oninvalid=\'setCustomValidity(secsMsg)\'/></td>' % (artifact['id'], minutes, artifact['id'], seconds)
		html += '\n     <td><input type="date" id="%s_artifact_date" value="%s" size=\'10\'/></td>' % (artifact['id'], myDate)
		html += '\n     <td><button style="color:black;" onclick="save_artifact(\'%s\');">&check;</button></td>' % (artifact['id'])
		html += '\n     <td><button style="color:black;" onclick="delete_video(\'%s\');">X</button></td>' % (artifact['id'])
		html += '\n   </tr>'
		return html


	# This returns a video attached to a specific run
	@classmethod
	def get_run_videos(cls, run_id):
		command = "SELECT * FROM artifacts_to_runs WHERE run_id = '%s'" % run_id
		results = cls.execute_commands([command], failOnException=True, fetching=True)
		if len(results) == 0:
			return "none"
		else:
			 return results[0][0]

	# This returns the runs attached to videos
	@classmethod
	def get_runs_video(cls, video_id):
		command = "SELECT * FROM artifacts_to_runs WHERE video_id=%s" % video_id
		results = cls.execute_commands([command], failOnException=True, fetching=True)
		myResults = []
		for result in results:
			myResults.append(result[1])
		return myResults

#Artifact.create()
