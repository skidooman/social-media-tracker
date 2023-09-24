import os, sys, math
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
	html += '\n  </h4></td>'
	html += '\n  <td valign="top"><h4>Media<br>'
	html += '\n    <input type="checkbox" id="linkedin" name="linkedin" value="linkedin"><label for="linkedin">LinkedIn<br>'
	html += '\n    <input type="checkbox" id="youtube" name="youtube" value="youtube"><label for="youtube">YouTube<br>'	
	html += '\n  </h4></td>'
	languages = Run.Run.getLanguages()
	print ('languages: %s' % languages)
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
	print (cols)
	html += '\n  <td align="center" valign="top"><h4>Languages<br>'
	html += '\n    <table border="0"><tr>'
	for col in cols:
		html += '\n      <td>'
		for lang in col:
			html += '\n          <input type="checkbox" id="%s" name="%s" value="%s"><label for="%s">%s<br>' % (lang[0], lang[0], lang[0], lang[0], lang[0])
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
	html += '\n  <script src="static/filter.js"></script>'
	html += '\n  <style>button { padding: 4px; margin: 1px; font-size: 100%; font-weight: bold; color: white; background: transparent; border: none; width: 100%; text-align: left; outline: none; cursor: pointer;}</style>'
	html += '\n</head>'
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
		original_date_after=data['original_date_after'], linkedin=data['linkedin'], youtube=data['youtube'])
	return answer[0].encode() # The first report is the runs
	
# main driver function
if __name__ == '__main__':
	# run() method of Flask class runs the application
	# on the local development server.
	app.run()
