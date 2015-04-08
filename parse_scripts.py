from utils import has_colon, make_hist, mostly_capital_letters, strip_html, check_logistical_aside
import re
from string import lower
from operator import itemgetter
import logging

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

def add_line(name, speaker_text, line, colon=True):
	identifier = name.lower()
	if not speaker_text.get(identifier):
		speaker_text[identifier] = []
	if colon:
		name += ':'
	index = line.index(name) + len(name)
	raw_line = line[index:]
	sans_parans_line = re.sub(r'\(.*\)', '', raw_line)
	speaker_text[identifier].append((raw_line, sans_parans_line))
	return speaker_text

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
	speaker_text, actions, stage_directions, locations, misc = {}, [], [], [], []
	cleaned_script = clean_names(script)
	for l in cleaned_script.split(DELIM):
		l, name = strip_html(l), None
		if not l:
			continue
		elif check_logistical_aside(l, '(', ')'):
			actions.append(l)
		elif check_logistical_aside(l, '[', ']'):
			stage_directions.append(l)
		elif mostly_capital_letters(l, .05):
			locations.append(l)
		elif get_name(l):
			speaker_text = add_line(get_name(l), speaker_text, l)
		elif has_colon(l):
			words = l.split(':')[0].split()
			if words[0].lower() in speaker_text.keys():
				name = l.split(':')[0]
				speaker_text = add_line(name, speaker_text, l)
		else:
			special_case = handle_special_case(speaker_text, l)
			if special_case:
				misc.append(special_case)
	
	print misc
	#return speaker_text, actions, stage_directions, locations
	return None

def separate_meta(lines, ep, delim='====='):
	has_delim = filter(lambda s: delim in s, lines)
	if not has_delim:
		logging.debug('no equals delimiter in episode %s\n' % ep)
		return False

	index = lines.index(has_delim[0])
	return lines[:index], lines[index+1:]
