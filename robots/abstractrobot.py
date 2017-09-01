#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,stat
from time import *
from PIL import Image
import paho.mqtt.client as mqtt
import uuid
#~ import subprocess
from threading import Thread
#const
SPEED_DEFAULT=700

#iot mosquitto
node="%012x"%uuid.getnode()
iot_name="ev3-%s"%node[2:]
iot=mqtt.Client(iot_name)
try:
	iot.connect("ev3dev.gabbler.ru", 1977)
except:
	print('No connection to mqtt server')

class AbstractMotor(object):
	_name=''
	_address=''
	def forward(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		self.rotate(abs(rot),speed,stop)
	def backward(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		self.rotate(-abs(rot),speed,stop)
	def rotate(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		self._rotate(rot,speed,stop)
	def run(self,speed=SPEED_DEFAULT,stop='coast'):
		self._run(speed,stop)
	def stop(self):
		self._stop()
	def publish(self):
		attrs=self._publish()
		for name in attrs:
			iot.publish(bytes("%s/%s/%s"%(iot_name,self._name,name)),bytes(attrs[name]))

class NXTSensor(object):
	__name=''
	def __init__(self,address):
		self.__address=address
		with open('/sys/class/lego-sensor/'+self.__address+'/address','r') as fa:
			self.__name=fa.read().strip().replace(':i2c1','').replace(':i2c2','').replace(':i2c3','').replace(':i2c4','').replace('\n','')
	def set_mode(self,mode):
		with open('/sys/class/lego-sensor/%s/mode'%(self.__address),'w') as fp:
			fp.write(mode)
	def value(self):
		with open('/sys/class/lego-sensor/%s/value0'%(self.__address),'r') as fp:
			return float(fp.read())
	def value1(self):
		with open('/sys/class/lego-sensor/%s/value1'%(self.__address),'r') as fp:
			return float(fp.read())
	def value2(self):
		with open('/sys/class/lego-sensor/%s/value2'%(self.__address),'r') as fp:
			return float(fp.read())
	def publish(self):
		with open('/sys/class/lego-sensor/%s/value0'%(self.__address),'r') as fp:
			iot.publish(bytes("%s/%s/value"%(iot_name,self.__name)),bytes(fp.read().replace('\n','')))
		
class NXTColor(NXTSensor):
	__colors={0:'none', 1: 'black', 2: 'blue', 3: 'green', 4: 'yellow', 5: 'red', 6: 'white', 7: 'brown'}
	def __init__(self,address):
		EV3Sensor.__init__(self,address)
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
			
class NXTButton(object):
	def __init__(self,address):
		self.__address=address
	def value(self):
		pass


class NXTLCD(object):
	__width=178
	__height=128
	__bits=24
	def __init__(self):
		self.__buffer=[0]*self.__height*self.__bits
		#~ self.__buffer=numpy.zeros(shape=(self.__height,self.__width),dtype=numpy.uint8)	
	def imread(self,fname):
		self.__buffer=Image.open(fname).convert('1')
	def show(self):
		with open('/dev/fb0','w+') as fp:
			#~ fp.write(self.__buffer.tobytes("raw", "1;IR"))
			fp.write(self.__buffer.tostring())
		#~ fp = os.open('/dev/fb0', os.O_RDWR)
		#~ os.write(fp,self.__buffer.tostring())#tobytes("raw", "1;IR"))
		#~ os.close(fp)
		#~ 

class AbstractRobot(object):
	_motors={}
	_sensors={}
	_leds={}
	_buttons={}
	_camera=None
	_lcd=None
	_sound=None
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
	#move
	def forward(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		try:
			self._motors['outB'].forward(rot,speed,stop)
		except:
			pass
		try:
			self._motors['outC'].forward(rot,speed,stop)
		except:
			pass
	def backward(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		try:
			self._motors['outB'].backward(rot,speed,stop)
		except:
			pass
		try:
			self._motors['outC'].backward(rot,speed,stop)
		except:
			pass
	def left(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		try:
			self._motors['outB'].forward(rot,speed,stop)
		except:
			pass
		try:
			self._motors['outC'].backward(rot,speed,stop)
		except:
			pass
	def right(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		try:
			self._motors['outB'].backward(rot,speed,stop)
		except:
			pass
		try:
			self._motors['outC'].forward(rot,speed,stop)
		except:
			pass
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
