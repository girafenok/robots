#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nxtrobot import *
from time import sleep

#max_speed = 1023

robo=NXTRobot("00:16:53:0E:B5:80")#NXT ID <- Settings - NXT Version
robo.motor('outA').speed(1023)
robo.motor('outA').forward(2)#rot
robo.motor('outA').backward(1)#rot
robo.done()
