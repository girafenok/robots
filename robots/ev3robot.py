#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,stat
from time import *
from PIL import Image
import paho.mqtt.client as mqtt
import uuid
import subprocess
#const
SPEED_DEFAULT=70

#iot mosquitto
node="%012x"%uuid.getnode()
iot_name="ev3-%s"%node[2:]
iot=mqtt.Client(iot_name)
iot.connect("ev3dev.gabbler.ru", 1977)

class EV3Motor(object):
	__name=''
	__address=''
	attrs_names={'position':'degrees','duty_cycle_sp':'speed','stop_command':'stop'}
	def __init__(self,address):
		self.__address=address
		with open('/sys/class/tacho-motor/'+self.__address+'/address','r') as fp:
			self.__name=fp.read().replace('\n','')
	def set_attributes(self,attributes):
		for attr in attributes:
			with open('/sys/class/tacho-motor/%s/%s'%(self.__address,attr[0]),'w') as fp:
				fp.write(str(attr[1]))	
	def forward(self,degrees=0,speed=SPEED_DEFAULT,stop='hold'):
		self.rotate(abs(degrees),speed,stop)
	def backward(self,degrees=0,speed=SPEED_DEFAULT,stop='hold'):
		#~ self.rotate(speed,int(self.attrs['position_sp'])-degrees)
		self.rotate(-abs(degrees),speed,stop)
	def rotate(self,degrees=0,speed=SPEED_DEFAULT,stop='coast'):
		self.set_attributes([('position_sp',degrees),('duty_cycle_sp',speed),('stop_command',stop),('command','run-to-rel-pos')])
	def run(self,speed=SPEED_DEFAULT,stop='hold'):
		self.set_attributes([('duty_cycle_sp',speed),('stop_command',stop),('command','run-forever')])
	def stop(self):
		self.set_attributes([('command','stop')])
	def publish(self):
		for attr in ['position','duty_cycle_sp','stop_command']:
			with open('/sys/class/tacho-motor/%s/%s'%(self.__address,attr),'r') as fp:
				iot.publish(bytes("%s/%s/%s"%(iot_name,self.__name,self.attrs_names[attr])),bytes(fp.read().replace('\n','')))

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
	def publish(self):
		with open('/sys/class/lego-sensor/%s/value0'%(self.__address),'r') as fp:
			iot.publish(bytes("%s/%s/value"%(iot_name,self.__name)),bytes(fp.read().replace('\n','')))
		
class EV3Color(EV3Sensor):
	pass


class EV3Leds(object):
	colors={'red':{'green':'0','red':'255'},'yellow':{'green':'255','red':'255'},'green':{'green':'255','red':'0'}}
	def __init__(self,address):
		self.__address=address
	def set_mode(self,mode):
		with open('/sys/class/leds/ev3:%s:ev3dev/trigger'%(self.__address),'w') as fp:
			fp.write(mode)
	def set_color(self,color):
		with open('/sys/class/leds/ev3:%s:ev3dev/brightness'%(self.__address),'w') as fp:
			fp.write(str(color))
	def set_preset(self,color):
		if color == 'black' or color == 0:
			with open('/sys/class/leds/ev3:%s:red:ev3dev/brightness'%(self.__address),'w') as fp:
				fp.write(str(0))
			with open('/sys/class/leds/ev3:%s:green:ev3dev/brightness'%(self.__address),'w') as fp:
				fp.write(str(0))
		elif color == 'red' or color == 1:
			with open('/sys/class/leds/ev3:%s:red:ev3dev/brightness'%(self.__address),'w') as fp:
				fp.write(str(255))
			with open('/sys/class/leds/ev3:%s:green:ev3dev/brightness'%(self.__address),'w') as fp:
				fp.write(str(0))
		elif color == 'yellow' or color == 2:
			with open('/sys/class/leds/ev3:%s:red:ev3dev/brightness'%(self.__address),'w') as fp:
				fp.write(str(35))
			with open('/sys/class/leds/ev3:%s:green:ev3dev/brightness'%(self.__address),'w') as fp:
				fp.write(str(255))
		elif color == 'green' or color == 3:
			with open('/sys/class/leds/ev3:%s:red:ev3dev/brightness'%(self.__address),'w') as fp:
				fp.write(str(0))
			with open('/sys/class/leds/ev3:%s:green:ev3dev/brightness'%(self.__address),'w') as fp:
				fp.write(str(255))
		elif color == 'orange' or color == 4:
			with open('/sys/class/leds/ev3:%s:red:ev3dev/brightness'%(self.__address),'w') as fp:
				fp.write(str(255))
			with open('/sys/class/leds/ev3:%s:green:ev3dev/brightness'%(self.__address),'w') as fp:
				fp.write(str(255))


