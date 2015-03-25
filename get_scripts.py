import requests
import re

URL = "http://www.seinology.com/scripts/script-%s.shtml"
NAME_PATTERN = re.compile(r'^[^:]+: ')

def episode_nums(first, last):
	""" generate list of episode numbers for querying site
		
		param first:
			int - starting episode of the range (inclusive)
		param last:
			int - ending episode of the range (inclusive)
	"""
	# clip shows
	skip_eps = (100, 101, 177, 178)
	
	#double episodes
	double_eps = ((82, 83), (179, 180))

	episode_nums = ['0%i' % i if i < 10 else str(i) 
					for i in xrange(first, last+1) if i not in skip_eps]
	
	
	# rename double episodes to 82and83
	for ep1, ep2 in double_eps:
		try:
			episode_nums[episode_nums.index(ep1)] = '%sand%s' % (ep1, ep2)
			episode_nums.remove(str(ep2))
		except ValueError:
			pass

	return episode_nums

def get_script(ep_num):
	""" Request seinology given an episode number

		param ep_num:
			str - the episode number to query (based on seinology nomenclature
			i.e. 82and83 instead of 82)
	"""
	escapes = { '&#145;': "\'", '&#146;': "\'", '&#147;': '\"', '&#148;': '\"',
				'&#150;': '-', '&#38;': '&', '&amp;': '&' }
	print 'now getting episode', ep_num
	url = URL % ep_num
	r = requests.get(url)
	if r.status_code != 200:
		message = 'failed: %s\n' % url
		with open('log.txt', 'a') as f:
			f.write(message)
		print message
		return ''

	t = re.findall(r'<font size="-2">[\S\s]*', r.text)
	t = re.sub(r'</font>[\S\s]*', '', t[0])
	t = t.replace('\n', '').replace('\t', '')
	for key, val in escapes.iteritems():
		t = t.replace(key, val)
	return t

def get_scripts(first=1, last=180):
	""" wrapper to get scripts from seinology

		param first:
			int - start of range (inclusive)

		param last:
			int - end of range (inclusive)
	"""
	scripts = [get_script(ep) for ep in episode_nums(first, last)]
	return scripts

def clean_names(lines):
	def get_similar_names(names):
		""" Takes a list of names and sees if there is an uncommon name that is
			similar to a common name
		"""
		def make_hist(iterable):
			hist = {}
			for elem in iterable:
				if len(elem) < 10:
					hist[elem] = hist.get(elem, 0) + 1
			return hist

		# def is_similar(a, b):
		# 	""" Checks if two iterables have similar membership
		# 	"""
		# 	a_hist, b_hist = make_hist(a), make_hist(b)
		# 	diff = len([x for x in a_hist.items() if x not in b_hist.items()] +
		# 		   	   [x for x in b_hist.items() if x not in a_hist.items()])
		# 	return diff <= 2 and diff > 0
		def missing_letters(a, b):
			candidates = [a,b]
			candidates.sort()
			larger, smaller = candidates
			len_l, len_s, similar = len(larger), len(smaller), 0
			if len_l % len_s <= 2:
				for i,c in enumerate(larger):
					print i, c, larger, smaller	
					if larger[i] == smaller[i]:
						similar += 1
					elif len_s < len_l:
						smaller = smaller[:i] + 'x' + smaller[i:]
						len_s += 1
			return len_l - similar <= 2
		names_hist = make_hist(names)
		similar_names = []
		comparisons = [(a, b) for a in names_hist for b in names_hist
					   if missing_letters(a, b) and a != b]
		return comparisons
		#for name, instances in names_hist.iteritems():
		#	for cmp_name, cmp_instances in names_hist.iteritems():
		#		tup = ((cmp_name, cmp_instances), (name, instances))
		#		if is_similar(cmp_name, name) and tup not in similar_names \
		#		   and tuple(reversed(tup)) not in similar_names:
		#			similar_names.append(tup)
		#return similar_names


	names = get_names(lines)
	similar_names =  get_similar_names(names)
	return similar_names
	print 'similar names are:', similar_names
	for data1, data2 in similar_names:
		orig, replace = data1[0], data2[0]
		print data1, data2
		if data1[1] > data2[1]:
			lines = [l.replace(data2[0], data1[0]) for l in lines]
	return lines

def get_names(lines):
	names = [NAME_PATTERN.match(l).group(0).replace(':', '') for l in lines if NAME_PATTERN.match(l)]
	return names

def get_name(line):
	return NAME_PATTERN.match(line).group(0).replace(':', '')
	
def get_lines(text, speaker="JERRY"):
	spoken_lines = filter(lambda x: re.match(NAME_PATTERN, x), text.split('<br>'))
	return spoken_lines

def get_speaker_text(lines, names=None, speaker="JERRY"):
	def clean_text(words):
		words = re.sub('\([^\)]+\)', '', words)
		#words = re.sub('\"[^\"]+\"', '', words)
		return words

	names = set(names)
	data = { name: [] for name in set(names) }
	for line in lines:
		name = get_name(line)
		start = line.index(name + ': ') + len(name) + 2
		line_text = clean_text(line[start:])
		if not data.get(name):
			data[name] = []
		data[name].append(line_text)
	return data

def test(start=14, end=15):
	scripts = get_scripts(start, end)
	for script in scripts:
		lines = get_lines(script)
		print len(lines)
		uncleaned = set(get_names(lines))
		print uncleaned
		lines = clean_names(lines)
		cleaned = set(get_names(lines))
		print 'discarded names are: ', uncleaned.difference(cleaned)
		print 'names are:', ", ".join(cleaned)
		return lines, script, cleaned

def separate_meta(lines, ep, delim='====='):
	find_delim = filter(lambda s: delim in s, lines)
	if not find_delim:
		with open('error_log', 'a') as f:
			f.write('no equals delimiter in episode %i', ep)
		return False

	index = lines.index(find_delim[0])
	return lines [:index], lines[index:]

def check_for_equals(start=1, end=180):
	no_equals = []
	for script_i in episode_nums(start, end):
		script = get_script(script_i)
		lines = script.split('<br><br>')
		equal_string = filter(lambda s: '=====' in s, lines)
		if equal_string:
			msg = 'equals in episode %s at line %i' % (script_i , lines.index(equal_string[0]))
			with open('equals.txt', 'a') as f:
				f.write(msg + '\n')
		else:
			print 'equals not in here'
			no_equals.append(script_i)
			with open('no_equals.txt', 'a') as f:
				f.write(str(script_i))
	return no_equals



a = get_scripts(1,1)
b,c = separate_meta(a[0].split('<br><br>'), 1)
d = clean_names(c)
print d
# import sys
# if len(sys.argv) > 1:
# 	lines, script, names = test(int(sys.argv[1]), int(sys.argv[2]))
# else:
# 	lines, scripts, names = test()
# data = get_speaker_text(lines, names)
#print check_for_equals()
