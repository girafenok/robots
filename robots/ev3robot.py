#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ev3robot.py
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

import os,stat
from time import *
from PIL import Image
import paho.mqtt.client as mqtt
import uuid
#~ import subprocess
from threading import Thread
from abstractrobot import *

#iot mosquitto
#~ node="%012x"%uuid.getnode()
#~ iot_name="ev3-%s"%node[2:]
#~ iot=mqtt.Client(iot_name)
#~ try:
	#~ iot.connect("ev3dev.gabbler.ru", 1977)
#~ except:
	#~ pass
class EV3Motor(AbstractMotor):
	attrs_names={'position':'rot','speed_sp':'speed','stop_action':'stop'}
	speed_koef=1050.0/1023.0
	def __init__(self,address):
		self._address=address
		with open('/sys/class/tacho-motor/'+self._address+'/address','r') as fp:
			self._name=fp.read().replace('\n','')
		self._reset()
	def _reset(self):
		self._set_attributes([('command','reset')])
	def _set_attributes(self,attributes):
		for attr in attributes:
			with open('/sys/class/tacho-motor/%s/%s'%(self._address,attr[0]),'w') as fp:
				fp.write(str(attr[1]))	
	def _get_attribute(self,attr):
		with open('/sys/class/tacho-motor/%s/%s'%(self._address,attr),'r') as fp:
			return fp.read().replace('\n','')
	def _rotate(self,speed,rot,stop,wait):
		self._set_attributes([('position_sp',rot*360),('speed_sp',int(speed*self.speed_koef)),('stop_action',stop),('command','run-to-rel-pos')])
		start_position=int(self._get_attribute('position'))
		if wait:
			while int(self._get_attribute('position'))!=start_position+rot*360: pass
	def _run(self,speed,stop):
		self._set_attributes([('speed_sp',int(speed*self.speed_koef)),('stop_action',stop),('command','run-forever')])
	def _stop(self):
		self._set_attributes([('command','stop')])
	def _value(self):
		int(self._get_attribute('position'))
	def _publish(self):
		attrs={}
		for attr in ['position','speed_sp','stop_action']:
			with open('/sys/class/tacho-motor/%s/%s'%(self._address,attr),'r') as fp:
				attrs[self.attrs_names[attr]]=fp.read().replace('\n','')
		return attrs

class EV3Sensor(object):
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
		
class EV3Color(EV3Sensor):
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

class EV3Leds(object):
	colors={'black':{'green':'0','red':'0'},'orange':{'green':'255','red':'255'},'red':{'green':'0','red':'255'},'yellow':{'green':'255','red':'35'},'green':{'green':'255','red':'0'},'brown':{'green':'69','red':'89'}}
	def __init__(self,address):
		self.__address=address
	def color(self,c):
		with open('/sys/class/leds/ev3:%s:green:ev3dev/brightness'%(self.__address),'w') as fp:
			fp.write(self.colors[c]['green'])
		with open('/sys/class/leds/ev3:%s:red:ev3dev/brightness'%(self.__address),'w') as fp:
			fp.write(self.colors[c]['red'])
#~ class EV3Led(object):
	#~ def __init__(self,address):
		#~ self.__address=address
	#~ def set_mode(self,mode):
		#~ with open('/sys/class/leds/ev3:%s:ev3dev/trigger'%(self.__address),'w') as fp:
			#~ fp.write(mode)
	#~ def brightness(self,value):
		#~ with open('/sys/class/leds/ev3:%s:ev3dev/brightness'%(self.__address),'w') as fp:
			#~ fp.write(str(int(value)))


class EV3Sound(AbstractSound):
	def __init__(self):
		AbstractSound.__init__(self)
	def _play(self,fname):
		fname=os.path.exists('/home/robot/.sounds/%s'%fname)  and '/home/robot/.sounds/%s'%fname or 'music/%s'%fname
		os.system('mpg123 -q %s '%fname)
	def _tone(self,tone,time):
 		with open('/sys/devices/platform/snd-legoev3/tone','w') as fp:
			fp.write("%i %i"%(tone,time))
		sleep(time/1000.0)
	def _say(self,msg,speed=175,bass=100):
		os.system('espeak -a %s -s %s "%s" --stdout | aplay -q'%(bass,speed,msg))
	def _volume(self,volume):
		with open('/sys/devices/platform/snd-legoev3/volume','w') as fp:
			fp.write(str(volume))
			
