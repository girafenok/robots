#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *
from time import *

robo=EV3Robot()
robo.motor('outA').run()
sleep(3)
robo.motor('outA').stop()
