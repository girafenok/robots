#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *
from time import *

# port 1 - lego ev3 color sensor
robo=EV3Robot()
robo.beep()
while True:
	if robo.is_color('none'): #no color
		pass
	elif robo.is_color('black'): #black
		robo.sound().say('black')
	elif robo.is_color('blue'): #blue
		robo.sound().say('blue')
	elif robo.is_color('green'): #green
		robo.sound().say('green')
	elif robo.is_color('yellow'): #yellow
		robo.sound().say('yellow')
	elif robo.is_color('red'): #red
		robo.sound().say('red')
	elif robo.is_color('white'): #white
		robo.sound().say('white')
	elif robo.is_color('brown'): #brown
		robo.sound().say('brown')
	sleep(1)
robo.done()
