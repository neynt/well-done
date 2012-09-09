import math
import random
from my_geom import square2d, box2d, sign

import display

import sprites as spr
from world import town

class Creature:
	""" An entity that stores its own location, and can change it. """
	def __init__(self, cur_level, x, y, hp, maxhp, name='generic creature', img=spr.SLIME):
		self.name = name
		self.img = img
		self.x = x
		self.y = y
		self.alive = True
		self.hp = hp
		self.maxhp = maxhp

		self.move_time = 100
		self.attack_time = 100

		self.min_atk = 1
		self.max_atk = 2

		self.cur_level = cur_level
		self.delay = 0

		# The distance the creature can see without light.
		self.vision_range = 1.8

		self.inv = []

	def take_damage(self, amount):
		self.hp -= amount
		if self.hp <= 0:
			self.alive = False

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

	def advance_ticks(self, num_ticks):
		self.delay -= num_ticks
		while self.delay <= 0:
			fov = self.field_of_view()
			if (Player.x, Player.y) in fov:
				if max(abs(Player.x-self.x), abs(Player.y-self.y)) == 1:
					dmg = self.attack(Player)
					display.msg("The slime slimes you for %d damage!" % dmg, color=(255,0,0))
				else:
					dx = sign(Player.x - self.x)
					dy = sign(Player.y - self.y)
					new_x = self.x + dx
					new_y = self.y + dy
					self.delay += self.move_time
					if self.cur_level.passable(new_x, new_y):
						self.x = new_x
						self.y = new_y
			else:
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
	maxmp = 20
	gold = 100
	entering_text = False
	entered_text = ""
	equipment = []

	def take_damage(self, amount):
		self.hp -= amount
		if self.hp <= 0:
			display.msg('You have died.', color=(255,0,0))
			self.alive = False

	def attack(self, target):
		dmg = random.randint(self.min_atk, self.max_atk)
		target.take_damage(dmg)
		self.cur_level.advance_ticks(self.move_time)
		return dmg

	def advance_ticks(self, num_ticks):
		self.mp = min(self.maxmp, self.mp+(self.maxmp/2500*num_ticks))
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
			if i.name == "knife":
				self.min_atk += 4
				self.max_atk += 4
			if i.name == "flimsy mail":
				self.maxhp += 20
			if i.name == "doublesword":
				self.min_atk += 3
				self.max_atk += 4
				self.attack_time *= 0.8
			if i.name == "fast boots":
				self.move_time *= 0.5
			if i.name == "night-vision goggles":
				self.vision_range += 2

		return

Player = PlayerCreature(town, 10, 10, hp=5.0, maxhp=5.0, img=spr.PLAYER, name='Player')