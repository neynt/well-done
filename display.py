# A generic library that eases the creation of games.
# Basically a thin thin THIN wrapper over pygame.
# Feel free to extend this extensible library.

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
sprites_grey = None
sprites_blue = None
sprite_width = 16
sprite_height = 16
font = None

class MessageLog:
	""" Basically print() for graphics. """
	width = 400
	lines = []
	def __init__(self, width):
		self.width = width

	def output(self, text, color):
		# aka Schlemiel's Algorithm
		start = 0
		for end in range(0, len(text)):
			w, _ = font.size(text[start:end])
			if w > self.width:
				self.lines.append((text[start:end-1], color))
				start = end-1
		self.lines.append((text[start:], color))

	def draw(self, dest, height):
		line_height = font.get_linesize()
		num_lines = height // line_height
		for line,color in msg_log.lines[-num_lines:]:
			draw_text(line, dest, color)
			dest = (dest[0], dest[1]+line_height)

msg_log = None

# you must call these one by one in your program to configure the library
def init_window(size=(600,400), title='unnamed game'):
	global screen
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption(title)

def init_sprites(filename='', sw=16, sh=16):
	global sprites, sprites_grey, sprites_blue, sprite_width, sprite_height
	sprite_width = sw
	sprite_height = sh
	if os.path.exists(filename):
		sprites = pygame.image.load(filename).convert_alpha()

		sprites_grey = sprites.copy()
		for x,y in ((x,y) for x in xrange(sprites.get_width()) for y in xrange(sprites.get_height())):
			c = sprites_grey.get_at((x,y))
			avg = (c.r + c.g + c.b) // 7
			c.r = c.g = c.b = avg
			sprites_grey.set_at((x,y), c)

		sprites_blue = sprites.copy()
		for x,y in ((x,y) for x in xrange(sprites.get_width()) for y in xrange(sprites.get_height())):
			c = sprites_blue.get_at((x,y))
			avg = (c.r + c.g + c.b) // 4
			c.r = c.r // 2
			c.g = c.g // 2
			c.b = c.b
			sprites_blue.set_at((x,y), c)
	else:
		# If file doesn't exist, troll user with a full red spritesheet
		sprites = pygame.Surface((sprite_width*10, sprite_height*20)).convert_alpha()
		sprites.fill((255, 0, 0))

def init_font(name='', size=16):
	global font
	# If name is blank, then the pygame default font will be used
	font = pygame.font.Font(name, 16)

def init_msg_log(width):
	global msg_log
	msg_log = MessageLog(width)

# callable functions
def draw_sprite(sid, dest, sheet=None):
	if sheet == None: sheet = sprites
	x = sid%10 * sprite_width
	y = sid//10 * sprite_height
	screen.blit(sheet, dest, area=(x, y, sprite_width, sprite_height))

def draw_text(text, dest, color=(255,255,255)):
	render = font.render(text, False, color)
	screen.blit(render, dest)

def draw_rect(rect, color):
	pygame.draw.rect(screen, color, rect, 1)

def fill_rect(rect, color):
	screen.fill(color, rect)

def msg(text, color=(255,255,255)):
	msg_log.output(text, color)

def clear(color = (0,0,0)):
	screen.fill((color))

def update():
	pygame.display.update()
