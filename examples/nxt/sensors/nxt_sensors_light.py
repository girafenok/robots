#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nxtrobot import *
from time import *

robo=NXTRobot("00:16:53:0E:B5:80",sensors=('light',None,None,None))#NXT ID <- Settings - NXT Version
while True:
	print("light: %i"%robo.sensor('in1').value())
	sleep(1)
