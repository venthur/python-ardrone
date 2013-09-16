# -*- coding: utf-8 -*-
# Copyright (c) 2013 Adrian Taylor
# Inspired by equivalent node.js code by Felix Geisendörfer
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
import os


"""
H.264 video decoder for AR.Drone 2.0. Uses ffmpeg.
"""

import sys
from subprocess import PIPE, Popen
from threading  import Thread
import time
import libardrone
import ctypes
import numpy as np
import sys


try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names


def enqueue_output(out, outfileobject, frame_size):
    frame_size_bytes = frame_size[0] * frame_size[1] * 3
    while True:
        buffer_str = out.read(frame_size_bytes)
        im = np.frombuffer(buffer_str, count=frame_size_bytes, dtype=np.uint8)
        im = im.reshape((frame_size[0], frame_size[1], 3))
        outfileobject.image_ready(im)


# Logic for making ffmpeg terminate on the death of this process
def set_death_signal(signal):
    libc = ctypes.CDLL('libc.so.6')
    PR_SET_DEATHSIG = 1
    libc.prctl(PR_SET_DEATHSIG, signal)


def set_death_signal_int():
    if sys.platform != 'darwin':
        SIGINT = 2
        SIGTERM = 15
        set_death_signal(SIGINT)


"""
Usage: pass a listener, with a method 'data_ready' which will be called whenever there's output
from ffmpeg. This will be called in an arbitrary thread. You can later call H264ToPng.get_data_if_any to retrieve
said data.
You should then call write repeatedly to write some encoded H.264 data.
"""
class H264Decoder(object):

    def __init__(self, outfileobject=None, frame_size=(360, 640)):
        if outfileobject is not None:

            if (H264Decoder.which('ffmpeg') is None):
                raise Exception("You need to install ffmpeg to be able to run ardrone")

            p = Popen(["nice", "-n", "15", "ffmpeg", "-i", "-", "-f", "sdl",
                       "-probesize", "2048", "-flags", "low_delay", "-f",
                       "rawvideo", "-pix_fmt", 'rgb24', "-"],
                      stdin=PIPE, stdout=PIPE, stderr=open('/dev/null', 'w'),
                      bufsize=0, preexec_fn=set_death_signal_int)
            t = Thread(target=enqueue_output, args=(p.stdout, outfileobject, frame_size))
            t.daemon = True # thread dies with the program
            t.start()
        else:
            if (H264Decoder.which('ffplay') is None):
                raise Exception("You need to install ffmpeg and ffplay to be able to run ardrone in debug mode")

            p = Popen(["nice", "-n", "15", "ffplay", "-probesize", "2048",
                       "-flags", "low_delay", "-i", "-"],
                      stdin=PIPE, stdout=open('/dev/null', 'w'),
                      stderr=open('/dev/null', 'w'), bufsize=-1,
                      preexec_fn=set_death_signal_int)

        self.writefd = p.stdin

    def write(self, data):
        self.writefd.write(data)

    @staticmethod
    def which(program):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        return None
