import sqlite3

DB_LOCATION = 'db/scripts_db'

def run_query(statement):
	db = sqlite3.connect(DB_LOCATION)
	try:
		cursor = db.cursor()
		cursor.execute(statement)
		db.commit()
	except Exception as e:
		raise e
	finally:
		db.close()
	return True

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
					last_name TEXT, actor_first_name TEXT, actor_last_name TEXT
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
				spoken_line(spoken_id INTEGER PRIMARY KEY NOT NULL,
					text TEXT, episode_id INTEGER, line_order INTEGER,
					FOREIGN KEY(episode_id) REFERENCES episode(ep_id))'''
		)
		print 'created spoken line table'

		cursor.execute('''
			CREATE TABLE IF NOT EXISTS
				character_spoken_line_join(char_id NUMBER NOT NULL,
					spoken_id NOT NULL)'''
		)
		print 'created character, spoken lines join table'

		cursor.execute('''
			CREATE TABLE IF NOT EXISTS
				stage_direction(stage_id INTEGER PRIMARY KEY NOT NULL,
					text TEXT, episode_id INTEGER, line_order INTEGER,
					FOREIGN KEY(episode_id) REFERENCES episode(ep_id))'''
		)
		print 'created stage direction table'
		
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS
				misc(misc_id INTEGER PRIMARY KEY NOT NULL,
					 line_text TEXT)'''
		)
		print 'created misc table'
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
	items = kwargs.items()
	table_statement = '{}({})'.format(table, ', '.join(['"' + key + '"' for key, val in items]))
	value_statement = ", ".join(['"' + val + '"' for key, val in items])
	query = "INSERT INTO {} VALUES({})".format(table_statement, value_statement)
	run_query(query)
	print 'finished w'
	return True

def drop_table(table_name):
	if not table_name:
		raise Exception('Please provide table name')

	run_query("DROP TABLE {}".format(table_name))
	return True

if __name__ == '__main__':
	create_tables()
