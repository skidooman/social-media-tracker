from collections import OrderedDict
import csv, datetime, math

def buildDatabase(filename):
	overall_database = []
	with open(filename, 'r') as csvFile:
		counter = 0
		entries = csv.reader(csvFile)
		for entry in entries:
			database = {}
			if counter < 2:
				counter += 1
				continue
			try:
				# id
				database['id'] = entry[0]
			except Exception:
				break
			
			# Text
			database['text'] = entry[1]

			# Date
			try:
				database['date'] = datetime.datetime.strptime(entry[2], "%b %d, %Y").strftime("%Y-%m-%d")
			except Exception:
				print ("Date is absent from %s, date will be today" % entry)
				database['date'] = datetime.datetime.now().strftime("%Y-%m-%d")
			
			# Views
			database['views'] = entry[6]

			# Time
			myTime = 0
			try:
				myTime = float(entry[4])
			except Exception:
				pass
			minutes = myTime*600
			database['minutes'] = minutes

			# Displays
			try:
				database['displays'] = int(entry[3])
			except Exception as e:
				database['displays'] = 0
			print ('append %s' % database)
			overall_database.append(database)

		return overall_database

def saveJSON(database, filename):
	with open(filename, 'w') as file:
		file.write('[')
		counter = 0
		for entry in database:
			file.write('\t\t{"id":"' +  entry['id'] + '",')
			file.write('"date":"' + entry['date'] + '",')
			file.write('"views":"%s",' % entry['views'])
			file.write('"text-link":"",')
			file.write('"internal_video":"false",')
			file.write('"video-link":"",')
			file.write('"text":"%s",' % entry['text'].replace('"', '\''))
			file.write('"comments":"0", "likes":"0", "reposts":"0",')
			file.write('"displays":"%s", ' % entry['displays'])
			file.write('"minutes":"%s"' % round(entry['minutes']))
			if counter == len(database)-1:
				file.write('}\n')
			else:
				file.write('},\n')
			counter += 1
		file.write(']')

#database = buildDatabase('table_data_setp2023.csv')
#saveJSON(database, 'LinkedIn_oct22.html.json')
