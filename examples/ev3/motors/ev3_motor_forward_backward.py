#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *

#max_speed = 1000
robo=EV3Robot()
robo.motor('outA').forward(2,100)#rot,speed
robo.motor('outA').backward(1,100)#rot,speed
