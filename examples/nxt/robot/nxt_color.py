#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nxtrobot import *
from time import *

# port 4 - nxt ev3 color sensor
robo=NXTRobot("00:16:53:14:61:93")
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
