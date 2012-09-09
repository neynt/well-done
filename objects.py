class Item:
	""" Anything that can be on a map. May or may not be
	able to be picked up by the player. """
	def __init__(self, img, name='generic item', holdable=True, value=0, equippable=False, luminosity=0):
		self.img = img
		self.name = name
		self.holdable = holdable
		self.value = value

		self.equippable = equippable
		self.luminosity = luminosity
		self.attr = {}

	def describe(self):
		descs = []
		descs.append("This is a %s." % self.name)
		if self.value > 0:
			descs.append("It is worth %d gold." % self.value)
		if self.equippable:
			descs.append("You can equip it.")
		if self.luminosity > 0:
			if self.luminosity > 10:
				adj = "strong"
			else:
				adj = "weak"
			descs.append("It gives off a %s glow." % adj)

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