import sys
import pygame
from pygame.locals import *
# Our very own display module that manages all graphical things.
import display
# Game modules
import sprites as spr
from namegenerator import generate_name

# Game config
keys_n = [K_k, K_KP8]
keys_ne = [K_u, K_KP9]
keys_e = [K_l, K_KP6]
keys_se = [K_n, K_KP3]
keys_s = [K_j, K_KP2]
keys_sw = [K_b, K_KP1]
keys_w = [K_h, K_KP4]
keys_nw = [K_y, K_KP7]

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
	def __init__(self, img, passable=True, items=[]):
		self.img = img
		self.passable = passable

		# Make a new copy of the items list for each tile
		# (otherwise, every tile will have the same items list)
		self.items = list(items)

class Portal:
	""" Takes a user from one Level to another. """
	def __init__(self, dest_level, dest_x, dest_y, name="a generic portal"):
		self.dest_level = dest_level
		self.dest_x = dest_x
		self.dest_y = dest_y
		self.name = name

class Level:
	""" Represents a floor of a dungeon or other map. """
	def __init__(self, w, h, is_shop=False):
		self.width = w
		self.height = h

		# In a shop, dropping an item sells it and picking one up buys it
		self.is_shop = is_shop

		# 2D list of tiles
		self.tiles = [[Tile(spr.ROCK) for i in xrange(h)] for i in xrange(w)]

		# list of portals
		self.portals = {}

	def all_tiles(self):
		for t in (self.tiles[x][y] for x in xrange(self.width) for y in xrange(self.height)):
			yield t
	
	def passable(self, x, y):
		if x < 0 or x >= self.width or y < 0 or y >= self.height:
			return False
		return self.tiles[x][y].passable;

	def clear(self, img):
		for t in self.all_tiles():
			t.img = img
	
	def generate_dungeon(self):
		self.clear(spr.MUD_FLOOR)

class Player:
	x = 0
	y = 0
	hp = 60.0
	maxhp = 100
	mp = 20.0
	maxmp = 20

	gold = 100

	entering_text = False
	entered_text = ""

	inv = []

# Game variables
# Maps
town = Level(24, 24)
town.clear(spr.GRASS)
town.tiles[6][8].items.append(Item(spr.MUD_FLOOR, name="slab of dried mud", value=9001))
town.tiles[6][8].items.append(Item(spr.GOLD_NUGGET, name="gold nugget", value=9001))
for i in xrange(10):
	town.tiles[3][3+i].items.append(Item(spr.GOLD_NUGGET, name="gold nugget", value=9001))
town.tiles[5][5].items.append(Item(spr.SHOP, name="humble shop", holdable=False))
town.tiles[12][12].items.append(Item(spr.WELL, name="well of doom", holdable=False))

shop = Level(16, 16, is_shop=True)
shop.clear(spr.ROCK)
shop.tiles[0][0].items.append(Item(spr.SHOP, holdable=False))

well = [Level(24, 24) for i in xrange(20)]
well[0].generate_dungeon()

shop.portals[(0,0)] = Portal(town, 5, 5, "the town")
town.portals[(12, 12)] = Portal(well[0], 5, 5, "the well of doom")
town.portals[(5, 5)] = Portal(shop, 0, 0, "the humble shop")
well[0].portals[(5, 5)] = Portal(town, 12, 12, "the town")

cur_level = town

def init():
	display.init_window((800, 600), title='Well Done')
	display.init_sprites('sprites.png', 16, 16)
	display.init_font('runescape_uf.ttf')
	display.init_msg_log(780)
	# enable key repeat
	pygame.key.set_repeat(1, 200)

