import time
import logging
from string import ascii_uppercase, ascii_letters
import re

def has_colon(s):
	return ':' in s

def make_hist(iterable):
	hist = {}
	for i in iterable:
		hist[i] = hist.get(i, 0) + 1
	return hist

def mostly_capital_letters(n, threshold=.25):
	caps_count = len(filter(lambda s: s in ascii_uppercase, n))
	letters_count = len(filter(lambda s: s in ascii_letters, n))
	return (letters_count - caps_count) <= threshold * letters_count

def strip_html(s):
	s = re.sub(r'</[a-z]+>', '', s)
	s = re.sub(r'<[-a-z0-9 "=]+>', '', s)
	return s

def check_logistical_aside(s, starting_delim='(', ending_delim=None):
	end = True
	if ending_delim:
		end = ending_delim in s[-3:]
	return starting_delim in s[:2] and end
