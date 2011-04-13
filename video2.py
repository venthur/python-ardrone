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

    def run(self):
        print 'preparing server...'
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(0)
        sock.bind(('', 5555))
        self.stopping = False
        # will the drone send one frame per udp package?

        print 'sending wakeup'
        sock.sendto("\x01\x00\x00\x00", ('192.168.1.1', 5555))

        print 'waiting for incoming data'
        j = 0
        while not self.stopping:
            j += 1
            inputready, outputready, exceptready = select.select([sock, sys.stdin], [], [])
            for i in inputready:
                if i == sock:
                    print 'reading socket...',
                    t = datetime.datetime.now()
                    while 1:
                        try:
                            j += 1
                            data, address = sock.recvfrom(65535)    # max udp packet size
                        except:
                            print "dropped", j-1, "frames"
                            j = 0
                            break
                    br = video.BitReader(data)
                    t_decode = video.read_picture(br)
                    t2 = datetime.datetime.now()
                    print 'ok.', (t2 - t).microseconds / 1000000., 'sec', t_decode
                elif i == sys.stdin:
                    sys.stdin.readline()
                    print "stopping the loop"
                    self.stopping = True
        print 'left receiving loop'
        sock.close()

    def stop(self):
        print "signaling thread to stop"
        self.stopping = True

def main():
    vthread = ARDroneVideoThread()
    vthread.start()
    #time.sleep(60)
    #vthread.stop()
    vthread.join()

if __name__ == '__main__':
    main()

