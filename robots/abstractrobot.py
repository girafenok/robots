#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  abstractrobot.py
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




import os
#from time import *
#~ from PIL import Image
import paho.mqtt.client as mqtt
import uuid
#~ import subprocess
from threading import Thread
from time import *
#const
SPEED_DEFAULT=512

#iot mosquitto
node="%012x"%uuid.getnode()
iot_name="robo-%s"%node[2:]
iot=mqtt.Client(iot_name)
try:
	iot.connect("ev3dev.gabbler.ru", 1977)
except:
	print('No connection to mqtt server')

class AbstractLed(object):
	def __init__(self,address):
		self.__address=address
	def set_mode(self,mode):
		with open('/sys/class/leds/%s/trigger'%(self.__address),'w') as fp:
			fp.write(mode)
	def brightness(self,value):
		with open('/sys/class/leds/%s/brightness'%(self.__address),'w') as fp:
			fp.write(str(int(value)))




class AbstractMotor(object):
	_name=''
	_address=''
	_speed=SPEED_DEFAULT
	def reset(self):
		self._reset()
	def speed(self,value):
		self._speed=value
	def forward(self,rot=1,stop='hold',async=False):
		self.rotate(rot=abs(rot),speed=self._speed,stop=stop,async=async)
	def backward(self,rot=1,stop='hold',async=False):
		self.rotate(rot=-abs(rot),speed=self._speed,stop=stop,async=async)
	def rotate(self,speed=SPEED_DEFAULT,rot=1,stop='hold',async=False):
		self._rotate(speed=speed,rot=rot,stop=stop,async=async)
	def run(self,speed=SPEED_DEFAULT,stop='coast'):
		self._run(speed,stop)
	def stop(self):
		self._stop()
	def value(self):
		return self._value()
	def publish(self):
		attrs=self._publish()
		for name in attrs:
			iot.publish(bytes("%s/%s/%s"%(iot_name,self._name,name)),bytes(attrs[name]))

		
class AbstrcatColorSensor(object):
	__colors={0:'none', 1: 'black', 2: 'blue', 3: 'green', 4: 'yellow', 5: 'red', 6: 'white', 7: 'brown'}
	def __init__(self,address):
		self.set_mode_color()
	def set_mode_color(self):
		self.set_mode('COL-COLOR')
	def set_mode_light(self):
		self.set_mode('COL-REFLECT')
	def set_mode_ambient(self):
		self.set_mode('COL-AMBIENT')
	def set_mode_rgb(self):
		self.set_mode('RGB-RAW')
	def color(self):
		return self.__colors[int(self.value())]
	def rgb(self):
		return (self.value(),self.value1(),self.value2())


class AbstractSound(object):
	# 0 - sub contr octave, 1 - contr octave, 2 - big octave, 3 - small octave, 4 - 1 octave, 5 - 2 octave, 6 - 3 octave, 7 - 4 octave, 8 - 5 octave
	_tones_map={
		'sleep': [0],
	#			0		1		2		3		  4		  5		 6		 7		 8
		'C': [16.352, 32.703, 65.406, 130.812, 261.62, 523.25, 1046.5, 2093,   4186],
		'C#':[17.324, 34.648, 69.296, 138.59,  277.18, 554.37, 1108.7, 2217.5, 4434.8],
		'D': [18.354, 36.708, 73.416, 146.83,  293.66, 587.33, 1174.7, 2349.3, 4698.6],
		'D#':[19.44,  38.88,  77.78,  155.56,  311.13, 622.26, 1244.5, 2489,   4978],
		'E': [20.602, 41.203, 82.407, 164.81,  329.63, 659.26, 1318.5, 2637,   5274],
		'F': [21.827, 43.654, 87.307, 174.61,  349.23, 698.46, 1396.9, 2793.8, 5587.7],
		'F#':[23.12,  46.25,  92.5,   185,     370,    740,    1480,   2960,   5920],
		'G': [24.5,   49,     98,     196,     392,    784,    1568,   3136,   6272],
		'G#':[25.95,  51.9,   103.8,  207,     415.3,  830.6,  1661.2, 3332.4, 6664.8],
		'A': [27.5,   55,     110,    220,     440,    880,    1720,   3440,   6880],
		'A#': [29.13,  58.26,  116.54, 233,     466.16, 932.32, 1864.6, 3729.2, 7458.4],
		'B': [30.87,  61,     123.48, 247,     493,    987.75, 1975.5, 3951,   7902]
	}	
	def play(self,fname,async=False):
		if async:
			Thread(target=self._play, args=(fname,)).start()
		else:
			self._play(fname)
	def tone(self,tone,time,async=False):
		if async:
			Thread(target=self.__tones, args=([(tone,time)],)).start()
		else:
			self.__tones([(tone,time)])
	def tones(self,tones,async=False):
		if async:
			Thread(target=self.__tones, args=(tones,)).start()
		else:
			self.__tones(tones)
	def __tones(self,tones):
		for tone in tones:
			if isinstance(tone[0],(str,unicode)): freq = tone[0]!='sleep' and self._tones_map[tone[0][:len(tone[0])-1]][int(tone[0][-1])] or 0
			self._tone(freq,tone[1])
	def beep(self):
		self._tone(440,250)
	def say(self,msg,speed=175,bass=100,async=False):
		if async:
			Thread(target=self._say, args=(msg,speed,bass,)).start()
		else:
			self._say(msg,speed,bass)
	def volume(self,volume):
		self._volume(volume)
			
