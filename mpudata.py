#!/usr/bin/python
# =============== PACKETS ================= 
# For 16-bit signed integers.
from euclid import Quaternion, Vector3


def two_bytes(d1,d2):
    d = ord(d1)*256 + ord(d2)
    if d > 32767:
        d -= 65536

    return d

# For 32-bit signed integers.

def four_bytes(d1, d2, d3, d4):
    d = ord(d1)*(1<<24) + ord(d2)*(1<<16) + ord(d3)*(1<<8) + ord(d4)
    
    if d > 2147483648:

        d-= 4294967296

    return d

class debug_packet (object):

    # body of packet is a debug string

    def __init__(self,l):

        sss = []

        for c in l[3:21]:

            if ord(c) != 0:

                sss.append(c)

        self.s = "".join(sss)



    def display(self):
        print "debug : " + self.s
        #sys.stdout.write(self.s)
        #f_file.write(self.s + '\n')


class data_packet (object):

    def __init__(self, l):
        self.data = [0,0,0,0,0,0,0,0,0]
        self.type = ord(l[2])
        if self.type == 0:   # accel
            self.data[0] = four_bytes(l[3],l[4],l[5],l[6]) * 1.0 / (1<<16)
            self.data[1] = four_bytes(l[7],l[8],l[9],l[10]) * 1.0 / (1<<16)
            self.data[2] = four_bytes(l[11],l[12],l[13],l[14]) * 1.0 / (1<<16)

        elif self.type == 1:   # gyro
            self.data[0] = four_bytes(l[3],l[4],l[5],l[6]) * 1.0 / (1<<16)
            self.data[1] = four_bytes(l[7],l[8],l[9],l[10]) * 1.0 / (1<<16)
            self.data[2] = four_bytes(l[11],l[12],l[13],l[14]) * 1.0 / (1<<16)
          
        elif self.type == 2:   # compass/
            self.data[0] = four_bytes(l[3],l[4],l[5],l[6]) * 1.0 / (1<<16)
            self.data[1] = four_bytes(l[7],l[8],l[9],l[10]) * 1.0 / (1<<16)
            self.data[2] = four_bytes(l[11],l[12],l[13],l[14]) * 1.0 / (1<<16)
         

        elif self.type == 3:   # quat
            self.data[0] = four_bytes(l[3],l[4],l[5],l[6]) * 1.0 / (1<<30)
            self.data[1] = four_bytes(l[7],l[8],l[9],l[10]) * 1.0 / (1<<30)
            self.data[2] = four_bytes(l[11],l[12],l[13],l[14]) * 1.0 / (1<<30)
            self.data[3] = four_bytes(l[15],l[16],l[17],l[18]) * 1.0 / (1<<30)

        elif self.type == 4:   # euler
            self.data[0] = four_bytes(l[3],l[4],l[5],l[6]) * 1.0 / (1<<16)

            self.data[1] = four_bytes(l[7],l[8],l[9],l[10]) * 1.0 / (1<<16)

            self.data[2] = four_bytes(l[11],l[12],l[13],l[14]) * 1.0 / (1<<16)
            

        elif self.type == 5:   # rot

            self.data[0] = two_bytes(l[3],l[4]) * 1.0 / (1<<14)

            self.data[1] = two_bytes(l[5],l[6]) * 1.0 / (1<<14)

            self.data[2] = two_bytes(l[7],l[8]) * 1.0 / (1<<14)

            self.data[3] = two_bytes(l[9],l[10]) * 1.0 / (1<<14)

            self.data[4] = two_bytes(l[11],l[12]) * 1.0 / (1<<14)

            self.data[5] = two_bytes(l[13],l[14]) * 1.0 / (1<<14)

            self.data[6] = two_bytes(l[15],l[16]) * 1.0 / (1<<14)

            self.data[7] = two_bytes(l[17],l[18]) * 1.0 / (1<<14)

            self.data[8] = two_bytes(l[19],l[20]) * 1.0 / (1<<14)
            

        elif self.type == 6:   # heading

            self.data[0] = four_bytes(l[3],l[4],l[5],l[6]) * 1.0 / (1<<16)
            
        else:   # unsupported
            pass

    def display(self):
        if self.type == 0:
			sss = 'accel: %7.3f %7.3f %7.3f' % \
                (self.data[0], self.data[1], self.data[2])
			print sss
			#f_file.write(sss + '\n')

        elif self.type == 1:
			sss = 'gyro: %9.5f %9.5f %9.5f' % \
                (self.data[0], self.data[1], self.data[2])
			print sss
			#f_file.write(sss + '\n')
        elif self.type == 2:
			sss = 'compass: %7.4f %7.4f %7.4f' % \
                (self.data[0], self.data[1], self.data[2])

			print sss
			#f_file.write('sss'+ '\n')

        elif self.type == 3:
			sss = 'quat: %7.4f %7.4f %7.4f %7.4f' % \
                (self.data[0], self.data[1], self.data[2], self.data[3])

			print sss
			#f_file.write(sss + '\n')

        elif self.type == 4:
			sss = 'euler: %7.4f %7.4f %7.4f' % \
                (self.data[0], self.data[1], self.data[2])

			print sss
			#f_file.write(sss + '\n')

        elif self.type == 5:
			sss = 'rotation matrix: \n%7.3f %7.3f %7.3f\n%7.3f %7.3f %7.3f\n%7.3f %7.3f %7.3f' % \
                (self.data[0], self.data[1], self.data[2], self.data[3], \
                 self.data[4], self.data[5], self.data[6], self.data[7], \
                 self.data[8])

			print sss
			f_file.write( sss + '\n')

        elif self.type == 6:
			sss = 'heading: %7.4f' % self.data[0]
			print sss 
			#f_file.write(sss + '\n')
        else:
			print 'what?'
			#f_file.write('what' + '\n')


