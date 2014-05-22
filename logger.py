#!/usr/bin/python
import sys
import serial
from serial.tools import list_ports
from mpudata import quat_packet, debug_packet, data_packet
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import euclid
import pymysql

class mpu9150interface(object):
    def __init__(self):
        #self.connect()
        #self.read()
        print "init"
        self.SIZE = 200
        self.x_list = [None]*self.SIZE
        self.y_list = [None]*self.SIZE
        self.z_list = [None]*self.SIZE

        self.gyrox_list = [None]*self.SIZE
        self.gyroy_list = [None]*self.SIZE
        self.gyroz_list = [None]*self.SIZE

        self.mag_list = [None]*self.SIZE
        self.quat_list = [None]*self.SIZE
        self.accel_list = [None]*self.SIZE
        self.calibrated_list = [None] * self.SIZE
        
        self.calibrated_x = [None] * self.SIZE
        self.calibrated_y = [None] * self.SIZE
        self.calibrated_z = [None] * self.SIZE

        self.linearAccel_x = [None] * self.SIZE
        self.linearAccel_y = [None] * self.SIZE
        self.linearAccel_z = [None] * self.SIZE
                
        self.port="null"
        self.gravity = np.array([0,0,0])

    def connect(self):
        ports = list(self.serial_ports())
        for idx,val in enumerate(ports):
            print str(idx) + ". "+val

        num = raw_input("Select the port for the MPU-9150 : ")

        self.port = ports[int(num)]

        self.s = serial.Serial(self.port , 115200 , timeout=1)
        #self.ser.open()

        #self.s.close()
        
        if self.s.isOpen():
            print "Connected..."
        else:
            self.s.open()
    
    def send(self, str):
        for i in range(0,len(str)):
            self.s.write(str[i])
            time.sleep(0.1)
                
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

    def zeroing(self):
        self.index=0
        while (self.index <2 ):
            self.read_debug()
            #print self.index,
        self.gravity = np.array([ self.data[0],self.data[1] ,self.data[2] ])
        print self.gravity
                
    def read_debug(self):
        NUM_BYTES = 23
        p = None

        time.sleep(0.0005)

        while self.s.inWaiting() >= NUM_BYTES:
            #time.sleep(0.01)
            if self.index_accel >= self.SIZE:
                break
            rs = self.s.read(NUM_BYTES)
            if ord(rs[0]) == ord('$'):
                pkt_code = ord(rs[1])
                #print "."
                print "\r",#+str(pkt_code),
                if pkt_code == 1:
                    d = debug_packet(rs)
                    d.display()
                elif pkt_code == 2:
                    p = quat_packet(rs)
                    self.quat_list[self.index_quat] = p
                    self.index_quat = self.index_quat + 1
                    print self.index_quat
                    #p.display()
                    print "+",
                elif pkt_code == 3:
                    d = data_packet(rs)
                    #d.display()
                    self.data = d.data
                    datatype = d.type

                    if datatype ==0:
                        #self.index = self.index+1
                        #print self.index
                        self.accel_list[self.index_accel] = d
                        self.x_list[self.index_accel] = d.data[0]
                        self.y_list[self.index_accel] = d.data[1]
                        self.z_list[self.index_accel] = d.data[2]

                        vec = [d.data[0] , d.data[1], d.data[2]]
                        #vec = vec - self.gravity
                        #norm = np.linalg.norm(vec)
                        #norm = norm-1
                        #self.mag_list[self.index_accel] = norm
                        
                        self.index_accel = self.index_accel +1
                        print "-",

                    if datatype == 1:
                        self.gyrox_list[self.index_accel] = d.data[0]
                        self.gyroy_list[self.index_accel] = d.data[1]
                        self.gyroz_list[self.index_accel] = d.data[2]

            sys.stdout.flush()

    def read(self):

        
        self.index_quat = 0
        self.index_accel = 0 
        print "logging..."


        n=0
        while( self.index_quat < (self.SIZE-1)):
            self.send("invz")
            self.read_debug()
            
            print self.index_accel,
            sys.stdout.flush()

        #self.s.close()
        print "plotting..."
        #plt.plot(self.mag_list)
        #plt.show()

        for i in range(0,self.SIZE):
            #print i 
            q = self.quat_list[i]
            d = self.accel_list[i]

            if (q is not None) and (d is not None):
            #if not isinstance(q,None) and not isinstance(d,None)
                #print d
                v = euclid.Vector3(d.data[0], d.data[1], d.data[2])
                #quat = q.to_q().conjugated()
                quat = q.to_q()
                invquat = q.to_q().conjugated()
                #print quat
                #print v
                ###########
                q = quat*v

                q.z = q.z-1
                #print q
                self.calibrated_list[i] = q
                self.calibrated_x[i] = q.x
                self.calibrated_y[i] = q.y
                self.calibrated_z[i] = q.z

                q = invquat * q

                self.linearAccel_x[i] = q.x
                self.linearAccel_y[i] = q.y
                self.linearAccel_z[i] = q.z



        #plt.plot(self.calibrated_x)
        #plt.show()
        #plt.plot(self.calibrated_y)
        #plt.show()
        #plt.plot(self.calibrated_z)
        #plt.show()

    def UpdateSQL(self):
        conn = pymysql.connect(host='onefit2.cafe24.com',port=3306,user='ziql',passwd='zikto430',db='ProjectP')
        cur  = conn.cursor()

        accelx = ','.join(str(e) for e in self.x_list)
        accely = ','.join(str(e) for e in self.y_list)
        accelz = ','.join(str(e) for e in self.z_list)

        linAccelX = ','.join(str(e) for e in self.calibrated_x) 
        linAccelY = ','.join(str(e) for e in self.calibrated_y) 
        linAccelZ = ','.join(str(e) for e in self.calibrated_z)

        print self.quat_list

        quat1 = ','.join(str(e.q0) for e in self.quat_list if e is not None)
        quat2 = ','.join(str(e.q1) for e in self.quat_list if e is not None)
        quat3 = ','.join(str(e.q2) for e in self.quat_list if e is not None)
        quat4 = ','.join(str(e.q3) for e in self.quat_list if e is not None)

        breaker = "\",\""

        activity = "eat"
        meta ="simulation"
        
        command1 = "INSERT INTO Quo( AccelX, AccelY, AccelZ, CalibX, CalibY, CalibZ, Quat1, Quat2, Quat3, Quat4, Activity, Meta) VALUES"
        command2 = " (\""+accelx+breaker+accely+breaker+accelz + breaker + linAccelX + breaker+linAccelY + breaker + linAccelZ + breaker + quat1 + breaker + quat2+ breaker + quat3+breaker+quat4+breaker+activity+breaker+meta+"\")"

        command = command1+ command2

        cur.execute(command)
        conn.commit()

        print (cur.description)
        print "done"

