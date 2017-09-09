#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  nxt_sensors_pushbutton.py
#  
#  Copyright 2017 girafenok <girafenok@gabbler.ru>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from nxtrobot import *
from time import *

robo=NXTRobot("00:16:53:0E:B5:80",sensors=('button',None,None,None))#NXT ID <- Settings - NXT Version
i=1
while True:
	if robo.sensor('in1').value(): 
		print("Button press %i"%i)
		i+=1
	sleep(0.2)
