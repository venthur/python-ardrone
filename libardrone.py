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
Docstring goes here.
"""


import socket
import struct
import sys
import threading
import time


__author__ = "Bastian Venthur"


class ARDrone(object):

    def __init__(self):
        self.seq_nr = 1
        # worked with 0.1 see if it works w/ 0.2 (should work with < 0.25)
        self.timer_t = 0.2
        self.com_watchdog_timer = threading.Timer(self.timer_t, self.commwdg)
        self.lock = threading.Lock()
        self.speed = 0.5

    def takeoff(self):
        self.at(at_ftrim)
        self.at(at_ref, True)

    def land(self):
        self.at(at_ref, False)

    def hover(self):
        self.at(at_pcmd, False, 0, 0, 0, 0)

    def move_left(self):
        self.at(at_pcmd, True, -self.speed, 0, 0, 0)

    def move_right(self):
        self.at(at_pcmd, True, self.speed, 0, 0, 0)

    def move_up(self):
        self.at(at_pcmd, True, 0, 0, self.speed, 0)

    def move_down(self):
        self.at(at_pcmd, True, 0, 0, -self.speed, 0)

    def move_forward(self):
        self.at(at_pcmd, True, 0, -self.speed, 0, 0)

    def move_backward(self):
        self.at(at_pcmd, True, 0, self.speed, 0, 0)

    def turn_left(self):
        self.at(at_pcmd, True, 0, 0, 0, -self.speed)

    def turn_right(self):
        self.at(at_pcmd, True, 0, 0, 0, self.speed)

    def reset(self):
        self.at(at_ref, False, True)
        self.at(at_ref, False, False)

    def trim(self):
        self.at(at_ftrim)

    def set_speed(self, speed):
        self.speed = speed

    def at(self, cmd, *args, **kwargs):
        """Wrapper for the low level at commands.

        This method takes care that the sequence number is increased after each
        at command and the watchdog timer is started to make sure the drone
        receives a command at least every second.
        """
        self.lock.acquire()
        self.com_watchdog_timer.cancel()
        cmd(self.seq_nr, *args, **kwargs)
        self.seq_nr += 1
        self.com_watchdog_timer = threading.Timer(self.timer_t, self.commwdg)
        self.com_watchdog_timer.start()
        self.lock.release()

    def commwdg(self):
        self.at(at_comwdg)

###############################################################################
### Preliminary high level commands
###############################################################################

def trim():
    at_ftrim(1)

def takeoff():
#    at_comwdg(1)
#    time.sleep(0.05)
    at_ftrim(1)
    time.sleep(0.1)
    at_config(1, "control:altitude_max", "500")
    time.sleep(0.1)
    at_ref(1, True)

def land():
    at_pcmd(1, True, 0, 0, -0.1, 0)
    time.sleep(2)
    at_ref(1, False)

def hover():
    at_pcmd(1, False, 0, 0, 0, 0)

def turn_left():
    at_pcmd(1, True, 0, 0, 0, -0.5)

def turn_right():
    at_pcmd(1, True, 0, 0, 0, 0.5)

def navdata_demo():
    at_config(1, "general:navdata_demo", "TRUE")

def XXX():
    """Emergency halt -- will stop the engines no matter what!"""
    at_ref(1, False, False)
    at_ref(1, False, True)
    at_ref(1, False, False)

def start_video_stream():
    """Start enable the video stream."""
    # send something to the drones video port to trigger sending video data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto("\x01\x00\x00\x00", ('192.168.1.1', 5555))
    sock.close()

###############################################################################
### Low level AT Commands
###############################################################################

def at_ref(seq, takeoff, emergency=False):
    """
    Basic behaviour of the drone: take-off/landing, emergency stop/reset)

    Parameters:
    seq -- sequence number
    takeoff -- True: Takeoff / False: Land
    emergency -- True: Turn of the engines
    """
    p = 0b10001010101000000000000000000
    if takeoff:
        p += 0b1000000000
    if emergency:
        p += 0b0100000000
    at("REF", seq, [p])

def at_pcmd(seq, progressive, lr, fb, vv, va):
    """
    Makes the drone move (translate/rotate).

    Parameters:
    seq -- sequence number
    progressive -- True: enable progressive commands, False: disable (i.e.
        enable hovering mode)
    lr -- left-right tilt: float [-1..1] negative: left, positive: right
    rb -- front-back tilt: float [-1..1] negative: forwards, positive:
        backwards
    vv -- vertical speed: float [-1..1] negative: go down, positive: rise
    va -- angular speed: float [-1..1] negative: spin left, positive: spin 
        right

    The above float values are a percentage of the maximum speed.
    """
    p = 1 if progressive else 0
    at("PCMD", seq, [p, float(lr), float(fb), float(vv), float(va)])

def at_ftrim(seq):
    """
    Tell the drone it's lying horizontally.

    Parameters:
    seq -- sequence number
    """
    at("FTRIM", seq)

def at_zap(seq, stream):
    """
    Selects which video stream to send on the video UDP port.

    Parameters:
    seq -- sequence number
    stream -- Integer: video stream to broadcast
    """
    # FIXME: improve parameters to select the modes directly
    at("ZAP", seq, [stream])

def at_config(seq, option, value):
    at("CONFIG", seq, [str(option), str(value)])

def at_comwdg(seq):
    """
    Reset communication watchdog.
    """
    # FIXME: no sequence number
    at("COMWDG", seq)

def at_aflight(seq, flag):
    """
    Makes the drone fly autonomously.

    Parameters:
    seq -- sequence number
    flag -- Integer: 1: start flight, 0: stop flight
    """
    at("AFLIGHT", seq, [flag])

def at_pwm(seq, m1, m2, m3, m4):
    """
    Sends control values directly to the engines, overriding control loops.

    Parameters:
    seq -- sequence number
    m1 -- front left command
    m2 -- fright right command
    m3 -- back right command
    m4 -- back left command
    """
    # FIXME: what type do mx have?
    pass

def at_led(seq, anim, f, d):
    """
    Control the drones LED.

    Parameters:
    seq -- sequence number
    anim -- Integer: animation to play
    f -- ?: frequence in HZ of the animation
    d -- Integer: total duration in seconds of the animation
    """
    pass

def at_anim(seq, anim, d):
    """
    Makes the drone execute a predefined movement (animation).

    Parameters:
    seq -- sequcence number
    anim -- Integer: animation to play
    d -- Integer: total duration in sections of the animation
    """
    at("ANIM", seq, [anim, d])

def at(command, seq, params=[]):
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
            param_str += ',"'+p+'"'
    msg = "AT*%s=%i%s\r" % (command, seq, param_str)
    print msg
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg, ("192.168.1.1", 5556))

def f2i(f):
    """Interpret IEEE-754 floating-point value as signed integer.

    Arguments:
    f -- floating point value
    """
    return struct.unpack('i', struct.pack('f', f))[0]

###############################################################################
### navdata
###############################################################################

def decode_packet(packet):
    """Decode a navdata packet."""
    offset = 0
    header, drone_state, seq_nr, vision_flag =  struct.unpack_from("IIII", packet, offset)
    #print "HEADER:"
    #print header, drone_state, seq_nr, vision_flag
    offset += struct.calcsize("IIII")
    option = 1
    while 1:
        try:
            id, size =  struct.unpack_from("HH", packet, offset)
            offset += struct.calcsize("HH")
        except:
            break
        data = []
        for i in range(size-struct.calcsize("HH")):
            data.append(struct.unpack_from("c", packet, offset)[0])
            offset += struct.calcsize("c")
        #print "OPTION %i:" % option
        option += 1
        #print id, size, "".join(data)
        # navdata_tag_t in navdata-common.h
        if id == 0:
            data2 = struct.unpack_from("IIfffIfffI", "".join(data))
            print "Control State: %s Battery: %s\nTheta (pitch): %s Phi (roll): %s Psi (yaw): %s\nAltitude: %s vx: %s vy: %s vz: %s Frame index: %s" % tuple([str(i) for i in data2])
#      ctrl_state;             /*!< Flying state (landed, flying, hovering, etc.) defined in CTRL_STATES enum. */
#      vbat_flying_percentage; /*!< battery voltage filtered (mV) */
#
#      theta;                  /*!< UAV's pitch in milli-degrees */
#      phi;                    /*!< UAV's roll  in milli-degrees */
#      psi;                    /*!< UAV's yaw   in milli-degrees */
#
#      altitude;               /*!< UAV's altitude in centimeters */
#
#      vx;                     /*!< UAV's estimated linear velocity */
#      vy;                     /*!< UAV's estimated linear velocity */
#      vz;                     /*!< UAV's estimated linear velocity */
#
#      num_frames;			  /*!< streamed frame index */ // Not used -> To integrate in video stage.


if __name__ == "__main__":

    import termios
    import fcntl
    import sys
    import os
    
    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    drone = ARDrone()

    try:
        while 1:
            try:
                c = sys.stdin.read(1)
                c = c.lower()
                print "Got character", `c`
                if c == 'a':
                    drone.move_left()
                if c == 'd':
                    drone.move_right()
                if c == 'w':
                    drone.move_forward()
                if c == 's':
                    drone.move_backward()
                if c == ' ':
                    drone.land()
                if c == '\n':
                    drone.takeoff()
                if c == 'q':
                    drone.turn_left()
                if c == 'e':
                    drone.turn_right()
                if c == '1':
                    drone.move_up()
                if c == '2':
                    drone.hover()
                if c == '3':
                    drone.move_down()
                if c == 't':
                    drone.reset()
                if c == 'x':
                    drone.hover()
                if c == 'y':
                    drone.trim()
            except IOError:
                pass
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

