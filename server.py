import os, sys, math
from flask import Flask, flash, redirect, render_template, Response, request
from werkzeug.utils import secure_filename
from collections import OrderedDict
sys.path.append(os.getcwd() + '/database')
from database import Run, Campaign, Importing, Artifact
import plotly.express as px
from io import BytesIO


UPLOAD_FOLDER = os.getcwd() + '/files'
ALLOWED_EXTENSIONS = {'htm', 'html'}
YT_ALLOWED_EXTENSIONS = {'csv'}

# For snapping, we may need to include the path to templates
templates_dir = 'templates'
static_dir = 'static'
app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'


@app.route('/add_run_videos/<video_id>/<run_id>')
def add_run_videos(video_id, run_id):
	# The logic here is that a run can only have one video
	# So if you delete all of these entries, you should be good.
	try:
		Artifact.Artifact.add_run_videos(video_id, run_id)
		return "OK", 200
	except Exception as e:
		print (e)
		return "Error", 400


def allowed_file(filename, media):
	allowed_extensions = ALLOWED_EXTENSIONS
	if media == 'youtube':
		allowed_extensions = YT_ALLOWED_EXTENSIONS
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/campaign')
def campaign():
	html = head()
	html += '\n\n<body onload="filter(\'/campaigns_chunk/0/50\', \'campaigns\')">\n\n'
	html += menu()
	html += filters('/campaigns_chunk/0/50', runs_or_campaigns='campaigns')
	html += '\n\t<table border="0"><tr><td><button onclick="window.location=\'/edit_campaign/1/-1\';" style="background-color: black;">New campaign</button></td><td width="80%"></td></tr></table>'
	html += main()
	return html

#@app.route('/campaigns', methods=['POST'])
@app.route('/campaigns', methods=['GET', 'POST'])
def campaigns():
	data = request.json
	#{'image': False, 'external_text': False, 'internal_video': False, 'external_video': False, 'simple': False, 'original_date_before': False, 'original_date_after': False}
	answer = Campaign.Campaign.getRecordsHTMLTable(1, image=data['image'], external_text=data['external_text'], 
		internal_video=data['internal_video'], external_video=data['external_video'], 
		simple=data['simple'], original_date_before=data['original_date_before'],
		original_date_after=data['original_date_after'], linkedin=data['linkedin'], tiktok=data['tiktok'], 
		youtube=data['youtube'], languages=data['languages'])
	
	#answer = Campaign.Campaign.getRecordsHTMLTable(1)
	return answer[0].encode() # The first report is the runs


#@app.route('/campaigns', methods=['POST'])
@app.route('/campaigns_chunk/<start_record>/<chunk_size>', methods=['GET', 'POST'])
def campaigns_chunk(start_record, chunk_size):
	data = request.json
	#{'image': False, 'external_text': False, 'internal_video': False, 'external_video': False, 'simple': False, 'original_date_before': False, 'original_date_after': False}
	answer = Campaign.Campaign.getRecordsHTMLTable(1, image=data['image'], external_text=data['external_text'], 
		internal_video=data['internal_video'], external_video=data['external_video'], 
		simple=data['simple'], original_date_before=data['original_date_before'],
		original_date_after=data['original_date_after'], linkedin=data['linkedin'], tiktok=data['tiktok'], 
		youtube=data['youtube'], languages=data['languages'], startRecord=int(start_record), 
		endRecord=int(start_record)+int(chunk_size))
	
	#answer = Campaign.Campaign.getRecordsHTMLTable(1)
	return answer[0].encode() # The first report is the runs

@app.route('/delete_campaign/<user_id>/<campaign_id>')
def delete_campaign(user_id, campaign_id):
	Campaign.Campaign.deleteRecord(user_id, campaign_id)
	return '<html><head><script>window.location.href="/campaign";</script></head><body>Redirecting...</body></html>'

@app.route('/delete_run_videos/<run_id>')
def delete_run_videos(run_id):
	# The logic here is that a run can only have one video
	# So if you delete all of these entries, you should be good.
	try:
		print ('deleting')
		Artifact.Artifact.delete_run_videos(run_id)
		return "OK", 200
	except Exception as e:
		print (e)
		return "Error", 400

