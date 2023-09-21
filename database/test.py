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


def getRecords(internal_video=None, external_video=None, video=None):
	html = Data.getRecordsHTMLTable(1)
	with open('table_data.html', 'w') as reportFile:
		reportFile.write('<html><body>\n\n')
		reportFile.write(html)
		reportFile.write('\n\n</body></html>')

	html = Run.getRecordsHTMLTable(1, internal_video=internal_video, external_video=external_video, video=video)
	with open('table.html', 'w') as reportFile:
		reportFile.write('<html><body>\n\n')
		reportFile.write(html)
		reportFile.write('\n\n</body></html>')


if __name__ == "__main__":
	if sys.argv[1] == 'init':
		init()
		getRecords()
	elif sys.argv[1] == 'list':
		print ('generating list')
		getRecords()
	elif sys.argv[1] == 'video':
		print ('video')
		getRecords(external_video=True)
