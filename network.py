import select
import socket
import threading

import libardrone


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