@app.route('/edit/<user_id>/<entry_id>')
def edit(user_id, entry_id):
	entry = Run.Run.getRecord(user_id, entry_id)
	html = head()
	html += '\n\n<body>\n\n'
	html += menu()
	html += "<script>function submitChanges(user_id, id) {"
	html += "\n language = document.getElementById('language').value;"
	html += "\n payload = JSON.stringify({" 
	html += "\n  user_id: user_id, "
	html += "\n      id: id,"
	html += "\n      language: language,"
	html += "\n        });"
	html += "\n  fetch('/submit', {"
	html += "\n    method: 'POST',"
	html += "\n    body: payload,"
	html += "\n    headers: {'Content-type': 'application/json; charset=UTF-8', }"
	html += "\n  })"
	html += "\n  .then(function(response){"
	html += "\n         //alert (response.text());"
	html += "\n        if(response.text())"
	html += "\n		window.location='/';"
	html += "\n		else alert('error');})"
	html += "\n  .then(function(data)"
	html += "\n    {console.log(data);"
	html += "\n    }).catch(error => console.error('Error:', error))"; 
	html += "\n }</script>"
	html += "\n<table border='0'>"
	html += '\n   <tr><td>ID</td><td>%s</td></tr>' % entry[0]
	html += '\n   <tr><td>Description</td><td>%s</td></tr>' % entry[2]
	html += '\n   <tr><td>Language</td><td><input type="text" id="language" maxlength="2" size="1" value="%s"/></td></tr>' % entry[10]
	html += '\n   <tr><td>Text</td><td>%s</td></tr>' % entry[4]
	html += '\n\  <tr><td><button onclick="submitChanges(\'%s\',\'%s\');" style="color:black;">Submit</button></td></tr>' % (user_id, entry_id)
	html += "\n</table>"
	html += '\n</body></html>'
	return html


