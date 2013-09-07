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
Python library for the AR.Drone.

V.1 This module was tested with Python 2.6.6 and AR.Drone vanilla firmware 1.5.1.
V.2.alpha
"""

import copy
import logging
import socket
import struct
import sys
import threading
import multiprocessing

import arnetwork

import time
import numpy as np
from mutex import mutex

__author__ = "Bastian Venthur"

ARDRONE_NAVDATA_PORT = 5554
ARDRONE_VIDEO_PORT = 5555
ARDRONE_COMMAND_PORT = 5556
ARDRONE_CONTROL_PORT = 5559

SESSION_ID = "943dac23"
USER_ID = "36355d78"
APP_ID = "21d958e4"

DEBUG = False


class ARDrone(object):
    """ARDrone Class.

    Instanciate this class to control your drone and receive decoded video and
    navdata.
    Possible value for video codec (drone2):
      NULL_CODEC    = 0,
      UVLC_CODEC    = 0x20,       // codec_type value is used for START_CODE
      P264_CODEC    = 0x40,
      MP4_360P_CODEC = 0x80,
      H264_360P_CODEC = 0x81,
      MP4_360P_H264_720P_CODEC = 0x82,
      H264_720P_CODEC = 0x83,
      MP4_360P_SLRS_CODEC = 0x84,
      H264_360P_SLRS_CODEC = 0x85,
      H264_720P_SLRS_CODEC = 0x86,
      H264_AUTO_RESIZE_CODEC = 0x87,    // resolution is automatically adjusted according to bitrate
      MP4_360P_H264_360P_CODEC = 0x88,
    """

    def __init__(self, is_ar_drone_2=False):

        self.seq_nr = 1
        self.timer_t = 0.2
        self.com_watchdog_timer = threading.Timer(self.timer_t, self.commwdg)
        self.lock = threading.Lock()
        self.speed = 0.2

        time.sleep(0.5)
        self.config_ids_string = [SESSION_ID, USER_ID, APP_ID]
        self.configure_multisession(SESSION_ID, USER_ID, APP_ID, self.config_ids_string)
        self.set_session_id (self.config_ids_string, SESSION_ID)
        time.sleep(0.5)
        self.set_profile_id(self.config_ids_string, USER_ID)
        time.sleep(0.5)
        self.set_app_id(self.config_ids_string, APP_ID)
        time.sleep(0.5)
        self.set_video_bitrate_control_mode(self.config_ids_string, "1")
        time.sleep(0.5)
        self.set_video_bitrate(self.config_ids_string, "10000")
        time.sleep(0.5)
        self.set_max_bitrate(self.config_ids_string, "10000")
        time.sleep(0.5)
        self.set_fps(self.config_ids_string, "30")
        time.sleep(0.5)
        self.set_video_codec(self.config_ids_string, 0x81)

        self.last_command_is_hovering = True
        self.nav_pipe, nav_pipe_other = multiprocessing.Pipe()
        self.com_pipe, com_pipe_other = multiprocessing.Pipe()

        self.network_process = arnetwork.ARDroneNetworkProcess(nav_pipe_other, com_pipe_other, is_ar_drone_2, self)
        self.network_process.start()

        self.ipc_thread = arnetwork.IPCThread(self)
        self.ipc_thread.start()

        self.image_shape = (360, 640, 3)
        self.image = np.zeros(self.image_shape, np.uint8)
        self.navdata = dict()
        self.navdata[0] = dict(zip(['ctrl_state', 'battery', 'theta', 'phi', 'psi', 'altitude', 'vx', 'vy', 'vz', 'num_frames'], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
        self.time = 0

        self.last_command_is_hovering = True

        time.sleep(1.0)

        self.at(at_config_ids , self.config_ids_string)
        self.at(at_config, "general:navdata_demo", "TRUE")


    def takeoff(self):
        """Make the drone takeoff."""
        self.at(at_ftrim)
        self.at(at_config, "control:altitude_max", "20000")
        self.at(at_ref, True)

    def land(self):
        """Make the drone land."""
        self.at(at_ref, False)

    def hover(self):
        """Make the drone hover."""
        self.at(at_pcmd, False, 0, 0, 0, 0)

    def move_left(self):
        """Make the drone move left."""
        self.at(at_pcmd, True, -self.speed, 0, 0, 0)

    def move_right(self):
        """Make the drone move right."""
        self.at(at_pcmd, True, self.speed, 0, 0, 0)

    def move_up(self):
        """Make the drone rise upwards."""
        self.at(at_pcmd, True, 0, 0, self.speed, 0)

    def move_down(self):
        """Make the drone decent downwards."""
        self.at(at_pcmd, True, 0, 0, -self.speed, 0)

    def move_forward(self):
        """Make the drone move forward."""
        self.at(at_pcmd, True, 0, -self.speed, 0, 0)

    def move_backward(self):
        """Make the drone move backwards."""
        self.at(at_pcmd, True, 0, self.speed, 0, 0)

    def turn_left(self):
        """Make the drone rotate left."""
        self.at(at_pcmd, True, 0, 0, 0, -self.speed)

    def turn_right(self):
        """Make the drone rotate right."""
        self.at(at_pcmd, True, 0, 0, 0, self.speed)

    def reset(self):
        """Toggle the drone's emergency state."""
        self.at(at_ref, False, True)
        self.at(at_ref, False, False)

    def trim(self):
        """Flat trim the drone."""
        self.at(at_ftrim)

    def set_speed(self, speed):
        """Set the drone's speed.

        Valid values are floats from [0..1]
        """
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

    def configure_multisession(self, session_id, user_id, app_id, config_ids_string):
        self.at(at_config, "custom:session_id", session_id)
        self.at(at_config, "custom:profile_id", user_id)
        self.at(at_config, "custom:application_id", app_id)

    def set_session_id (self, config_ids_string, session_id):
        self.at(at_config_ids , config_ids_string)
        self.at(at_config, "custom:session_id", session_id)

    def set_profile_id (self, config_ids_string, profile_id):
        self.at(at_config_ids , config_ids_string)
        self.at(at_config, "custom:profile_id", profile_id)

    def set_app_id (self, config_ids_string, app_id):
        self.at(at_config_ids , config_ids_string)
        self.at(at_config, "custom:application_id", app_id)

    def set_video_bitrate_control_mode (self, config_ids_string, mode):
        self.at(at_config_ids , config_ids_string)
        self.at(at_config, "video:bitrate_control_mode", mode)

    def set_video_bitrate (self, config_ids_string, bitrate):
        self.at(at_config_ids , config_ids_string)
        self.at(at_config, "video:bitrate", bitrate)

    def set_max_bitrate(self, config_ids_string, max_bitrate):
        self.at(at_config_ids , config_ids_string)
        self.at(at_config, "video:max_bitrate", max_bitrate)

    def set_fps (self, config_ids_string, fps):
        self.at(at_config_ids , config_ids_string)
        self.at(at_config, "video:codec_fps", fps)

    def set_video_codec (self, config_ids_string, codec):
        self.at(at_config_ids , config_ids_string)
        self.at(at_config, "video:video_codec", codec)

    def commwdg(self):
        """Communication watchdog signal.

        This needs to be send regulary to keep the communication w/ the drone
        alive.
        """
        self.at(at_comwdg)

    def halt(self):
        """Shutdown the drone.

        This method does not land or halt the actual drone, but the
        communication with the drone. You should call it at the end of your
        application to close all sockets, pipes, processes and threads related
        with this object.
        """
        self.lock.acquire()
        self.com_watchdog_timer.cancel()
        self.com_pipe.send('die!')
        self.network_process.terminate()
        self.network_process.join()
        self.ipc_thread.stop()
        self.ipc_thread.join()
        self.lock.release()

    def get_image(self):
        _im = np.copy(self.image)
        return _im

    def get_navdata(self):
        _navdata = copy.deepcopy(self.navdata)
        return _navdata

    def set_navdata(self, _navdata):
        self.navdata = _navdata

    def set_image(self, image):
        if (image.shape == self.image_shape):
            self.image = image
        self.image = image

    def apply_command(self, command):
        available_commands = ["emergency",
        "land", "takeoff", "move_left", "move_right", "move_down", "move_up",
        "move_backward", "move_forward", "turn_left", "turn_right", "hover"]
        if command not in available_commands:
            logging.error("Command %s is not a recognized command" % command)

        if command != "hover":
            self.last_command_is_hovering = False

        if (command == "emergency"):
            self.reset()
        elif (command == "land"):
            self.land()
            self.last_command_is_hovering = True
        elif (command == "takeoff"):
            self.takeoff()
            self.last_command_is_hovering = True
        elif (command == "move_left"):
            self.move_left()
        elif (command == "move_right"):
            self.move_right()
        elif (command == "move_down"):
            self.move_down()
        elif (command == "move_up"):
            self.move_up()
        elif (command == "move_backward"):
            self.move_backward()
        elif (command == "move_forward"):
            self.move_forward()
        elif (command == "turn_left"):
            self.turn_left()
        elif (command == "turn_right"):
            self.turn_right()
        elif (command == "hover" and not self.last_command_is_hovering):
            self.hover()
            self.last_command_is_hovering = True

