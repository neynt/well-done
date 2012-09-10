import sys
import random
import pygame
from pygame.locals import *
# Our very own display module that manages all graphical things.
import display
# Game modules
from my_geom import range2d, box2d, line2d, square2d
import sprites as spr
from creature import Creature
from player import Player
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
	town.creatures.append(Player)

	prev_up = None
	prev_down = None

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

	# Equipment (garb)
	EQ_X = 640
	EQ_Y = 200
	display.draw_text('Your equipment:', (EQ_X, EQ_Y))
	if Player.equipment:
		for i,item in enumerate(Player.equipment):
			EQ_Y += 16
			if item.equip_slot:
				display.draw_text('%d: %s (%s)' % (i,item.name,item.equip_slot), (EQ_X, EQ_Y))
			else:
				display.draw_text('%d: %s' % (i,item.name), (EQ_X, EQ_Y))
	else:
		EQ_Y += 16
		display.draw_text('None!', (EQ_X, EQ_Y))

	EQ_Y += 16
	# also write empty slots under garb
	for slot in Player.equip_slots.iterkeys():
		fs = Player.equip_slots[slot] - Player.equipped[slot]
		if fs:
			EQ_Y += 16
			if fs == 1: pl = ''
			else: pl = 's'
			display.draw_text('%d free slot%s (%s)' % (fs,pl,slot), (EQ_X, EQ_Y))

	# Stats
	display.draw_text('Attack damage: %d-%d' % (Player.min_atk, Player.max_atk), (420, 60))
	display.draw_text('Attack speed: %d' % (10000/Player.attack_time), (420, 76))
	display.draw_text('Move speed: %d' % (10000/Player.move_time), (420, 92))

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

def index_top_item(items):
	for i in range(len(items)-1, -1, -1):
		if items[i].holdable:
			return i
	return None

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
	display.msg("%s which item? %s" % (verb, ', '.join(ilist)), color=(0,255,255))

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
	i = prompt_item(items, 'In[v]oke')
	# TODO: Move item usage effects to Item class (somehow)
	if i is not None:
		item = Player.inv[i]
		if item.action:
			if item.action(Player):
				Player.inv.pop(i)
		else:
			display.msg("There is no obvious use for this item.")

def take_item():
	items = Player.cur_level.tiles[Player.x][Player.y].items
	i = index_top_item(items)
	if i is not None:
		item = items[i]
		if Player.cur_level.is_shop:
			shop_ask = item.value
			if Player.gold >= shop_ask:
				display.msg('Buy the %s for %d gold? (y/N)' % (item.name, shop_ask), color=(0,255,255))
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

		# Use item in inventory
		elif event.key == K_v:
			use_item()

		# Take/buy item
		elif event.key == K_g:
			take_item()

		# Drop/sell item
		elif event.key == K_d:
			drop_item()

		# Cycle items on ground
		elif event.key == K_c:
			cycle_items()

		# Wait one step
		elif event.key == K_PERIOD:
			Player.cur_level.advance_ticks(100)

		# Rest until full hp
		elif event.key == K_s:
			display.msg("You sleep for 5000 ticks.")
			Player.cur_level.advance_ticks(5000)

		# Apply object on ground (aka enter a portal)
		elif event.key in keys_action:
			if (Player.x, Player.y) in Player.cur_level.portals:
				portal = Player.cur_level.portals[(Player.x, Player.y)]
				if portal.name == "the well of doom":
					max_depth = max([i+1 for i,w in enumerate(well) if w.visited] + [0])
					if max_depth > 1:
						display.msg("Which level? (max: %d)" % max_depth)
						response = text_input()
						try:
							lv = int(response)
							if 2 <= lv <= max_depth:
								# find the entry point in the upper level's portals
								for p in well[lv-2].portals.values():
									if p.name == "well level %d" % lv:
										portal = p
										break
								else:
									display.msg("critical error!")
							elif lv == 1:
								pass
							else:
								raise ValueError

						except ValueError:
							display.msg("Invalid level.")
							redraw()
							return
					# if max depth is <= 1, then just go to first level of well

				Player.change_level_to(portal.dest_level, portal.dest_x, portal.dest_y)
				display.msg('You enter %s.' % portal.name)

		# Equip/remove items
		elif event.key == K_e:
			if len(Player.equipment) >= 10:
				display.msg("You may only equip 10 items.")
			else:
				eq = [(i,item) for i,item in enumerate(Player.inv) if item.equippable]
				if len(eq) == 0:
					display.msg("You don't have any equipment to equip.")
				else:
					i = prompt_item(eq, "Equip")
					if i is not None:
						display.msg(Player.equip(i))

		elif event.key == K_r:
			if len(Player.equipment) == 0:
				display.msg("You have nothing equipped.")
			else:
				eq = enumerate(Player.equipment)
				i = prompt_item(eq, "Remove")
				if i is not None:
					display.msg(Player.remove_equipment(i))

		# examine item in inventory
		elif event.key == K_i:
			items = enumerate(Player.inv)
			if items:
				i = prompt_item(items, "Inspect")
				if i is not None:
					display.msg(Player.inv[i].describe())
			else:
				display.msg("You are not holding any items to inspect.")

		# examine item on ground
		elif event.key == K_x:
			items = Player.cur_level.tiles[Player.x][Player.y].items
			if items:
				i = prompt_item(enumerate(items), "Examine")
				if i is not None:
					display.msg(items[i].describe())
			else:
				display.msg("Nothing here to examine.")

		# Enter (to manually enter commands)
		elif event.key == K_RETURN:
			text = text_input()
			display.msg('Just showing off that I can accept text input. You typed: %s' % text)

		redraw()
		return
	else:
		handle_event_universe(event)

def handle_event_dead(event):
	if event.type == KEYDOWN:
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
	else:
		handle_event_universe(event)
	redraw()
	return

def handle_event_universe(event):
	if event.type == QUIT:
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
		if Player.won:
			Player.hp = -666
			Player.alive = False
			Player.cur_level.advance_ticks(0)
			Player.cur_level.illuminated = False
			display.msg("When it got exposed to daylight, the Triforce went berserk and killed everyone forever. Then it blew up the sun.", (255,0,255))
			display.msg("Well done.", (255,0,0))
			display.msg("The end. Thanks for playing!")
			redraw()
			while True:
				event = pygame.event.wait()
				handle_event_universe(event)
		if not Player.alive:
			display.msg("You have died.", (255,0,0))
			while not Player.alive:
				event = pygame.event.wait()
				handle_event_dead(event)
