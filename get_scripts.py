#!/usr/bin/env python

import requests
import re
from operator import itemgetter
import string
import time
import logging
from utils import make_hist, mostly_capital_letters


logging.basicConfig(filename='errors.log', level=logging.DEBUG,
					format='%(asctime)s %(message)s')
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

def fetch_script_from_net(ep_num):
	""" request seinology for script
		param ep_num:
			str - the episode number to query
	"""
	url = URL % ep_num
	try:
		r = requests.get(url)
	except Exception as e:
		logging.debug(e.message)
		return False

	if r.status_code != 200:
		logging.debug('failed: %s' % url)
		return False

	return r.text

def fetch_script_from_file(ep_num):
	""" Fetches previously saved script
	"""
	with open('scripts/%s.txt' % ep_num, 'r') as f:
		script = ''.join(f.readlines())
	return script

def clean_raw_script_html(script, ep_num):
	""" Request seinology given an episode number

		param ep_num:
			str - the episode number to query (based on seinology nomenclature
			i.e. 82and83 instead of 82)
	"""
	escapes = { '&#145;': "'", '&#146;': "'", '&#147;': "'", '&#148;': "'",
				'&#150;': '-', '&#38;': '&', '&amp;': '&', '&nbsp;': ' ',
				'&#146t': "'", '&#63;': '?', '&#62;': '>', '&#61;': '=',
				'&#60;': '<', '&#59;': ';', '&#58;': ':', '&#33;': '!',
				'&quot;': "'", '"': "'"}
	text = script.split('<font size="-2">')
	if len(text) < 2:
		logging.debug('failed to split text for: %s' % ep_num)
		return text
	
	text = text[1].replace('\n', '').replace('\t', '')
	ends = ('The End', 'THE END', 'the End')
	has_end = [end for end in ends if end in text]
	if has_end:
		text = text.split(has_end[0])[0]
	
	for key, val in escapes.iteritems():
		text = text.replace(key, val)
	return text

def store_scripts(first, last):
	for i in episode_nums(first, last):
		script = fetch_script_from_net(i)
		with open('scripts/%s.txt' % i, 'w') as f:
			f.write(script)
			print 'wrote script %s' % i
		time.sleep(3)
	return True

def fetch_clean_script(ep_num, source='file'):
	actions = {'file': fetch_script_from_file, 'net': fetch_script_from_net}
	script = actions[source](ep_num)
	cleaned_script = clean_raw_script_html(script, ep_num)
	return cleaned_script

def fetch_clean_scripts(first, last):
	for i in episode_nums(first, last):
		yield fetch_clean_script(i)

if __name__ == '__main__':
	import sys
	length, last = len(sys.argv), 180
	if length > 4 or length < 2:
		print 'Usage: get_scripts.py store [first] [last]'
		sys.exit(1)
	elif length == 4:
		command, last = sys.argv[1], int(sys.argv[3])
	commands = { 'store': store_scripts }
	command = sys.argv[1]
	commands[command](int(sys.argv[2]), last)
	print 'finished'
