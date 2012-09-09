import random
import sprites as spr

from my_geom import box2d
from level import Level
from objects import Item, Portal

town = Level(25, 25)
town.illuminated = True
town.generate_town()

shop = [Level(16, 16, is_shop=True) for i in xrange(16)]
for i,loc in enumerate(random.sample(town.get_main_region(), 16)):
	x,y = loc
	shop[i].generate_shop()
	shop_type = random.randint(0, 1)
	if shop_type == 0:
		# General store
		shop_items = [Item(spr.TORCH, name="torch", value=40, luminosity=3)]
		shop_items.append(Item(spr.SCROLL, name="town portal scroll", value=50))
		shop_items.append(Item(spr.ESSENCE, name="ultrabright essence", value=1500, luminosity=999))
		shop_img = spr.SHOP
		shop_name = "general store"

	elif shop_type == 1:
		# Weapon shop
		shop_items = [Item(spr.KNIFE, name="knife", value=150, equippable=True)]
		shop_items.append(Item(spr.THORNMAIL, name="flimsy mail", value=200, equippable=True))
		shop_items.append(Item(spr.ZEAL, name="doublesword", value=250, equippable=True))
		shop_items.append(Item(spr.BOOTS_SWIFTNESS, name="fast boots", value=600, equippable=True))
		shop_items.append(Item(spr.DFG, name="night-vision goggles", value=1, equippable=True))
		shop_img = spr.SHOP_WEAPONS
		shop_name = "weapon store"

	for a,b in box2d(2, 2, 5, 5):
		shop[i].add_item((a,b), random.choice(shop_items))

	town.add_item((x,y), Item(shop_img, name=shop_name, holdable=False))
	town.portals[(x,y)] = Portal(shop[i], 1, 1, name="the "+shop_name)
	shop[i].portals[(1,1)] = Portal(town, x, y, name="the town")
	shop[i].add_item((1,1), Item(spr.DOOR, holdable=False))

	shop[i].illuminated = True

well = [Level(13+i*2, 13+i*2) for i in xrange(20)]