#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *
from time import sleep

#max_speed = 1023
#Conect left motor to port C
#Conect right motor to port B

robo=EV3Robot()#NXT ID <- Settings - NXT Version
for i in range(4):
	robo.roundLeft(1,0.5)
	robo.roundRight(1,0.5)
robo.done()
