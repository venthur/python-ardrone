import select
import socket
import threading
import multiprocessing

import libardrone
import arvideo


class ARDroneNetworkThread(threading.Thread):

    def __init__(self, drone):
        threading.Thread.__init__(self)
        self.drone = drone
        self.stopping = False

    def run(self):
        video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        video_socket.setblocking(0)
        video_socket.bind(('', libardrone.ARDRONE_VIDEO_PORT))
        video_socket.sendto("\x01\x00\x00\x00", ('192.168.1.1', libardrone.ARDRONE_VIDEO_PORT))

        nav_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        nav_socket.setblocking(0)
        nav_socket.bind(('', libardrone.ARDRONE_NAVDATA_PORT))
        nav_socket.sendto("\x01\x00\x00\x00", ('192.168.1.1', libardrone.ARDRONE_NAVDATA_PORT))
 
        while not self.stopping:
            # TODO: check if we should use a timeout here like below
            inputready, outputready, exceptready = select.select([nav_socket, video_socket], [], [])
            for i in inputready:
                if i == video_socket:
                    while 1:
                        try:
                            data, address = video_socket.recvfrom(65535)
                        except:
                            break
                        self.drone.new_video_packet(data)
                elif i == nav_socket:
                    while 1:
                        try:
                            data, address = nav_socket.recvfrom(65535)
                        except:
                            break
                        self.drone.new_navdata_packet(data)
        video_socket.close()
        nav_socket.close()

    def stop(self):
        self.stopping = True


class ARDroneNetworkProcess(multiprocessing.Process):

    def __init__(self, nav_pipe, video_pipe):
        multiprocessing.Process.__init__(self)
        self.nav_pipe = nav_pipe
        self.video_pipe = video_pipe
        self.stopping = False

    def run(self):
        video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        video_socket.setblocking(0)
        video_socket.bind(('', libardrone.ARDRONE_VIDEO_PORT))
        video_socket.sendto("\x01\x00\x00\x00", ('192.168.1.1', libardrone.ARDRONE_VIDEO_PORT))

        nav_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        nav_socket.setblocking(0)
        nav_socket.bind(('', libardrone.ARDRONE_NAVDATA_PORT))
        nav_socket.sendto("\x01\x00\x00\x00", ('192.168.1.1', libardrone.ARDRONE_NAVDATA_PORT))

        while not self.stopping:
            inputready, outputready, exceptready = select.select([nav_socket, video_socket], [], [])
            for i in inputready:
                if i == video_socket:
                    while 1:
                        try:
                            data, address = video_socket.recvfrom(65535)
                        except:
                            break
                        br = video.BitReader(data)
                        w, h, image, t = arvideo.read_picture(br)
                        try:
                            self.video_pipe.send(image)
                        except e:
                            print "error while sending in video pipe."
                            print e
                elif i == nav_socket:
                    while 1:
                        try:
                            data, address = nav_socket.recvfrom(65535)
                        except:
                            break
                        navdata = libardrone.decode_navdata(data)
                        self.nav_pipe.send(navdata)
        video_socket.close()
        nav_socket.close()

    def stop(self):
        self.stopping = True


class IPCThread(threading.Thread):

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
                    self.drone.image = image
                elif i == self.drone.nav_pipe:
                    while self.drone.nav_pipe.poll():
                        _ = self.drone.nav_pipe.recv()

    def stop(self):
        self.stopping = True

