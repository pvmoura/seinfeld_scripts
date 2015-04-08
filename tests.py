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

if __name__ == "__main__":
	test_similar()
	test_lines()