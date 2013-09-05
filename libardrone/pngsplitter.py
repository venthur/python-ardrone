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
Splits a stream of PNGs into individual files.
"""

import struct
import time

"""
Usage: Call put_data repeatedly. An array of PNG files will be returned each time you call it.
"""
class PNGSplitter(object):

    def __init__(self, listener):
        self.buffer = ""
        self.offset         = 0;
        self.pngStartOffset = None
        self.state          = self.handle_header
        self.chunk          = None
        self.listener       = listener
        self.data_size      = 0
        self.init_time = time.time()

    """
    Write some data.
    """
    def write(self, data):
        self.data_size += len(data)
        self.buffer += data
        while True:
            (found_png, made_progress) = self.state()
            if found_png:
                self.listener.image_ready(self.buffer[0:self.offset])
                self.buffer = self.buffer[self.offset:] 
                self.offset = 0
                self.state = self.handle_header
            if not made_progress:
                return

    def handle_header(self):
        self.pngStartOffset = self.offset
        if self.fewer_remaining_than(8):
            return (False, False)
        self.offset += 8
        self.state = self.handle_chunk_header
        return (False, True)

    def handle_chunk_header(self):
        if self.fewer_remaining_than(8):
            return (False, False)
        self.state = self.handle_chunk_data
        self.chunk = struct.unpack( ">I4s", self.buffer[self.offset:(self.offset + 8)])
        self.offset += 8
        return (False, True)

    def handle_chunk_data(self):
        chunk_size = self.chunk[0] + 4
        if self.fewer_remaining_than(chunk_size):
            return (False, False)
        self.offset += chunk_size
        if self.chunk[1] == "IEND":
            return (True, True)
        else:
            self.state = self.handle_chunk_header
            return (False, True)

    def fewer_remaining_than(self, desired_size):
        return len(self.buffer) < self.offset + desired_size