@app.route('/edit_campaign/<user_id>/<campaign_id>')
def edit_campaign(user_id, campaign_id):
	#entry = Campaign..getRecord(user_id, campaign_id)
	html = head()
	try:
		if int(campaign_id) > -1:
			#html += '\n\n<body onload="load(\'/runs_campaign/%s\')">\n\n' % campaign_id
			html += '\n\n<body onload="load_runs(\'/runs_campaign_chunk/%s/0/50\')">\n\n' % campaign_id
		else:
			#html += '\n\n<body onload="load(\'/runs_simple\')">\n\n'
			html += '\n\n<body onload="load_runs(\'/runs_simple_chunk/0/50\')">\n\n'
	except Exception:
		html += '\n\n<body onload="load(\'/runs_simple\')">\n\n'
	

	html += menu()
	html += "<script>function submitChanges() {"
	html += "\n var title = document.getElementById('title').value;"
	html += "\nvar runs = document.getElementsByClassName('run_check');"
	html += "\nvar selected_runs = [];"
	html += "\nfor (var i = 0; i < runs.length; i++){"
	html += "\n  if (runs[i].checked) selected_runs.push(runs[i].value);"
	html += "\n}"
	html += "\n payload = JSON.stringify({" 
	html += "\n  user_id: %s, " % user_id
	html += "\n      campaign_id: document.getElementById('id').value,"
	html += "\n      title: title,"
	html += "\n      description: document.getElementById('description').value,"
	html += "\n      location: document.getElementById('location').value,"
	html += "\n      runs: selected_runs,"
	html += "\n        });"
	html += "\n  fetch('/submit_campaign', {"
	html += "\n    method: 'POST',"
	html += "\n    body: payload,"
	html += "\n    headers: {'Content-type': 'application/json; charset=UTF-8', }"
	html += "\n  })"
	html += "\n  .then(function(response){"
	html += "\n         //alert (response.text());"
	html += "\n        if(response.text())"
	html += "\n		window.location='/campaign';"
	html += "\n		else alert('error');})"
	html += "\n  .then(function(data)"
	html += "\n    {console.log(data);"
	html += "\n    }).catch(error => console.error('Error:', error))"
	html += "\n }\n"
	html += "\n</script>"

	html += "\n<table border='0'>"
	html += '\n  <tr><td>'
	html += '\n   <table border="0">'
	thisCampaign = Campaign.Campaign.getRecord(user_id, campaign_id)
	if thisCampaign:
		html += '\n    <tr><td align="left"><h4>ID</h4></td><td align="left"><input value="%s" style="disabled: true;" type="text" id="id" maxlength="255" size="16" readonly></td></tr>' % thisCampaign[0]
		html += '\n    <tr><td align="left"><h4>Title</h4></td><td align="left"><input value="%s" type="text" id="title" maxlength="255" size="84"></td></tr>' % thisCampaign[1]
		html += '\n    <tr><td align="left"><h4>Description</h4></td><td align="left"><textarea id="description" cols="80" rows="5" maxlength="2048">%s</textarea></td></tr>' % thisCampaign[2]
		html += '\n    <tr><td align="left"><h4>Location</h4></td><td align="left"><input value="%s" type="text" id="location" maxlength="255" size="84"></td></tr>' % thisCampaign[3]
	else:
		html += '\n    <tr><td align="left"><h4>ID</h4></td><td align="left"><input style="disabled: true;" type="text" id="id" maxlength="255" size="16" readonly></td></tr>'
		html += '\n    <tr><td align="left"><h4>Title</h4></td><td align="left"><input type="text" id="title" maxlength="255" size="84"></td></tr>'
		html += '\n    <tr><td align="left"><h4>Description</h4></td><td align="left"><textarea id="description" cols="80" rows="5" maxlength="2048"></textarea></td></tr>'	
		html += '\n    <tr><td align="left"><h4>Location</h4></td><td align="left"><input type="text" id="location" maxlength="255" size="84"></td></tr>'
	html += '\n   </tr></table>'
	html += '\n  </td><td valign="top"> &nbsp; &nbsp;</td><td valign="top">'
	
	campaigns = Campaign.Campaign.getRecords(user_id)
	# We need fields 0 to be in alphabetical order, but we also need field 1
	# OrderedDict should be ideal for such a task
	dict = OrderedDict()
	for campaign in campaigns:
		dict[campaign[1]] = campaign[0]

	if None in dict.keys():
		dict.pop(None)

	keys = sorted(dict.keys())

	'''html += '\n   <h4>Sub-campaigns</h4>'
	html += '\n     <select id="" multiple size="4">'        
	for key in keys:
		if not dict[key] == campaign_id:
			html += '\n      <option value="%s">%s</option>' % (dict[key], key)
	html += '\n     </select>' '''

	html += '\n   <h4>Select a campaign to edit</h4>'
	html += '\n     <select id="campaign_selection" multiple size="6">'        
	for key in keys:
		if not dict[key] == campaign_id:
			html += '\n      <option value="%s">%s</option>' % (dict[key], key)
	html += '\n     </select>'

	# We shouldn't allow inserting new Artefacts if an ID wasn't attributed
	if int(campaign_id) > -1:
		html += Artifact.Artifact.getExistingArtifactsTable()

	html += '\n </tr>'
	html += "\n</table>"

	commitWord = 'Add'
	try:
		if int(campaign_id) > -1:
			commitWord = 'Update'
	except Exception:
		pass

	html += "\n<table border='0'><tr><td><button id='submit' onclick='submitChanges();' style='background-color: black;'>" + commitWord + "</button></td><td><button onclick='window.location=\'/campaign\'' style='background-color:black;'>Cancel</button></td><td width='80%'></td></tr></table>"
	
	# On double click on a campaign to edit ==> populate the menu with the right info
	html += '\n<script>\ndocument.getElementById("campaign_selection").ondblclick = async function(){'
	html += '\n  let runs; const result = await fetch("/get_campaign_runs/" + this.value);'
	html += '\n  runs = await result.json();'
	html += '\n  let campaign; const result_campaign = await fetch("/get_campaign/%s/" + this.value);' % user_id
	html += '\n  campaign = await result_campaign.json();'
	html += '\n  console.log(campaign);'
	html += '\n  for (var i=0; i < runs.length; i++){'
	html += '\n     try { var checkbox = document.getElementById(runs[i][0]); checkbox.checked = true; }'
	html += '\n     catch(e) { console.log(e);}'
	html += '\n  }'
	html += '\n document.getElementById("id").value = campaign["campaign"];'
	html += '\n document.getElementById("title").value = campaign["title"];'
	html += '\n document.getElementById("description").value = campaign["description"];'
	html += '\n document.getElementById("location").value = campaign["location"];'
	html += '\n document.getElementById("submit").innerHTML = "Update"'
	html += '\n    return runs;'
	html += '\n}\n</script>'
	html += main()
	#html += '\n</body></html>'
	return html

