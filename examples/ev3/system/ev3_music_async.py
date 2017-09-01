#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *
from time import *

robo=EV3Robot()
robo.sound().play('comp.mp3',async=True)

while True:
	robo.led('left').color('yellow')
	robo.led('right').color('black')
	sleep(2)
	robo.led('left').color('black')
	robo.led('right').color('yellow')
	sleep(2)