def redraw():
	display.clear((64,64,64))
	# Draw the map
	display.fill_rect((0,0, 400,400), (0,0,0))
	for x,y in ((x,y) for x in xrange(-12, 13) for y in xrange(-12, 13)):
		# for each tile in the player's vision:
		ax, ay = x+Player.x, y+Player.y
		if 0 <= ax < cur_level.width and 0 <= ay < cur_level.height:
			cur_tile = cur_level.tiles[ax][ay]
			# draw the terrain
			display.draw_sprite(cur_tile.img, ((x+12)*16, (y+12)*16))
			# draw each item, starting with the ones on the bottom of the pile
			for i in cur_tile.items:
				display.draw_sprite(i.img, ((x+12)*16, (y+12)*16))

	# Draw player's sprite (always at center of map)
	display.draw_sprite(spr.PLAYER, (16*12, 16*12))

	# Message log
	display.fill_rect((5,405, 790,190), (32,32,32))
	display.msg_log.draw((10, 410), 160)

	# Player text entry
	if Player.entering_text:
		display.fill_rect((9,575, 782,16), (64,64,64))
		display.draw_text(Player.entered_text, (12,576))

	# Draw player's health bar
	display.fill_rect((400,0, 400,16), (128,0,0))
	display.fill_rect((400,0, 400*(Player.hp/Player.maxhp), 16), (255,0,0))
	display.draw_text('HP: %d/%d' % (Player.hp, Player.maxhp), (405, 1))
	
	# Player's wealth and inventory
	display.draw_text('Gold: %d' % (Player.gold), (405, 40), (255,255,0))

	INV_X = 410
	INV_Y = 80
	for i in xrange(75):
		x,y = i%15, i//15
		display.draw_rect((INV_X+x*19, INV_Y+y*19, 18, 18), (255,255,255))
	for i,item in enumerate(Player.inv):
		x,y = i%15, i//15
		display.draw_sprite(item.img, (INV_X+1+x*19, INV_Y+1+y*19))

	display.fill_rect((400,16, 400,16), (192,192,192))
	display.fill_rect((400,16, 400*(Player.mp/Player.maxmp), 16), (255,255,0))
	display.draw_text('ENERGY: %d/%d' % (Player.mp, Player.maxmp), (405, 17), (0,0,0))
	display.update()

init()

display.msg("Well Done")
display.msg("You have arrived in the village of %s, seeking the treasures that await you in its well." % generate_name().capitalize())

redraw()

def text_input():
	Player.entering_text = True
	Player.entered_text = ""
	redraw()
	while True:
		event = pygame.event.wait()
		if event.type == KEYDOWN:
			if event.key == K_RETURN:
				Player.entering_text = False
				return Player.entered_text
			entered_char = event.unicode
			if entered_char.isalnum() or entered_char.isspace():
				Player.entered_text += entered_char
			elif event.key == K_BACKSPACE:
				Player.entered_text = Player.entered_text[:-1]
			redraw()

while True:
	# The good old infinite game loop.
	event = pygame.event.wait()
	if event.type == KEYDOWN:
		old_x = Player.x
		old_y = Player.y
		if event.key in keys_n + keys_ne + keys_nw:
			Player.y -= 1
		if event.key in keys_e + keys_se + keys_ne:
			Player.x += 1
		if event.key in keys_s + keys_se + keys_sw:
			Player.y += 1
		if event.key in keys_w + keys_nw + keys_sw:
			Player.x -= 1
		if Player.x != old_x or Player.y != old_y:
			if not cur_level.passable(Player.x, Player.y):
				Player.x = old_x
				Player.y = old_y
			else:
				itemlist = ', '.join(item.name for item in cur_level.tiles[Player.x][Player.y].items)
				if itemlist:
					display.msg('You see here: %s' % itemlist)

		if event.key == K_COMMA:
			items = cur_level.tiles[Player.x][Player.y].items
			for i in range(len(items)-1, -1, -1):
				if items[i].holdable:
					Player.inv.append(items[i])
					display.msg('You take the %s.' % items[i].name)
					del items[i]
					break
			else:
				display.msg('There is nothing here to take.')
		elif event.key == K_a:
			if (Player.x, Player.y) in cur_level.portals:
				portal = cur_level.portals[(Player.x, Player.y)]
				cur_level = portal.dest_level
				Player.x = portal.dest_x
				Player.y = portal.dest_y
				Player.mp -= 1
				display.msg('You enter %s.' % portal.name)
		elif event.key == K_RETURN:
			text = text_input()
			display.msg('What is a %s?' % text)
		redraw()
	elif event.type == QUIT:
		pygame.quit()
		sys.exit()
