from User import User
from Run import Run
from Data import Data
from Campaign import Campaign
from Artifact import Artifact
import sys, os, time
from linkedin_analysis import buildDatabase as LI_Database
from linkedin_analysis import saveJSON as LI_save_json
from youtube_analysis import buildDatabase as YT_Database
from youtube_analysis import saveJSON as YT_save_json

def add_linkedIn(filename):
	database = LI_Database(filename)
	LI_save_json(database, '%s.json' % filename)
	if filename.endswith('march23.html'):
		Run.importFile(1, 'linkedin', '2023-03-31', "%s.json" % filename)
	else:
		myTime = os.path.getmtime(filename)
		timestamp = time.strftime("%Y-%m-%d", time.strptime(time.ctime(myTime)))
		print ("TIMESTAMP: %s" % timestamp)
		Run.importFile(1, 'linkedin', timestamp, "%s.json" % filename) 

def add_youtube(filename):
	database = YT_Database(filename)
	print (database)
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
	Artifact.create()
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


if __name__ == "__main__":
	if sys.argv[1] == 'init':
		init()
		getRecords()
	elif sys.argv[1] == 'reruns':
		Campaign.getRerunRecommendations(1)
	elif sys.argv[1] == 'add_LI':
		add_linkedIn(sys.argv[2])
	elif sys.argv[1] == 'add_YT':
		add_youtube(sys.argv[2])
	elif sys.argv[1] == 'list':
		getRecords()
	else:
		image = None
		external_text = None
		internal_video = None
		external_video = None
		simple = None
		original_date_before = None
		original_date_after = None
		for i in range(0, len(sys.argv)):
			print (sys.argv[i])
			if sys.argv[i] == 'image':
				image = True
			elif sys.argv[i] == 'external_video':
				external_video = True
			elif sys.argv[i] == 'internal_video':
				internal_video = True
			elif sys.argv[i] == 'external_text':
				external_text = True
			elif sys.argv[i] == 'simple':
				simple = True
			elif sys.argv[i].startswith('original_date_before='):
				print ("TRIGGER")
				original_date_before = sys.argv[i].split('=')[1]
			elif sys.argv[i].startswith('original_date_after='):
				original_date_after = sys.argv[i].split('=')[1]
		getRecords(image, external_text, internal_video, external_video, simple, original_date_before, original_date_after)

