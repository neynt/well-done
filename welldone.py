import sys
import random
import pygame
from pygame.locals import *
# Our very own display module that manages all graphical things.
import display
# Game modules
from my_geom import range2d, box2d, line2d, square2d
import sprites as spr
from creature import Creature, Player
from world import town, shop, well
from objects import Item, Tile, Portal
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

def init():
	display.init_window((800, 600), title='Well Done')
	display.init_sprites('sprites.png', 16, 16)
	display.init_font('runescape_uf.ttf')
	display.init_msg_log(780)
	# enable key repeat
	pygame.key.set_repeat(1, 200)

	# Gold cheat:
	#for i in xrange(10):
	#	town.tiles[3][3].items.append(Item(spr.GOLD_NUGGET, name="gold nugget", value=9001))
	town.add_item((12,12), Item(spr.WELL, name="well of doom", holdable=False))

	prev_up = None
	prev_down = None
	for i in xrange(20):
		well[i].generate_dungeon()
		mr = well[i].get_main_region()

		treasures = random.sample(mr, 5)
		for loc in treasures:
			well[i].add_item(loc, Item(spr.GOLD_NUGGET, name="gold nugget", value=100))

		mobs = random.sample(mr, 5)
		for mob in mobs:
			well[i].creatures.append(Creature(well[i], *mob, hp=10, maxhp=10, name="malicious slime"))

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

	town.portals[(5, 5)] = Portal(shop[0], 1, 1, "the humble shop")
	town.creatures.append(Player)

	display.msg("Well Done")
	display.msg("You have arrived in the village of %s, seeking the treasures that await you in its well." % generate_name().capitalize())

	redraw()

def redraw():
	display.clear((64,64,64))
	# Draw the map
	display.fill_rect((0,0, 400,400), (0,0,0))

	Player.cur_level.recalc_light()

	for x,y in box2d(-12, -12, 25, 25):
		# for each tile in the player's map range:
		ax, ay = x+Player.x, y+Player.y
		if Player.cur_level.in_bounds(ax, ay):
			cur_tile = Player.cur_level.tiles[ax][ay]
			seen = Player.can_see(ax, ay)
			if seen == 1: # Illuminated and in LoS
				cur_tile.memorized = True
				# draw the terrain
				display.draw_sprite(cur_tile.img, ((x+12)*16, (y+12)*16))
				# draw each item, starting with the ones on the bottom of the pile
				for i in cur_tile.items:
					display.draw_sprite(i.img, ((x+12)*16, (y+12)*16))
			elif seen == 2: # In night vision range
				cur_tile.memorized = True
				display.draw_sprite(cur_tile.img, ((x+12)*16, (y+12)*16), sheet=display.sprites_blue)
				# draw each item, starting with the ones on the bottom of the pile
				for i in cur_tile.items:
					display.draw_sprite(i.img, ((x+12)*16, (y+12)*16), sheet=display.sprites_blue)
			elif cur_tile.memorized:
				display.draw_sprite(cur_tile.img, ((x+12)*16, (y+12)*16), sheet=display.sprites_grey)
				for i in cur_tile.items:
					if not i.holdable:
						display.draw_sprite(i.img, ((x+12)*16, (y+12)*16), sheet=display.sprites_grey)

	# Draw creatures, including the player
	for c in Player.cur_level.creatures:
		sx, sy = c.x-Player.x+12, c.y-Player.y+12
		if 0 <= sx < 25 and 0 <= sy < 25 and Player.can_see(c.x, c.y):
			display.draw_sprite(c.img, (sx*16, sy*16))
			if c != Player:
				# health bar
				display.fill_rect((sx*16, sy*16, 16*(float(c.hp)/c.maxhp), 1), (255,0,0))

	# Message log
	display.fill_rect((5,405, 790,190), (32,32,32))
	display.msg_log.draw((10, 410), 160)

	# Player text entry
	if Player.entering_text:
		display.fill_rect((9,575, 782,16), (64,64,64))
		display.draw_text(Player.entered_text, (12,576))

	# Draw player's health bar
	display.fill_rect((400,0, 400,16), (128,0,0))
	display.fill_rect((400,0, 400*(float(Player.hp)/Player.maxhp), 16), (255,0,0))
	display.draw_text('HP: %d/%d' % (Player.hp, Player.maxhp), (405, 1))
	# energy bar
	display.fill_rect((400,16, 400,16), (192,192,192))
	display.fill_rect((400,16, 400*(float(Player.mp)/Player.maxmp), 16), (255,255,0))
	display.draw_text('ENERGY: %d/%d' % (Player.mp, Player.maxmp), (405, 17), (0,0,0))
	
	# Player's wealth and inventory
	display.draw_text('Gold: %d' % (Player.gold), (405, 40), (255,255,0))
	display.draw_text('Inventory', (410, 156))
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

	# Equipment
	display.draw_text('Equipment', (660, 200))
	for i,item in enumerate(Player.equipment):
		display.draw_text('%d: %s' % (i,item.name), (660, 216+i*16))

	# Stats
	display.draw_text('Attack damage: %d-%d' % (Player.min_atk, Player.max_atk), (420, 60))
	display.draw_text('Attack time: %d' % Player.attack_time, (420, 76))
	display.draw_text('Move time: %d' % Player.move_time, (420, 92))

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

