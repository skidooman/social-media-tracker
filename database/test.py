from User import User
from Run import Run
from Data import Data
import sys

def init():
	User.create()
	Run.create()
	Data.create()
	id = User.add('Steve', 'Barriault', 'skidoomaniac@yahoo.com', 'vector123')

	Run.importFile(id, 'linkedin', '2022-10-01', 'LinkedIn_oct22.html.json')


def getRecords(image=None, external_text=None, internal_video=None, external_video=None, simple=None):
	print ("simple: %s" % simple)
	html = Data.getRecordsHTMLTable(1)
	with open('table_data.html', 'w') as reportFile:
		reportFile.write('<html><body>\n\n')
		reportFile.write(html)
		reportFile.write('\n\n</body></html>')

	html = Run.getRecordsHTMLTable(1, image=image, external_text=external_text, internal_video=internal_video, 
		external_video=external_video, simple=simple)
	with open('table.html', 'w') as reportFile:
		reportFile.write('<html><body>\n\n')
		reportFile.write(html)
		reportFile.write('\n\n</body></html>')


if __name__ == "__main__":
	if sys.argv[1] == 'init':
		init()
		getRecords()
	elif sys.argv[1] == 'list':
		getRecords()
	else:
		image = None
		external_text = None
		internal_video = None
		external_video = None
		simple = None
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
		getRecords(image, external_text, internal_video, external_video, simple)
