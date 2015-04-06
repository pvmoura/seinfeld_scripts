def read_info(filename):
	characters = {}
	with open(filename, 'r') as f:
		for line in f.readlines():
			line = line.strip()
			if 'EPISODE' not in line and line:
				characters[line] = characters.get(line, 0) + 1
	return characters
chars = read_info('characters.txt')
