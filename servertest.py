#!/usr/bin/env python
# coding=utf-8

import socket
import time
import os
import threading
phone_ip = ''
key = 0
def get_ip_address():
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.connect(("1.1.1.1",80))
    ipaddr = s.getsockname()[0]
    s.close()
    return ipaddr

def get_phone_ip(clientSocket):
    clientSocket.send("get_ip\n")
    phone_ip = clientSocket.recv(1024)
    return phone_ip

def sendvideo():
    global phone_ip
    number = len(phone_ip) - 1
    phone_ip = phone_ip[0:number]
    pipline ='raspivid -n -w 240 -h 320 -b 4500000 -fps 30 -vf -hf -t 999999 -o - | gst-launch-1.0 -e -vvv fdsrc ! h264parse ! rtph264pay pt=96 config-interval=10 ! udpsink host='+ phone_ip +' port=5000 alsasrc device=hw:1,0 ! queue ! audioconvert ! rtpL16pay ! udpsink host='+ phone_ip +' port=5555'
    os.system(pipline)
   # print pipline

def receive():
    receive_sound ='gst-launch-1.0 -v udpsrc port=1111 caps="application/x-rtp, media=(string)audio, clock-rate=(int)41000, channels=(int)1, payload=(int)96" ! rtpL16depay ! audioconvert ! autoaudiosink sync=false'
    os.system(receive_sound)

def server():
     global phone_ip
     phone_ip = 0
     serverName = '121.42.62.140'
     serverPort = 10000
     clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
     clientSocket.connect((serverName,serverPort))
     clientSocket.send("pi\n") 
     while 1 :
         phone_ip = get_phone_ip(clientSocket)
         print phone_ip
         ipaddr = get_ip_address()
         clientSocket.send("ip "+ipaddr+"\n")
         
         time.sleep(2)
     clientSocket.close() 

def startthreading():
     global key
     t1 = threading.Thread(target=server)
   #  t2 = threading.Thread(target=hc_sr04)
     t3 = threading.Thread(target=sendvideo)
     t4 = threading.Thread(target=receive)
     t1.start()
     time.sleep(2)
     if key == 0 :
         t3.start()
         key = 1
         t4.start()
     pass
try:
     time.sleep(1)
     startthreading()

except :
     print 'wrong'
