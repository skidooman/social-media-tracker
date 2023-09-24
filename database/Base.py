#!/usr/bin/python
# This is the base class for all our database classes

import psycopg2
from config import config
from psycopg2 import sql

class Base:
	def getUniques(column, table):
	    conn = None
	    try:
	        params = config()
	        conn = psycopg2.connect(**params)
	        cursor = conn.cursor()
	        data = cursor.execute(sql.SQL('SELECT DISTINCT {} FROM %s' % table).format(sql.Identifier(column)))
	        results = cursor.fetchall()
	        return results
	    except Exception as error:
	        print ('Could not retrieve uniques: %s' % error)

	def execute_commands(commands, fetching=False):
	    conn = None
	    try:
	        # read the connection parameters
	        params = config()
	        # connect to the PostgreSQL server
	        conn = psycopg2.connect(**params)
	        cursor = conn.cursor()
	        # create table one by one
	        for command in commands:
	            cursor.execute(command)
		# close communication with the PostgreSQL database server
	        #returnValue = cursor.fetchone()[0]
	        #print ('returnValue: %s' % returnValue)
	        results = 0
	        if fetching:
	           results = cursor.fetchall()
	        else:
	           # commit the changes
	           conn.commit()
	        
	        conn.close()
	        cursor.close()
	        #print ('last step' + returnValue)
	        return results
	    except (Exception, psycopg2.DatabaseError) as error:
	        print ('exception on execution')
	        print (error)
	        return 1
	    finally:
	        if conn is not None:
	            conn.close()
	
	def recordExistsIdString(name_table, id):
		conn = None
		try:
			# read the connection parameters
			params = config()
			# connect to the PostgreSQL server
			conn = psycopg2.connect(**params)
			cur = conn.cursor()
			cur.execute('SELECT EXISTS(SELECT 1 FROM %s WHERE id=CAST(%s as VarChar))' % (name_table, id))
			status = cur.fetchone()
			return status[0]

		except (Exception, psycopg2.DatabaseError) as error:
			print ('EEEORR')
			print(error)
		finally:
			if conn is not None:
				conn.close()