class EV3Button(object):
	def __init__(self,address):
		self.__address=address
	def value(self):
		pass


class EV3LCD(object):
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

class EV3Camera(object):
	camera=None
	def __init__(self,address):
		self.__address=address
		try:
			import cv2
			self.camera=cv2.VideoCapture(self.__address)
			#~ capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH ,640)
			#~ capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT ,480)
		except:
			pass
	def capture(self):
		return self.camera.read()[1] if self.camera!=None else None
	def publish(self):
		pass
class EV3Robot(AbstractRobot):
	_sensor_types={'lego-ev3-color':lambda a: EV3Color(a),'lego-nxt-touch':lambda a: EV3Sensor(a),'lego-ev3-touch':lambda a: EV3Sensor(a),'lego-ev3-ir':lambda a: EV3Sensor(a),'lego-ev3-us':lambda a: EV3Sensor(a),'lego-nxt-us':lambda a: EV3Sensor(a),'lego-nxt-light':lambda a: EV3Sensor(a),'nxt-analog':lambda a: EV3Sensor(a),'lego-ev3-gyro':lambda a: EV3Sensor(a)}
	def __init__(self,camera=False):
		#Camera
		if camera: self._camera=EV3Camera(0)
		#Motor
		for motor in os.listdir('/sys/class/tacho-motor'):
			with open('/sys/class/tacho-motor/'+motor+'/address','r') as fp:
				self._motors[fp.read().replace('\n','')]=EV3Motor(motor)
		#Seonsor
		try:
			for sensor in os.listdir('/sys/class/lego-sensor'):
				with open('/sys/class/lego-sensor/'+sensor+'/driver_name','r') as fd: driver=fd.read().strip()
				with open('/sys/class/lego-sensor/'+sensor+'/address','r') as fa: name=fa.read().strip().replace(':i2c1','').replace(':i2c2','').replace(':i2c3','').replace(':i2c4','').replace('\n','')
				self._sensors[name]=self._sensor_types[driver](sensor)
		except:
			pass
		#Leds
		self._leds['left:red']=AbstractLed('ev3:left:red:ev3dev')
		self._leds['left:green']=AbstractLed('ev3:left:green:ev3dev')
		self._leds['right:red']=AbstractLed('ev3:right:red:ev3dev')
		self._leds['right:green']=AbstractLed('ev3:right:green:ev3dev')
		self._leds['left']=EV3Leds('left')
		self._leds['right']=EV3Leds('right')
		#Sound
		self._sound=EV3Sound()
		#Buttons
		self._buttons['left']=EV3Button('left')
		self._buttons['right']=EV3Button('right')
		self._buttons['up']=EV3Button('up')
		self._buttons['down']=EV3Button('down')
		self._buttons['ok']=EV3Button('ok')
		self._buttons['cancel']=EV3Button('cancel')
		#LCD
		self._lcd=EV3LCD()
		print(self._sensors,self._motors)
if __name__ == '__main__':
	pass
	#~ robo=EV3Robot()
	#~ robo.motor('outA').run(100)
	#~ sleep(2)
	#~ robo.motor('outA').stop()
	#~ robo.motor('outA').rotate(100,720)
	#lego-ev3-color modes: COL-REFLECT COL-AMBIENT COL-COLOR REF-RAW RGB-RAW COL-CAL
	#lego-ev3-gyro modes: GYRO-ANG GYRO-RATE GYRO-FAS GYRO-G&A GYRO-CAL TILT-RATE TILT-ANG
	#lego-ev3-ir modes: US-DIST-CM US-DIST-IN US-LISTEN US-SI-CM US-SI-IN US-DC-CM US-DC-IN
	
	#~ robo.sensor('in2').set_mode('RGB-RAW')
	#~ robo.led('left').set_color('green')
	#~ robo.led('right').set_color((255,100))
	#~ while True:
		#~ pass
		#~ print(robo.sensor('in2').value())
		#~ cv2.imwrite("capture.jpg", robo.capture())
		#~ sleep(1)