class EV3Sound(object):
	def play(self,sound):
		pass
	def play_tone(self,sound):	# as sudo
		with open('/sys/devices/platform/snd-legoev3/tone','w') as fp:
			fp.write(str(sound))
	def beep(self,params=None):
		subprocess.call('beep %s'%(str(params)), shell=True)
	def speak(self,msg,speed=175,bass=100):
		subprocess.call('espeak -a %s -s %s "%s" --stdout | aplay'%(bass,speed,msg), shell=True)
	def set_volume(self,volume):
		subprocess.call('amixer set Playback,0 %s'%(str(volume) + '%'), shell=True)


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
		import cv2
		self.__address=address
		try:
			self.camera=cv2.VideoCapture(self.__address)
			#~ capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH ,640)
			#~ capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT ,480)
		except:
			pass
	def capture(self):
		return self.camera.read()[1] if self.camera!=None else None
	def publish(self):
		pass
class EV3Robot(object):
	__motors={}
	__sensors={}
	leds={}
	buttons={}
	camera=None
	lcd=None
	sensor_types={'lego-ev3-color':lambda a: EV3Color(a),'lego-nxt-touch':lambda a: EV3Sensor(a),'lego-ev3-touch':lambda a: EV3Sensor(a),'lego-ev3-ir':lambda a: EV3Sensor(a),'lego-ev3-us':lambda a: EV3Sensor(a),'lego-nxt-us':lambda a: EV3Sensor(a),'lego-nxt-light':lambda a: EV3Sensor(a),'nxt-analog':lambda a: EV3Sensor(a),'lego-ev3-gyro':lambda a: EV3Sensor(a)}
	def __init__(self,is_camera=False):
		#Camera
		if is_camera: self.camera=EV3Camera(0)
		#Motor
		for motor in os.listdir('/sys/class/tacho-motor'):
			with open('/sys/class/tacho-motor/'+motor+'/address','r') as fp:
				self.__motors[fp.read().replace('\n','')]=EV3Motor(motor)
		#Seonsor
		try:
			for sensor in os.listdir('/sys/class/lego-sensor'):
				with open('/sys/class/lego-sensor/'+sensor+'/driver_name','r') as fd: driver=fd.read().strip()
				with open('/sys/class/lego-sensor/'+sensor+'/address','r') as fa: name=fa.read().strip().replace(':i2c1','').replace(':i2c2','').replace(':i2c3','').replace(':i2c4','').replace('\n','')
				self.__sensors[name]=self.sensor_types[driver](sensor)
		except:
			pass
		#Leds
		self.leds['left:red']=EV3Leds('left:red')
		self.leds['left:green']=EV3Leds('left:green')
		self.leds['right:red']=EV3Leds('right:red')
		self.leds['right:green']=EV3Leds('right:green')
		self.leds['right']=EV3Leds('right')
		self.leds['left']=EV3Leds('left')
		#Sound
		self.sound=EV3Sound()
		#Buttons
		self.buttons['left']=EV3Button('left')
		self.buttons['right']=EV3Button('right')
		self.buttons['up']=EV3Button('up')
		self.buttons['down']=EV3Button('down')
		self.buttons['ok']=EV3Button('ok')
		self.buttons['cancel']=EV3Button('cancel')
		#LCD
		self.lcd=EV3LCD()
		print(self.__sensors,self.__motors)
	def motor(self,port):
		return self.__motors[port]
	def sensor(self,port):
		return self.__sensors[port]
	def led(self,led):
		return self.leds[led]
	def screen(self):
		return self.lcd
	def publish(self,topic,data):
		iot.publish(bytes("%s/%s"%(iot_name,topic)),bytes(data))
	#move
	def forward(self,degrees=0,speed=SPEED_DEFAULT,stop='hold'):
		try:
			self.__motors['outB'].forward(degrees,speed,stop)
		except:
			pass
		try:
			self.__motors['outC'].forward(degrees,speed,stop)
		except:
			pass
	def backward(self,degrees=0,speed=SPEED_DEFAULT,stop='hold'):
		try:
			self.__motors['outB'].backward(degrees,speed,stop)
		except:
			pass
		try:
			self.__motors['outC'].backward(degrees,speed,stop)
		except:
			pass
	def left(self,degrees=0,speed=SPEED_DEFAULT,stop='hold'):
		try:
			self.__motors['outB'].forward(degrees,speed,stop)
		except:
			pass
		try:
			self.__motors['outC'].backward(degrees,speed,stop)
		except:
			pass
	def right(self,degrees=0,speed=SPEED_DEFAULT,stop='hold'):
		try:
			self.__motors['outB'].backward(degrees,speed,stop)
		except:
			pass
		try:
			self.__motors['outC'].forward(degrees,speed,stop)
		except:
			pass
	#sensors
	def is_object(self,distance=8):
		try:
			res=self.__sensors['in1'].value()<distance
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
			res=int(self.__sensors['in3'].value())==1
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
