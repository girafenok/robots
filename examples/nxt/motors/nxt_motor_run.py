#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nxtrobot import *
from time import *

#max_speed = 1000

robo=NXTRobot("00:16:53:0E:B5:80")#NXT ID <- Settings - NXT Version
robo.motor('outA').run(1000)#speed
sleep(2)
robo.motor('outA').run(-1000,'hold')#speed
sleep(2)
robo.motor('outA').stop()

