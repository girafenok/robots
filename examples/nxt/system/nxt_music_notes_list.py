#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nxtrobot import *
from time import *

kuznechik=(("F4",250),("C4",250),("F4",250),("C4",250),("F4",250),("E4",250),("E4",500),("E4",250),("C4",250),("E4",250),("C4",250),("E4",250),("F4",250),("F4",500),("F4",250),("C4",250),("F4",250),("C4",250),("F4",250),("E4",250),("E4",500),("E4",250),("C4",250),("E4",250),("C4",250),("E4",250),("F4",750))

robo=NXTRobot("00:16:53:0E:B5:80")#NXT ID <- Settings - NXT Version
robo.sound().tones(kuznechik)
