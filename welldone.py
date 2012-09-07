import sys
import random
import pygame
from pygame.locals import *
# Our very own display module that manages all graphical things.
import display
# Game modules
import sprites as spr
from level import Item, Tile, Portal, Creature, Level
from my_geom import range2d, box2d, line2d
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
keys_action = [K_a, K_KP5]

keys_n_all = keys_n + keys_ne + keys_nw
keys_e_all = keys_e + keys_se + keys_ne
keys_s_all = keys_s + keys_se + keys_sw
keys_w_all = keys_w + keys_nw + keys_sw

class Player(Creature):
	mp = 20.0
	maxmp = 20
	gold = 100
	entering_text = False
	entered_text = ""
	inv = []

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
	for x,y in box2d(-12, -12, 25, 25):
		# for each tile in the player's map range:
		ax, ay = x+Player.x, y+Player.y
		if 0 <= ax < Player.cur_level.width and 0 <= ay < Player.cur_level.height:
			cur_tile = Player.cur_level.tiles[ax][ay]
			if Player.cur_level.sight(Player.x, Player.y, ax, ay):
				cur_tile.memorized = True
				# draw the terrain
				display.draw_sprite(cur_tile.img, ((x+12)*16, (y+12)*16))
				# draw each item, starting with the ones on the bottom of the pile
				for i in cur_tile.items:
					display.draw_sprite(i.img, ((x+12)*16, (y+12)*16))
			elif cur_tile.memorized:
				display.draw_sprite(cur_tile.img, ((x+12)*16, (y+12)*16), sheet=display.sprites_grey)

	# Draw creatures
	for c in Player.cur_level.creatures:
		sx, sy = c.x-Player.x+12, c.y-Player.y+12
		if 0 <= sx < 25 and 0 <= sy < 25:
			print(c)
			display.draw_sprite(c.img, (sx*16, sy*16))

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

	INV_X = 420
	INV_Y = 190
	INV_W = 10
	INV_H = 10
	# inventory slot boxes
	for i in xrange(INV_W*INV_H):
		x,y = i%INV_W, i//INV_W
		display.draw_rect((INV_X+x*21, INV_Y+y*21, 20, 20), (255,255,255))
	# inventory axis labels (for EZ-dropping/selling)
	for i in xrange(INV_W):
		display.draw_text('%d' % i, (INV_X+i*21+6, INV_Y-15))
	for i in xrange(INV_H):
		display.draw_text('%d' % i, (INV_X-9, INV_Y+i*21+3))

	# actual items
	for i,item in enumerate(Player.inv):
		x,y = i%INV_W, i//INV_W
		display.draw_sprite(item.img, (INV_X+2+x*21, INV_Y+2+y*21))

	display.fill_rect((400,16, 400,16), (192,192,192))
	display.fill_rect((400,16, 400*(Player.mp/Player.maxmp), 16), (255,255,0))
	display.draw_text('ENERGY: %d/%d' % (Player.mp, Player.maxmp), (405, 17), (0,0,0))
	display.update()


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
			elif event.key == K_ESCAPE:
				Player.entering_text = False
				Player.entered_text = ""
				return ""
			elif event.key == K_BACKSPACE:
				Player.entered_text = Player.entered_text[:-1]

			entered_char = event.unicode
			if entered_char.isalnum() or entered_char.isspace():
				Player.entered_text += entered_char
			redraw()
		else:
			# Give any events not caught by text_input() to the
			# standard event handler
			handle_event_standard(event)

def list_items():
	items = Player.cur_level.tiles[Player.x][Player.y].items
	ilist = []
	for item in items:
		if Player.cur_level.is_shop and item.holdable: ilist.append('%s (%d g)' % (item.name, item.value))
		else: ilist.append('%s' % item.name)

	itemlist = ', '.join(ilist)
	if ilist:
		display.msg('You see here: %s' % itemlist)

def take_item():
	items = Player.cur_level.tiles[Player.x][Player.y].items

	for i in range(len(items)-1, -1, -1):
		if items[i].holdable:
			item = items[i]
			if Player.cur_level.is_shop:
				shop_ask = item.value
				if Player.gold >= shop_ask:
					display.msg('Buy the %s for %d gold? (y/N)' % (item.name, shop_ask))
					response = text_input()
					if response.lower().startswith('y'):
						display.msg('You bought it!')
						Player.gold -= shop_ask
						Player.inv.append(item)
						del items[i]
					return
				else:
					# Cannot afford shop item
					display.msg('You cannot afford the %s! It costs %d gold.' % (item.name, shop_ask))
					return
			else:
				# not a shop; just take the item!
				display.msg('You take the %s.' % item.name)
				Player.inv.append(item)
				del items[i]
				return
	else:
		display.msg('There is nothing here to take.')
		return

