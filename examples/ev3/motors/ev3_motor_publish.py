#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *

#publish motor's attributes to mqtt server ev3dev.gabbler.ru, port 1977

#max_speed = 1023
robo=EV3Robot()
robo.motor('outA').publish()
robo.motor('outA').rotate(rot=2,speed=800)
robo.motor('outA').publish()
robo.motor('outA').rotate(rot=-2,speed=800)
robo.motor('outA').publish()
