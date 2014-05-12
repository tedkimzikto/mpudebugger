#!/usr/bin/python

import serial
from serial.tools import list_ports
import sys
import os
from mpudata import quat_packet, debug_packet, data_packet
import threading
import time



class Mpu9150:
    def __init__(self):
        print "initializing 9150 class"

    def command(self, line):
        if line == "help":
            print "accel - print accel data"
            print "connect - connect to module"
            print "sample - change thie sampling rate"
        elif line == "write":
            self.write()
        elif line == "debug loop":
            self.debug_loop()
        elif line == "read":
            self.read()
        elif line == "connect":
            self.connect()
        elif line == "sample":
            self.change_sampling_rate()
        elif line =="":
            print "say something"     
        elif line == "q":
            print "quitting"
        else:
            print line+" : unkonwn command. type help"


    def send(self, str):
         for i in range(0,len(str)):
                self.s.write(str[i])
                time.sleep(0.01)
            
    def write(self):
        command = ""
        while command != "q":
            command = raw_input("To Mpu>")
            self.send(command)

    def read_debug_loop(self):
        self.running = True
        self.read_debug_flag = True
        while self.read_debug_flag:
            self.read_debug()
            time.sleep(0.01)
            
    def debug_loop(self):
        read_thread = threading.Thread(target = self.read_debug_loop)
        read_thread.start()

        while 1:
            command = raw_input("To Mpu9150>")
            if command == "q":
                read_thread.shutdown = True
                self.read_debug_flag = False
                read_thread.join()
                break
            self.send(command)
                        
    def loop_read(self):
        while 1:
            self.read()
        
    def ToggleAccel(self):
        print "toggle"

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
            print "Port busy"

    def change_sampling_rate(self):
        print "changing sampling rates to : "
        print "1. 100,000"
        print "2. 50,000"
        print "3. 25,000"
        print "4. 20,000"
        print "5. 10,000"
        command = raw_input("Choose sampling rate(1-5) : ")

        self.ser.write("inv"+command)
        

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
            self.running = not self.running
            '''
            if(self.running):
                print "\r+",
            else:
                print "\r-",

            sys.stdout.flush()
            '''    
            rs = self.s.read(NUM_BYTES)
            if ord(rs[0]) == ord('$'):
                #print ord(rs[0]) + ord(rs[1])
                pkt_code = ord(rs[1])
                if pkt_code == 1:
                    d = debug_packet(rs)
                    d.display()
                    print d
                    #self.debug_delegate.dispatch(d)
                elif pkt_code == 3:
                    d = data_packet(rs)
                    #d.display()
                    data = d.data
                    datatype = d.type

                    if datatype == 0:
                        print "1:"+data[0]
                        print "2:"+data[1]
                        print "3:"+data[2]

    def read(self):

        NUM_BYTES = 23

        p = None

        while self.s.inWaiting() >= NUM_BYTES:

            rs = self.s.read(NUM_BYTES)

            if ord(rs[0]) == ord('$'):
                pkt_code = ord(rs[1])

                if pkt_code == 1:

                    d =debug_packet(rs)
                    print d
                    #self.debug_delegate.dispatch(d)

                elif pkt_code == 2:

                    p = quat_packet(rs)
                    #
                    #self.quat_delegate.dispatch(p) 

                elif pkt_code == 3:
                    d = data_packet(rs)
                    #d.display()3
                    #self.data_delegate.dispatch(d)

                else:
                    sss = "no handler for pkt_code",pkt_code
                    print sss
                    #f_file.write(sss + '\n')

            else:

                c = ' '
                print "serial misaligned!"
                               
                while not ord(c) == ord('$'):

                    c = self.s.read(1)

                self.s.read(NUM_BYTES-1)



if __name__ == "__main__":
    command = ""
    mpu9150 = Mpu9150()
    while(command != "quit"):
        command = raw_input("mpu9150> ")
        mpu9150.command(command)
