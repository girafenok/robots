#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *
from time import *

kuznechik=(("F4",250),("C4",250),("F4",250),("C4",250),("F4",250),("E4",250),("E4",500),("E4",250),("C4",250),("E4",250),("C4",250),("E4",250),("F4",250),("F4",500),("F4",250),("C4",250),("F4",250),("C4",250),("F4",250),("E4",250),("E4",500),("E4",250),("C4",250),("E4",250),("C4",250),("E4",250),("F4",750))

robo=EV3Robot()
robo.tones(kuznechik)
robo.done()
