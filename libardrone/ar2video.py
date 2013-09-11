#!/usr/bin/env python

# Copyright (c) 2011 Bastian Venthur
# Copyright (c) 2013 Adrian Taylor
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
Video decoding for the AR.Drone 2.0.

This is just H.264 encapsulated in a funny way.
"""

import h264decoder
import paveparser


class ARVideo2(object):
    def __init__(self, drone, debug=False):
        self.h264 = h264decoder.H264Decoder(self, drone.image_shape)
        self.paveparser = paveparser.PaVEParser(self.h264)
        self.latest_image = None
        self._drone = drone

    """
    Called by the PNG splitter when there's an image ready
    """
    def image_ready(self, image):
        self.latest_image = image
        self._drone.set_image(image)

    """
    Guaranteed to return an image as a PIL Image object.
    """
    def get_image(self):
        return self.latest_image

    def write(self, data):
        self.paveparser.write(data)