def list_ground_items():
	items = Player.cur_level.tiles[Player.x][Player.y].items
	ilist = []
	for item in items:
		if Player.cur_level.is_shop and item.holdable: ilist.append('%s (%d g)' % (item.name, item.value))
		else: ilist.append('%s' % item.name)

	itemlist = ', '.join(ilist)
	if ilist:
		display.msg('You see here: %s' % itemlist, color=(128,128,128))

def prompt_item(items, verb='Apply', format=lambda x: '%d: %s' % (x[0], x[1].name)):
	items = list(items)
	ilist = []
	for x in items:
		ilist.append(format(x))
	display.msg("%s which item? %s" % (verb, ', '.join(ilist)))

	response = text_input()
	try:
		rid = int(response)
		if rid in [i[0] for i in items]:
			return rid
		else:
			raise ValueError
	except ValueError:
		display.msg('Invalid item.')
		redraw()
		return None

def use_item():
	items = enumerate(Player.inv)
	i = prompt_item(items, 'Use')
	# TODO: Move item usage effects to Item class (somehow)
	if i is not None:
		item = Player.inv[i]
		if item.name == "town portal scroll":
			display.msg("You start to channel the spell...")
			Player.cur_level.advance_ticks(1000)
			display.msg("Your surroundings suddenly change.")
			Player.inv.pop(i)
			Player.cur_level.creatures.remove(Player)
			Player.cur_level = town
			town.creatures.append(Player)
			Player.x = 12
			Player.y = 12
		else:
			display.msg("There is no obvious use for this item.")

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
	if len(Player.inv) == 0:
		display.msg('Your inventory is empty.')
		return

	verb = 'Drop'
	items = enumerate(Player.inv)
	if Player.cur_level.is_shop:
		i = prompt_item(items, "Sell", format=lambda x: '%d: %s (%d g)' % (x[0], x[1].name, x[1].value))
	else:
		i = prompt_item(items, "Drop")

	if i is not None:
		item = Player.inv.pop(i)
		if Player.cur_level.is_shop:
			display.msg('Sold for %d gold.' % item.value)
			Player.gold += item.value
		Player.cur_level.add_item((Player.x, Player.y), item)

def cycle_items():
	items = Player.cur_level.tiles[Player.x][Player.y].items
	if items:
		items.append(items.pop(0))
		list_ground_items()

