import requests
import re
from operator import itemgetter
import string
import time
URL = "http://www.seinology.com/scripts/script-%s.shtml"

def episode_nums(first, last):
	""" generate list of episode numbers for querying site
		
		param first:
			int - starting episode of the range (inclusive)
		param last:
			int - ending episode of the range (inclusive)
	"""
	# clip shows
	skip_eps = (100, 101, 177, 178, 142)
	
	#double episodes
	double_eps = (('82', '83'), ('179', '180'))

	episode_nums = ['0%i' % i if i < 10 else str(i) 
					for i in xrange(first, last+1) if i not in skip_eps]
	
	
	# rename double episodes to 82and83
	for ep1, ep2 in double_eps:
		try:
			episode_nums[episode_nums.index(ep1)] = '%sand%s' % (ep1, ep2)
			episode_nums.remove(ep2)
		except ValueError:
			pass

	return episode_nums

def get_script(ep_num):
	""" request seinology for script
		param ep_num:
			str - the episode number to query
	"""
	url = URL % ep_num
	r = requests.get(url)
	if r.status_code != 200:
		msg = 'failed: %s' % url
		log(msg)
		print msg
		return ''

	return r.text



def clean_raw_script_html(ep_num):
	""" Request seinology given an episode number

		param ep_num:
			str - the episode number to query (based on seinology nomenclature
			i.e. 82and83 instead of 82)
	"""
	escapes = { '&#145;': "'", '&#146;': "'", '&#147;': '"', '&#148;': '"',
				'&#150;': '-', '&#38;': '&', '&amp;': '&', '&nbsp;': ' ',
				'&#146t': "'", '&#63;': '?', '&#62;': '>', '&#61;': '=',
				'&#60;': '<', '&#59;': ';', '&#58;': ':', '&#33;': '!',
				'&quot;', '"'}
	t = r.text.split('<font size="-2">')
	if len(t) < 2:
		log('failed to split text for: %s' % ep_num)
		return ''	
	
	t = t[1].replace('\n', '').replace('\t', '')
	ends = ('The End', 'the end', 'The end', 'the End')
	has_end = [end for end in ends if end in t]
	if has_end:
		t = t.split(has_end[0])[0]
	
	for key, val in escapes.iteritems():
		t = t.replace(key, val)
	return t

def clean_names(lines):
	def make_hist(iterable):
		hist = {}
		for i in iterable:
			hist[i] = hist.get(i, 0) + 1
		return hist
	
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
	
	names = get_names(lines)
	hist = make_hist(names)
	typo_pairs = set([tuple(
					  sorted([(a, hist[a]), (b, hist[b])], key=itemgetter(1)))
					  for a in hist for b in hist
					  if a != b and is_similar(a, b)])
	for wrong, right in typo_pairs:
		wrong_string, wrong_count = wrong
		right_string, right_count = right
		if float(right_count/wrong_count) > 3:
			for line in lines:
				line.replace(wrong_string, right_string)
	return lines

def test_lines():
	test1 = ['JERRY: ', 'JERRY: ', 'JERY: ']
	assert clean_names(test1) == ['JERRY: ', 'JERRY: ', 'JERRY: ']
	test1 = ['ELAINE: ', 'ELAINE: ', 'ELANE: ']
	assert clean_names(test1) == ['ELAINE: ', 'ELAINE: ', 'ELAINE: ']
	test1 = ['GEORGE: ', 'GEORGE: ', 'GERGE: ']
	assert clean_names(test1) == ['GEORGE: ', 'GEORGE: ', 'GEORGE: ']