def filters(url, graphDirs=[], runs_or_campaigns='runs'):
	html 	= '<table border="0" width="100%">'
	html += '<tr>'
	html += '\n  <td valign="top"><h3>Filters</h3><button onclick="filter(\'%s\', \'%s\')" style="background:black;">Submit</button></td>' % (url, runs_or_campaigns)
	html += '\n  <td valign="top"><h4>Types<br>'
	html += '\n    <input type="checkbox" id="image" name="image" value="image"><label for="image">Images<br>'
	html += '\n    <input type="checkbox" id="article" name="article" value="article"><label for="article">Articles<br>'
	html += '\n    <input type="checkbox" id="ivideos" name="ivideos" value="ivideos"><label for="ivideos">Internal videos<br>'
	html += '\n    <input type="checkbox" id="xvideos" name="xvideos" value="xvideos"><label for="xvideos">External videos<br>'
	html += '\n    <input type="checkbox" id="simple" name="simple" value="simple"><label for="simple">Simple posts<br>'
	html += '\n  </h4></td>'
	html += '\n  <td valign="top"><h4>Publication date<br>'
	html += '\n    Start date: <input type="date" id="pub_start"><br>'
	html += '\n    End date: <input type="date" id="pub_end"><br>'
	html += '\n  </h4></td>'
	html += '\n  <td valign="top"><h4>Media<br>'
	html += '\n    <input type="checkbox" id="linkedin" name="linkedin" value="linkedin"><label for="linkedin">LinkedIn<br>'
	html += '\n    <input type="checkbox" id="tiktok" name="tiktok" value="tiktok"><label for="tiktok">TikTok<br>'	
	html += '\n    <input type="checkbox" id="youtube" name="youtube" value="youtube"><label for="youtube">YouTube<br>'	
	html += '\n  </h4></td>'
	languages = Run.Run.getLanguages()
	maxRows = 5
	colNum = math.ceil(len(languages)/maxRows)
	cols = []
	front_index = maxRows
	end_index = 0
	for i in range(0, colNum):
		cols.append(languages[end_index:front_index-1])
		end_index = front_index
		front_index += maxRows
		if front_index > len(languages):
			front_index = len(languages)
	html += '\n  <td align="center" valign="top"><h4>Languages<br>'
	html += '\n    <table border="0"><tr>'
	for col in cols:
		html += '\n      <td>'
		for lang in col:
			html += '\n          <input type="checkbox" id="%s" name="language" value="%s"><label for="%s">%s<br>' % (lang[0], lang[0], lang[0], lang[0])
		html += '\n      </td>'
	html += '\n    </tr></table>'
	html += '\n  </h4></td>'
	html += '\n  <td width="40%">'
	titles = ['<b>Languages</b>', '<b>Media</b>']
	index = 0
	for graph in graphDirs:
		fig = px.pie(names=graph.keys(), values=graph.values(), title=titles[index])
		fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
		fig.update_layout(font=dict(size=45, family="Arial Black"))
		stream = BytesIO()
		fig.write_image(stream, format='svg')
		stream.seek(0)
		data = stream.getvalue().decode()
		html += '\n   %s' % data 
		index += 1
	html += '\n  &nbsp;</td>'
	html += '\n</tr>'
	html += '</table>'
	return html

@app.route('/generate_graph', methods=['GET'])
def generate_graph():
	labels = []
	values = []
	for arg in request.args:
		labels.append(arg)
		values.append(int(request.args.get(arg)))
	#labels = ['English', 'French', 'Chinese']
	#values = [50, 30, 20]
	fig = px.pie(names=labels, values=values)
	fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
	stream = BytesIO()
	fig.write_image(stream, format='svg')
	stream.seek(0)
	data = stream.getvalue().decode()
	return data

@app.route('/get_campaign/<user_id>/<campaign_id>')
def get_campaign(user_id, campaign_id):
	data = Campaign.Campaign.getRecord(user_id, campaign_id)
	dict = {}
	dict['campaign'] = data[0]
	dict['title'] = data[1]
	dict['description'] = data[2]
	dict['location'] = data[3]
	return dict

