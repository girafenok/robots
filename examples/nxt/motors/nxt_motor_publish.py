#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nxtrobot import *
from time import sleep

#max_speed = 1023

#Publsih motor attributes to mqtt server ev3dev.gabbler.ru
robo=NXTRobot("00:16:53:0E:B5:80")#NXT ID <- Settings - NXT Version
robo.motor('outA').publish()
robo.motor('outA').rotate(rot=2,speed=1023)
robo.motor('outA').publish()
robo.motor('outA').rotate(rot=-1,speed=1023)
robo.motor('outA').publish()
robo.done()
