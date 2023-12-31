from User import User
from Run import Run
from Data import Data
from Campaign import Campaign
import sys, os, time
from linkedin_analysis import buildDatabase as LI_Database
from linkedin_analysis import saveJSON as LI_save_json
from tiktok_analysis import augmentDict as TT_Database
from tiktok_analysis import saveJSON as TT_save_json
from youtube_analysis import buildDatabase as YT_Database
from youtube_analysis import saveJSON as YT_save_json

def add_linkedIn(filename):
	print ('in add_linkedIn')
	database = LI_Database(filename)
	print ('database OK')
	LI_save_json(database, '%s.json' % filename)
	print ('json ok')
	if filename.endswith('march23.html'):
		Run.importFile(1, 'linkedin', '2023-03-31', "%s.json" % filename)
	else:
		print ('importing file %s' % filename)
		myTime = os.path.getmtime(filename)
		timestamp = time.strftime("%Y-%m-%d", time.strptime(time.ctime(myTime)))
		print ('running Run.importFile')
		Run.importFile(1, 'linkedin', timestamp, "%s.json" % filename) 

def add_tiktok(filename):
	database = TT_Database(filename)
	print (database)
	TT_save_json(database, '%s.json' % filename)
	myTime = os.path.getmtime(filename)
	timestamp = time.strftime("%Y-%m-%d", time.strptime(time.ctime(myTime)))
	Run.importFile(1, 'tiktok', timestamp, "%s.json" % filename) 

def add_youtube(filename):
	database = YT_Database(filename)
	YT_save_json(database, '%s.json' % filename)
	myTime = os.path.getmtime(filename)
	timestamp = time.strftime("%Y-%m-%d", time.strptime(time.ctime(myTime)))
	Run.importFile(1, 'youtube', timestamp, "%s.json" % filename) 

def init():
	User.create()
	Run.create()
	Data.create()
	id = User.add('Steve', 'Barriault', 'skidoomaniac@yahoo.com', 'vector123')
	Campaign.create()
	#id = Campaign.add(title='test', description='test', location='test', runs=['abcd'])
	#print ('ID: %s' % id)

	#Run.importFile(id, 'linkedin', '2022-10-01', 'LinkedIn_oct22.html.json')


def getRecords(image=None, external_text=None, internal_video=None, external_video=None, simple=None,
		original_date_before=None, original_date_after=None):
	html = Data.getRecordsHTMLTable(1)
	with open('table_data.html', 'w') as reportFile:
		reportFile.write('<html><body>\n\n')
		reportFile.write(html)
		reportFile.write('\n\n</body></html>')

	html, keywordHtml = Run.getRecordsHTMLTable(1, image=image, external_text=external_text, internal_video=internal_video, 
		external_video=external_video, simple=simple, original_date_before=original_date_before, 
		original_date_after=original_date_after)
	with open('table.html', 'w') as reportFile:
		reportFile.write('<html><head><link rel="stylesheet" href="sortable-table.css"><script src="sortable-table.js"></script></head><body>\n\n')
		reportFile.write(html)
		reportFile.write('\n\n</body></html>')

	#print (keywordHtml)
	with open('hashes.html', 'w') as reportFile:
		reportFile.write('<html><head><link rel="stylesheet" href="sortable-table.css"><script src="sortable-table.js"></script></head><body>\n\n')
		reportFile.write(keywordHtml)
		reportFile.write('\n\n\</body></html>')
