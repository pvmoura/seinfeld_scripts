from utils import make_hist, mostly_capital_letters, strip_html

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
		if float(right_count/wrong_count) > 3:
			script.replace(wrong_string, right_string)
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

def breakdown_lines(script):
	""" 
	"""
	speaker_text, actions, stage_directions, locations = {}, [], [], []
	cleaned_script = clean_names(script)
	for l in script.split(DELIM):
		l = strip_html(l)
		if not l:
			continue
		elif check_logistical_aside(l, '(', ')'):
			actions.append(l)
		elif check_logistical_aside(l, '[', ']'):
			stage_directions.append(l)
		elif mostly_capital_letters(l, .4):
			locations.append(l)
		else:
			name = get_name(l)
			if not name and has_colon(l):
				name = l.split(':')[0]
			if name:
				name = name.lower()
				if not speaker_text.get(name):
					speaker_text[name] = []
				index = l.index(name + ':') + len(name) + 1
				speaker_text[name].append(l[index:])
	return speaker_text, actions, stage_directions, locations

def separate_meta(lines, ep, delim='====='):
	has_delim = filter(lambda s: delim in s, lines)
	if not has_delim:
		logging.debug('no equals delimiter in episode %s\n' % ep)
		return False

	index = lines.index(has_delim[0])
	return lines[:index], lines[index+1:]
