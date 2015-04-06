import string
import re

def mostly_capital(n):
	caps = filter(lambda s: s in string.ascii_uppercase, n)
	len_n, len_c = len(n), len(caps)
	return (len_n - len_c) <= .4 * len_n

def stage_direction(s):
	return '[' in s[:2] and ']' in s[-2:]

def strip_html(s):
	s = re.sub(r'<[a-z]+>', '', s)
	s = re.sub(r'</[a-z]+>', '', s)
	s = re.sub(r'<[-a-z0-9 "=]+>', '', s)
	return s

def has_colon(s):
	return ':' in s

def wrapper(*args):
	def func(x):
		returns = []
		for use, f in args:
			val = f(x) if use else not f(x)
			returns.append(str(val))
		return eval(' and '.join(returns))
	return func

 
	
def check_misc(filename):
	with open(filename, 'r') as f:
		lines = [strip_html(line.strip()) for line in f.readlines()]
		lines = [line for line in lines if line and 
				 '=================' not in line]
		filters = (mostly_capital, stage_direction, has_colon)
		caps = filter(wrapper((True, filters[0]), (False, filters[1])), lines)
		stage = filter(stage_direction, lines)
		colons = filter(wrapper((True, filters[2]), (False, filters[1]),
								(False, filters[0])), lines)
		possible_misses = filter(wrapper((True, filters[0]), (True, filters[1]),
								 (True, filters[2])), lines)
	return possible_misses, caps, stage, colons

a,b,c,d = check_misc('stage_directions.txt')
