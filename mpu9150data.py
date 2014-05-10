#!/usr/bin/python

import sys
import serial
from serial.tools import list_ports
from mpudata import quat_packet, debug_packet, data_packet
import os
import time
import numpy as np
import matplotlib.pyplot as plt

class mpu9150interface(object):
    def __init__(self):
        #self.connect()
        #self.read()

        self.port="null"

    def connect(self):
        ports = list(self.serial_ports())
        for idx,val in enumerate(ports):
            print str(idx) + ". "+val

        num = raw_input("Select the port for the MPU-9150 : ")

        self.port = ports[int(num)]

        self.s = serial.Serial(self.port , 115200 , timeout=1)
        #self.ser.open()

        if self.s.isOpen():
            print "Connected..."
        else:
            self.s.open()
    
    def send(self, str):
        for i in range(0,len(str)):
            self.s.write(str[i])
            time.sleep(0.01)
                
    def write(self):
        command = ""
        while command != "q":
            command = raw_input("To Mpu>")
            self.send(command)

    def serial_ports(self):
        """
        Returns a generator for all available serial ports
        """
        if os.name == 'nt':
            # windows
            for i in range(256):
                try:
                    s = serial.Serial(i)
                    s.close()
                    yield 'COM' + str(i + 1)
                except serial.SerialException:
                    pass
        else:
            # unix
            for port in list_ports.comports():
                yield port[0]
                
    def read_debug(self):
        NUM_BYTES = 23
        p = None

        while self.s.inWaiting() >= NUM_BYTES:
            rs = self.s.read(NUM_BYTES)
            if ord(rs[0]) == ord('$'):
                pkt_code = ord(rs[1])
                print "\r@"
                if pkt_code == 1:
                    d = debug_packet(rs)
                    d.display()                
                elif pkt_code == 3:
                    d = data_packet(rs)
                    #d.display()
                    data = d.data
                    datatype = d.type

                    if datatype ==0:
                        self.index = self.index+1
                        if(self.index == 1000):
                            self.index=0
                        self.x_list[self.index] = data[0]
                        self.y_list[self.index] = data[1]
                        self.z_list[self.index] = data[2]
                        #plt.plot(self.x_list)
                        #plt.show()
                        #plt.pause(0.001)
                        #print ","
                        
                        if (self.index %2 == 1):
                            print "+",
                        else:
                            print "-",
                        sys.stdout.flush()
                        #print "1:"+str(data[0])
                        #print "2:"+str(data[1])
                        #print "3:"+str(data[2])

    def read(self):
        #self.fig = plt.figure()
        self.x_list = [None]*1000
        self.y_list = [None]*1000
        self.z_list = [None]*1000
        self.index = 0
        while True:
            self.read_debug()

if __name__ =="__main__":
    mpu =mpu9150interface()
    if (len(sys.argv) == 2):
        if sys.argv[1] == "setup":
            mpu.connect()
            mpu.write()
        else:
            mpu.s = serial.Serial(sys.argv[1],115200, timeout =1)
            #mpu.s = serial.Serial("/dev/cu.usbmodemfa141",115200, timeout =1)        
            mpu.read()
