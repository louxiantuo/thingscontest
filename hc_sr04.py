#!/usr/bin/env python
# coding=utf-8

import RPi.GPIO as GPIO
import time
import os
import threading

count_far = 0
count_near = 0
#key表示摄像头是否被打开，1则已经被打开，0则已经被关闭
key = 0
    

def checkdist():
     #发出信号
     GPIO.output(2,GPIO.HIGH)
     #保持10us以上
     time.sleep(0.000010)
     GPIO.output(2,GPIO.LOW)
     while not GPIO.input(3):
         pass


     #发现高电平时开始计时
     t1 = time.time()
     while GPIO.input(3):
         pass


     #高电平结束停止计时
     t2 = time.time()
     #返回距离，单位为米
     return (t2 - t1)*340/2
'''
GPIO.setmode(GPIO.BCM)
GPIO.setup(2,GPIO.OUT,initial = GPIO.LOW)
GPIO.setup(3,GPIO.IN)
count_far = 0
count_near = 0
#key表示摄像头是否被打开，1则已经被打开，0则已经被关闭
key = 0
time.sleep(2)

try:
     while True:
         print 'distance :%0.2f m' %checkdist()
         distance = checkdist()
         if distance < 1.0 :
             count_near = count_near + 1
             count_far = 0
         else :
             count_far = count_far + 1
             count_near = 0
         if count_near >= 5 :
             if key == 0 :
                 thread.start_new_thread(os.system('raspivid -t 0 -h 720 -w 1080 -fps 25 -hf -b 2000000 -o - | gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=192.168.31.145 port=5000'))
                 #os.system('python test.py')
                 key = 1
         if count_far >= 5 :
             if key == 1 :
                 os.system('pgrep gst-launch-1.0 | xargs kill -s 9')
                 key = 0
                 print("%d",key);

         time.sleep(0.5)
except KeyboardInterrupt:
     GPIO.cleanup()
       
'''
def hc_sr04():
     global count_far
     global count_near
     global key
     GPIO.setmode(GPIO.BCM)
     GPIO.setup(2,GPIO.OUT,initial = GPIO.LOW)
     GPIO.setup(3,GPIO.IN)
#    while True:
     print 'distance :%0.2f m' %checkdist()
     distance = checkdist()
     if distance < 1.0 :
         count_near = count_near + 1
         count_far = 0
     else :
         count_far = count_far + 1
         count_near = 0
         
    # if key == 0 and count_far >= 5:
    #     count_far = 0
     time.sleep(0.5)
     GPIO.cleanup()
     pass

def video():
     os.system('raspivid -t 0 -h 720 -w 1080 -fps 25 -hf -b 2000000 -o - | gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=192.168.31.145 port=5000')
     pass
def audio():
    os.system('gst-launch-0.10 -v alsasrc device=hw:1,0 ! audioconvert ! audioresample ! alawenc ! rtppcmapay ! udpsink host=192.168.31.103 port=5555')
    pass
def startthread():
    global count_near
    global count_far
    global key
#   t1 = threading.Thread(target=checkdist)
    t2 = threading.Thread(target=hc_sr04)
    t3 = threading.Thread(target=video)
    t4 = threading.Thread(target=audio)
#   t1.start()
    t2.start()
    if key == 0 and count_near >= 3:
         t3.start()
         t4.start()
         key = 1 
         count_near = 0
    if count_far >= 20 and key == 1:
         print "888888888888888888888888888"
         os.system('pkill -9 gst-launch-1.0')
         os.system('pkill -9 gst-launch-0.10')
         os.system('pkill -9 raspivid')
         print "888888888888888888888888888"
        #t2.stop()
        #t4.stop()   
         count_far = 0
         key = 0
    pass
try:
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(2,GPIO.OUT,initial = GPIO.LOW)
#     GPIO.setup(3,GPIO.IN)
#     t2 = threading.Thread(target=hc_sr04)
#     t3 = threading.Thread(target=video)
#     t4 = threading.Thread(target=audio)

#    count_far = 0
 #    count_near = 0
     #key表示摄像头是否被打开，1则已经被打开，0则已经被关闭
  #   key = 0

     time.sleep(2)
     while True:
         '''
         print 'distance :%0.2f m' %checkdist()
         distance = checkdist()
         if distance < 1.0 :
             count_near = count_near + 1
             count_far = 0
         else :
             count_far = count_far + 1
             count_near = 0
         '''
         #t2.start()
        # if count_near >= 5 :
         startthread()
#GPIO.cleanup()
    

except KeyboardInterrupt:
     GPIO.cleanup()

