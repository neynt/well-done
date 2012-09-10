import random

import sprites as spr

from my_geom import range2d, box2d
from level import Level
from objects import Item
from creature import Creature

def generate_shop(w, h, shop_items):
	level = Level(w, h, is_shop=True)

	for x,y in range2d(w, h):
		t = level.tiles[x][y]
		if x == 0 or y == 0 or x == w-1 or y == h-1:
			t.img = spr.WOOD_WALL
			t.blocking = True
			t.transparent = False
		else:
			t.img = spr.WOOD_FLOOR
			t.blocking = False
			t.transparent = True

	for a,b in box2d(2, 2, 5, 5):
		level.add_item((a,b), random.choice(shop_items))
	for a,b in box2d(9, 2, 5, 5):
		level.add_item((a,b), random.choice(shop_items))
	for a,b in box2d(2, 9, 5, 5):
		level.add_item((a,b), random.choice(shop_items))
	for a,b in box2d(9, 9, 5, 5):
		level.add_item((a,b), random.choice(shop_items))

	level.illuminated = True
	return level

def generate_dungeon(w, h, difficulty=1):
	level = Level(w, h)

	new_map = [[0 for _ in xrange(h)] for _ in xrange(w)]
	# initialize new_map to noise (0.43% filled)
	for x,y in range2d(w, h):
		if random.random() < 0.43:
			new_map[x][y] = 1

	# apply cellular automation
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

	# apply changes to actual map
	for x,y in range2d(w, h):
		tile = level.tiles[x][y]
		if new_map[x][y] == 1:
			tile.img = spr.ROCK
			tile.blocking = True
			tile.transparent = False
		else:
			tile.img = spr.MUD_FLOOR
			tile.blocking = False
			tile.transparent = True

	# spawn treasures and creatures
	mr = level.get_main_region()

	treasures = random.sample(mr, difficulty)
	for loc in treasures:
		level.add_item(loc, Item(spr.GOLD_NUGGET, name="gold nugget", value=50+difficulty*25))

	mobs = random.sample(mr, difficulty)
	for loc in mobs:
		c = Creature(level, *loc, hp=difficulty*10, maxhp=difficulty*10, name="malicious slime", gold=10+difficulty*5)
		c.min_atk = difficulty
		c.max_atk = difficulty*2

		level.creatures.append(c)
		
	return level
