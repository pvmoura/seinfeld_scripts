#!/usr/bin/env python

from utils import make_hist, mostly_capital_letters, strip_html
import re
from string import lower
from operator import itemgetter
import logging
from db import insert

logging.basicConfig(filename='errors.log', level=logging.DEBUG,
					format='%(asctime)s %(message)s')

DELIM = '<br><br>'

def clean_names(script):
	""" Take a script and clear it's names of typos
		params script
			str - A script string
	"""
	def is_similar(a, b):
		smaller, larger = sorted([a,b], key=lambda x: len(x)) 
		len_s, len_l, similar = len(smaller), len(larger), 0
		for i, c in enumerate(larger):
			if i < len_s and c == smaller[i]:
				similar += 1
			elif len_s < len_l:
				smaller = smaller[:i] + 'x' + smaller[i:]
				len_s += 1
		return len_l - similar <= 2
	
	names = get_names(script)
	hist = make_hist(names)
	typo_pairs = set([tuple(
					  sorted([(a, hist[a]), (b, hist[b])], key=itemgetter(1)))
					  for a in hist.iterkeys() for b in hist.iterkeys()
					  if a != b and is_similar(a, b)])

	for wrong, right in typo_pairs:
		wrong_string, wrong_count = wrong
		right_string, right_count = right
		if float(right_count)/float(wrong_count) > 3:
			script = script.replace(wrong_string, right_string)
	return script

def get_name(line, characters=None):
	""" Get the name (if it exists) from a line
		
		param line:
			str - a script line

		'JERRY: Some text' will output 'JERRY' 
	"""
	def check_name_against_tuple(name, char_tuple):
		# if no first name
		name, char_list = name.lower(), map(lambda s: s.lower(), char_tuple)
		try:
			return (char_list.index(name), None)
		except ValueError:
			pass
		full_name = ' '.join([c for c in a[:3] if c])
		if name == full_name:
			return (0, 3)
		
		return None	
	colon_split, name_location = line.split(':'), None
	if len(colon_split) > 1:
		name = colon_split[0]
		name = re.sub(' {0,3}\(.+\)', '', name)
		if characters:
			name_location = [(c, check_name_against_tuple(c))
							 for c in characters if check_name_against_tuple(c)]
		if name_location:
			return name_location
		elif (len(name) < 20 and mostly_capital_letters(name)):
			return name 
	return None

def get_names(script):
	""" From a list of lines determine characters' names
		param script
			str - a script string
	"""
	names = [get_name(l) for l in script.split(DELIM)]
	return filter(lambda n: n is not None, names)

def process_lines(script):
	""" 
	"""
	def add_spoken(names, name, line, data, delim=None):
		names.add(name)
		data['type'] = 'spoken'
		text = get_spoken_text(name, line, delim)
		data['text'] = text
		if len(text) > 400:
			data['special'] = 'monologue'
		data['speaker'] = name
		return names, data
	
	def speaker_index(line, names):
		for index, word in enumerate(line.split()):
			if not word.lower() in names:
				return index
		return False
	
	def get_spoken_text(name, line, delim=None):
		identifier = name.lower()
		if delim:
			identifier += delim
		try:
			index = line.lower().index(identifier) + len(identifier)
		except ValueError:
			index = 0
		return re.sub(r'\(.*\)', '', line[index:])

	def process_line(index, line, names):
		line, name, data = strip_html(line), get_name(line), {}
		data['raw_text'] = line
		data['line_order'] = index
		data['table'] = 'line'
		if re.match(r'^[(\[]', line):
			data['type'] = 'action' if line[0] == '(' else 'stage_direction'
		elif name:
			names, data = add_spoken(names, name.lower(), line, data, ':')
		elif re.match(r'[:;]', line):
			delim = ':' if ':' in line[:20] else ';'
			split_line = line.split(delim)
			names_set = set(map(lambda s: s.lower(), split_line[0]))
			print names_set == names_set.intersection(names)
			if names_set == names_set.intersection(names):
				names, data = add_spoken(names, split_line[0], line, data,delim)
			else:
				data['type'] = 'misc'
		elif speaker_index(line, names):
			index = speaker_index(line, names)
			name = ' '.join(line.split()[:index])
			names, data = add_spoken(names, name, line, data)
		elif mostly_capital_letters(line, .05):
			data['type'] = 'location'
		elif re.match(r'[\)\]]$', line):
			data['type'] = 'action' if line[-1] == ')' else 'stage_direction'
		elif len(l) > 400:
			#probably a monologue
			names, data = add_spoken(names, 'jerry', line, data)
		else:
			data['type'] = 'misc'

		return data

	names = set([',', 'and', '&'])
	cleaned_script = clean_names(script)
	names = names.union(get_names(cleaned_script))
	lines = [process_line(i, l, names)
			 for i, l in enumerate(cleaned_script.split(DELIM)) if l]	
	return lines

def separate_meta(script, ep, delim='====='):
	""" The meta information is always separated from the script text by
		a line of ='s. This function, given a script, splits the script on that
		delimiter
		
		param script
			str - a script string
		param ep
			str - a seinology episode reference
		param delim
			str - the meta delimiter, ==== as default
	"""
	lines = script.split(DELIM)
	has_delim = filter(lambda s: delim in s, lines)
	if not has_delim:
		logging.debug('no equals delimiter in episode %s\n' % ep)
		return False
	index = 0
	while has_delim:
		index = lines.index(has_delim.pop(0), index+1)	
	return DELIM.join(lines[:index]), DELIM.join(lines[index+1:])
