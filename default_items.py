from objects import Item
import sprites as spr

weapons = [
	Item(spr.KNIFE, name="knife", value=30, equippable=True,
		equip_slot='hand',
		attr={
		'attack_damage': (4,4),
		}),
	Item(spr.SWORD, name="sword", value=200, equippable=True,
		equip_slot='hand',
		attr={
		'attack_damage': (8,12),
		}),
	Item(spr.SCIMITAR, name="scimitar", value=450, equippable=True,
		equip_slot='hand',
		attr={
		'attack_damage': (6,25),
		}),
	Item(spr.BATTLEAXE, name="battleaxe", value=800, equippable=True,
		equip_slot='hand',
		attr={
		'attack_damage': (20,100),
		'attack_haste': 1.5,
		}),
	Item(spr.WAR_HAMMER, name="huge hammer", value=1650, equippable=True,
		equip_slot='hand',
		attr={
		'attack_damage': (160,180),
		'attack_haste': 2.0,
		}),
	Item(spr.ZEAL, name="doublesword", value=250, equippable=True,
		equip_slot='hand',
		attr={
		'attack_haste': 0.5,
		}),
]

armors = [
	Item(spr.FLIMSY_MAIL, name="flimsy mail", value=50, equippable=True,
		equip_slot='torso',
		attr={
		'health': 40,
		}),
	Item(spr.PLATE_MAIL, name="plate mail", value=500, equippable=True,
		equip_slot='torso',
		attr={
		'health': 100,
		}),
	Item(spr.PLATE_PLATE, name="plate plate", value=1500, equippable=True,
		equip_slot='torso',
		attr={
		'health': 300,
		}),
	Item(spr.ROBE, name="blue robe", value=100, equippable=True,
		equip_slot='torso',
		attr={
		'health': 25,
		'energy': 20,
		}),
	Item(spr.ROBE_RED, name="archmage robe", value=2000, equippable=True,
		equip_slot='torso',
		attr={
		'health': 80,
		'energy': 300,
		}),
	Item(spr.THORNMAIL, name="thorned platemail", value=2500, equippable=True,
		equip_slot='torso',
		attr={
		'attack_damage': (0,10),
		'health': 500,
		}),
	Item(spr.BOOTS_SWIFTNESS, name="fast boots", value=600, equippable=True,
		equip_slot='feet',
		attr={
		'movement_haste': 0.5,
		}),
	Item(spr.DFG, name="bat goggles", value=1000, equippable=True,
		equip_slot='head',
		attr={
		'night_vision': 5,
		}),
	Item(spr.HELMET, name="helmet", value=100, equippable=True,
		equip_slot='head',
		attr={
		'health': 30,
		}),
]