class ARDrone2(ARDrone):
    def __init__(self):
        ARDrone.__init__(self, True)

###############################################################################
### Low level AT Commands
###############################################################################

def at_ref(seq, takeoff, emergency=False):
    """
    Basic behaviour of the drone: take-off/landing, emergency stop/reset)

    Parameters:
    seq -- sequence number
    takeoff -- True: Takeoff / False: Land
    emergency -- True: Turn off the engines
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
    at("FTRIM", seq, [])

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
    """Set configuration parameters of the drone."""
    at("CONFIG", seq, [str(option), str(value)])

def at_config_ids(seq, value):
    """Set configuration parameters of the drone."""
    at("CONFIG_IDS", seq, value)

def at_ctrl(seq, num):
    """Ask the parrot to drop its configuration file"""
    at("CTRL", seq, [num, 0])

def at_comwdg(seq):
    """
    Reset communication watchdog.
    """
    # FIXME: no sequence number
    at("COMWDG", seq, [])

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
    raise NotImplementedError()

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

###############################################################################
### navdata
###############################################################################
def decode_navdata(packet):
    """Decode a navdata packet."""
    offset = 0
    _ = struct.unpack_from("IIII", packet, offset)
    drone_state = dict()
    drone_state['fly_mask'] = _[1] & 1 # FLY MASK : (0) ardrone is landed, (1) ardrone is flying
    drone_state['video_mask'] = _[1] >> 1 & 1 # VIDEO MASK : (0) video disable, (1) video enable
    drone_state['vision_mask'] = _[1] >> 2 & 1 # VISION MASK : (0) vision disable, (1) vision enable */
    drone_state['control_mask'] = _[1] >> 3 & 1 # CONTROL ALGO (0) euler angles control, (1) angular speed control */
    drone_state['altitude_mask'] = _[1] >> 4 & 1 # ALTITUDE CONTROL ALGO : (0) altitude control inactive (1) altitude control active */
    drone_state['user_feedback_start'] = _[1] >> 5 & 1 # USER feedback : Start button state */
    drone_state['command_mask'] = _[1] >> 6 & 1 # Control command ACK : (0) None, (1) one received */
    drone_state['fw_file_mask'] = _[1] >> 7 & 1 # Firmware file is good (1) */
    drone_state['fw_ver_mask'] = _[1] >> 8 & 1 # Firmware update is newer (1) */
    drone_state['fw_upd_mask'] = _[1] >> 9 & 1 # Firmware update is ongoing (1) */
    drone_state['navdata_demo_mask'] = _[1] >> 10 & 1 # Navdata demo : (0) All navdata, (1) only navdata demo */
    drone_state['navdata_bootstrap'] = _[1] >> 11 & 1 # Navdata bootstrap : (0) options sent in all or demo mode, (1) no navdata options sent */
    drone_state['motors_mask'] = _[1] >> 12 & 1 # Motor status : (0) Ok, (1) Motors problem */
    drone_state['com_lost_mask'] = _[1] >> 13 & 1 # Communication lost : (1) com problem, (0) Com is ok */
    drone_state['vbat_low'] = _[1] >> 15 & 1 # VBat low : (1) too low, (0) Ok */
    drone_state['user_el'] = _[1] >> 16 & 1 # User Emergency Landing : (1) User EL is ON, (0) User EL is OFF*/
    drone_state['timer_elapsed'] = _[1] >> 17 & 1 # Timer elapsed : (1) elapsed, (0) not elapsed */
    drone_state['angles_out_of_range'] = _[1] >> 19 & 1 # Angles : (0) Ok, (1) out of range */
    drone_state['ultrasound_mask'] = _[1] >> 21 & 1 # Ultrasonic sensor : (0) Ok, (1) deaf */
    drone_state['cutout_mask'] = _[1] >> 22 & 1 # Cutout system detection : (0) Not detected, (1) detected */
    drone_state['pic_version_mask'] = _[1] >> 23 & 1 # PIC Version number OK : (0) a bad version number, (1) version number is OK */
    drone_state['atcodec_thread_on'] = _[1] >> 24 & 1 # ATCodec thread ON : (0) thread OFF (1) thread ON */
    drone_state['navdata_thread_on'] = _[1] >> 25 & 1 # Navdata thread ON : (0) thread OFF (1) thread ON */
    drone_state['video_thread_on'] = _[1] >> 26 & 1 # Video thread ON : (0) thread OFF (1) thread ON */
    drone_state['acq_thread_on'] = _[1] >> 27 & 1 # Acquisition thread ON : (0) thread OFF (1) thread ON */
    drone_state['ctrl_watchdog_mask'] = _[1] >> 28 & 1 # CTRL watchdog : (1) delay in control execution (> 5ms), (0) control is well scheduled */
    drone_state['adc_watchdog_mask'] = _[1] >> 29 & 1 # ADC Watchdog : (1) delay in uart2 dsr (> 5ms), (0) uart2 is good */
    drone_state['com_watchdog_mask'] = _[1] >> 30 & 1 # Communication Watchdog : (1) com problem, (0) Com is ok */
    drone_state['emergency_mask'] = _[1] >> 31 & 1 # Emergency landing : (0) no emergency, (1) emergency */
    data = dict()
    data['drone_state'] = drone_state
    data['header'] = _[0]
    data['seq_nr'] = _[2]
    data['vision_flag'] = _[3]
    offset += struct.calcsize("IIII")
    has_flying_information = False
    while 1:
        try:
            id_nr, size = struct.unpack_from("HH", packet, offset)
            offset += struct.calcsize("HH")
        except struct.error:
            break
        values = []
        for i in range(size - struct.calcsize("HH")):
            values.append(struct.unpack_from("c", packet, offset)[0])
            offset += struct.calcsize("c")
        # navdata_tag_t in navdata-common.h
        if id_nr == 0:
            has_flying_information = True
            values = struct.unpack_from("IIfffifffI", "".join(values))
            values = dict(zip(['ctrl_state', 'battery', 'theta', 'phi', 'psi', 'altitude', 'vx', 'vy', 'vz', 'num_frames'], values))
            # convert the millidegrees into degrees and round to int, as they
            # are not so precise anyways
            for i in 'theta', 'phi', 'psi':
                values[i] = int(values[i] / 1000)
        data[id_nr] = values



    return data, has_flying_information


if __name__ == "__main__":
    '''
    For testing purpose only
    '''
    import termios
    import fcntl
    import os

    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    drone = ARDrone(is_ar_drone_2=True)

    import cv2
    try:
        startvideo = True
        video_waiting = False
        while 1:
            time.sleep(.0001)
            if startvideo:
                try:
                    cv2.imshow("Drone camera", cv2.cvtColor(drone.get_image(), cv2.COLOR_BGR2RGB))
                    cv2.waitKey(1)
                except:
                    if not video_waiting:
                        print "Video will display when ready"
                    video_waiting = True
                    pass

            try:
                c = sys.stdin.read(1)
                c = c.lower()
                print "Got character", c
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
                if c == 'i':
                    startvideo = True
                    try:
                        navdata = drone.get_navdata()

                        print 'Emergency landing =', navdata['drone_state']['emergency_mask']
                        print 'User emergency landing = ', navdata['drone_state']['user_el']
                        print 'Navdata type= ', navdata['drone_state']['navdata_demo_mask']
                        print 'Altitude= ', navdata[0]['altitude']
                        print 'video enable= ', navdata['drone_state']['video_mask']
                        print 'vision enable= ', navdata['drone_state']['vision_mask']
                        print 'command_mask= ', navdata['drone_state']['command_mask']
                    except:
                        pass

                if c == 'j':
                    print "Asking for configuration..."
                    drone.at(at_ctrl, 5)
                    time.sleep(0.5)
                    drone.at(at_ctrl, 4)
            except IOError:
                pass
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
        drone.halt()

