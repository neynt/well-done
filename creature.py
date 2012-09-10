import math
import random
from my_geom import square2d, box2d, sign

import display

import sprites as spr

class Creature:
	""" An entity that stores its own location, and can change it. """
	def __init__(self, cur_level, x, y, hp, maxhp, name='generic creature', gold=10, equip_slots={}, img=spr.SLIME):
		self.name = name
		self.img = img
		self.x = x
		self.y = y
		self.won = False
		self.alive = True
		self.hp = hp
		self.maxhp = maxhp

		self.move_time = 100
		self.attack_time = 100

		self.min_atk = 1
		self.max_atk = 2

		self.cur_level = cur_level
		self.delay = 0

		# amount of gold dropped by the creature
		self.gold = gold

		# The distance the creature can see without light.
		self.vision_range = 1.8

		# The coordinate that this creature will path to.
		self.goal = None

		# Body slots (for equipment)
		self.equip_slots = equip_slots
		# body parts that already have equipment
		self.equipped = {b:0 for b,_ in equip_slots.items()}

		# Inventory and equipment.
		self.inv = []
		self.equipment = []

	def take_damage(self, amount):
		self.hp -= amount
		if self.hp <= 0:
			self.alive = False
		return amount

	def heal(self, amount):
		if self.hp + amount > self.maxhp:
			amount = self.maxhp-self.hp
		self.hp = self.hp + amount
		return amount

	def attack(self, target):
		dmg = random.randint(self.min_atk, self.max_atk)
		target.take_damage(dmg)
		self.delay += self.attack_time
		return dmg

	def field_of_view(self):
		for x,y in box2d(-12, -12, 25, 25):
			ax, ay = x+self.x, y+self.y
			if not self.cur_level.in_bounds(ax, ay):
				continue
			if self.can_see(ax, ay):
				yield (ax,ay)

	def move_toward(self, x, y):
		dx = sign(x - self.x)
		dy = sign(y - self.y)
		new_x = self.x + dx
		new_y = self.y + dy
		self.delay += self.move_time

		if self.cur_level.passable(new_x, new_y):
			self.x = new_x
			self.y = new_y

	def advance_ticks(self, num_ticks):
		self.delay -= num_ticks
		while self.delay <= 0:
			fov = self.field_of_view()
			target = None

			for c in self.cur_level.creatures:
				if c.name == 'Player' and (c.x, c.y) in fov:
					target = c
					self.goal = (target.x, target.y)

			if target and max(abs(target.x-self.x), abs(target.y-self.y)) == 1:
				dmg = self.attack(target)
				display.msg("The slime slimes you for %d damage!" % dmg, color=(255,0,0))

			elif self.goal:
				self.move_toward(*self.goal)
			else:
				# just stay still
				self.delay += 100

	def can_see(self, x, y):
		# If target is in line of sight and illuminated
		if self.cur_level.sight(self.x, self.y, x, y) and self.cur_level.tiles[x][y].lit:
			return 1

		# If target is within creature's "night vision" range
		if self.cur_level.sight(self.x, self.y, x, y, self.vision_range):
			return 2

		return False

class PlayerCreature(Creature):
	mp = 20.0
	maxmp = 20.0
	entering_text = False
	entered_text = ""

	def take_damage(self, amount):
		self.hp -= amount
		if self.hp <= 0:
			self.alive = False
		return amount

	def attack(self, target):
		dmg = random.randint(self.min_atk, self.max_atk)
		taken = target.take_damage(dmg)
		display.msg('You slice the %s for %d damage!' % (target.name, taken), color=(0,255,0))
		self.cur_level.advance_ticks(self.move_time)
		return dmg

	def advance_ticks(self, num_ticks):
		self.mp = min(self.maxmp, self.mp+(self.maxmp/25000*num_ticks))
		self.hp = min(self.maxhp, self.hp+(self.maxhp/25000*num_ticks))

	# Recalculate stats. Should be called after equipment changes.
	def recalc_stats(self):
		self.maxhp = 5.0
		self.maxmp = 20.0
		self.min_atk = 2
		self.max_atk = 4
		self.attack_time = 100
		self.move_time = 100
		self.vision_range = 1.8
		for i in self.equipment:
			for attr,val in i.attr.items():
				if attr == 'attack_damage':
					a,b = val
					self.min_atk += a
					self.max_atk += b
				elif attr == 'attack_haste':
					self.attack_time *= val
				elif attr == 'health':
					self.maxhp += val
				elif attr == 'energy':
					self.maxmp += val
				elif attr == 'movement_haste':
					self.move_time *= val
				elif attr == 'night_vision':
					self.vision_range = math.sqrt(self.vision_range**2 + val**2)
		return

	def equip(self, i):
		item = self.inv[i]
		sl = item.equip_slot
		# Item has an equip slot?
		if sl:
			# I have that equip slot?
			if sl in self.equip_slots:
				# My equip slot isn't already filled?
				max_in_slot = self.equip_slots[sl]
				cur_in_slot = self.equipped[sl]
				if cur_in_slot >= max_in_slot:
					return "You already have enough items on your %s." % sl
				else:
					self.equipped[sl] += 1
			else:
				return "You do not have a %s." % sl

		# now we're sure the item can be equipped
		self.inv.pop(i)
		self.equipment.append(item)
		self.recalc_stats()
		return "You equip the %s." % item.name

	def remove_equipment(self, i):
		item = self.equipment.pop(i)
		sl = item.equip_slot

		# Item has an equip slot?
		if sl:
			self.equipped[sl] -= 1

		self.inv.append(item)
		self.recalc_stats()
		return "You remove the %s." % item.name

	def change_level_to(self, dest, x, y):
		self.cur_level.creatures.remove(self)
		dest.creatures.append(self)

		self.x = x
		self.y = y

		self.cur_level = dest
		dest.visited = True

		# shabby last-minute win condition
		if (dest.name == "town" and (
			any(item.name == 'triforce' for item in self.inv) or
			any(item.name == 'triforce' for item in self.equipment)
		)):
			self.won = True