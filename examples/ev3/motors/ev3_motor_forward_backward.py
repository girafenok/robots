#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *

#max_speed = 1023
robo=EV3Robot()
robo.motor('outA').forward(rot=2,speed=1023)#rot,speed
robo.motor('outA').backward(rot=1,speed=1023)#rot,speed