@app.route('/get_campaign_runs/<campaign_id>')
def get_campaign_runs(campaign_id):
	return Campaign.Campaign.getRuns(campaign_id)

@app.route('/get_run_videos/<run_id>')
def get_run_videos(run_id):
	# The logic here is that a run can only have one video
	# So if you delete all of these entries, you should be good.
	try:
		run = str(Artifact.Artifact.get_run_videos(run_id))
		return run, 200
	except Exception as e:
		print (e)
		return "Error", 400

@app.route('/get_total_campaigns', methods=['GET', 'POST'])
def get_total_campaigns():
	return str(len(Campaign.Campaign.getRecords(1)))

@app.route('/get_total_hashes', methods=['POST'])
def get_total_hashes():
	print ('in get_total_hashes')
	data = request.json
	myDict = Run.Run.getHashesDict(1, image=data['image'], external_text=data['external_text'], 
		internal_video=data['internal_video'], external_video=data['external_video'], 
		simple=data['simple'], original_date_before=data['original_date_before'],
		original_date_after=data['original_date_after'], linkedin=data['linkedin'], tiktok=data['tiktok'], youtube=data['youtube'])	
	print (len(myDict))
	return str(len(myDict)) # The second report is the hashes

@app.route('/get_total_runs', methods=['GET', 'POST'])
def get_total_runs():
	return str(len(Run.Run.getRecords(1)))

@app.route('/hashes', methods=['POST'])
def hashes():
	data = request.json
	#{'image': False, 'external_text': False, 'internal_video': False, 'external_video': False, 'simple': False, 'original_date_before': False, 'original_date_after': False}	print ("get_total_campaigns: %s" % len(Campaign.Campaign.getRecords(1)))
	answer = Run.Run.getRecordsHTMLTable(1, image=data['image'], external_text=data['external_text'], 
		internal_video=data['internal_video'], external_video=data['external_video'], 
		simple=data['simple'], original_date_before=data['original_date_before'],
		original_date_after=data['original_date_after'], linkedin=data['linkedin'], tiktok=data['tiktok'], youtube=data['youtube'])
	return answer[1].encode() # The second report is the hashes

# This downloads runs by chunks
@app.route('/hashes_chunk/<start_record>/<chunk_size>', methods=['POST'])
def hashes_chunk(start_record, chunk_size):
	data = request.json
	#{'image': False, 'external_text': False, 'internal_video': False, 'external_video': False, 'simple': False, 'original_date_before': False, 'original_date_after': False}
	answer = Run.Run.getHashesHtml(1, image=data['image'], external_text=data['external_text'], 
		internal_video=data['internal_video'], external_video=data['external_video'], 
		simple=data['simple'], original_date_before=data['original_date_before'],
		original_date_after=data['original_date_after'], linkedin=data['linkedin'], tiktok=data['tiktok'],
		youtube=data['youtube'], languages=data['languages'], startRecord=int(start_record), 
		endRecord=int(start_record)+int(chunk_size))
	return answer


@app.route('/hash')
def hash():
	html = head()
	html += '\n\n<body onload="filter(\'/hashes_chunk/0/50\', \'hashes\')">\n\n'
	html += menu()
	html += filters('/hashes_chunk/0/50, \'hashes\'', runs_or_campaigns='hashes')
	html += main()
	return html

def head():
	html = '<html>'
	html += '\n<head>\n  <link rel="stylesheet" href="/static/sortable-table.css">\n  <script src="/static/sortable-table.js"></script>'
	html += '\n  <script src="/static/filter.js"></script><script src="/static/utilities.js"></script>'
	html += '\n  <style>button { padding: 4px; margin: 1px; font-size: 100%; font-weight: bold; color: white; background: transparent; border: none; width: 100%; text-align: left; outline: none; cursor: pointer;}</style>'
	html += '\n  <style type="text/css"> svg {width: 200; height: auto;} .centerDiv { position: fixed; width:500px; height: 500px; margin: 0 auto; top:50%, left: 50%, transform: translate(-50%,-50%); z-index:10; visibility: hidden; background-color:blue; } </style> '
	html += '\n</head>'
	return html

