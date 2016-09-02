#!/usr/bin/env python
# coding=utf-8

#import threading
import socket
#from socket import *

def get_ip_address():
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.connect(("1.1.1.1",80))
    ipaddr = s.getsockname()[0]
    s.close()
    return ipaddr

if  __name__ == '__main__' :
    ipaddr = get_ip_address()
    serverName = '192.168.1.112'
    serverPort = 12000
    clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    #sentence = raw_input(ipaddr)
    clientSocket.send(ipaddr)
    modifiedSentence = clientSocket.recv(1024)
    print 'from server:',modifiedSentence
    clientSocket.close()
