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
	def addArtifact(cls, video_id, campaign_id, language, format, seconds, date_creation):
		from config import config
		import psycopg2
		print ('video_id %s' % video_id)
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
			command = "UPDATE artifacts SET format='%s', language='%s', seconds=%s, created='%s' WHERE id=%s" % (format, language, seconds,  date_creation, video_id)
			cls.execute_commands([command], failOnException=True)
		return video_id

	@classmethod
	def getArtifact(cls, id):
		command = "SELECT * FROM artifacts"
		result = cls.execute_commands([command], fetching=True)
		print (result)
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
		html += '\n    remove.innerHTML = "<td><button style=\'color:black;\'>X</button></td>";'
		html += '\n    newCounter--;'
		html += "\n}"
		
		html += '\n async function save_artifact(index) {'
		# Verify if the data is clean
		html += '\n    var lang = 0; var secs = 0; var date = 0;'
		html += '\n    var langCell = document.getElementById(index+"_artifact_language").value;'
		html += '\n    var minsCell = document.getElementById(index+"_artifact_mins").value;'
		html += '\n    var secsCell = document.getElementById(index+"_artifact_secs").value;'
		html += '\n    var idCell = document.getElementById(index+"_artifact_id").innerHTML;'
		html += '\n alert(idCell);'
		html += '\n    var formatCell = document.getElementById(index+"_artifact_format").value;'
		html += '\n    var dateCell = document.getElementById(index+"_artifact_date").value;'

		# Phase 1: If date, mins or secs are not clean, throw
		html += '\n    if (langCell.toLowerCase() != langCell || langCell.length < 2) lang++;'
		html += '\n    if (!/^\d+$/.test(secsCell)) secs++;'
		html += '\n    if (minsCell != "" && !/^\d+$/.test(minsCell)) mins++;'
		html += '\n    if (dateCell == "") date++;'
		html += '\n    if (lang || secs || date) { var msg="Missing or faulty: "; if(lang) msg += " language"; if(mins) msg += " minutes"; if(secs) msg += " seconds"; if(date) msg += " date";  alert(msg); return;}'
		
		# Phase 2: Attempt to save to server
		html += '\n  var id = idCell; if (!/^\d+$/.test(id)) id = -1'
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
		html += "\n  if (response.ok) { alert('Saved'); document.getElementById(index+'_artifact_id').innerHTML=await response.text(); } else { alert('Server did not honor request'); }} catch {alert('Unknown failure');}" 
		#html += "\n  .then(function(response){"
		#html += "\n        /*alert (response.text());"
		#html += "\n        if(response.text())"
		#html += "\n             alert('OK');"
		#html += "\n             else alert('error');*/})"
		#html += "\n  .then(function(data)"
		#html += "\n    {console.log(data);"
		#html += "\n    }).catch(error => console.error('Error:', error));" 

		html += '\n}'

		html += "</script>"
		html += '\n   <h4>Artifacts                  '
		html += '\n   <button id="add_artifact" onclick="add_artifact();" style="background-color: black; width: 100px;">Add artifact</button></h4>'
		html += '\n<table id="artifacts" width="50%"><tr><th>ID</th><th>Orientation</th><th>Lang</th><th>Mins</th><th>Secs</th><th>Created</td></tr>'
		artifacts = cls.getAllCampaignArtifacts()
		print ('artifacts: %s' % artifacts)
		for artifact in artifacts.keys():
			artifact = cls.getArtifact(artifact)
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
