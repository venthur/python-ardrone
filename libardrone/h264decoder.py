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


"""
H.264 video decoder for AR.Drone 2.0. Uses ffmpeg.
"""

import sys
from subprocess import PIPE, Popen
from threading  import Thread
import time
import libardrone
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, outfileobject):
    while True:
        r = out.read(65536)
        outfileobject.write(r)

"""
Usage: pass a listener, with a method 'data_ready' which will be called whenever there's output
from ffmpeg. This will be called in an arbitrary thread. You can later call H264ToPng.get_data_if_any to retrieve
said data.
You should then call write repeatedly to write some encoded H.264 data.
"""
class H264ToPNG(object):
    def __init__(self, outfileobject=None):
        if outfileobject is not None:
            p = Popen(["nice", "-n", "15", "ffmpeg", "-i", "-", "-f", "sdl", "-probesize", "2048", "-flags", "low_delay", "-f", "image2pipe", "-vcodec", libardrone.IMAGE_ENCODING, "-"], stdin=PIPE, stdout=PIPE, stderr=open('/dev/null', 'w'))
            t = Thread(target=enqueue_output, args=(p.stdout, outfileobject))
            t.daemon = True # thread dies with the program
            t.start()
        else:
            p = Popen(["nice", "-n", "15", "ffplay", "-probesize", "2048", "-flags", "low_delay", "-i", "-"], stdin=PIPE, stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))

        self.writefd = p.stdin

    def write(self, data):
        self.writefd.write(data)