def drop_item():
	verb = 'Drop'
	if Player.cur_level.is_shop:
		verb = 'Sell'

	itemlist = []
	for i,item in enumerate(Player.inv):
		if Player.cur_level.is_shop: itemlist.append('%d: %s (%d g)' % (i, item.name, item.value))
		else: itemlist.append('%d: %s' % (i, item.name))

	display.msg(verb + ' which item? ' + ', '.join(itemlist))
	response = text_input()

	try:
		rid = int(response)
		item = None
		if 0 <= rid < len(Player.inv):
			item = Player.inv[rid]
			if Player.cur_level.is_shop:
				display.msg('Sold for %d gold.' % item.value)
				Player.gold += item.value
			Player.inv.pop(rid)
			Player.cur_level.tiles[Player.x][Player.y].items.append(item)
		else:
			raise ValueError
	except ValueError:
		display.msg('Invalid item.')
		return

def cycle_items():
	items = Player.cur_level.tiles[Player.x][Player.y].items
	items.append(items.pop(0))
	list_items()

def handle_event_standard(event):
	if event.type == KEYDOWN:

		# Movement keys
		old_x = Player.x
		old_y = Player.y
		if event.key in keys_n_all:
			Player.y -= 1
		if event.key in keys_e_all:
			Player.x += 1
		if event.key in keys_s_all:
			Player.y += 1
		if event.key in keys_w_all:
			Player.x -= 1
		# if the player has moved...
		if Player.x != old_x or Player.y != old_y:
			if not Player.cur_level.passable(Player.x, Player.y):
				# move player back to original position
				Player.x = old_x
				Player.y = old_y
				return

			# list items on floor
			list_items()
			
			# recalculate vision
			
			redraw()
			return

		# Take/buy item
		if event.key == K_COMMA:
			take_item()
			redraw()
			return

		# Drop/sell item
		if event.key == K_d:
			drop_item()
			redraw()
			return

		# Cycle items on ground
		if event.key == K_c:
			cycle_items()
			redraw()
			return

		# Apply object (usually to enter a portal)
		elif event.key in keys_action:
			if (Player.x, Player.y) in Player.cur_level.portals:
				portal = Player.cur_level.portals[(Player.x, Player.y)]
				Player.cur_level = portal.dest_level
				Player.x = portal.dest_x
				Player.y = portal.dest_y
				Player.mp -= 1
				display.msg('You enter %s.' % portal.name)
				redraw()
			return

		# Enter (to manually enter commands)
		elif event.key == K_RETURN:
			text = text_input()
			display.msg('What is a %s?' % text)
			redraw()
			return
		
		elif event.key == K_0:
			well[19].generate_dungeon()
			display.msg('You feel the dungeons shifting beneath your feet.')
			redraw()
			return

	elif event.type == QUIT:
		pygame.quit()
		sys.exit()
		return

init()

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
town.creatures.append(Creature(town, 22, 22, 10, 10))

shop = Level(16, 16, is_shop=True)
shop.generate_shop()
shop.add_item((1,1), Item(spr.DOOR, holdable=False))

Player = Player(town, 10, 10, 60, 100)

well = [Level(13+i*2, 13+i*2) for i in xrange(20)]
prev_up = None
prev_down = None
for i in xrange(20):
	well[i].generate_dungeon()
	mr = well[i].get_main_region()
	treasures = random.sample(mr, 5)
	for loc in treasures:
		well[i].add_item(loc, Item(spr.GOLD_NUGGET, name="gold nugget", value=100))

	if i == 19:
		pass
	else:
		to_up, to_down = random.sample(mr, 2)
		well[i].add_item(to_up, Item(spr.ROPE_UP, holdable=False))
		well[i].add_item(to_down, Item(spr.WELL, holdable=False))
		if i == 0:
			well[i].portals[to_up] = Portal(town, 12, 12)
			town.portals[(12,12)] = Portal(well[0], *to_up)
		else:
			well[i-1].portals[prev_down] = Portal(well[i], *to_up)
			well[i].portals[to_up] = Portal(well[i-1], *prev_down)
		prev_up = to_up
		prev_down = to_down

shop.portals[(1,1)] = Portal(town, 5, 5, "the town")
town.portals[(5, 5)] = Portal(shop, 0, 0, "the humble shop")
display.msg("Well Done")
display.msg("You have arrived in the village of %s, seeking the treasures that await you in its well." % generate_name().capitalize())

redraw()

while True:
	# The good old infinite game loop.
	event = pygame.event.wait()
	handle_event_standard(event)