@app.route('/import')
def importFunction():
	html = head()
	html += '\n\n<body>\n\n'
	html += menu()
	html += "<script>function submitFile(media) {"
	html += "\n var file = document.getElementById(media);"
	html += "\n var data = new FormData();"
	html += "\n data.append('file', file.files[0])"
	html += "\n data.append('user', %s)" % 1
	html += "\n document.getElementById('linkedin').disabled=true;"	
	html += "\n document.getElementById('tiktok').disabled=true;"
	html += "\n document.getElementById('youtube').disabled=true;"
	html += "\n document.getElementById('LI').style.visibility='hidden';"
	html += "\n document.getElementById('TT').style.visibility='hidden';"
	html += "\n document.getElementById('YT').style.visibility='hidden';"
	html += "\n fetch('/upload/' + media, { method:'POST', body: data }).then( response => {if (response.url.endsWith('import') || response.url.endsWith('import/')) alert('Upload FAILED'); else alert('Upload succeeded!');window.location.href=response.url;} );"
	
	html += "\n }</script>"

	html += '\n<h2>Import data points</h2>'
	html += '\n<h4><table border="0">'
	html += '\n  <tr><td>LinkedIn</td><td><input file type="file" id="linkedin"></td><td><button onclick="submitFile(\'linkedin\')" id="LI" style="color:black;">Upload</button></td></tr>'
	html += '\n  <tr><td>TikTok</td><td><input file type="file" id="tiktok"></td><td><button onclick="submitFile(\'tiktok\')" id="TT" style="color:black;">Upload</button></td></tr>'
	html += '\n  <tr><td>YouTube</td><td><input file type="file" id="youtube"></td><td><button onclick="submitFile(\'youtube\')" id="YT" style="color:black;">Upload</button></td></tr>'
	html += '\n</table></h4>'
	html += "\n</body></html>"
	return html

@app.route('/')
def index():
	html = head()
	html += '\n\n<body onload="filter(\'/runs_chunk/0/50\', \'runs\')">\n\n'
	html += menu()
	#graphDirs = [{'English':50, 'French':30, 'Chinese':20}]
	graphDirs = Run.Run.getGraphDirs()
	html += filters('/runs_chunk/0/50', graphDirs, runs_or_campaigns='runs')
	html += main()
	return html

def main():
	html = '\n<main>'
	html += '\n<div id="main"></div>'

	html += '\n</main>'
	html += '</body>'
	html += '</html>'
	return html

def menu():
	html = '<table border="0" width="100%" style="background-color: #000000">'
	html += '<tr>'
	html += '\n  <td width="25%"><h2 style="color: white;">Social Media Tracker</h2></td>'
	html += '\n  <td><button onclick="window.location.href=\'/\';"><h3 style="color:white; background: transparent; border: none;">Runs</h3></button></td>'
	html += '\n  <td><button onclick="window.location.href=\'/hash\';"><h3 style="color:white; background: transparent;">Hashes</h3></button></td>'
	html += '\n  <td><button onclick="window.location.href=\'/campaign\';"><h3 style="color:white; background: transparent;">Campaign</h3></button></td>'
	html += '\n  <td><button onclick="window.location.href=\'/reruns\';"><h3 style="color:white; background: transparent;">Reruns</h3></button></td>'
	html += '\n  <td><button onclick="window.location.href=\'/import\';"><h3 style="color:white; background: transparent;">Import</h3></button></td>'
	html += '\n  <td width="75%">&nbsp;</td>'
	html += '\n</tr>'
	html += '</table>'
	return html

@app.route('/reruns')
def reruns():
	html = head()
	html += '\n\n<body>\n\n'
	html += menu()
	html += Campaign.Campaign.getRerunRecommendationsHTML(1)
	html += '</body></html>'
	return html


@app.route('/runs', methods=['POST'])
def runs():
	data = request.json
	#{'image': False, 'external_text': False, 'internal_video': False, 'external_video': False, 'simple': False, 'original_date_before': False, 'original_date_after': False}
	answer = Run.Run.getRecordsHTMLTable(1, image=data['image'], external_text=data['external_text'], 
		internal_video=data['internal_video'], external_video=data['external_video'], 
		simple=data['simple'], original_date_before=data['original_date_before'],
		original_date_after=data['original_date_after'], linkedin=data['linkedin'], tiktok=data['tiktok'],
		youtube=data['youtube'], languages=data['languages'])
	return answer[0].encode() # The first report is the runs

