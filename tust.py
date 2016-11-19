#!/usr/bin/env python
# coding=utf-8

import socket
import time
import os
import threading
import requests
import RPi.GPIO as GPIO
from simple_recognizer import adduser as reg

#远程服务器属性
serverName = '115.29.55.106'
serverPort = 10000
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
directions=['RIGHT','LEFT','UP','DOWN']
filename=""
#打开所有GPIO口，setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(20,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)
GPIO.setup(27,GPIO.OUT)
#GPIO.setup(25,GPIO.OUT)//继电器未使用
GPIO.setup(2,GPIO.OUT,initial = GPIO.LOW)
GPIO.setup(3,GPIO.IN)
time.sleep(1)
#将所有舵机状态都设置成不变
GPIO.output(18,1)
GPIO.output(20,1)
GPIO.output(21,1)
GPIO.output(27,1)
#GPIO27 low to left
#GPIO18 LOW TO RIGHT
#GPIO22 low to down 
#GPIO23 low to up
#GPIO25 打开即打开继电器给STM32上电
#GPIO.output(25,0)
#超声波的距离是否超过一米
count_far = 0
count_near = 0
key_cam = 0 #为了控制不是人脸识别在同一时刻同时开启
#warning = 0#warning = 0 时没有人接近，warning = 1时有人接近
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
    return (t2-t1)*340/2


#将读取的超声波数据进行处理
def hc_sr04():
    global count_far
    global count_near
    global warning
    global key_cam
    global filename
    print 'distance: %0.2f m' %checkdist()
    print key_cam
    distance =checkdist()
    if distance < 1.0:
        count_near = count_near + 1
        count_far = 0
    else :
        count_far = count_far + 1
        count_near = 0
    if count_near >= 3 and key_cam == 0:#人脸识别在这里开始并向服务器返回对应的值
        key_cam = 1
        #表示这个已经打开除非count_far的值大于10的时候才会把key打开
        clientSocket.send("warning\n")
        t3 = threading.Thread(target=sendvideo)
        t3.start()
        # get user name
        print 'warning'
         # warning = 1
    if count_far >= 10 :
        key_cam = 0
    time.sleep(0.5)
    pass

#手机端IP
phone_ip = ''
#key表示摄像头打开的次数
key = 0

#获取本地树莓派自身的IP地址
def get_ip_address():
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.connect(("1.1.1.1",80))
    ipaddr = s.getsockname()[0]
    s.close()
    return ipaddr

#获取远程手机端的IP地址
def get_phone_ip(clientSocket):
    clientSocket.send("get_ip\n")
    phone_ip = clientSocket.recv(1024)
    return phone_ip

#从服务器获得方向指令并去掉\n
def get_dir(clentSocket):
    dir = clentSocket.recv(1024)
    number =len(dir) - 1
    dir = dir[0:number]             
    return dir

#将dir字符串解析并改变舵机的方向
def dir_change(dir):
    if dir == 'RIGHT':
         GPIO.output(18,0)
         time.sleep(0.10)
         GPIO.output(18,1)
    if dir == 'UP':
         GPIO.output(27,0)
         time.sleep(0.10)
         GPIO.output(27,1)
    if dir == 'DOWN':
         GPIO.output(21,0)
         time.sleep(0.10)
         GPIO.output(21,1)
    if dir == 'LEFT':
         GPIO.output(20,0)
         time.sleep(0.10)
         GPIO.output(20,1)
    
pass   
      
#发送声音和视频管道
def sendvideo():
    global phone_ip
    number = len(phone_ip) - 1
    phone_ip = phone_ip[0:number]
    pipline ='gst-launch-0.10 v4l2src ! queue ! "video/x-raw-yuv,width=320,height=240,framerate=(fraction)15/1" ! videoflip method=clockwise  ! x264enc speed-preset=ultrafast pass=qual quantizer=10 tune=zerolatency ! rtph264pay ! udpsink host='+phone_ip+' port=1111 alsasrc device=hw:1,0 ! queue ! audioconvert  ! rtpL16pay  ! udpsink host='+phone_ip+' port=2222'
    os.system(pipline)

#接受从手机端来的声音管道
def receive():
    receive_sound ='gst-launch-1.0 -v udpsrc port=1111 caps="application/x-rtp, media=(string)audio, clock-rate=(int)41000, channels=(int)1, payload=(int)96" ! rtpL16depay ! audioconvert ! autoaudiosink sync=false'
    os.system(receive_sound)

#服务器主进程
def server():
     global phone_ip
     global warning
     global clientSocket
     phone_ip = 0
     clientSocket.send("pi\n")
     print 'pi'
     phone_ip = get_phone_ip(clientSocket)
     print phone_ip
     ipaddr = get_ip_address()
     clientSocket.send("ip "+ipaddr+"\n")   
     print ipaddr
     while 1 :
         print 'dir'
         dir = get_dir(clientSocket)
         print dir
         if dir in directions:
             print 'dir........'
             dir_change(dir)
         elif dir:
             create_person(dir)
         else:
             pass
         dir = 'MID'
         ipaddr = get_ip_address()
         clientSocket.send("ip "+ipaddr+"\n")
         print ipaddr
         
         time.sleep(0.5)
     clientSocket.close() 
def startthreading():
     global key
     t1 = threading.Thread(target=server)
     t2 = threading.Thread(target=hc_sr04)
     #t3 = threading.Thread(target=sendvideo)
     t4 = threading.Thread(target=receive)
    #t5 = threading.Thread(target=thread_dir)
     #os.system('gst-launch-1.0 -v uridecodebin uri=file:///home/pi/doorbell.wav ! audioconvert ! audioresample ! audio/x-raw, rate=8000 ! autoaudiosink')
     if key == 0:
        t1.start()
     #  t5.start()
     time.sleep(2)
     t2.start()
     time.sleep(2)    
     if key == 0 :
        # t2.start()
        # t3.start()
         key = 1
         t4.start()
     pass
    
try:
     time.sleep(1)
     while True:
        startthreading()

except KeyboardInterrupt:     
         GPIO.cleanup()