def test_similar():
	test1 = ['JERRY: ', 'JERRY: ', 'JERY: ', 'ASDFD: ', 'DR. WATLY: ']
	assert clean_names(test1) == set([(('JERY', 1), ('JERRY', 2))])
	test1 = ['CLAIRE: ', 'CLAIRE: ', 'CLAIE: ', 'ASDFD: ', 'DR. WATLY: ']
	assert clean_names(test1) == set([(('CLAIE', 1), ('CLAIRE', 2))])
	test1 = ['KRAME: ', 'KRAMER: ', 'KRAMER: ', 'ASDFD: ', 'DR. WATLY: ']
	assert clean_names(test1) == set([(('KRAME',1), ('KRAMER', 2))])
	test1 = ['GEORGE: ', 'GEORGE: ', 'GERGE: ', 'ASDFD: ', 'DR. WATLY: ']
	assert clean_names(test1) == set([(('GERGE',1), ('GEORGE', 2))])
	test1 = ['ELAINE: ', 'ELAINE: ', 'ELANE: ', 'ASDFD: ', 'DR. WATLY: ']
	assert clean_names(test1) == set([(('ELANE', 1), ('ELAINE', 2))])
	test1 = ['ELNE: ', 'ELAINE: ', 'ELAINE: ', 'ASDFD: ', 'DR. WATLY: ']
	assert clean_names(test1) == set([(('ELNE', 1), ('ELAINE', 2))])

def get_names(lines):
	names = [get_name(l) for l in lines]
	return filter(lambda n: n is not None, names)

def get_name(line):
	def mostly_capital(n):
		caps = filter(lambda s: s in string.ascii_uppercase, n)
		len_n, len_c = len(n), len(caps)
		return (len_n - len_c) <= .25 * len_n

	colon_split = line.split(':')
	if len(colon_split) > 1:
		name = colon_split[0]
		if len(name) < 20 and mostly_capital(name):
			return name 
	return None
	
def get_lines(lines, speaker="JERRY"):
	spoken_lines = filter(lambda x: get_name(x), lines)
	return spoken_lines

def breakdown_lines(lines):
	speaker_text, actions, misc = {}, [], []
	lines = clean_names(lines)
	for l in lines:
		name = get_name(l)
		if name:
			if not speaker_text.get(name):
				speaker_text[name] = []
			index = l.index(name + ':') + len(name) + 1
			speaker_text[name].append(l[index:])
		elif l and l[0] == '(' and ')' in l[-3:]:
			actions.append(l)
		else:
			misc.append(l)
	return speaker_text, actions, misc

def separate_meta(lines, ep, delim='====='):
	has_delim = filter(lambda s: delim in s, lines)
	if not has_delim:
		log('no equals delimiter in episode %s\n' % ep)
		return False

	index = lines.index(has_delim[0])
	return lines[:index], lines[index:]

def log(msg=None, log='error_log.txt'):
	with open(log, 'a') as f:
		f.write(msg + '\n')
	return True

def run(ep):
	a = get_script(ep)
	return a
	b,c = separate_meta(a.split('<br><br>'), ep)
	e,f,g = breakdown_lines(c)
	return b,e,f,g

def store_scripts(s, l):
	for i in episode_nums(s, l):
		script = run(i)
		with open('scripts/%s.txt' % i, 'w') as f:
			f.write(script)
			print 'wrote script %s' % i
		time.sleep(3)
	return True

def get_file(s, l):
	def write_file(filename,iterable, episode):
		with open(filename, 'a') as f:
			f.write('EPISODE: %s\n\n' % episode)
			f.write('\n'.join(iterable))
			f.write('\n\n')
		return True
	for i in episode_nums(s, l):
		meta, a,b,c = run(i)
		write_file('meta.txt', meta, i)
		write_file('characters.txt', a, i)
		write_file('actions.txt', b, i)
		write_file('stage_directions.txt', c, i)
		time.sleep(3)
		print 'done with episode %s\n' % i


if __name__ == '__main__':
	import sys
	length, last = len(sys.argv), 180
	if length > 3 or length < 2:
		print 'Usage: sys_test.py [first] [last]'
		sys.exit(1)
	elif length == 3:
		last = int(sys.argv[2])
	#get_file(int(sys.argv[1]), last)
	store_scripts(int(sys.argv[1]), last)
	print 'all finished. open names.txt'
