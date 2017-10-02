#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *

#max_speed = 1023
robo=EV3Robot()
robo.motor('outA').speed(1023)
robo.motor('outA').forward(2)#rot
robo.motor('outA').backward(1)#rotd
robo.done()
