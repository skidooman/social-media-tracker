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
			'UNIQUE(run_id, user_id, date))')
		return cls.execute_commands([command])

	@classmethod
	def add(cls, run_id, user_id, date, views, likes, comments, reposts):
		command = ("INSERT INTO data (run_id, user_id, date, views, likes, comments, reposts)"
			"VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')") % (run_id, user_id, date, views, likes, comments, reposts)
		return cls.execute_commands([command])

	@classmethod
	def getRecords(cls, user_id, run_id=None):
		command = "SELECT * FROM data WHERE user_id = %s " % user_id
		if run_id:
			command += ", run_id = %s" % run_id
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
		html += '\n\t\t\t\t<th><button>date</button></th>'
		html += '\n\t\t\t\t<th><button>views</button></th>'
		html += '\n\t\t\t\t<th><button>likes</button></th>'
		html += '\n\t\t\t\t<th><button>comments</button></th>'
		html += '\n\t\t\t\t<th><button>reposts</button></th>'
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
		

