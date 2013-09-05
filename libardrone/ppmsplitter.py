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
Splits a stream of PPMs into individual files.
Usage: Call put_data repeatedly. An array of PNG files will be returned each time you call it.
"""
class PPMSplitter(object):

    def __init__(self, listener):
        self.buffer = ""
        self.offset = 0;
        self.listener       = listener

    def write(self, data):
        self.buffer += data
        index = 1
        image_found = False
        while index > 0:
            index = self.buffer[self.offset + 1:].find('P6\n')
            if index >= 1:
                index += self.offset + 1
                image_found = True
                image_buffered = self.buffer[0:index]
                self.buffer = self.buffer[index:]
                self.offset = 0
        if image_found:
            self.listener.image_ready(image_buffered)
        else:
            self.offset += len(data)
