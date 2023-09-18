from User import User
from Run import Run
from Data import Data

User.create()
Run.create()
Data.create()
id = User.add('Steve', 'Barriault', 'skidoomaniac@yahoo.com', 'vector123')

Run.importFile(id, 'linkedin', '2022-10-01', 'LinkedIn_oct22.html.json')

'''records = Data.getRecords(1)
print (records)
print (len(records))
#importJSON(cls, user_id, media, date_str, filename)
'''

html = Data.getRecordsHTMLTable(1)
with open('table_data.html', 'w') as reportFile:
	reportFile.write('<html><body>\n\n')
	reportFile.write(html)
	reportFile.write('\n\n</body></html>')

html = Run.getRecordsHTMLTable(1)
with open('table.html', 'w') as reportFile:
	reportFile.write('<html><body>\n\n')
	reportFile.write(html)
	reportFile.write('\n\n</body></html>')
