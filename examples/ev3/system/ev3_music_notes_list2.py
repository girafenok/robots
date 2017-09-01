#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ev3robot import *
from time import *

a = 550
starwars = (("G3",a),("G3",a),("G3",a),("D#3",a*0.75),("B3",a*0.25), ("G3",a),("D#3",a*0.75),("B3",a*0.25),("G3",a*2), ("D4",a),("D4",a),("D4",a),("D#4",a*0.75),("B3",a*0.25), ("F#3",a),("D#3",a*0.75),("B3",a*0.25),("G3",a*2),)

b = 410
dengi = (("F4",b),("F4",b),("E4",b/2),("D4",b/2),("C4",b),("D4",b/2),("D4",b/2),("D4",b/2),("E4",b/2),("D4",b/2),("C4",b/2),("A3",b),("A3",b/2),("B3",b/2),("C4",b/2),("A3",b/2),("G3",b/2),("C4",b/2),("C4",b/2),("C4",b/2),("F4",b/2),("E4",b/2),("D4",b/2),("C4",b/2),("C4",b))

c = 630
phone = (("E5",c/3),("G5",c),("sleep",1000),("G5",c/3),("E5",c),("sleep",1000),("A5",c/3),("G5",c/3),("A5",c/3),("G5",c/3),("A5",c/3),("G5",c/3),("A5",c/3),("G5",c/3),("A5",c/3),("B5",c),("sleep",1000),("E5",c/3),("G5",c),("sleep",1000),("G5",c/3),("E5",c),("sleep",1000),("A5",c/3),("G5",c/3),("A5",c/3),("G5",c/3),("A5",c/3),("G5",c/3),("A5",c/3),("G5",c/3),("A5",c/3),("B5",c))

d = 150
nokia = (("E5",d),("D5",d),("F#4",d*1.8),("G#4",d*1.8),("C#5",d),("B4",d),("D4",d*1.8),("E4",d*1.8),("B4",d),("A4",d),("C#4",d*1.8),("E4",d*1.8),("A4",d*3))

e = 300
pinkpanther = (("D#4",e/2),("E4",e),("sleep",500),("F#4",e/2),("G4",e),("sleep",500),("D#4",e/2),("E4",e),("F#4",e/2),("G4",e),("C5",e/2),("B4",e),("E4",e/2),("G4",e),("B4",e/2),("A#4",e*2.8),("A4",e/2),("G4",e/2),("E4",e/2),("D4",e/2),("E4",e*2),("sleep",1000), ("D#4",e/2),("E4",e),("sleep",500),("F#4",e/2),("G4",e),("sleep",500),("D#4",e/2),("E4",e),("F#4",e/2),("G4",e),("C5",e/2),("B4",e),("G4",e/2),("B4",e),("E5",e*0.55),("D#5",e*2.85))

f = 445
crazyfrog = (("D3",f),("F3",f),("D3",f/2),("D3",f/4),("G3",f/2),("D3",f/2),("C3",f/2),("D3",f),("A3",f),("D3",f/2),("D3",f/4),("A#3",f/2),("A3",f/2),("F3",f/2),("D3",f/2),("A3",f/2),("D4",f/2),("D3",f/4),("C3",f/2),("C3",f/4),("A2",f/2),("E3",f/2),("D3",f*2.2))



robo=EV3Robot()

robo.sound().tones(starwars)
sleep(2)

robo.sound().tones(dengi)
sleep(2)

robo.sound().tones(phone)
sleep(2)

robo.sound().tones(nokia)
sleep(2)

robo.sound().tones(pinkpanther)
sleep(2)

robo.sound().tones(crazyfrog)
