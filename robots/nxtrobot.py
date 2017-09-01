#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

#iot mosquitto
node="%012x"%uuid.getnode()
iot_name="ev3-%s"%node[2:]
iot=mqtt.Client(iot_name)
try:
	iot.connect("ev3dev.gabbler.ru", 1977)
except:
	pass
class NXTComm(object):
	brick=None
	def __init__(self,brick):
		self.brick=brick
	def _send(self,data,block_recv=3):
		self.brick.send(chr(len(data)%256)+chr(len(data)//256)+data)
		if data[0]!=chr(0x80): recv=self.brick.recv(block_recv)
		return recv

class NXTMotor(NXTComm,AbstractMotor):
	attrs_names={'position':'rot','speed_sp':'speed','stop_action':'stop'}
	speed_koef=0.1
	__stop_actions={'coast':chr(0x01),'hold':chr(0x07)}
	__stop='coast'
	__speed=0
	def __init__(self,address,brick):
		NXTComm.__init__(self,brick)
		self._address=chr(address)
	def _rotate(self,rot,speed,stop):
		self.__stop=stop
		self.__speed=speed
		speed=int(speed*self.speed_koef) if speed>=0 else 255-abs(int(speed*self.speed_koef))
		rot=int(rot*360%256) if rot>=0 else 255-abs(int(rot*360%256))
		#~ rot*=360
		#~ rotc=''
		#~ for i in range(5):
			#~ rotc+=chr(rot%256)
			#~ rot//=256
		#~ print(rotc)
		self._send(chr(0x00)+chr(0x04)+self._address+chr(speed)+self.__stop_actions[stop]+chr(0x00)+chr(0x00)+chr(0x20)+chr(rot)+chr(0x00)+chr(0x00)+chr(0x00)+chr(0x00))
	def _run(self,speed,stop='coast'):
		self.__stop=stop
		self.__speed=speed
		speed=int(speed*self.speed_koef) if speed>=0 else 255-abs(int(speed*self.speed_koef))
		self._send(chr(0x00)+chr(0x04)+self._address+chr(speed)+self.__stop_actions[stop]+chr(0x00)+chr(0x00)+chr(0x20)+chr(0x00)+chr(0x00)+chr(0x00)+chr(0x00)+chr(0x00))
	def _stop(self):
		self.__speed=0
		self._run(0,self.__stop)
		#~ self.set_attributes([('command','stop')])
	def _publish(self):
		return {'position':0,'stop':self.__stop,'speed':self.__speed}

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
	def __init__(self,address):
		self._brick=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
		self._brick.connect((address, 1))
		#Motor
		self._motors['outA']=NXTMotor(0x00,self._brick)
		self._motors['outB']=NXTMotor(0x01,self._brick)
		self._motors['outC']=NXTMotor(0x02,self._brick)
		self._sensors['in1']=None#self.sensor_types[driver](sensor)
		self._sensors['in2']=None#self.sensor_types[driver](sensor)
		self._sensors['in3']=None#self.sensor_types[driver](sensor)
		self._sensors['in4']=None#self.sensor_types[driver](sensor)
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





