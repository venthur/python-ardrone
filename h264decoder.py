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
try:
    from Queue import Queue, Empty
except ImportError:
	from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue, outfileobject):
    for d in iter(out.read, b''):
        outfileobject.write(d)
    out.close()

"""
Usage: pass a listener, with a method 'data_ready' which will be called whenever there's output
from ffmpeg. This will be called in an arbitrary thread. You can later call H264ToPng.get_data_if_any to retrieve
said data.
You should then call write repeatedly to write some encoded H.264 data.
"""
class H264ToPNG:

	def __init__(self, outfileobject):
		p = Popen(["ffmpeg", "-i", "-", "-f", "image2pipe", "-vcodec", "png", "-r", "5", "-"], stdin=PIPE, stdout=PIPE)
		self.writefd = p.stdin
		self.q = Queue()
		t = Thread(target=enqueue_output, args=(p.stdout, q, outfileobject))
		t.daemon = True # thread dies with the program
		t.start()

	def write(self, data):
		self.writefd.write(data)
