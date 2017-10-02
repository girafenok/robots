#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nxtrobot import *
from time import sleep

#max_speed = 1023
#Conect left motor to port C
#Conect right motor to port B

robo=NXTRobot("00:16:53:0E:B5:80")#NXT ID <- Settings - NXT Version
for speed in range(200,1023,50):
	robo.speed(speed)
	robo.forward(1)
robo.forward(10)
for speed in range(1023,200,-50):
	robo.speed(speed)
	robo.forward(1)
robo.done()

