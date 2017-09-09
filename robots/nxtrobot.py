#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  nxtrobot.py
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
import bluetooth
from abstractrobot import *
#const
SPEED_DEFAULT=700

#~ #iot mosquitto
#~ node="%012x"%uuid.getnode()
#~ iot_name="ev3-%s"%node[2:]
#~ iot=mqtt.Client(iot_name)
#~ try:
	#~ iot.connect("ev3dev.gabbler.ru", 1977)
#~ except:
	#~ pass
class NXTComm(object):
	brick=None
	def __init__(self,brick):
		self.brick=brick
	def _send(self,data):
		self.brick.send(chr(len(data)%256)+chr(len(data)//256)+data)
		if data[0]!=chr(0x80):
			length=self.brick.recv(2)
			#~ print(ord(length[1])*16+ord(length[0]))
			recv=self.brick.recv(ord(length[1])*16+ord(length[0]))
			return recv

class NXTMotor(NXTComm,AbstractMotor):
	attrs_names={'position':'rot','speed_sp':'speed','stop_action':'stop'}
	speed_koef=100.0/1023.0
	__stop_actions={'coast':chr(0x01),'hold':chr(0x07)}
	__stop='coast'
	__position=0
	__speed=0
	def __init__(self,address,brick):
		NXTComm.__init__(self,brick)
		self._address=chr(address)
		self._reset()
	def _reset(self,isRelative=0):
		self._send(chr(0x00)+chr(0x0A)+self._address+chr(isRelative))
	def _rotate(self,speed,rot,stop,wait):
		self.__position=self._value()
		self.__stop=stop
		self.__speed=abs(speed)*(-1,1)[speed>0]
		speed=abs(int(speed*self.speed_koef)) if rot>=0 else 255-abs(int(speed*self.speed_koef))
		self._send(chr(0x00)+chr(0x04)+self._address+chr(speed)+self.__stop_actions[stop]+chr(0x00)+chr(0x00)+chr(0x20)+chr(0x00)+chr(0x00)+chr(0x00)+chr(0x00))
		if wait:
			if rot>=0:
				while self._value()<self.__position+abs(rot)*360-90*self.__speed*self.speed_koef/100: sleep(0.008)
			else:
				while self._value()>self.__position-abs(rot)*360+90*self.__speed*self.speed_koef/100: sleep(0.008)
		#~ print(rot,self._value())
		self._stop()
	def _run(self,speed,stop='coast'):
		self.__stop=stop
		self.__speed=speed
		speed=int(speed*self.speed_koef) if speed>=0 else 255-abs(int(speed*self.speed_koef))
		self._send(chr(0x00)+chr(0x04)+self._address+chr(speed)+self.__stop_actions[stop]+chr(0x00)+chr(0x00)+chr(0x20)+chr(0x00)+chr(0x00)+chr(0x00)+chr(0x00)+chr(0x00))
		self.__position=self._value()
	def _stop(self):
		self.__speed=0
		self._run(0,self.__stop)
		self.__position=self._value()
	def _publish(self):
		return {'position':self.__position,'stop':self.__stop,'speed':self.__speed}
	def _value(self):
		state=self._send(chr(0x00)+chr(0x06)+self._address)
		value=sum(ord(state[i+21])*256**i for i in range(4))
		return value if value<2**31 else -2**32+value
		
		
		

class NXTSensor(NXTComm):
	__name=''
	def __init__(self,address,brick):
		NXTComm.__init__(self,brick)
		self.__address=chr(address)
	def set_mode(self,sensor,mode=0x00):
		state=self._send(chr(0x00)+chr(0x05)+self.__address+chr(sensor)+chr(mode))
	def value(self):
		state=self._send(chr(0x00)+chr(0x07)+self.__address)
		return ord(state[13])*256+ord(state[12])
	def publish(self):
		iot.publish(bytes("%s/%s/value"%(iot_name,self._name)),bytes(self.value()))
		
class NXTPushButton(NXTSensor):
	_name='button'
	def __init__(self,address,brick):
		NXTSensor.__init__(self,address,brick)
		self.set_mode(0x01,0x20)
	
class NXTLight(NXTSensor):
	_name='light'
	def __init__(self,address,brick):
		NXTSensor.__init__(self,address,brick)
		self.set_mode(0x05)
	def set_reflect(self,ref=True):
		self.set_mode(0x05 if ref else 0x06)
	
class NXTColor(NXTSensor):
	_name='color'
	__colors={0:'none', 1: 'black', 2: 'blue', 3: 'green', 4: 'yellow', 5: 'red', 6: 'white', 7: 'brown'}
	def __init__(self,address):
		NXTSensor.__init__(self,address)
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

class NXTUltrasonic(NXTSensor):
	_name='ultrasonic'
	def __init__(self,address,brick):
		NXTSensor.__init__(self,address,brick)
		self.set_mode(0x0B,0x00)

class NXTSound(NXTComm,AbstractSound):
	def __init__(self,brick):
		AbstractSound.__init__(self)
		NXTComm.__init__(self,brick)
	def _play(self,fname):
		self._send(chr(0x00)+chr(0x02)+chr(0x00)+fname+'.rso'+chr(0x00))
	def _tone(self,tone,time):
 		self._send(chr(0x00)+chr(0x03)+chr(int(tone)%256)+chr(int(tone)//256)+chr(int(time)%256)+chr(int(time)//256))
		sleep(time/1000.0)
		self._send(chr(0x00)+chr(0x03)+chr(0)+chr(0)+chr(0)+chr(0))
	def _say(self,msg,speed=175,bass=100):
		pass
	def _volume(self,volume):
		pass
			
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

class NXTRobot(AbstractRobot):
	_sensor_types={'':lambda a,b: None,None: lambda a,b: None,'light':lambda a,b: NXTLight(a,b),'button':lambda a,b: NXTPushButton(a,b),'ultrasonic':lambda a,b: NXTUltrasonic(a,b)}
	def __init__(self,address,sensors=[]):
		self._brick=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
		self._brick.connect((address, 1))
		#Motor
		self._motors['outA']=NXTMotor(0x00,self._brick)
		self._motors['outB']=NXTMotor(0x01,self._brick)
		self._motors['outC']=NXTMotor(0x02,self._brick)
		self._sensors['in1']=self._sensor_types[sensors[0]](0x00,self._brick)
		self._sensors['in2']=self._sensor_types[sensors[1]](0x01,self._brick)
		self._sensors['in3']=self._sensor_types[sensors[2]](0x02,self._brick)
		self._sensors['in4']=self._sensor_types[sensors[3]](0x03,self._brick)
		#Sensor
		#Sound
		self._sound=NXTSound(self._brick)
		#Buttons
		self._buttons['left']=NXTButton('left')
		self._buttons['right']=NXTButton('right')
		self._buttons['ok']=NXTButton('ok')
		self._buttons['cancel']=NXTButton('cancel')
		#LCD
		self._lcd=NXTLCD()
		print(self._sensors,self._motors)





