import os, sys, math
from flask import Flask, render_template, Response, request

sys.path.append(os.getcwd() + '/database')
from database import Run 

# For snapping, we may need to include the path to templates
templates_dir = 'templates'
static_dir = 'static'
app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)

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
	html += '\n\  <tr><td><button onclick="submitChanges(\'%s\',\'%s\');" style="color:black;">Submit</button></td></tr>' % (user_id, entry_id)
	html += "\n</table>"
	html += '\n</body></html>'
	return html


def filters(url):
	html = '<table border="0" width="100%">'
	html += '<tr>'
	html += '\n  <td valign="top"><h3>Filters</h3><button onclick="filter(\'%s\')" style="background:black;">Submit</button></td>' % url
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
	html += '\n  <td width="40%">&nbsp;</td>'
	html += '\n</tr>'
	html += '</table>'
	return html

@app.route('/hashes', methods=['POST'])
def hashes():
	data = request.json
	#{'image': False, 'external_text': False, 'internal_video': False, 'external_video': False, 'simple': False, 'original_date_before': False, 'original_date_after': False}
	answer = Run.Run.getRecordsHTMLTable(1, image=data['image'], external_text=data['external_text'], 
		internal_video=data['internal_video'], external_video=data['external_video'], 
		simple=data['simple'], original_date_before=data['original_date_before'],
		original_date_after=data['original_date_after'], linkedin=data['linkedin'], youtube=data['youtube'])
	return answer[1].encode() # The second report is the hashes

@app.route('/hash')
def hash():
	html = head()
	html += '\n\n<body onload="filter(\'/hashes\')">\n\n'
	html += menu()
	html += filters('/hashes')
	html += main()
	return html

def head():
	html = '<html>'
	html += '\n<head>\n  <link rel="stylesheet" href="static/sortable-table.css">\n  <script src="static/sortable-table.js"></script>'
	html += '\n  <script src="static/filter.js"></script><script src="static/utilities.js"></script>'
	html += '\n  <style>button { padding: 4px; margin: 1px; font-size: 100%; font-weight: bold; color: white; background: transparent; border: none; width: 100%; text-align: left; outline: none; cursor: pointer;}</style>'
	html += '\n</head>'
	return html

@app.route('/import')
def importFunction():
	html = head()
	html += '\n\n<body>\n\n'
	html += menu()
	html += '\n<h2>Import data points</h2>'
	html += '\n<h4><table border="0">'
	html += '\n  <tr><td>LinkedIn</td><td><input file type="file" id="linkedin"></td><td><button id="LI" style="color:black;">Upload</button></td></tr>'
	html += '\n  <tr><td>YouTube</td><td><input file type="file" id="youtube"></td><td><button id="YT" style="color:black;">Upload</button></td></tr>'
	html += '\n</table></h4>'
	html += "\n</body></html>"
	return html



@app.route('/')
def index():
	html = head()
	html += '\n\n<body onload="filter(\'/runs\')">\n\n'
	html += menu()
	html += filters('/runs')
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
	html += '\n  <td><button onclick="window.location.href=\'/import\';"><h3 style="color:white; background: transparent;">Import</h3></button></td>'
	html += '\n  <td width="75%">&nbsp;</td>'
	html += '\n</tr>'
	html += '</table>'
	return html


@app.route('/runs', methods=['POST'])
def runs():
	data = request.json
	#{'image': False, 'external_text': False, 'internal_video': False, 'external_video': False, 'simple': False, 'original_date_before': False, 'original_date_after': False}
	answer = Run.Run.getRecordsHTMLTable(1, image=data['image'], external_text=data['external_text'], 
		internal_video=data['internal_video'], external_video=data['external_video'], 
		simple=data['simple'], original_date_before=data['original_date_before'],
		original_date_after=data['original_date_after'], linkedin=data['linkedin'], youtube=data['youtube'], 
		languages=data['languages'])
	return answer[0].encode() # The first report is the runs

@app.route('/submit', methods=['POST'])
def submit():
	data = request.json
	print ('language: %s' % data['language'])
	status = Run.Run.update(data['user_id'], data['id'], data['language'])
	return 'Status: %s' % status

# main driver function
if __name__ == '__main__':
	# run() method of Flask class runs the application
	# on the local development server.
	app.run()
