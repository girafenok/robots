#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nxtrobot import *
from time import *

#max_speed = 1023

robo=NXTRobot("00:16:53:0E:B5:80")#NXT ID <- Settings - NXT Version
robo.motor('outA').run(speed=1023)
sleep(2)
robo.motor('outA').run(speed=-1023,stop='hold')
sleep(2)
robo.motor('outA').stop()
robo.done()
