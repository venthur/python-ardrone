import select
import socket
import struct
import time

DRONE_IP = "192.168.1.1"
ARDRONE_NAVDATA_PORT = 5554
ARDRONE_COMMAND_PORT = 5556

def at(command, seq, params):
    """
    Parameters:
    command -- the command
    seq -- the sequence number
    params -- a list of elements which can be either int, float or string
    """
    param_str = ''
    for p in params:
        if type(p) == int:
            param_str += ",%d" % p
        elif type(p) == float:
            param_str += ",%d" % f2i(p)
        elif type(p) == str:
            param_str += ',"' + p + '"'
    msg = "AT*%s=%i%s\r" % (command, seq, param_str)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg, ("192.168.1.1", ARDRONE_COMMAND_PORT))

def f2i(f):
    """Interpret IEEE-754 floating-point value as signed integer.
    Arguments:
    f -- floating point value
    """
    return struct.unpack('i', struct.pack('f', f))[0]


if __name__ == '__main__':
    nav_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    nav_socket.connect((DRONE_IP, ARDRONE_NAVDATA_PORT))
    nav_socket.setblocking(0)
    nav_socket.send("\x01\x00\x00\x00")

    seq = 1
    stopping = False
    while not stopping:
        inputready, outputready, exceptready = select.select([nav_socket], [], [], 20)
        seq += 1
        at("COMWDG", seq, [])
        if len(inputready) == 0:
            stopping = True
        for i in inputready:
            while 1:
                try:
                    data = nav_socket.recv(500)
                except IOError:
                    break

    raise Exception("Should not get here")
