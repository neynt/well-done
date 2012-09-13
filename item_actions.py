import display
# Use effects items can have.

def tp_target_to(level, x, y):
	def f(target):
		display.msg("You start to channel the spell...")
		target.cur_level.advance_ticks(1000)
		if target in target.cur_level.creatures:
			display.msg("Your surroundings suddenly change.")
			target.change_level_to(level, x, y)
			return True
		else:
			# stupid player died while channeling
			return False
	return f

def heal_target(amount=0):
	def x(target):
		restored = target.heal(amount)
		display.msg("You gain %d health." % restored)
		return True
	return x
