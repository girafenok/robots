#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *

#max_speed = 1023
robo=EV3Robot()
robo.motor('outA').rotate(rot=2,speed=800)
robo.motor('outA').rotate(rot=-1,speed=800)