if __name__ =="__main__":
    mpu = mpu9150interface()
    if (len(sys.argv) == 2):
        if sys.argv[1] == "setup":
            mpu.connect()
            mpu.write()
            mpu.s.close()
        else:
            mpu.s = serial.Serial(sys.argv[1],115200, timeout =1)
            print mpu.s
            if(mpu.s.isOpen()):
                print "connected..."
            #mpu.s = serial.Serial("/dev/cu.usbmodemfa141",115200, timeout =1)        
            #mpu.read()
            #raw_input("press enter to zeroing...")
            #mpu.zeroing()
            raw_input("press enter to start...")
            f,axarr = plt.subplots(3,3)
            #mpu.send("invz")
            mpu.read()
            mpu.s.close()
            #mpu.UpdateSQL()
            axarr[0,0].plot(mpu.calibrated_x)
            axarr[0,0].set_ylim( [-2,2])
            axarr[0,1].plot(mpu.calibrated_y)
            axarr[0,1].set_ylim([-2,2])
            axarr[0,2].plot(mpu.calibrated_z)
            axarr[0,2].set_ylim([-2,2])
            #plt.show()
            #raw_input("press enter to start...")
            #mpu.read()
            #axarr[1,0].plot(mpu.gyrox_list)
            #axarr[1,1].plot(mpu.gyroy_list)
            #axarr[1,2].plot(mpu.gyroz_list)

            axarr[1,0].plot(mpu.x_list)
            axarr[1,0].set_ylim( [-2,2])
            axarr[1,1].plot(mpu.y_list)
            axarr[1,1].set_ylim( [-2,2])
            axarr[1,2].plot(mpu.z_list)
            axarr[1,2].set_ylim( [-2,2])

            axarr[2,0].plot(mpu.linearAccel_x)
            axarr[2,0].set_ylim( [-2,2])
            axarr[2,1].plot(mpu.linearAccel_y)
            axarr[2,1].set_ylim( [-2,2])
            axarr[2,2].plot(mpu.linearAccel_z)
            axarr[2,2].set_ylim( [-2,2])

            plt.show()
            #mpu.s.close()
