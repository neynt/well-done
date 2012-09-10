class Item:
	""" Anything that can be on a map. May or may not be
	able to be picked up by the player. """
	def __init__(self, img, name='generic item', desc=None, holdable=True, value=0,
		equippable=False, equip_slot=None, luminosity=0, attr={}, action=None):
		self.img = img
		self.name = name
		self.desc = desc
		self.holdable = holdable
		self.value = value

		self.equippable = equippable
		self.equip_slot = equip_slot
		self.luminosity = luminosity
		self.attr = attr
		self.action = action

	def describe(self):
		descs = []
		descs.append("This is a %s." % self.name)
		if self.desc:
			descs.append(self.desc)
		if self.value > 0:
			descs.append("It is worth %d gold." % self.value)
		if self.equippable:
			if self.equip_slot:
				descs.append("You can equip it on your %s." % self.equip_slot)
			else:
				descs.append("You can equip it." )
		if self.luminosity > 0:
			if self.luminosity >= 20:
				adj = "blinding"
			elif self.luminosity >= 10:
				adj = "very bright"
			elif self.luminosity >= 5: # lanterns
				adj = "bright"
			elif self.luminosity >= 3: # torches
				adj = "soft"
			else:
				adj = "dim"
			descs.append("It gives off %s light." % adj)
		for attr,val in self.attr.items():
			if attr == 'attack_damage':
				descs.append("Attack damage +%d-%d." % val)
			elif attr == 'movement_haste':
				if val < 1:
					descs.append("It makes you move %.3g times faster." % (1/val))
				else:
					descs.append("It makes you move %.3g times slower." % (val))
			elif attr == 'attack_haste':
				if val < 1:
					descs.append("It makes you attack %.3g times faster." % (1/val))
				else:
					descs.append("It makes you attack %.3g times slower." % (val))
			elif attr == 'health':
				descs.append("Health +%d." % val)
			elif attr == 'energy':
				descs.append("Energy +%d." % val)
			elif attr == 'night_vision':
				descs.append("It lets you see farther in the dark.")

		return ' '.join(descs)

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

		# Illuminated by a light source
		self.lit = False

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
