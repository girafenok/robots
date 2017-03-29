#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  trikrobot.py
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
#  MA 02110-1301, USA.*-

import os,stat
from time import *



class TrikMotor(object):
	def __init__(self,address):
		self.__address=address
	def set_attributes(self,attributes):
		for attr in attributes:
			with open('/sys/class/tacho-motor/%s/%s'%(self.__address,attr[0]),'w') as fp:
				fp.write(str(attr[1]))
			
	def rotate(self,speed=100,degrees=0,stop='coast'):
		self.set_attributes([('position_sp',degrees),('duty_cycle_sp',speed),('stop_command',stop),('command','run-to-rel-pos')])
	def run(self,speed=100,stop='coast'):
		self.set_attributes([('duty_cycle_sp',speed),('stop_command',stop),('command','run-forever')])
	def stop(self):
		self.set_attributes([('command','stop')])

#~ class EV3Sensor(object):
	#~ def __init__(self,address):
		#~ self.__address=address
	#~ def set_mode(self,mode):
		#~ with open('/sys/class/lego-sensor/%s/mode'%(self.__address),'w') as fp:
			#~ fp.write(mode)
	#~ def value(self):
		#~ with open('/sys/class/lego-sensor/%s/value0'%(self.__address),'r') as fp:
			#~ return float(fp.read())

#~ class EV3Color(EV3Sensor):
	#~ pass


class TrikLeds(object):
	colors={'red':{'green':'0','red':'255'},'yellow':{'green':'255','red':'255'},'green':{'green':'255','red':'0'}}
	def __init__(self,address):
		self.__address=address
	def set_mode(self,mode):
		with open('/sys/class/leds/led_%s/trigger'%(self.__address),'w') as fp:
			fp.write(mode)
	def set_color(self,color):
		with open('/sys/class/leds/led_%s/brightness'%(self.__address),'w') as fp:
			fp.write(str(color))

#~ class EV3Sound(object):
	#~ def play(self,sound):
		#~ pass
	#~ def play_tone(self,sound):
		#~ pass
#~ class EV3Button(object):
	#~ def __init__(self,address):
		#~ self.__address=address


#~ class EV3LCD(object):
	#~ screen=Im
	#~ def __init__(self):
		

#~ class EV3Camera(object):
	#~ camera=None
	#~ def __init__(self,address):
		#~ self.__address=address
		#~ try:
			#~ self.camera=cv2.VideoCapture(0)
			#~ #capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH ,640)
			#~ #capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT ,480)
		#~ except:
			#~ pass
	#~ def capture(self):
		#~ return self.camera.read()[1] if self.camera!=None else None
class TrikRobot(object):
	motors={}
	sensors={}
	leds={}
	buttons={}
	camera=None
	lcd=None
	#~ sensor_types={'lego-ev3-color':lambda a: EV3Color(a),'lego-nxt-touch':lambda a: EV3Sensor(a),'lego-ev3-touch':lambda a: EV3Sensor(a),'lego-ev3-ir':lambda a: EV3Sensor(a),'lego-ev3-us':lambda a: EV3Sensor(a),'lego-nxt-us':lambda a: EV3Sensor(a),'lego-nxt-light':lambda a: EV3Sensor(a),'nxt-analog':lambda a: EV3Sensor(a),'lego-ev3-gyro':lambda a: EV3Sensor(a)}
	def __init__(self):
		#Motor
		#~ for motor in os.listdir('/sys/class/tacho-motor'):
			#~ with open('/sys/class/tacho-motor/'+motor+'/address','r') as fp:
				#~ self.motors[fp.read().replace('\n','')]=EV3Motor(motor)
		#~ #Seonsor
		#~ try:
			#~ for sensor in os.listdir('/sys/class/lego-sensor'):
				#~ with open('/sys/class/lego-sensor/'+sensor+'/driver_name','r') as fd: driver=fd.read().strip()
				#~ with open('/sys/class/lego-sensor/'+sensor+'/address','r') as fa: name=fa.read().strip().replace(':i2c1','').replace(':i2c2','').replace(':i2c3','').replace(':i2c4','').replace('\n','')
				#~ self.sensors[name]=self.sensor_types[driver](sensor)
		#~ except:
			#~ pass
		#~ #Camera
		#~ self.camera=EV3Camera(0)
		#~ #Leds
		self.leds['green']=TrikLeds('green')
		self.leds['red']=TrikLeds('red')
		#~ #Sound
		#~ sound=EV3Sound()
		#~ #Buttons
		#~ self.buttons['left']=EV3Button('left')
		#~ self.buttons['right']=EV3Button('right')
		#~ self.buttons['up']=EV3Button('up')
		#~ self.buttons['down']=EV3Button('down')
		#~ self.buttons['ok']=EV3Button('ok')
		#~ self.buttons['cancel']=EV3Button('cancel')
		#~ #LCD
		#~ self.lcd=EV3LCD()
		#~ print(self.sensors,self.motors)
	#~ def motor(self,port):
		#~ return self.motors[port]
	#~ def sensor(self,port):
		#~ return self.sensors[port]
	def led(self,led):
		return self.leds[led]
	#~ def screen(self):
		#~ return self.lcd
	
	
	
if __name__ == '__main__':		
	robo=TrikRobot()
	#~ robo.motor('outA').run(100)
	#~ sleep(2)
	#~ robo.motor('outA').stop()
	#~ robo.motor('outA').rotate(100,720)
	#lego-ev3-color modes: COL-REFLECT COL-AMBIENT COL-COLOR REF-RAW RGB-RAW COL-CAL
	#lego-ev3-gyro modes: GYRO-ANG GYRO-RATE GYRO-FAS GYRO-G&A GYRO-CAL TILT-RATE TILT-ANG
	#lego-ev3-ir modes: US-DIST-CM US-DIST-IN US-LISTEN US-SI-CM US-SI-IN US-DC-CM US-DC-IN
	
	#~ robo.sensor('in2').set_mode('RGB-RAW')
	robo.led('red').set_color(255)
	robo.led('green').set_color(255)
	#~ robo.led('right').set_color((255,100))
	while True:
		pass
		#~ print(robo.sensor('in2').value())
		#~ cv2.imwrite("capture.jpg", robo.capture())
		#~ sleep(1)






