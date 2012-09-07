import random
import sprites as spr
from my_geom import range2d, box2d, line2d

class Item:
	""" Anything that can be on a map. May or may not be
	able to be picked up by the player. """
	def __init__(self, img, name='generic item', holdable=True, value=0):
		self.img = img
		self.name = name
		self.holdable = holdable
		self.value = value

class Tile:
	""" Represents a single tile in a Level. """
	def __init__(self, img, blocking=False, transparent=True, items=[]):
		# The image (from sprites.py) that will be drawn for the tile's terrain
		self.img = img

		# Can things pass through this tile? Maybe have some ghosts
		# that ignore this?
		self.blocking = blocking

		# Can light pass through this tile? If not, it will block player's
		# vision
		self.transparent = True

		# Seen/memorized by the player
		self.seen = False
		self.memorized = False

		# Make a new copy of the items list for each tile
		# (otherwise, every tile will have the same items list)
		self.items = list(items)
		self.creatures = []

class Portal:
	""" Takes a user from one Level to another. """
	def __init__(self, dest_level, dest_x, dest_y, name="a generic portal"):
		self.dest_level = dest_level
		self.dest_x = dest_x
		self.dest_y = dest_y
		self.name = name

class Creature:
	""" An entity that stores its own location, and can change it. """
	def __init__(self, cur_level, x, y, hp, maxhp):
		self.img = spr.SLIME
		self.x = x
		self.y = y
		self.hp = hp
		self.maxhp = maxhp
		self.cur_level = cur_level

class Level:
	""" Represents a floor of a dungeon or other map. """
	def __init__(self, w, h, is_shop=False):
		self.width = w
		self.height = h

		self.is_shop = is_shop

		# 2D list of tiles
		self.tiles = [[Tile(spr.ROCK) for i in xrange(h)] for i in xrange(w)]

		# dict of portals
		self.portals = {}

		# list of creatures
		self.creatures = []

	def add_item(self, position, item):
		x,y = position
		self.tiles[x][y].items.append(item)

	def all_tiles(self):
		for t in (self.tiles[x][y] for x in xrange(self.width) for y in xrange(self.height)):
			yield t
	
	def all_empty_tiles(self):
		for t in all_tiles():
			if not t.blocking:
				yield t

	# Returns a list of all coordinates that can be reached
	# from the original coordinate.
	def floodfill(self, visited, x, y, jukes=0):
		deltas = [(-1,-1), (0,-1), (1,-1),
                  (-1, 0),         (1, 0),
                  (-1, 1), (0, 1), (1, 1)]
		candidates = [(x,y)]
		in_region = []

		while candidates:
			a,b = candidates.pop()
			if (a,b) in visited or self.tiles[a][b].blocking:
				continue

			visited[(a,b)] = True
			in_region.append((a,b))
			for i,j in deltas:
				candidates.append((a+i, b+j))
		return in_region

	# Returns a list of lists of tuple coordinates.
	# Each inner list describes a contiguous region.
	def get_regions(self):
		regions = []
		visited = {}
		for x,y in range2d(self.width, self.height):
			if not self.tiles[x][y].blocking and not (x,y) in visited:
				new_region = self.floodfill(visited, x, y)
				# Make sure this "region" isn't empty
				if new_region:
					regions.append(new_region)
		return regions

	def get_main_region(self):
		return sorted(self.get_regions(), key=len, reverse=True)[0]
	
	def sight(self, x1, y1, x2, y2):
		for x,y in line2d(x1, y1, x2, y2)[:-1]:
			if self.tiles[x][y].blocking:
				return False
		return True
	
	def passable(self, x, y):
		if self.tiles[x][y].blocking:
			return False

		# out of bounds?
		if x < 0 or x >= self.width or y < 0 or y >= self.height:
			return False

		# occupied by creature?
		if any(c.x == x and c.y == y for c in self.creatures):
			return False
			
		return True;
	
	def clear(self, img):
		for t in self.all_tiles():
			t.img = img
	
	# Level generation things.
	def generate_shop(self):
		w,h = self.width, self.height
		for x,y in range2d(w, h):
			t = self.tiles[x][y]
			if x == 0 or y == 0 or x == w-1 or y == h-1:
				t.img = spr.WOOD_WALL
				t.blocking = True
				t.transparent = False
			else:
				t.img = spr.WOOD_FLOOR
				t.blocking = False
				t.transparent = True

	def generate_dungeon(self):
		w,h = self.width, self.height
		new_map = [[0 for _ in xrange(h)] for _ in xrange(w)]
		for x,y in range2d(w, h):
			if random.random() < 0.43:
				new_map[x][y] = 1

		for i in xrange(2):
			temp_map = [[0 for _ in xrange(h)] for _ in xrange(w)]
			for x,y in range2d(w, h):
				wall_count = 0
				for i,j in box2d(x-1, y-1, 3, 3):
					if 0 <= i < w and 0 <= j < h:
						wall_count += new_map[i][j]
					else:
						# sides = instawall
						wall_count += 3

				if wall_count >= 5:
					temp_map[x][y] = 1

			new_map = temp_map

		for x,y in range2d(w, h):
			tile = self.tiles[x][y]
			if new_map[x][y] == 1:
				tile.img = spr.ROCK
				tile.blocking = True
			else:
				tile.img = spr.MUD_FLOOR
				tile.blocking = False

		for region in sorted(self.get_regions(), key=len, reverse=True):
			print("Region of size %d" % len(region))