# This downloads runs by chunks
@app.route('/runs_chunk/<start_record>/<chunk_size>', methods=['POST'])
def runs_chunk(start_record, chunk_size):
	data = request.json
	#{'image': False, 'external_text': False, 'internal_video': False, 'external_video': False, 'simple': False, 'original_date_before': False, 'original_date_after': False}
	answer = Run.Run.getRecordsHTMLTable(1, image=data['image'], external_text=data['external_text'], 
		internal_video=data['internal_video'], external_video=data['external_video'], 
		simple=data['simple'], original_date_before=data['original_date_before'],
		original_date_after=data['original_date_after'], linkedin=data['linkedin'], tiktok=data['tiktok'],
		youtube=data['youtube'], languages=data['languages'], startRecord=int(start_record), 
		endRecord=int(start_record)+int(chunk_size))
	return answer[0].encode() # The first report is the runs

@app.route('/runs_campaign/<campaign_id>', methods=['POST'])
def runs_campaign(campaign_id):
	answer = Run.Run.getRecordsHTMLTable(1, checks=True, campaign=campaign_id)
	return answer[0].encode() # The first report is the runs

# This version will only download a chunk of runs
@app.route('/runs_campaign_chunk/<campaign_id>/<start_index>/<chunk_size>', methods=['POST'])
def runs_campaign_chunk(campaign_id, start_index, chunk_size):
	answer = Run.Run.getRecordsHTMLTable(1, checks=True, campaign=campaign_id, startRecord=int(start_index), endRecord=int(start_index) + int(chunk_size))
	return answer[0].encode() # The first report is the runs

@app.route('/runs_simple', methods=['POST'])
def runs_simple():
	answer = Run.Run.getRecordsHTMLTable(1, checks=True)
	return answer[0].encode() # The first report is the runs

# This version will only download a chunk of runs
@app.route('/runs_simple_chunk/<start_record>/<chunk_size>', methods=['POST'])
def runs_simple_chunk(start_record, chunk_size):
	answer = Run.Run.getRecordsHTMLTable(1, checks=True, startRecord=int(start_record), 
		endRecord=int(start_record)+int(chunk_size))
	return answer[0].encode() # The first report is the runs

@app.route('/submit', methods=['POST'])
def submit():
	data = request.json
	status = Run.Run.update(data['user_id'], data['id'], data['language'])
	return 'Status: %s' % status

@app.route('/submit_campaign', methods=['POST'])
def submit_campaign():
	data = request.json
	status = None
	try:
		intId = int(data['campaign_id'])
		# If we make it here we have already an ID, no need to add
		status = Campaign.Campaign.update(data['campaign_id'], title=data['title'], description=data['description'], location=data['location'], runs=data['runs'])
	except Exception:
		status = Campaign.Campaign.add(data['user_id'], title=data['title'], description=data['description'], location=data['location'], runs=data['runs'])

	return 'Status: %s' % status

@app.route('/update_artefact', methods=['POST'])
def update_artefact():
	data = request.json
	print (data)
	try:
		video_id = Artifact.Artifact.addArtifact(data['id'], data['campaign'], data['language'], data['format'], data['seconds'], data['date'])
	except Exception as e:
		print (e)
		return "ERROR", 400
	return str(video_id), 200

@app.route('/upload/<media>', methods=['POST', 'GET'])
def upload_file(media):
	print ('upload %s' % media)
	print (request.method)
	if request.method == 'POST':
		print ('request data is')
		print (request.data)
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		print ('file is')
		print (file)
		# If the user does not select a file, the browser submits an
		# empty file without a filename.
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename, media):
			print ('allowed file')
			filename = secure_filename(file.filename)
			print ('filename: %s' % filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			print ('file save ok')
			try:
				if media == 'linkedin':
					print ('calling add_linkedIn')
					Importing.add_linkedIn(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				elif media == 'tiktok':
					Importing.add_tiktok(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				elif media == 'youtube':
					print ('in youtube')
					Importing.add_youtube(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				flash ('upload successful')
				return redirect('/')
			except Exception as e:
				print (e)
				flash('Upload failed')
				return redirect('/import')
			'''try:
				Importing.add_linkedIn(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			except Exception as e:
				print (e)'''
	return "ERROR"

# main driver function
if __name__ == '__main__':
	# run() method of Flask class runs the application
	# on the local development server.
	app.run()
