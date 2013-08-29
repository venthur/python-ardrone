# Copyright (c) 2011 Bastian Venthur
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


"""
This module provides access to the data provided by the AR.Drone.
"""

import select
import socket
import threading
import multiprocessing
import Image
import numpy as np
import StringIO

import libardrone
import time

class ARDroneNetworkProcess(multiprocessing.Process):
    """ARDrone Network Process.

    This process collects data from the video and navdata port, converts the
    data and sends it to the IPCThread.
    """

    def __init__(self, nav_pipe, video_pipe, com_pipe, is_ar_drone_2):
        multiprocessing.Process.__init__(self)
        self.nav_pipe = nav_pipe
        self.video_pipe = video_pipe
        self.com_pipe = com_pipe
        self.is_ar_drone_2 = is_ar_drone_2
        if is_ar_drone_2:
            import ar2video
            self.ar2video = ar2video.ARVideo2(self.video_pipe)
        else:
            import arvideo

    def run(self):
        if self.is_ar_drone_2:
            video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            video_socket.connect(('192.168.1.1', libardrone.ARDRONE_VIDEO_PORT))
            video_socket.setblocking(0)
        else:
            video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            video_socket.setblocking(0)
            video_socket.bind(('', libardrone.ARDRONE_VIDEO_PORT))
            video_socket.sendto("\x01\x00\x00\x00", ('192.168.1.1', libardrone.ARDRONE_VIDEO_PORT))

        nav_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        nav_socket.setblocking(0)
        nav_socket.bind(('', libardrone.ARDRONE_NAVDATA_PORT))
        nav_socket.sendto("\x01\x00\x00\x00", ('192.168.1.1', libardrone.ARDRONE_NAVDATA_PORT))

        control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        control_socket.connect(('192.168.1.1', libardrone.ARDRONE_CONTROL_PORT))
        print "Connected to control port"
        control_socket.setblocking(0)

        stopping = False
        #loop receiving data and calculate bit rate
        import time
        start = time.time()
        bitrate = 0.0
        data_bits = 0.0
        while not stopping:
            #time.sleep(.0001)
            #print "Waiting for network intput at time ", time.time()
            inputready, outputready, exceptready = select.select([nav_socket, video_socket, self.com_pipe, control_socket], [], [])
            for i in inputready:
                if i == video_socket:
                    while 1:
                        try:
                            data = video_socket.recv(4096)
                            data_bits += len(data) * 8.0
                            timediff = time.time() - start
                            if self.is_ar_drone_2:
                                self.ar2video.write(data)
                            if timediff > 0.0:
                                bitrate = (data_bits / timediff) / 1000000
                                print bitrate
                        except IOError:
                            # we consumed every packet from the socket and
                            # continue with the last one
                            break
                        # Sending is taken care of by the decoder
                    if not self.is_ar_drone_2:
                        w, h, image, t = arvideo.read_picture(data)
                        self.video_pipe.send(image)
                elif i == nav_socket:
                    #print "Navigation socket"
                    while 1:
                        try:
                            data = nav_socket.recv(4096)
                        except IOError:
                            # we consumed every packet from the socket and
                            # continue with the last one
                            break
                    navdata = libardrone.decode_navdata(data)
                    self.nav_pipe.send(navdata)
                elif i == self.com_pipe:
                    _ = self.com_pipe.recv()
                    stopping = True
                    break
                elif i == control_socket:

                    print "Control socket: "
                    while 1:

                        try:
                            data = control_socket.recv(4096)
                            print "Control Socket says ", data
                        except IOError:
                            break
        video_socket.close()
        nav_socket.close()


class IPCThread(threading.Thread):
    """
    Inter Process Communication Thread.
    This thread collects the data from the ARDroneNetworkProcess and forwards it to the ARDrone.
    """

    def __init__(self, drone):
        threading.Thread.__init__(self)
        self.drone = drone
        self.stopping = False

    def run(self):
        while not self.stopping:
            #time.sleep(.0001)
            inputready, outputready, exceptready = select.select([self.drone.video_pipe, self.drone.nav_pipe], [], [], 1)
            for i in inputready:
                if i == self.drone.video_pipe:
                    while self.drone.video_pipe.poll():
                        image = self.drone.video_pipe.recv()
                    _image = Image.open(StringIO.StringIO(image))
                    self.drone.image = np.asarray(_image)
                elif i == self.drone.nav_pipe:
                    while self.drone.nav_pipe.poll():
                        navdata = self.drone.nav_pipe.recv()
                    self.drone.navdata = navdata

    def stop(self):
        """Stop the IPCThread activity."""
        self.stopping = True
