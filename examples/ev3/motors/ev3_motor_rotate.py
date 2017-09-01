#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *

#max_speed = 1000
robo=EV3Robot()
robo.motor('outA').rotate(2,800)#rot,speed
robo.motor('outA').rotate(-1,800)#rot,speed
