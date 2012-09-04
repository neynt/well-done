import random

consonants = 'bcdfghjklmnpqrstvwxyz'
vowels = 'aeiou'

def generate_name():
	name = ''
	ns = 0
	vs = 0
	for i in xrange(random.randint(4, 9)):
		if ns >= 2:
			name += random.choice(vowels)
			ns = 0
			vs = 1
			continue
		elif vs >= 2:
			name += random.choice(consonants)
			ns = 1
			vs = 0
		else:
			if random.randint(0, 1):
				name += random.choice(vowels)
				ns = 0
				vs += 1
			else:
				name += random.choice(consonants)
				ns += 1
				vs = 0
	return name