class AbstractRobot(object):
	_motors={}
	_sensors={}
	_leds={}
	_buttons={}
	_camera=None
	_lcd=None
	_sound=None
	_speed=SPEED_DEFAULT
	def motor(self,port):
		return self._motors[port]
	def sensor(self,port):
		return self._sensors[port]
	def led(self,led):
		return self._leds[led]
	def screen(self):
		return self._lcd
	def sound(self):
		return self._sound
	def publish(self,topic,data):
		iot.publish(bytes("%s/%s"%(iot_name,topic)),bytes(data))
	#sound
	def beep(self):
		self._sound.beep()
	def tone(self,tone,time,async=False):
		self._sound.tone(tone,time,async)
	def tones(self,tones,async=False):
		self._sound.tones(tones,async)
	def play(self,fname,async=False):
		self._sound.play(fname,async)
	def say(self,msg,speed=175,bass=100,async=False):
		self._sound.say(msg,speed,bass,async)
	def volume(self,vol):
		self._sound.volume(vol)
	#move
	def speed(self,value):
		self._speed=value
	def forward(self,rot=1,stop='hold'):
		self._motors['outB'].speed(self._speed)
		self._motors['outC'].speed(self._speed)
		self._motors['outB'].forward(rot,stop,async=True)
		self._motors['outC'].forward(rot,stop)
		self._motors['outB'].stop()
	def backward(self,rot=1,stop='hold'):
		self._motors['outB'].speed(self._speed)
		self._motors['outC'].speed(self._speed)
		self._motors['outB'].backward(rot,stop,async=True)
		self._motors['outC'].backward(rot,stop)
		self._motors['outB'].stop()
	def left(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		self._motors['outB'].speed(self._speed)
		self._motors['outC'].speed(self._speed)
		self._motors['outC'].backward(rot,stop,async=True)
		self._motors['outB'].forward(rot,stop)
		self._motors['outC'].stop()
	def right(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		self._motors['outB'].speed(self._speed)
		self._motors['outC'].speed(self._speed)
		self._motors['outB'].backward(rot,stop,async=True)
		self._motors['outC'].forward(rot,stop)
		self._motors['outB'].stop()
	#sensors
	def is_object(self,distance=8):
		try:
			res=self._sensors['in1'].value()<distance
		except:
			res=False
		return res
	def is_wall(self,distance=8):
		self.is_object(distance)
	def is_color(self,color=6):
		pass
	def is_light(self):
		pass
	def is_pushbutton_press(self):
		try:
			res=int(self._sensors['in3'].value())==1
		except:
			res=False
		return res
	def is_leftkey_press(self):
		pass
	def is_rightkey_press(self):
		pass
	def is_upkey_press(self):
		pass
	def is_bottomkey_press(self):
		pass
	def is_okkey_press(self):
		pass
	def is_cancelkey_press(self):
		pass
