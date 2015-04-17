from get_scripts import fetch_script_from_file, episode_nums, clean_raw_script_html
import re
from parse_scripts import separate_meta
from db import insert, lookup

def consolidate_meta(meta_info, sein_ref):
	info = {'seinology_ref': sein_ref, 'table': 'episode'}
	for i, meta in enumerate(meta_info.split('<br><br>')):
		for line in meta.split('<br>'):
			line = line.lower()
			if 'broadcast date' in line:
				line = line.replace('broadcast date: ', '')
				info['air_date'] = line
			elif 'pc:' in line and 'season' in line:
				line = line.replace('pc: ', '').replace(',', '')
				line = re.sub(r'[A-Za-z()]', '', line)
				info['code'], info['season'], info['episode'] = line.split()
			elif re.match(r'^episode', line) and '-' in line:
				info['title'] = line.split(' - ')[1]
			elif 'written by' in line or re.match(r'^part [12] written by', line):
				info['authors'] = re.sub(r'written by[:]{0,1} ', '', line)
			elif 'directed by' in line:
				info['director'] = re.sub(r'directed by[:]{0,1} ', '', line)
	return info

def get_characters(meta_info, ep):
	def breakup_name(name):
		def get_first_and_last(name):
			title, first, last, name_list  = "", "", "", name.split()
			last_index = 1
			if re.match(r'^[A-Za-z]{2,4}\. ', name):
				title = name_list[0]
				if len(name_list) > 2:
					first = name_list[1]
					last_index = 2
			else:
				first = name_list[0]
			last = ' '.join(name_list[last_index:])
			return title, first, last
		
		paran_split, special = re.split(r' \(', name), ""
		if len(paran_split) > 1 and name[-1] == ')':
			name, special = paran_split
			special = special.replace(')', '')
			if 'uncredited' in special.lower():
				special = ""
		
		title, first, last = get_first_and_last(name)

		return title, first, last, special

	episode_info = []
	for index, meta in enumerate(meta_info.split('<br><br>')):
		for line in meta.split('<br>'):
			if '.......' in line:
				char_split = map(lambda s: s.strip(), re.split('\.{3,}', line))
				actor, character = char_split
				actor = actor.replace('rc: ', '')
				character = re.sub(r'[Vv]oice of[ ]*', '', character)
				a = breakup_name(actor)
				b = breakup_name(character)
				info = {'first_name': b[1], 'last_name': b[2], 'title': b[0],
						'actor_first_name': a[1], 'actor_last_name': a[2],
						'special_name': b[3], 'table': 'character'}
				episode_info.append(info)
	return episode_info

if __name__ == '__main__':
	episodes_info = {}
	for ep in episode_nums(1,180):
		script = fetch_script_from_file(ep)
		script = clean_raw_script_html(script, ep)
		meta = separate_meta(script, ep)[0]
		for m in re.split(r'={6,}', meta):
			episode = lookup(table='episode', columns=('ep_id', ),
						query={'seinology_ref': ep})
			episode = episode[0]
			for character in get_characters(m, ep):
				result = insert(**character)
				insert(table='character_episode_join', char_id=result['id'],
					   ep_id=episode['ep_id'])
