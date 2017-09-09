#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *
from time import *

#max_speed = 1023
robo=EV3Robot()
robo.motor('outA').run(speed=500)
sleep(1)
robo.motor('outA').run(speed=-500)
sleep(2)
robo.motor('outA').stop()
