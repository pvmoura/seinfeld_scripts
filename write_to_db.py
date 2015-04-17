from parse_scripts import process_lines, separate_meta
from db import insert, lookup
from get_scripts import fetch_clean_script

def add_multiple_speakers(data, line_id):
	if data.get('speaker'):
		for splitter in ['and', '&', ',']:
			split_speakers = data.get('speaker').split(splitter)
			if len(split_speakers) > 1:
				for character in split_speakers:
					result = lookup(table='character', columns=('char_id',),
						   			query={'first_name': character})
					char_id = result[0]
					insert(table='character_spoken_line_join', char_id=char_id,
						   spoken_id=line_id)
	return True

def add_script_to_db(ep):
	script = fetch_clean_script(ep)
	meta, script = separate_meta(script, ep)
	for line_data in process_lines(script):
		add_to_db(line_data)


def add_to_db(line_data):
	conjunctions = ['and', '&', ',']
	if line_data.get('speaker'):
		speakers = line_data.pop('speaker')
		data = insert(**line_data)
		conjunction_present = filter(lambda s: s in conjunctions, speakers)
		if conjunction_present:
			line_data['speaker'] = speakers
			add_multiple_speakers(line_data, data['id'])
		else:
			print speakers
			char_id = lookup(table='character',
							 query={'first_name': speakers},
							 columns=('char_id', ))
			if not char_id:
				char_id = insert(table='character', first_name='speakers')
				char_id = char_id['id']
			else:
				char_id = char_id[0][0]
			insert(table='character_spoken_line_join', char_id=char_id,
				   spoken_id=data['id'])

add_script_to_db('01')	
