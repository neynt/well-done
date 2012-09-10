from creature import PlayerCreature
from world import town
import sprites as spr

# SCREW JAVA I HAVE GLOBAL VARIABLES
# HOW JELLY ARE YOU
Player = PlayerCreature(town, 12, 12, hp=5.0, maxhp=5.0, img=spr.PLAYER, name='Player',
	equip_slots={
		'head': 1,
		'hand': 2,
		'torso': 1,
		'feet': 1,
	})
Player.gold = 100