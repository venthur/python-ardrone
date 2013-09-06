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
import logging


"""
This module provides access to the data provided by the AR.Drone.
"""

import select
import socket
import threading
import multiprocessing
import Image
import StringIO
import libardrone

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
            self.ar2video = ar2video.ARVideo2(self.video_pipe, libardrone.DEBUG, libardrone.IMAGE_ENCODING)
        else:
            import arvideo

    def run(self):

        def _connect():
            logging.warn('Connection to ardrone')
            if self.is_ar_drone_2:
                video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                video_socket.connect(('192.168.1.1', libardrone.ARDRONE_VIDEO_PORT))
                video_socket.setblocking(0)
            else:
                video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                video_socket.setblocking(0)
                video_socket.bind(('', libardrone.ARDRONE_VIDEO_PORT))
                video_socket.sendto("\x01\x00\x00\x00", ('192.168.1.1', libardrone.ARDRONE_VIDEO_PORT))

            nav_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            nav_socket.setblocking(0)
            nav_socket.bind(('', libardrone.ARDRONE_NAVDATA_PORT))
            nav_socket.sendto("\x01\x00\x00\x00", ('192.168.1.1', libardrone.ARDRONE_NAVDATA_PORT))

            control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            control_socket.connect(('192.168.1.1', libardrone.ARDRONE_CONTROL_PORT))
            control_socket.setblocking(0)
            logging.warn('Connection established')
            return video_socket, nav_socket, control_socket

        def _disconnect(video_socket, nav_socket, control_socket):
            logging.warn('Disconnection to ardrone streams')
            video_socket.close()
            nav_socket.close()
            control_socket.close()

        video_socket, nav_socket, control_socket = _connect()

        stopping = False
        #loop receiving data and calculate bit rate
        import time
        start = time.time()
        bitrate = 0.0
        data_bits = 0.0
        connection_lost = 1
        reconnection_needed = False
        while not stopping:
            if reconnection_needed:
                _disconnect(video_socket, nav_socket, control_socket)
                video_socket, nav_socket, control_socket = _connect()
                reconnection_needed = False
            inputready, outputready, exceptready = select.select([nav_socket, video_socket, self.com_pipe, control_socket], [], [], 1.)
            if len(inputready) == 0:
                connection_lost += 1
                reconnection_needed = True
            for i in inputready:
                if i == video_socket:
                    while 1:
                        try:
                            data = video_socket.recv(65536)
                            data_bits += len(data) * 8.0
                            timediff = time.time() - start
                            if self.is_ar_drone_2:
                                self.ar2video.write(data)
                            if timediff > 0.0:
                                bitrate = (data_bits / timediff) / 1000000
                        except IOError:
                            # we consumed every packet from the socket and
                            # continue with the last one
                            break
                        # Sending is taken care of by the decoder
                    if not self.is_ar_drone_2:
                        w, h, image, t = arvideo.read_picture(data)
                        self.video_pipe.send(image)
                elif i == nav_socket:
                    while 1:
                        try:
                            data = nav_socket.recv(500)
                        except IOError:
                            # we consumed every packet from the socket and
                            # continue with the last one
                            break
                    navdata, has_information = libardrone.decode_navdata(data)
                    if (has_information):
                        self.nav_pipe.send(navdata)
                elif i == self.com_pipe:
                    _ = self.com_pipe.recv()
                    stopping = True
                    break
                elif i == control_socket:
                    reconnection_needed = False
                    while not reconnection_needed:
                        try:
                            data = control_socket.recv(65536)
                            if len(data) == 0:
                                logging.warning('Received an empty packet on control socket')
                                reconnection_needed = True
                            else:
                                logging.warning("Control Socket says : %s", data)

                        except IOError:
                            break
        _disconnect(video_socket, nav_socket, control_socket)

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
            inputready, outputready, exceptready = select.select([self.drone.video_pipe, self.drone.nav_pipe], [], [], 1)
            for i in inputready:
                if i == self.drone.video_pipe:
                    while self.drone.video_pipe.poll():
                        image = self.drone.video_pipe.recv()
                    try:
                        _image = Image.open(StringIO.StringIO(image))
                        self.drone.set_image(_image)
                    except:
                        logging.error("There has been a problem with an image")

                elif i == self.drone.nav_pipe:
                    while self.drone.nav_pipe.poll():
                        _navdata = self.drone.nav_pipe.recv()
                    self.drone.set_navdata(_navdata)

    def stop(self):
        """Stop the IPCThread activity."""
        self.stopping = True
