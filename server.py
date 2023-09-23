import os, sys
from flask import Flask, render_template, Response, request

sys.path.append(os.getcwd() + '/database')
from database import Run 

# For snapping, we may need to include the path to templates
templates_dir = 'templates'
static_dir = 'static'
app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)


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
	html += '\n  <td width="50%">&nbsp;</td>'
	html += '\n  </h4></td>'
	html += '\n</tr>'
	html += '</table>'
	return html


def menu():
	html = '<table border="0" width="100%" style="background-color: #000000">'
	html += '<tr>'
	html += '\n  <td width="25%"><h2 style="color: white;">Social Media Tracker</h2></td>'
	html += '\n  <td><button><h3 style="color:white; background: transparent; border: none;">Runs</h3></button></td>'
	html += '\n  <td><button><h3 style="color:white; background: transparent;">Hashes</h3></button></td>'
	html += '\n  <td width="75%">&nbsp;</td>'
	html += '\n</tr>'
	html += '</table>'
	return html

@app.route('/')
def index():
	html = '<html>'
	html += '\n<head>\n  <link rel="stylesheet" href="static/sortable-table.css">\n  <script src="static/sortable-table.js"></script>'
	html += '\n  <script src="static/filter.js"></script>'
	html += '\n  <style>button { padding: 4px; margin: 1px; font-size: 100%; font-weight: bold; color: white; background: transparent; border: none; width: 100%; text-align: left; outline: none; cursor: pointer;}</style>'

	html += '\n</head>'
	html += '\n\n<body onload="filter(\'/runs\')">\n\n'
	html += menu()
	html += filters('/runs')
	html += '\n<main>'
	html += '\n<div id="main"></div>'
	html += '\n</main>'
	html += '</body>'
	html += '</html>'
	
	return html

@app.route('/runs', methods=['POST'])
def runs():
	data = request.json
	print (dir(Run.Run))
	#{'image': False, 'external_text': False, 'internal_video': False, 'external_video': False, 'simple': False, 'original_date_before': False, 'original_date_after': False}
	answer = Run.Run.getRecordsHTMLTable(1, image=data['image'], external_text=data['external_text'], 
		internal_video=data['internal_video'], external_video=data['external_video'], 
		simple=data['simple'], original_date_before=data['original_date_before'],
		original_date_after=data['original_date_after'])
	return answer[0].encode()
	
# main driver function
if __name__ == '__main__':
	# run() method of Flask class runs the application
	# on the local development server.
	app.run()
