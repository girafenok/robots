#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *
#~ from time import *

robo=EV3Robot()
robo.volume(100)
robo.play('geroispo.mp3',poll=False)

while True:
	robo.led('left').color('yellow')
	robo.led('right').color('black')
	sleep(2)
	robo.led('left').color('black')
	robo.led('right').color('yellow')
	sleep(2)
robo.done()
