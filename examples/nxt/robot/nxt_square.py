#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nxtrobot import *
from time import sleep

#max_speed = 1023
#Conect left motor to port C
#Conect right motor to port B

robo=NXTRobot("00:16:53:0E:B5:80")#NXT ID <- Settings - NXT Version
for i in range(4):
	robo.forward(1)
	robo.left(0.63)
robo.done()
