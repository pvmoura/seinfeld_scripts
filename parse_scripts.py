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

def get_name(line):
	""" Get the name (if it exists) from a line
		
		param line:
			str - a script line

		'JERRY: Some text' will output 'JERRY' 
	"""
	colon_split = line.split(':')
	if len(colon_split) > 1:
		name = colon_split[0]
		name = re.sub(' {0,3}\(.+\)', '', name)
		if len(name) < 20 and mostly_capital_letters(name):
			return name 
	return None

def get_names(script):
	""" From a list of lines determine characters' names
		param script
			str - a script string
	"""
	names = [get_name(l) for l in script.split(DELIM)]
	return filter(lambda n: n is not None, names)

def possible_speaker(line, names):
	speaker_chars = [',', 'and', '&'] + names
	for index, word in enumerate(line.split()):
		presence = word.lower() in speaker_chars
		if not presence:
			return index
	return False

def add_line(name, names, line, colon=True):
	identifier = name.lower()
	if colon:
		name += ':'
	index = line.index(name) + len(name)
	sans_parans = re.sub(r'\(.*\)', '', line[index:])
	return sans_parans

def handle_special_case(speaker_text, line):
	split_line = line.split()
	if split_line[0].lower() in speaker_text.keys():
		if ';' in line:
			name, text = line.split(';')
			speaker_text = add_line(name, speaker_text, line, False)
			return False
		if possible_speaker(line, speaker_text.keys()):
			index = possible_speaker(line, speaker_text.keys())
			name = ' '.join(split_line[:index])
			speaker_text = add_line(name, speaker_text, line, False)
			return False
	return line

def breakdown_lines(script):
	""" 
	"""
	def add_spoken(name, names, line, data, colon=True):
		names.add(name)
		data['table'] = 'spoken_line'
		data['text'] = add_line(name, names, line, colon)
		return names, data

	names = set()
	cleaned_script = clean_names(script)
	for i, l in enumerate(cleaned_script.split(DELIM)):
		l, name, data = strip_html(l), get_name(l).lower(), {}
		data['raw_text'] = l
		data['line_order'] = i
		data['table'] = 'blocking'
		if not l:
			continue
		elif re.match(r'^[\(\[]', l):
			data['type'] = 'action' if l[0] == '(' else 'stage_direction'
		elif mostly_capital_letters(l, .05):
			data['type'] = 'location'
		elif name:
			names, data = add_spoken(names, name, l, data)
		elif re.match(r'[:;]', l) or possible_speaker(l, names):
			index = possible_speaker(l, names) or l.split
			words = l.split(':')[0].split()
			if words[0].lower() in names:
				names, data = add_spoken(names, l.split(':')[0], l, data)
		elif ';' in l:
			name, text = line.split(';')
			names, data = add_spoken(names, name, text, data, False)
		elif possible_speaker(l, names):
			index = possible_speaker(l, names)
			name = ' '.join(l.split()[:index])
			names, data = add_spoken(names, name, l, data)
		else:
			data = {'table': 'misc', 'raw_text': l}	
	
	return data

def separate_meta(lines, ep, delim='====='):
	""" The meta information is always separated from the script text by
		a line of ='s. This function 
	"""
	has_delim = filter(lambda s: delim in s, lines)
	if not has_delim:
		logging.debug('no equals delimiter in episode %s\n' % ep)
		return False

	index = lines.index(has_delim[0])
	return lines[:index], lines[index+1:]
