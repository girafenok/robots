#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *
from time import *

# port 1 - lego ev3 color sensor
robo=EV3Robot()
#First variant
#~ while True:
	#~ if robo.sensor('in1').value()==0: #no color
		#~ pass
	#~ elif robo.sensor('in1').value()==1: #black
		#~ robo.sound().say('black')
	#~ elif robo.sensor('in1').value()==2: #blue
		#~ robo.sound().say('blue')
	#~ elif robo.sensor('in1').value()==3: #green
		#~ robo.sound().say('green')
	#~ elif robo.sensor('in1').value()==4: #yellow
		#~ robo.sound().say('yellow')
	#~ elif robo.sensor('in1').value()==5: #red
		#~ robo.sound().say('red')
	#~ elif robo.sensor('in1').value()==6: #white
		#~ robo.sound().say('white')
	#~ elif robo.sensor('in1').value()==7: #brown
		#~ robo.sound().say('brown')
	#~ sleep(1)

#Second variant
while True:
	if robo.sensor('in1').color()=='none': #no color
		pass
	elif robo.sensor('in1').color()=='black': #black
		robo.sound().say('black')
	elif robo.sensor('in1').color()=='blue': #blue
		robo.sound().say('blue')
	elif robo.sensor('in1').color()=='green': #green
		robo.sound().say('green')
	elif robo.sensor('in1').color()=='yellow': #yellow
		robo.sound().say('yellow')
	elif robo.sensor('in1').color()=='red': #red
		robo.sound().say('red')
	elif robo.sensor('in1').color()=='white': #white
		robo.sound().say('white')
	elif robo.sensor('in1').color()=='brown': #brown
		robo.sound().say('brown')
	sleep(1)
