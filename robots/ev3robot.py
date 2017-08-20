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
	pass
class EV3Motor(object):
	__name=''
	__address=''
	attrs_names={'position':'rot','speed_sp':'speed','stop_action':'stop'}
	def __init__(self,address):
		self.__address=address
		with open('/sys/class/tacho-motor/'+self.__address+'/address','r') as fp:
			self.__name=fp.read().replace('\n','')
		self.set_attributes([('command','reset')])
	def set_attributes(self,attributes):
		for attr in attributes:
			with open('/sys/class/tacho-motor/%s/%s'%(self.__address,attr[0]),'w') as fp:
				fp.write(str(attr[1]))	
	def forward(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		self.rotate(abs(rot),speed,stop)
	def backward(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		self.rotate(-abs(rot),speed,stop)
	def rotate(self,rot=0,speed=SPEED_DEFAULT,stop='coast'):
		self.set_attributes([('position_sp',rot*360),('speed_sp',speed),('stop_action',stop),('command','run-to-rel-pos')])
	def run(self,speed=SPEED_DEFAULT,stop='hold'):
		self.set_attributes([('speed_sp',speed),('stop_action',stop),('command','run-forever')])
	def stop(self):
		self.set_attributes([('command','stop')])
	def publish(self):
		for attr in ['position','speed_sp','stop_action']:
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
class EV3Led(object):
	def __init__(self,address):
		self.__address=address
	def set_mode(self,mode):
		with open('/sys/class/leds/ev3:%s:ev3dev/trigger'%(self.__address),'w') as fp:
			fp.write(mode)
	def brightness(self,value):
		with open('/sys/class/leds/ev3:%s:ev3dev/brightness'%(self.__address),'w') as fp:
			fp.write(str(int(value)))


class EV3Sound(object):
	#4 - 1 octave, 5 - 2 octave, 6 - 3 octave, 7 - 4 octave, 8 - 5 octave,0 - sub octave, 1 - contr octave, 2 - big octave, 3 - small octave,
	__tones_map={'C':[16.352,32.703,65.406,130.81,261.63,523.25,1046.5,2093,4186,8372,16744], 'C#':[17.324,34.648,69.296,138.59,277.18,554.37,1108.7,2217.5,4434.9,8869.8,17739.7], 'D':[18.354,36.708,73.416,146.83,293.66,587.33,1174.7,2349.3,4698.6,9397.3,18794.5], 'D#':[], 'E':[20.602,41.203,82.407,164.81,329.63,659.26,1318.5,2637,5274,10548,21096.2], 'F':[21.827,43.654,87.307,174.61,349.23,698.46,1396.9,2793.8,5587.7,11175,22350.6], 'F#':[], 'G':[], 'G#':[], 'A':[], 'A#':[], 'B':[]}
	def play(self,fname,async=False):
		if async:
			Thread(target=self.__play, args=(fname,)).start()
		else:
			self.__play(fname)
	def __play(self,fname):
		fname=os.path.exists('/home/robot/.sounds/%s'%fname)  and '/home/robot/.sounds/%s'%fname or 'music/%s'%fname
		os.system('mpg123 -q %s '%fname)
	def tone(self,tone,time,async=False):
		if async:
			Thread(target=self.__tone, args=(tone,time,)).start()
		else:
			self.__tone(tone,time)
	def __tone(self,tone,time):
		if isinstance(tone,(str,unicode)):	tone=self.__tones_map[tone[:len(tone)-1]][int(tone[-1])]
 		with open('/sys/devices/platform/snd-legoev3/tone','w') as fp:
			fp.write("%i %i"%(tone,time))
		sleep(time/1000.0)
	def tones(self,tones,async=False):
		if async:
			Thread(target=self.__tone, args=(tones,)).start()
		else:
			self.__tones(tones)
	def __tones(self,tones):
		for tone in tones:
			self.__tone(tone[0],tone[1])
	def beep(self):
		self.__tone(440,250)
	def say(self,msg,speed=175,bass=100,async=False):
		if async:
			Thread(target=self.__say, args=(msg,speed,bass,)).start()
		else:
			self.__say(msg,speed,bass)
	def __say(self,msg,speed=175,bass=100):
		os.system('espeak -a %s -s %s "%s" --stdout | aplay -q'%(bass,speed,msg))
	def volume(self,volume):
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
class EV3Robot(object):
	__motors={}
	__sensors={}
	__leds={}
	buttons={}
	camera=None
	__lcd=None
	__sound=None
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
		self.__leds['left:red']=EV3Led('left:red')
		self.__leds['left:green']=EV3Led('left:green')
		self.__leds['right:red']=EV3Led('right:red')
		self.__leds['right:green']=EV3Led('right:green')
		self.__leds['left']=EV3Leds('left')
		self.__leds['right']=EV3Leds('right')
		#Sound
		self.__sound=EV3Sound()
		#Buttons
		self.buttons['left']=EV3Button('left')
		self.buttons['right']=EV3Button('right')
		self.buttons['up']=EV3Button('up')
		self.buttons['down']=EV3Button('down')
		self.buttons['ok']=EV3Button('ok')
		self.buttons['cancel']=EV3Button('cancel')
		#LCD
		self.__lcd=EV3LCD()
		print(self.__sensors,self.__motors)
	def motor(self,port):
		return self.__motors[port]
	def sensor(self,port):
		return self.__sensors[port]
	def led(self,led):
		return self.__leds[led]
	def screen(self):
		return self.__lcd
	def sound(self):
		return self.__sound
	def publish(self,topic,data):
		iot.publish(bytes("%s/%s"%(iot_name,topic)),bytes(data))
	#move
	def forward(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		try:
			self.__motors['outB'].forward(rot,speed,stop)
		except:
			pass
		try:
			self.__motors['outC'].forward(rot,speed,stop)
		except:
			pass
	def backward(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		try:
			self.__motors['outB'].backward(rot,speed,stop)
		except:
			pass
		try:
			self.__motors['outC'].backward(rot,speed,stop)
		except:
			pass
	def left(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		try:
			self.__motors['outB'].forward(rot,speed,stop)
		except:
			pass
		try:
			self.__motors['outC'].backward(rot,speed,stop)
		except:
			pass
	def right(self,rot=1,speed=SPEED_DEFAULT,stop='hold'):
		try:
			self.__motors['outB'].backward(rot,speed,stop)
		except:
			pass
		try:
			self.__motors['outC'].forward(rot,speed,stop)
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






