import sqlite3

DB_LOCATION = 'db/scripts_db'

def run_query(statement):
	db = sqlite3.connect(DB_LOCATION)
	try:
		cursor = db.cursor()
		cursor.execute(statement)
		result_id = cursor.lastrowid
		db.commit()
	except Exception as e:
		print statement
		raise e
	finally:
		db.close()
	return result_id 

def create_tables():
	db = sqlite3.connect(DB_LOCATION)
	try:
		cursor = db.cursor()
		cursor.execute("PRAGMA foreign_keys = ON")
		
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS 
				episode(ep_id INTEGER PRIMARY KEY NOT NULL, title TEXT,
						 code TEXT, season TEXT, episode TEXT, authors TEXT,
						 seinology_ref TEXT, air_date DATE, director TEXT)'''
		)
		print 'created episode table'

		cursor.execute('''
			CREATE TABLE IF NOT EXISTS
				character(char_id INTEGER PRIMARY KEY NOT NULL, first_name TEXT,
					last_name TEXT, actor_first_name TEXT, actor_last_name TEXT,					title TEXT, special_name TEXT
						   )'''
		)
		print 'created character table'

		cursor.execute('''
			CREATE TABLE IF NOT EXISTS
				character_episode_join(char_id NUMBER NOT NULL,
										 ep_id NUMBER NOT NULL)'''
		)
		print 'created character, episode join table'

		cursor.execute('''
			CREATE TABLE IF NOT EXISTS
				line(line_id INTEGER PRIMARY KEY NOT NULL, text TEXT,
					raw_text TEXT, episode_id INTEGER, line_order INTEGER,
					type TEXT, special TEXT,
					FOREIGN KEY(episode_id) REFERENCES episode(ep_id))'''
		)
		print 'created spoken line table'

		cursor.execute('''
			CREATE TABLE IF NOT EXISTS
				character_spoken_line_join(char_id NUMBER NOT NULL,
					spoken_id NOT NULL)'''
		)
		print 'created character, spoken lines join table'
		db.commit()
	except Exception as e:
		raise e
	finally:
		db.close()

	return True

def insert(**kwargs):
	table = kwargs.get('table')
	if not table:
		raise Exception('Please provide a table')
	del kwargs['table']
	items = map(lambda t: (str(t[0]), str(t[1])), kwargs.items())
	table_statement = '{}({})'.format(table, ', '.join(['"' + key + '"' for key, val in items]))
	value_statement = ", ".join(['"' + val + '"' for key, val in items])
	query = "INSERT INTO {} VALUES({})".format(table_statement, value_statement)
	result = run_query(query)
	print 'inserted into table:', table
	kwargs['id'] = result
	return kwargs

def lookup(**kwargs):
	table = kwargs.get('table')
	if not table:
		raise Exception('Please provide a table')
	del kwargs['table']
	column_string = ', '.join(kwargs['columns'])
	query = ', '.join(["%s='%s'" % (k, v) for k, v in kwargs['query'].items()])
	db = sqlite3.connect(DB_LOCATION)
	results = []
	try:
		c = db.cursor()
		statement = "SELECT {} FROM {} WHERE {}".format(column_string, table, query)
		print statement
		c.execute(statement)
		for result in c:
			results.append({kwargs['columns'][i]: v for i, v in enumerate(result)})
	except Exception as e:
		print statement
		raise e
	finally:
		db.close()
	return results

def drop_table(table_name):
	if not table_name:
		raise Exception('Please provide table name')

	run_query("DROP TABLE {}".format(table_name))
	return True

if __name__ == '__main__':
	create_tables()
