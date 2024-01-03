#!/usr/bin/python
# This class represents Data - results from a Run at a given time

from Base import Base

class Data(Base):

	@classmethod
	def create(cls):
		command = ('CREATE TABLE Data('
			'run_id VARCHAR(255),'
			'user_id INT,'
			'date DATE,'
			'views INT,'
			'likes INT,'
			'comments INT,'
			'reposts INT,'
			'displays INT,'
			'minutes INT,'
			'UNIQUE(run_id, user_id, date))')
		return cls.execute_commands([command])

	@classmethod
	def add(cls, run_id, user_id, date, views, likes, comments, reposts, displays=0, minutes=0):
		command = ("INSERT INTO data (run_id, user_id, date, views, likes, comments, reposts, displays, minutes)"
			"VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')") % (run_id, user_id, date, views, likes, comments, reposts, displays, minutes)
		print ("Adding data point %s - %s" % (run_id, date))
		return cls.execute_commands([command])

	@classmethod
	def getRecords(cls, user_id, run_id=None):
		command = "SELECT * FROM data WHERE user_id = %s " % user_id
		if run_id:
			command += "AND run_id = '%s'" % run_id
		command += ";"
		return cls.execute_commands([command], fetching=True)

	@classmethod
	def getRecordsHTMLTable(cls, user_id, run_id=None):
		records = cls.getRecords(user_id, run_id)
		html = '<div class="table-wrap">\n\t<table class="sortable">'
		html += '\n\t\t<thead>'
		html += '\n\t\t\t<tr>'
		html += ' '
		if not run_id:
			html += '\n\t\t\t\t<th><button>ID</button></th>'
		html += '\n\t\t\t\t<th><button>views</button></th>'
		html += '\n\t\t\t\t<th><button>data</button></th>'
		html += '\n\t\t\t\t<th><button>likes</button></th>'
		html += '\n\t\t\t\t<th><button>comments</button></th>'
		html += '\n\t\t\t\t<th><button>reposts</button></th>'
		html += '\n\t\t\t\t<th><button>displays</button></th>'
		html += '\n\t\t\t\t<th><button>minutes</button></th>'
		html += '\n\t\t\t</tr>'
		html += '\n\t\t</thead>'

		html += '\n\t\t<tbody>'

		maxCol = 5
		if not run_id:
			maxCol += 1
		
		for record in records:
			html += '\n\t\t\t<tr>'
			for col in range(0,maxCol):
				html += '\n\t\t\t\t<td>%s</td>' % record[col]
			html += '\n\t\t\t</tr>'
		
		html += '\n\t\t\t</tr>'
		html += '\n\t\t</tbody>'
		html += '\n\t</table>'
		html += '\n</div>'
		return html

	@classmethod
        #def update(cls, user_id, id, language):
	def update(cls, run_id, user_id, date, views, likes, comments, reposts, displays=0, minutes=0):
                command = "UPDATE Runs SET (views='%s', likes='%s', comments='%s', reposts='%s', displays='%s', minutes='%s') WHERE (user_id='%s' AND run_id='%s' AND date='%s')" % (views, likes, comments, reports, displays, minutes, user_id, run_id, date)
                print ('running %s' % command)
                cls.execute_commands([command], fetching=False)
                return True
		

