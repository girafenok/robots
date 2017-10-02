#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *
from time import *

# port 1 - lego ev3 color sensor
robo=EV3Robot()
robo.sensor('in1').set_mode_light()
while True:
	light=robo.sensor('in1').value()
	robo.led('left:red').brightness(light/100*255)
	robo.led('left:green').brightness(0)
	robo.led('right:red').brightness(light/100*255)
	robo.led('right:green').brightness(0)
	sleep(0.2)
robo.done()