def handle_event_standard(event):
	if event.type == KEYDOWN:

		if not Player.alive:
			if event.key in keys_action:
				Player.alive = True
				Player.hp = Player.maxhp
				Player.cur_level = town
				town.creatures.append(Player)
				Player.x = 12
				Player.y = 12
				display.msg("The light fades and you return to the world.")
			else:
				display.msg("You are dead. Press 'a' to revive.", color=(192,64,64))
			redraw()
			return

		# Movement keys
		new_x = Player.x
		new_y = Player.y
		if event.key in keys_n_all:
			new_y -= 1
		if event.key in keys_e_all:
			new_x += 1
		if event.key in keys_s_all:
			new_y += 1
		if event.key in keys_w_all:
			new_x -= 1
		# if the player has moved...
		if Player.x != new_x or Player.y != new_y:
			if not Player.cur_level.passable(new_x, new_y):
				occupant = Player.cur_level.occupant_at(new_x, new_y)
				if occupant:
					dmg = Player.attack(occupant)
					display.msg('You slice the %s for %d damage!' % (occupant.name, dmg), color=(0,255,255))
					if not occupant.alive:
						display.msg('You have murdered it, earning 50 gold!', color=(255,255,0))
						Player.gold += 50
				else:
					pass
				redraw()
				return

			Player.x = new_x
			Player.y = new_y

			Player.cur_level.advance_ticks(Player.move_time)

			# list items on floor
			list_ground_items()
			
			# recalculate vision
			# ... done in redraw() for now
			# TODO: move vision somewhere more efficient
			redraw()
			return

		# Use item in inventory
		elif event.key == K_v:
			use_item()
			redraw()
			return

		# Take/buy item
		elif event.key == K_COMMA:
			take_item()
			redraw()
			return

		# Drop/sell item
		elif event.key == K_d:
			drop_item()
			redraw()
			return

		# Cycle items on ground
		elif event.key == K_c:
			cycle_items()
			redraw()
			return

		# Wait one step
		elif event.key == K_PERIOD:
			Player.cur_level.advance_ticks(100)
			redraw()

		# Rest until full hp
		elif event.key == K_s:
			display.msg("You begin to sleep...")
			while Player.hp != Player.maxhp and Player.alive:
				Player.cur_level.advance_ticks(10000)
			display.msg("You stop sleeping.")
			redraw()

		# Apply object on ground (aka enter a portal)
		elif event.key in keys_action:
			if (Player.x, Player.y) in Player.cur_level.portals:
				portal = Player.cur_level.portals[(Player.x, Player.y)]

				Player.cur_level.creatures.remove(Player)
				portal.dest_level.creatures.append(Player)

				Player.cur_level = portal.dest_level
				Player.x = portal.dest_x
				Player.y = portal.dest_y
				Player.mp -= 1
				display.msg('You enter %s.' % portal.name)
				redraw()
			return

		# Equip/remove items
		elif event.key == K_e:
			if len(Player.equipment) >= 5:
				display.msg("You have already equipped 5 items.")
				redraw()
				return

			eq = [(i,item) for i,item in enumerate(Player.inv) if item.equippable]

			if len(eq) == 0:
				display.msg("You don't have any equipment to equip.")
				redraw()
				return

			i = prompt_item(eq, "Equip")
			if i is not None:
				item = Player.inv.pop(i)
				Player.equipment.append(item)
				display.msg("You equip the %s." % item.name)
				Player.recalc_stats()
				redraw()
			return

		elif event.key == K_r:
			if len(Player.equipment) == 0:
				display.msg("You have nothing equipped.")
				redraw()
				return

			eq = enumerate(Player.equipment)
			i = prompt_item(eq, "Remove")
			if i is not None:
				item = Player.equipment.pop(i)
				Player.inv.append(item)
				display.msg("You remove the %s." % item.name)
				Player.recalc_stats()
				redraw()
			return

		# Examine item
		elif event.key == K_x:
			items = enumerate(Player.inv)
			i = prompt_item(items, "Examine")
			if i is not None:
				display.msg(Player.inv[i].describe())
			redraw()

		# Enter (to manually enter commands)
		elif event.key == K_RETURN:
			text = text_input()
			display.msg('Just showing off that I can accept text input. You typed: %s' % text)
			redraw()
			return

	elif event.type == QUIT:
		pygame.quit()
		sys.exit()
		return

# BAYLIFE YOLO
if __name__ == '__main__':
	init()
	while True:
		# The good old infinite game loop.
		event = pygame.event.wait()
		handle_event_standard(event)
