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

