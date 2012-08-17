# A generic library that eases the creation of games.
# Basically a thin thin THIN wrapper over pygame.
# Feel free to extend this extensible library with your own extensions.

# May or may not just be an excuse to get a head start on a certain local
# 7 Day Roguelike contest.

# Typed by Jim "neynt" Zhang <hyriodula@gmail.com>

import pygame
import os

# initialize everything that has to be init'd in pygame
pygame.font.init()

# modular globals
screen = None
sprites = None
sprite_width = 16
sprite_height = 16
font = None

# you must call these one by one in your program to configure the library
def init_window(size=(600,400), title='unnamed game'):
	global screen
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption(title)

def init_sprites(filename='', sw=16, sh=16):
	global sprites, sprite_width, sprite_height
	sprite_width = sw
	sprite_height = sh
	if os.path.exists(filename):
		sprites = pygame.image.load(filename).convert_alpha()
	else:
		# If file doesn't exist, troll user with a full red spritesheet
		sprites = pygame.Surface((sprite_width*10, sprite_height*20)).convert_alpha()
		sprites.fill((255, 0, 0))

def init_font(name=''):
	global font
	# If name is blank, then the pygame default font will be used
	font = pygame.font.Font(pygame.font.match_font(name), 16)

# callable functions
def draw_sprite(sid, dest):
	x = sid%10 * sprite_width
	y = sid//10 * sprite_height
	screen.blit(sprites, dest, area=(x, y, sprite_width, sprite_height))

def draw_text(text, dest, color=(255,255,255)):
	render = font.render(text, False, color)
	screen.blit(render, dest)

def clear():
	screen.fill((0, 0, 0))

def update():
	pygame.display.update()

