#!/usr/bin/python
# This class represents Users, a list of users authorized on the system

from Base import Base

class User(Base):

	@classmethod
	def create(cls):
		# Name of table is User_<id>
		command = ('CREATE TABLE users ('
			'id SERIAL PRIMARY KEY,' 
			'first_name VARCHAR(255) NOT NULL,'
			'last_name VARCHAR(255) NOT NULL,'
			'email VARCHAR(255) NOT NULL UNIQUE,'
			'password VARCHAR(16) NOT NULL)')
		cls.execute_commands([command])
		return 'users'

	@classmethod
	def add(cls, firstName, lastName, email, password):
		command = ("INSERT INTO users (first_name, last_name, email, password) "
			"VALUES('%s', '%s', '%s', '%s') RETURNING id") % (firstName, lastName, email, password)
		cls.execute_commands([command])
		return '1'

