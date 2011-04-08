#!/usr/bin/env python


import threading
import socket
import time

import libardrone
import video

class ARDroneVideoThread(threading.Thread):

    def run(self):
        print 'preparing server...'
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        sock.bind(('', 5555))
        self.stopping = False
        # will the drone send one frame per udp package?

        print 'sending wakeup'
        sock.sendto("\x01\x00\x00\x00", ('192.168.1.1', 5555))

        print 'waiting for incoming data'
        while not self.stopping:
            print 'reading socket...',
            data, address = sock.recvfrom(65535)    # max udp packet size

            br = video.BitReader(data)
            video.read_picture(br)
            print 'ok.'
            # do something with the data
            print time.time(), len(data)
        print 'left receiving loop'
        socket.close()

    def stop(self):
        print "signaling thread to stop"
        self.stopping = True

def main():
    vthread = ARDroneVideoThread()
    vthread.start()
    time.sleep(60)
    vthread.stop()


if __name__ == '__main__':
    main()

