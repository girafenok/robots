#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *

#max_speed = 1023
#Conect left motor to port C
#Conect right motor to port B

robo=EV3Robot()
for i in range(4):
	robo.forward(1)
	robo.left(0.5)
robo.done()
