import math
import random
from my_geom import range2d, box2d, line2d, square2d

import sprites as spr
from objects import Tile

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

		self.illuminated = False

	def add_item(self, position, item):
		x,y = position
		self.tiles[x][y].items.append(item)

	def advance_ticks(self, num_ticks):
		for c in self.creatures:
			c.advance_ticks(num_ticks)
			if not c.alive:
				self.creatures.remove(c)

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

	def recalc_light(self):
		if self.illuminated:
			for x,y in range2d(self.width, self.height):
				self.tiles[x][y].lit = True
			return

		# Set all tiles to dark
		for x,y in range2d(self.width, self.height):
			self.tiles[x][y].lit = False

		# Go through every item on the map, illuminating tiles
		# that can be reached by the item
		for x,y in range2d(self.width, self.height):
			for i in self.tiles[x][y].items:
				if i.luminosity > 0:
					for a,b in self.field_of_view(x, y, i.luminosity):
						self.tiles[a][b].lit = True
		
		# Also illuminate if a luminous item is held by a creature
		for c in self.creatures:
			for i in c.inv:
				if i.luminosity > 0:
					for a,b in self.field_of_view(c.x, c.y, i.luminosity):
						self.tiles[a][b].lit = True
	
	def sight(self, x1, y1, x2, y2, r=25):
		dx = x1-x2
		dy = y1-y2
		if math.sqrt(dx**2 + dy**2) > r:
			return False
		for x,y in line2d(x1, y1, x2, y2)[:-1]:
			if not self.tiles[x][y].transparent:
				return False
		return True

	def field_of_view(self, x1, y1, r=25):
		seeable = []
		for x,y in box2d(-12, -12, 25, 25):
			# for each tile in map size:
			ax, ay = x1+x, y1+y
			if not self.in_bounds(ax, ay):
				continue

			if self.sight(x1, y1, ax, ay, r):
				yield (ax, ay)

	def in_bounds(self, x, y):
		return 0 <= x < self.width and 0 <= y < self.height

	def occupant_at(self, x, y):
		if self.in_bounds(x, y):
			occupants = [c for c in self.creatures if c.x == x and c.y == y]
			if not occupants:
				return None
			if len(occupants) > 1:
				print('EPIC FAIL - there is more than one occupant at %d, %d!', x, y)
				raise
			return occupants[0]
		return None
	
	def passable(self, x, y):
		if not self.in_bounds(x, y):
			return False
			
		if self.tiles[x][y].blocking:
			return False

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

	def generate_town(self):
		w,h = self.width, self.height
		path_tile = spr.COBBLESTONE

		def town_district(level, x, y, w, h):
			if w >= 5 and random.random() < 0.5 or w >= 10:
				hs_width = random.randint(w//3, 2*w//3)
				for i in range(h):
					level.tiles[x+hs_width][y+i].img = path_tile
				town_district(level, x, y, hs_width, h)
				town_district(level, x+hs_width+1, y, w-hs_width-1, h)
			elif h >= 5 and random.random() < 0.5 or h >= 10:
				vs_height = random.randint(h//3, 2*h//3)
				for i in range(w):
					level.tiles[x+i][y+vs_height].img = path_tile
				town_district(level, x, y, w, vs_height)
				town_district(level, x, y+vs_height+1, w, h-vs_height-1)
			else:
				return

		self.clear(spr.STONE_TILE)
		for x,y in square2d(0, 0, w, h):
			t = self.tiles[x][y]
			t.img = spr.STONE_WALL
			t.blocking = True
			t.transparent = False
		town_district(self, 1, 1, w-2, h-2)

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
				tile.transparent = False
			else:
				tile.img = spr.MUD_FLOOR
				tile.blocking = False
				tile.transparent = True

		for region in sorted(self.get_regions(), key=len, reverse=True):
			print("Region of size %d" % len(region))
