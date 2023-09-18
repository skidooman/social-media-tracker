#!/usr/bin/python
# This is the base class for all our database classes

import psycopg2
from config import config

class Base:
	def execute_commands(commands, fetching=False):
	    """ create tables in the PostgreSQL database"""
	    '''commands = (
	        """
	        CREATE TABLE vendors (
	            vendor_id SERIAL PRIMARY KEY,
	            vendor_name VARCHAR(255) NOT NULL
	        )
	        """,
	        """ CREATE TABLE parts (
	                part_id SERIAL PRIMARY KEY,
	                part_name VARCHAR(255) NOT NULL
	                )
	        """,
	        """
	        CREATE TABLE part_drawings (
	                part_id INTEGER PRIMARY KEY,
	                file_extension VARCHAR(5) NOT NULL,
	                drawing_data BYTEA NOT NULL,
	                FOREIGN KEY (part_id)
	                REFERENCES parts (part_id)
	                ON UPDATE CASCADE ON DELETE CASCADE
	        )
	        """,
	        """
	        CREATE TABLE vendor_parts (
	                vendor_id INTEGER NOT NULL,
	                part_id INTEGER NOT NULL,
	                PRIMARY KEY (vendor_id , part_id),
	                FOREIGN KEY (vendor_id)
	                    REFERENCES vendors (vendor_id)
	                    ON UPDATE CASCADE ON DELETE CASCADE,
	                FOREIGN KEY (part_id)
	                    REFERENCES parts (part_id)
	                    ON UPDATE CASCADE ON DELETE CASCADE
	        )
	        """)'''
	    conn = None
	    try:
	        # read the connection parameters
	        params = config()
	        # connect to the PostgreSQL server
	        conn = psycopg2.connect(**params)
	        print ('conn: %s' % conn)
	        cursor = conn.cursor()
	        print ('cursor: %s' % cursor)
	        # create table one by one
	        for command in commands:
	            print ('executing %s' % command)
	            cursor.execute(command)
	            print ('command successful')
		# close communication with the PostgreSQL database server
	        #returnValue = cursor.fetchone()[0]
	        #print ('returnValue: %s' % returnValue)
	        results = 0
	        if fetching:
	           results = cursor.fetchall()
	        else:
	           # commit the changes
	           conn.commit()
	        print ('committed')
	        
	        conn.close()
	        print ('cursor closed')
	        cursor.close()
	        print ('conn closed')
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

