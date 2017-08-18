#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *
from time import *

robo=EV3Robot()
#~ robo.lcd.imread('1.jpg')
#~ robo.lcd.show()
#~ sleep(10)
#~ robo.motor('outA').run()
#~ sleep(3)
#~ robo.motor('outA').stop()

#~ robo.motor('outA').forward(3)

#~ robo.sound().speak('Hello Ev3')
#~ robo.sound().tone('C#4',500)
#~ robo.sound().tone(480,500)
robo.sound().play('geroispo.mp3',async=True)


#~ robo.sound().tone(520,500)

#robo.sound().volume(2)
#robo.sound().beep()
#sleep(0.5)
#robo.sound().volume(75)
#robo.sound().beep()
#robo.sound().speak('Hello')
#robo.motor('outA').forward(1)



#Leds
robo.led('left').color('red')
robo.led('right').color('green')
sleep(5)
robo.led('left').color('orange')
robo.led('right').color('yellow')
sleep(5)
robo.led('left').color('black')
robo.led('right').color('black')
sleep(5)
robo.led('left:green').brightness('55')
robo.led('left:red').brightness('55')
robo.led('right:green').brightness('35')
robo.led('left:red').brightness('255')
sleep(5)