class quat_packet (object):

    def __init__(self, l):
        self.l = l

        self.q0 = four_bytes(l[3],l[4],l[5],l[6]) * 1.0 / (1<<30)

        self.q1 = four_bytes(l[7],l[8],l[9],l[10]) * 1.0 / (1<<30)

        self.q2 = four_bytes(l[11],l[12],l[13],l[14]) * 1.0 / (1<<30)

        self.q3 = four_bytes(l[15],l[16],l[17],l[18]) * 1.0 / (1<<30)
        #f_file.write("quaternion: " + " ".join([str(s).ljust(15) for s in[ self.q0, self.q1, self.q2, self.q3 ]])+ '\n')

    def display_raw(self):

		l = self.l
		sss = "".join(
			[ str(ord(l[0])), " "] + \

			[ str(ord(l[1])), " "] + \

			[ str(ord(a)).ljust(4) for a in 

								[ l[2], l[3], l[4], l[5], l[6], l[7], l[8], l[9], l[10] ] ] + \

			[ str(ord(a)).ljust(4) for a in 

								[ l[8], l[9], l[10] , l[11], l[12], l[13]] ]

            )
		print sss
		#f_file.write(sss + '\n');


    def display(self):

        if 1:
			sss = "qs " + " ".join([str(s).ljust(15) for s in

					[ self.q0, self.q1, self.q2, self.q3 ]])

			print sss
			#f_file.write(sss + '\n');

        if 0:

            euler0, euler1, euler2 = self.to_q().get_euler()
            sss = "eulers " + " ".join([str(s).ljust(15) for s in

                [ euler0, euler1, euler2 ]])

            print sss
            #f_file.write(sss + '\n')
			
        if 0:

            euler0, euler1, euler2 = self.to_q().get_euler()
            sss = "eulers " + " ".join([str(s).ljust(15) for s in

                [ (euler0 * 180.0 / 3.14159) - 90 ]])
            print sss
            #f_file.write(sss + '\n');

    def to_q(self):
        return Quaternion(self.q0, self.q1, self.q2, self.q3)
