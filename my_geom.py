def sign(x):
	if x > 0:
		return 1
	elif x < 0:
		return -1
	else:
		return 0

# python please add this to standard library
def range2d(w, h):
	return ((x,y) for x in xrange(w) for y in xrange(h))

# and this too
def box2d(x, y, w, h):
	return ((a+x,b+y) for (a,b) in range2d(w,h))

def square2d(x, y, w, h):
	# top
	for i in xrange(w):
		yield (x+i, y)

	# sides
	for i in xrange(h-2):
		yield (x, y+i+1)
		yield (x+w-1, y+i+1)

	# bot
	for i in xrange(w):
		yield (x+i, y+h-1)

# seriously i'm using python to avoid this kind of
# trivial stuff
def line2d(x1, y1, x2, y2):
	points = []
	issteep = abs(y2-y1) > abs(x2-x1)
	if issteep:
		x1, y1 = y1, x1
		x2, y2 = y2, x2
	rev = False
	if x1 > x2:
		x1, x2 = x2, x1
		y1, y2 = y2, y1
		rev = True
	deltax = x2 - x1
	deltay = abs(y2-y1)
	error = int(deltax / 2)
	y = y1
	ystep = None
	if y1 < y2:
		ystep = 1
	else:
		ystep = -1
	for x in range(x1, x2 + 1):
		if issteep:
			points.append((y,x))
		else:
			points.append((x,y))
		error -= deltay
		if error < 0:
			y += ystep
			error += deltax
	# Reverse list if coordinates were reversed
	if rev:
		points.reverse()
	return points