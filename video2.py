#!/usr/bin/env python

import datetime
import select
import socket
import sys
import threading
import time

import libardrone
import video

class ARDroneVideoThread(threading.Thread):

    def __init__(self, drone):
        threading.Thread.__init__(self)
        self.drone = drone


    def run(self):
        #print 'preparing video server...'
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(0)
        sock.bind(('', 5555))
        self.stopping = False

        #print 'sending video wakeup'
        sock.sendto("\x01\x00\x00\x00", ('192.168.1.1', 5555))

        print 'preparing navdata server...'
        sock_nav = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_nav.setblocking(0)
        sock_nav.bind(('', 5554))

        print 'sending navdata wakeup'
        sock_nav.sendto("\x01\x00\x00\x00", ('192.168.1.1', 5554))
        #libardrone.navdata_demo()
        self.drone.at(libardrone.at_config, "general:navdata_demo", "TRUE")
        time.sleep(0.04)
        libardrone.at("AT_CTRL", 0)

        print 'waiting for incoming data'
        while not self.stopping:
            inputready, outputready, exceptready = select.select([sock, sock_nav, sys.stdin], [], [])
            for i in inputready:
                if i == sock:
                    print 'reading video socket...',
                    t = datetime.datetime.now()
                    j = 0
                    while 1:
                        j += 1
                        try:
                            data, address = sock.recvfrom(65535)    # max udp packet size
                        except:
                            print "dropped", j-1, "frames"
                            break
                    br = video.BitReader(data)
                    width, height, image, t_decode = video.read_picture(br)
                    video.show_image(image, width, height)
                    t2 = datetime.datetime.now()
                    print 'ok.', (t2 - t).microseconds / 1000000., 'sec', t_decode
                elif i == sock_nav:
                    print 'reading navdata socket...',
                    j = 0
                    while 1:
                        j += 1
                        try:
                            data, address = sock_nav.recvfrom(65535)    # max udp packet size
                        except:
                            print "dropped", j-1, "frames"
                            break
                    navdata = libardrone.decode_navdata(data)
                    print navdata[0]
                elif i == sys.stdin:
                    sys.stdin.readline()
                    print "stopping the loop"
                    self.stopping = True
        print 'left receiving loop'
        sock.close()
        sock_nav.close()
        self.drone.halt()

    def stop(self):
        print "signaling thread to stop"
        self.stopping = True

def main():
    drone = libardrone.ARDrone()
    vthread = ARDroneVideoThread(drone)
    # FIXME: kill meeeeeeeeeee!
    vthread.drone = drone
    vthread.start()
    drone.halt()
    vthread.join()

if __name__ == '__main__':
    main()

